"""Probe Minerva for free GPUs and our own jobs, and record how long they waited.

Nothing here may block a submission. If `gpuavail` is missing, renamed, or
prints something unexpected, gpuavail() returns {} and the planner falls back
to static preference order.
"""

from __future__ import annotations

import json
import pathlib
import re
import subprocess
import time

COUNT = re.compile(r"^(\d+)/(\d+)$")

STATE = pathlib.Path.home() / ".local" / "state" / "marais"
WAITS = STATE / "waits.json"  # in-flight submits: jobid -> record
OBSERVED = STATE / "observed.jsonl"  # append-only: one line per job start

# Explicit widths + delimiter: never rely on bjobs default column widths.
BJOBS = (
    "bjobs -noheader "
    "-o 'jobid stat exec_host:40 job_name:80 delimiter=\"|\"' 2>/dev/null"
)


def sh(cmd: str, timeout: int = 20) -> tuple[int, str, str]:
    try:
        p = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=timeout
        )
        return p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired:
        return 124, "", f"timeout after {timeout}s"


def _ensure() -> None:
    STATE.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------------------------------
# our own jobs (bjobs shows only the caller's jobs on Minerva)
# --------------------------------------------------------------------------


def my_jobs() -> list[dict]:
    """[{'id','stat','exec_host','name'}, ...]; [] if bjobs is unavailable."""
    rc, out, _ = sh(BJOBS)
    if rc != 0:
        return []
    rows = []
    for line in out.splitlines():
        f = [x.strip() for x in line.split("|")]
        if len(f) >= 4 and f[0]:
            rows.append({"id": f[0], "stat": f[1], "exec_host": f[2], "name": f[3]})
    return rows


# --------------------------------------------------------------------------
# free cards
# --------------------------------------------------------------------------


def gpuavail() -> dict[str, tuple[int, int]]:
    """{'h100nvl': (9, 188), ...} -- free, total. {} if unreadable."""
    rc, out, _ = sh("gpuavail", timeout=25)
    if rc != 0 or "queue/model" not in out:
        return {}

    lines = [l for l in out.splitlines() if l.strip()]
    cols, body = None, []
    for i, line in enumerate(lines):
        if "queue/model" in line:
            cols = line.split()[1:]
            body = lines[i + 1 :]
            break
    if not cols:
        return {}

    by_queue: dict[str, dict[str, tuple[int, int]]] = {}
    for line in body:
        toks = line.split()
        if len(toks) < len(cols) + 1:
            continue
        queue, vals = toks[0], toks[-len(cols) :]
        if not all(COUNT.match(v) for v in vals):
            continue
        by_queue[queue] = {
            c: tuple(map(int, COUNT.match(v).groups()))  # type: ignore[arg-type]
            for c, v in zip(cols, vals)
        }

    # 'gpu' and 'gpuexpress' mirror the same pool; 'private' is not ours.
    for queue in ("gpu", "gpuexpress", "private"):
        if queue in by_queue:
            return by_queue[queue]
    return {}


# --------------------------------------------------------------------------
# observed waits (our own jobs only -- no cross-user permissions needed)
# --------------------------------------------------------------------------


def record_submit(model: str, gpu: str | None, job_id: str) -> None:
    _ensure()
    data = json.loads(WAITS.read_text()) if WAITS.exists() else {}
    data[job_id] = {"model": model, "gpu": gpu or "cpu", "t": time.time()}
    WAITS.write_text(json.dumps(data, indent=1))


def record_start(job_id: str) -> float | None:
    """Call when one of our jobs is first seen RUN. Returns the wait, seconds.

    Measured to the first `marais status` that sees RUN, so it is an upper
    bound on the true wait.
    """
    if not WAITS.exists():
        return None
    data = json.loads(WAITS.read_text())
    entry = data.pop(job_id, None)
    WAITS.write_text(json.dumps(data, indent=1))
    if not entry:
        return None
    secs = time.time() - entry["t"]
    _ensure()
    with open(OBSERVED, "a") as fh:
        fh.write(
            json.dumps(
                {
                    "gpu": entry["gpu"],
                    "model": entry["model"],
                    "jobid": job_id,
                    "seconds": round(secs, 1),
                }
            )
            + "\n"
        )
    return secs


def recent_waits(gpu: str | None, n: int = 5) -> list[float]:
    if not OBSERVED.exists():
        return []
    out = []
    for line in OBSERVED.read_text().splitlines():
        try:
            rec = json.loads(line)
        except ValueError:
            continue
        if rec.get("gpu") == (gpu or "cpu"):
            out.append(rec["seconds"])
    return out[-n:]


def mean_wait(gpu: str | None) -> float | None:
    """None until we have actually watched a job start on this card."""
    waits = recent_waits(gpu)
    return sum(waits) / len(waits) if waits else None
