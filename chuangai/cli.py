"""chuangai -- one command per row on the poster."""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import socket
import sys
import time

from . import opencode
from . import plan as planner
from . import probe, registry, render

STALE_S = 86400
RUNNING = ("RUN", "USUSP", "SSUSP")

# --------------------------------------------------------------------------
# parsers
# --------------------------------------------------------------------------


def _row_flags(p: argparse.ArgumentParser) -> None:
    p.add_argument("--gpu", help="force a card (l40s, h100nvl, b200, ...)")
    p.add_argument("--phi", action="store_true", help="this is PHI")
    p.add_argument("--force", action="store_true", help="ignore running servers")
    p.add_argument(
        "--allow-b200", action="store_true", help="permit the scarce B200 lane"
    )
    p.add_argument(
        "--dry-run", action="store_true", help="write the LSF file, do not submit"
    )


def _p_row() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="chuangai", add_help=True)
    _row_flags(p)
    return p


def _p_status() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="chuangai status")
    p.add_argument(
        "--check", action="store_true", help="TCP-probe each published server"
    )
    return p


def _p_reap() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="chuangai reap")
    p.add_argument("--older-than", type=float, default=24, metavar="HOURS")
    return p


# --------------------------------------------------------------------------
# shared state dir
# --------------------------------------------------------------------------


def _state_dir() -> pathlib.Path:
    return pathlib.Path(registry.host("burst")["state_dir"])


def _scripts_dir() -> pathlib.Path:
    """Per-user, outside the user's project folder (see probe.STATE)."""
    d = probe.STATE / "scripts"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _records() -> list[tuple[float, dict]]:
    sd, now, out = _state_dir(), time.time(), []
    if not sd.is_dir():
        return out
    for f in sorted(sd.glob("*.json")):
        try:
            out.append((now - f.stat().st_mtime, json.loads(f.read_text())))
        except (ValueError, OSError):
            continue
    return out


# --------------------------------------------------------------------------
# commands
# --------------------------------------------------------------------------


def cmd_help() -> int:
    print("chuangai -- pick the row that matches what you want to do\n")
    for r in registry.tasks():
        print(f"  chuangai {r['id']:<10} {r['label']}  [{r['wait']}]")
    print("\n  chuangai status            what is running right now")
    print("  chuangai reap              clear stale records")
    print("  chuangai list              show rows and verify the registry")
    print("\n  laptop:  ~/chuangai/bin/connect [model]    tunnel + opencode")
    return 0


def cmd_list() -> int:
    for r in registry.tasks():
        kind = r["kind"]
        extra = ""
        if kind == "job":
            extra = (
                f"{r.get('lane', 'burst'):<8} "
                f"{','.join(r.get('gpu_pref', ['cpu']))}"
            )
        print(f"  {r['id']:<10} {kind:<6} {r['label']:<34} {extra}")
    problems = registry.validate()
    if problems:
        print("\n  registry problems:")
        for p in problems:
            print(f"    - {p}")
        return 1
    print("\n  registry OK")
    return 0


def cmd_status(a) -> int:
    live, stale = [], []
    for age, d in _records():
        (stale if age > STALE_S else live).append((age, d))

    if not live:
        print("  no live servers published.")
    for age, d in sorted(live, key=lambda t: t[0]):
        tag = ""
        if a.check:
            try:
                socket.create_connection((d["host"], int(d["port"])), timeout=2).close()
                tag = "  reachable"
            except OSError:
                tag = "  UNREACHABLE"
        print(
            f"  {d.get('model', '?'):<16} {d.get('gpu', '?'):<8} "
            f"{d.get('gpus', '?')}x  {d.get('host', '?'):<9} "
            f"{time.strftime('%Hh%M', time.gmtime(age)):>7}  "
            f"{d.get('user', '?')}@{d.get('host')}:{d.get('port')}{tag}"
        )
    if stale:
        print(f"  ({len(stale)} record(s) older than 24h -- `chuangai reap`)")

    # our own jobs; first sight of RUN closes out the wait measurement
    mine = [j for j in probe.my_jobs() if j["name"].startswith("chuangai_")]
    for j in mine:
        if j["stat"] in RUNNING:
            probe.record_start(j["id"])
    if mine:
        print("\n  your jobs:")
        for j in mine:
            print(f"    {j['id']}  {j['stat']:<8} {j['exec_host']:<18} {j['name']}")
    return 0


