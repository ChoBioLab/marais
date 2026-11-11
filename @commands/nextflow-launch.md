---
name: nextflow-launch
description: "High‑level command to launch an nfcore/Nextflow pipeline via the `@agents/nextflow-runner`."
---

# nextflow-launch Command

**Usage**
```
nextflow-launch \
  --pipeline <pipeline>            # e.g. nfcore/rnaseq or a Git repo URL
  --profile <profile>              # Nextflow configuration profile
  --params <path-to-json>          # JSON file with pipeline parameters
  [--resume]                       # Optional flag to resume a previous run
```

The command forwards the arguments to the `nextflow-runner` agent, which runs the pipeline and logs provenance.

**Arguments**
- `pipeline` (string, required): Identifier of the Nextflow pipeline.
- `profile` (string, required): Execution profile (e.g., `docker`, `conda`).
- `params` (string, required): Path to a JSON file containing pipeline parameters.
- `resume` (boolean, optional): If set, adds `--resume` to the Nextflow command.

**Provenance**
Every execution creates a JSON file under `logs/provenance/nextflow/` (see the agent documentation) capturing version, parameters, and timestamps.

**Example**
```bash
nextflow-launch \
  --pipeline nfcore/rnaseq \
  --profile docker \
  --params ./rnaseq_params.json \
  --resume
```

*Implementation* – The command is a thin wrapper that invokes the `nextflow-runner` agent via the OpenCode `subagent` call or direct agent reference, passing the parsed arguments.

*Source* – Inspired by best‑practice pipeline orchestration patterns from the reference architecture (see the plan).