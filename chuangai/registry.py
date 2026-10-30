"""The registry is the single source of truth.

  tasks.yaml   poster rows, GPU preference, PHI promise
  models.yaml  what each alias is and where it can run
  hosts.yaml   lanes, queues, images, paths

Everything user-facing -- the poster, the CLI, the LSF file -- is generated
from these three files. Nothing else may hard-code a model name, a queue, or
a path.
"""

from __future__ import annotations

import functools
import pathlib

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1] / "registry"


def _load(name: str) -> dict:
    path = ROOT / f"{name}.yaml"
    try:
        with open(path) as fh:
            return yaml.safe_load(fh) or {}
    except FileNotFoundError:
        raise SystemExit(f"missing registry file: {path}")
    except yaml.YAMLError as exc:
        raise SystemExit(f"{path} is not valid YAML:\n{exc}")


@functools.lru_cache(maxsize=None)
def _tasks() -> tuple[dict, ...]:
    return tuple(_load("tasks")["tasks"])


@functools.lru_cache(maxsize=None)
def _models() -> dict:
    return {m["id"]: m for m in _load("models")["models"]}


@functools.lru_cache(maxsize=None)
def _hosts() -> dict:
    return _load("hosts")["hosts"]


@functools.lru_cache(maxsize=None)
def _aliases() -> dict:
    out = {}
    for r in _tasks():
        for a in r.get("aliases", []):
            out[a] = r["id"]
    return out


def tasks() -> list[dict]:
    return list(_tasks())


def row_ids() -> list[str]:
    return [r["id"] for r in _tasks()]


def canonical_row(name: str) -> str:
    name = name.strip().lower()
    if name in row_ids():
        return name
    try:
        return _aliases()[name]
    except KeyError:
        raise KeyError(name)


def row(rid: str) -> dict:
    rid = canonical_row(rid)
    for r in _tasks():
        if r["id"] == rid:
            out = dict(r)
            out.setdefault("kind", "job")
            out.setdefault("lane", "burst")
            return out
    raise KeyError(rid)  # unreachable


def model(mid: str) -> dict:
    try:
        return dict(_models()[mid])
    except KeyError:
        known = ", ".join(sorted(_models()))
        raise SystemExit(f"unknown model '{mid}' (known: {known})")


def host(name: str) -> dict:
    try:
        h = dict(_hosts()[name])
    except KeyError:
        known = ", ".join(sorted(_hosts()))
        raise SystemExit(f"unknown lane '{name}' (known: {known})")
    h.setdefault("mem", "120GB")
    h.setdefault("walltime", "12:00")
    h.setdefault("cores", 8)
    return h


def validate() -> list[str]:
    """Return a list of problems; empty means the registry is coherent."""
    problems = []

    # Model level: `served` keys job names, ports and opencode model ids,
    # so it must be present and unique.
    seen: dict[str, str] = {}
    for mid, m in _models().items():
        s = m.get("served")
        if not s:
            problems.append(f"models: {mid} has no served name")
        elif s in seen:
            problems.append(f"models: duplicate served name '{s}' ({seen[s]}, {mid})")
        else:
            seen[s] = mid
        if "reasoning" in m and not m["reasoning"]:
            problems.append(f"models: {mid} sets reasoning but it is empty")

    for r in _tasks():
        if r.get("kind") in ("web", "human"):
            continue
        if r.get("recipe") not in (None, "train", "index"):
            problems.append(f"{r['id']}: unknown recipe '{r['recipe']}'")
        try:
            m = model(r["model"])
        except SystemExit as exc:
            problems.append(f"{r['id']}: {exc}")
            continue
        try:
            h = host(r["lane"])
        except SystemExit as exc:
            problems.append(f"{r['id']}: {exc}")
            continue
        if r.get("phi_ok") and not h.get("phi_safe"):
            problems.append(
                f"{r['id']}: promises PHI but lane '{r['lane']}' is not phi_safe"
            )
        min_gpus = m.get("min_gpus", 1)
        if r.get("gpus", min_gpus) < min_gpus:
            problems.append(
                f"{r['id']}: gpus {r.get('gpus')} < min_gpus {min_gpus} for {m['id']}"
            )
        prefs = r.get("gpu_pref", [])
        bad = [g for g in prefs if g not in m["gpus_ok"]]
        if bad:
            problems.append(f"{r['id']}: {m['id']} cannot run on {', '.join(bad)}")
        if h["scheduler"] == "lsf":
            unknown = [g for g in prefs if g not in h["gpu_res"]]
            if unknown:
                problems.append(
                    f"{r['id']}: no LSF resource token for {', '.join(unknown)}"
                )

    return problems
