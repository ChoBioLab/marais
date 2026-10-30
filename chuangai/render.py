"""Render a Plan into a job script.

Two passes: partials first, then the template that includes them. In `.in`
files, lowercase `$vars` are template placeholders and UPPERCASE `$VARS`
belong to the shell -- `safe_substitute` leaves unknown placeholders alone,
which is what lets `$LSB_JOBID` and `$PORT` survive to runtime.

NOTE: `mem` is PER SLOT on Minerva (total = mem * ncpus).
"""

from __future__ import annotations

import pathlib
import string

from . import registry
from .plan import job_name

T = pathlib.Path(__file__).resolve().parents[1] / "templates"

PARTIALS = {
    "serve": ["stage", "health"],
    "train": ["stage"],
    "index": [],
}


def render(p, out_path: pathlib.Path) -> pathlib.Path:
    h = registry.host(p.host_name)
    m = p.model
    nodes = max(1, p.gpus // 4)

    if p.template == "index":
        ncpus = h["cores"]
        image = h["images"]["cpu"]
        queue = h.get("cpu_queue", "express")  # never the GPU queue
    else:
        ncpus = nodes * 8 if p.template == "train" else 2
        image = h["images"]["blackwell" if p.gpu == "b200" else "ada_hopper"]
        queue = h["queues"][0]

    if "<" in image:  # '<confirm>' would be parsed by bash as a redirect
        raise SystemExit(
            f"image path is still a placeholder: {image}\n"
            "Set it in registry/hosts.yaml before using this row."
        )

    # node-local SSD staging is opt-in; only then is ssd_gb requested
    stage_ssd = bool(h.get("stage_ssd")) and p.template in ("serve", "train")
    ssd_res = f",ssd_gb={m['weights_gb'] + 60}" if stage_ssd else ""

    mapping = dict(
        job=job_name(m["served"], p.gpu, p.gpus),
        project=h["project"],
        queue=queue,
        gpu_res=h["gpu_res"].get(p.gpu, "") if p.gpu else "",
        ngpus=p.gpus,
        nodes=nodes,
        ncpus=ncpus,
        tp=p.gpus,
        walltime=h["walltime"],
        mem=h["mem"],
        ssd_res=ssd_res,
        stage_ssd=int(stage_ssd),
        log_dir=h["log_dir"],
        state_dir=h["state_dir"],
        hf_home=h["hf_home"],
        keyfile=h["keyfile"],
        sif=image,
        model_repo=m["hf"],
        model_slug=m["slug"],
        served=m["served"],
        max_len=m["ctx"],
        parser=m["parser"],
        extra=m.get("vllm_extra", ""),
        reasoning=m.get("reasoning", ""),  # raw value, travels in the published record
        reasoning_flag=f"--reasoning-parser {m['reasoning']}" if m.get("reasoning") else "",
    )

    for name in ("stage", "health"):  # blank when not included
        mapping[name.upper()] = ""
    for name in PARTIALS[p.template]:
        tpl = string.Template((T / "partials" / f"{name}.sh.in").read_text())
        mapping[name.upper()] = tpl.safe_substitute(mapping)

    tpl = string.Template((T / f"{p.template}.lsf.in").read_text())
    out_path.write_text(tpl.safe_substitute(mapping))
    out_path.chmod(0o755)
    return out_path
