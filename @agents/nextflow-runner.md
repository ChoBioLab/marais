---
name: nextflow-runner
description: "Wraps the `nextflow run` CLI to execute nfcore pipelines with reproducible provenance logging."
---

# Nextflow Runner Agent

This agent provides a thin wrapper around the Nextflow command‑line interface. It:

1. Accepts a pipeline identifier (e.g., an nfcore module or a GitHub repo URL).
2. Allows the user to specify a profile, parameter JSON, and optional `-resume` flag.
3. Executes `nextflow run <pipeline> -profile <profile> -params-file <json> [--resume]`.
4. Captures the exact Nextflow version, the pipeline’s git commit hash (if applicable), and the full parameter JSON.
5. Writes a provenance JSON entry to `logs/provenance/nextflow/<timestamp>.json` containing:
   ```json
   {"pipeline": "<pipeline>", "profile": "<profile>", "params": {...}, "nextflow_version": "<v>", "pipeline_hash": "<git‑sha>", "timestamp": "<ISO‑8601>"}
   ```

The agent is deliberately minimal – it does **not** install Nextflow or manage containers; those are expected to be present in the environment (via Conda, Docker, or a module system).

*Implementation notes*
- Use the `shell` tool to invoke Nextflow.
- Validate that `nextflow` is on `$PATH`; if not, raise a clear error suggesting installation via Conda (`conda install -c bioconda nextflow`).
- Optionally, if the pipeline is a local directory, compute its Git SHA with `git rev-parse HEAD`.
- All stdout/stderr are captured and returned to the caller for debugging.

*Provenance* – This agent follows the reproducibility recommendations from the reference architecture (see the plan).