def cmd_reap(a) -> int:
    sd = _state_dir()
    if not sd.is_dir():
        print("nothing to reap")
        return 0
    cutoff, removed = time.time() - a.older_than * 3600, 0
    for f in sd.glob("*.json"):
        if f.stat().st_mtime < cutoff:
            f.unlink()
            removed += 1
    print(f"removed {removed} stale record(s)")
    return 0


def _submit(p, script: pathlib.Path) -> str:
    rc, out, err = probe.sh(f"bsub < {script}")
    if rc != 0:
        raise SystemExit(f"bsub failed:\n{err or out}")
    m = re.search(r"Job <(\d+)>", out)
    if not m:
        raise SystemExit(f"could not read a job id from bsub output:\n{out}")
    job_id = m.group(1)
    probe.record_submit(p.model["served"], p.gpu, job_id)
    return job_id


def launch(rid: str, a) -> int:
    r = registry.row(rid)

    # --- dispatch on kind before planning; web/human rows have no model ---
    if r["kind"] == "web":
        print(f"Open: {r['url']}")
        print("(Microsoft login required)")
        return 0
    if r["kind"] == "human":
        print(f"This one needs {r.get('who', 'Chris')}. Send:")
        print(f"  - what you ran: chuangai {rid}")
        print("  - what you expected")
        print("  - what you got, and the input that broke it")
        return 0

    p = planner.plan(
        rid, gpu=a.gpu, phi=a.phi, force=a.force, allow_b200=a.allow_b200
    )

    # --- always-on lane: there is no job to submit ---
    if p.scheduler == "none":
        path = opencode.write(p)
        print(f"{rid}: {p.model['served']} on {p.host_name}")
        print(f"wrote {path} -- start opencode when you are ready.")
        if p.note:
            print(f"  note: {p.note}")
        return 0

    # --- burst lane: reuse needs no script ---
    if p.job_id:
        print(f"{rid}: reusing {p.job_id} on {p.exec_host}")
        print(f"  laptop:  ~/chuangai/bin/connect {p.model['served']}  # tunnel + opencode")
        return 0

    h = registry.host(p.host_name)
    if not a.dry_run:
        pathlib.Path(h["log_dir"]).mkdir(parents=True, exist_ok=True)
        _state_dir().mkdir(parents=True, exist_ok=True)

    script = _scripts_dir() / f"{planner.job_name(p.model['served'], p.gpu, p.gpus)}.lsf"
    render.render(p, script)

    if p.template in ("train", "index"):
        print(f"{rid}: {p.template} job for {p.model['served']}")
        print(f"  script: {script}")
        if a.dry_run:
            print(f"  submit: bsub < {script}")
            return 0
        job_id = _submit(p, script)
        print(f"  submitted {job_id}")
        print("  watch:  chuangai status")
        return 0

    print(f"{rid}: {p.model['served']} on {p.gpus}x {p.gpu}")
    print(f"  script: {script}")
    if a.dry_run:
        print(f"  submit: bsub < {script}")
        return 0
    job_id = _submit(p, script)
    print(f"  submitted {job_id}")
    print("  next:  chuangai status                    # wait for it to appear")
    print(f"         ~/chuangai/bin/connect {p.model['served']}  # tunnel + opencode (laptop)")
    return 0


# --------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    args = list(argv if argv is not None else sys.argv[1:])
    if not args or args[0] in ("-h", "--help", "help"):
        return cmd_help()

    head, rest = args[0], args[1:]
    if head == "list":
        return cmd_list()
    if head == "status":
        return cmd_status(_p_status().parse_args(rest))
    if head == "reap":
        return cmd_reap(_p_reap().parse_args(rest))

    try:
        rid = registry.canonical_row(head)
    except KeyError:
        print(f"unknown row '{head}'. Try `chuangai help`.")
        return 2
    return launch(rid, _p_row().parse_args(rest))


if __name__ == "__main__":
    raise SystemExit(main())
