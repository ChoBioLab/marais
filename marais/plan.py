"""Decide where a row runs.

Scope limits, deliberate:

* `bjobs` only shows the submitting user's jobs on Minerva, so reuse is
  same-user / same-served / same-gpu / same-count. Cross-user discovery is
  the shared state dir (cli.cmd_status), never `bjobs`.
* Wait telemetry starts empty. Until `marais status` has observed a job go
  PEND -> RUN, `mean_wait` is None and selection is pure preference order.
"""

from __future__ import annotations

import dataclasses

from . import probe, registry

# Explainable wait buckets: 0 = fast enough to keep preference order.
WAIT_BUCKETS = ((1800, 0), (7200, 1))  # <=30m, <=2h, else 2

# Cards `gpuavail` cannot separate: it reports one aggregate `a100` column, so
# 40 GB and 80 GB A100s are indistinguishable. Usable only when named.
UNPROBEABLE = {"a10080g"}


@dataclasses.dataclass
class Plan:
    row: str
    model: dict
    host_name: str
    gpu: str | None
    gpus: int
    base_url: str
    scheduler: str = "lsf"  # 'lsf' | 'none'
    template: str = "serve"  # 'serve' | 'train' | 'index'
    job_id: str | None = None
    exec_host: str | None = None
    note: str = ""


def job_name(served: str, gpu: str | None, gpus: int) -> str:
    # gpus is encoded so a 4-GPU row cannot silently reuse a 2-GPU server.
    # `served` must be unique per model id (see models.yaml).
    return f"marais_{served}_{gpu or 'cpu'}_{gpus}x"


def _running_for(
    served: str, gpu: str | None, gpus: int, jobs: list[dict]
) -> dict | None:
    want = job_name(served, gpu, gpus)
    for j in jobs:
        if j["name"] == want and j["stat"] in ("RUN", "USUSP", "SSUSP"):
            return j
    return None


def _wait_bucket(gpu: str | None) -> int:
    wait = probe.mean_wait(gpu)
    if wait is None:
        return 0
    for limit, bucket in WAIT_BUCKETS:
        if wait <= limit:
            return bucket
    return 2


def _has_room(gpu: str, gpus: int, free: dict, explicit: bool) -> bool:
    if gpu in UNPROBEABLE:
        return explicit  # cannot see it; trust an explicit ask
    if not free:
        return True  # probe down: do not block submission
    return free.get(gpu, (0, 0))[0] >= gpus


def _choose(
    gpus: int, prefs: list[str], m: dict, allow_scarce: bool, explicit: bool
) -> str | None:
    """Preference order is the quality policy; wait time only demotes.

    A card is used if it has room. Among cards with room, the registry's own
    order wins unless observed mean wait puts a card in a worse bucket
    (>30m, >2h).
    """
    allowed = [g for g in prefs if g in m["gpus_ok"] and (g != "b200" or allow_scarce)]
    if not allowed:
        return None
    free = probe.gpuavail()
    avail = [g for g in allowed if _has_room(g, gpus, free, explicit)]
    if not avail:
        return None
    avail.sort(key=lambda g: (_wait_bucket(g), allowed.index(g)))
    return avail[0]


def _template_for(r: dict) -> str:
    if r["kind"] == "job" and "recipe" in r:
        return r["recipe"]  # 'train' | 'index'
    return "serve"


def plan(
    rid: str,
    gpu: str | None = None,
    phi: bool = False,
    force: bool = False,
    allow_b200: bool = False,
) -> Plan:
    r = registry.row(rid)
    m = registry.model(r["model"])
    host_name = r["lane"]
    h = registry.host(host_name)

    # PHI gate checks both sides: the row's promise and the lane's ability
    if phi and not (r.get("phi_ok") and h.get("phi_safe")):
        raise SystemExit(
            f"'{rid}' cannot be used for PHI.\n"
            f"lane '{host_name}' is outside the PHI-safe enclave.\n"
            "Run `marais help` and talk to Chris about an enclave lane."
        )

    template = _template_for(r)

    # --- always-on lane: no scheduler, no substitution, no fallback ---
    if h["scheduler"] == "none":
        rc, _, _ = probe.sh(
            f'curl -sf -m 4 {h["base_url"]}/models '
            f'-H "Authorization: Bearer $(cat {h["keyfile"]})"',
            timeout=8,
        )
        note = "" if rc == 0 else "vLLM on this lane is not answering"
        return Plan(
            rid,
            m,
            host_name,
            None,
            r.get("gpus", 1),
            h["base_url"],
            scheduler="none",
            template="serve",
            note=note,
        )

    # --- CPU-only shapes never enter the GPU queue ---
    if template == "index":
        return Plan(
            rid,
            m,
            host_name,
            None,
            0,
            h["base_url"],
            template="index",
            note="CPU-only job, no GPU requested",
        )

    # --- burst lane ---
    gpus = r.get("gpus", m.get("min_gpus", 1))
    prefs = [gpu] if gpu else list(r["gpu_pref"])
    explicit = gpu is not None
    if gpu == "b200":
        allow_b200 = True

    usable = [
        g
        for g in prefs
        if g in m["gpus_ok"] or (g == "cpu" and m.get("min_gpus", 1) == 0)
    ]
    if not usable:
        raise SystemExit(
            f"{m['hf']} cannot run on any of {prefs} "
            f"(supported: {', '.join(m['gpus_ok'])}).\n"
            "Use --gpu from that list, or a bigger row."
        )

    # reuse before availability, servers only: a training job is never reused
    if not force and template == "serve":
        jobs = probe.my_jobs()
        for g in usable:
            job = _running_for(m["served"], g, gpus, jobs)
            if job:
                return Plan(
                    rid,
                    m,
                    host_name,
                    g,
                    gpus,
                    h["base_url"],
                    template=template,
                    job_id=job["id"],
                    exec_host=job["exec_host"],
                    note="reused running server",
                )

    chosen = _choose(gpus, usable, m, allow_b200, explicit)
    if chosen is None:
        free = probe.gpuavail()
        seen = (
            ", ".join(f"{g}={free.get(g, ('?', '?'))[0]}" for g in usable)
            if free
            else "gpuavail unavailable"
        )
        raise SystemExit(
            f"no card has room for {gpus}x {m['served']} right now ({seen}).\n"
            "  -> `marais status` to see what is running\n"
            "  -> wait and retry, or name a card with --gpu"
        )

    return Plan(
        rid,
        m,
        host_name,
        chosen,
        gpus,
        h["base_url"],
        template=template,
        note=f"will submit {gpus}x {chosen}",
    )
