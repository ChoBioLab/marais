# Example Workflows

This directory contains ready‑to‑run workflow descriptors for common genomics and bio‑informatics tasks. Each file is a YAML description understood by the `run-workflow` command (or a custom sub‑agent) and demonstrates how to stitch together agents, commands, and Nextflow pipelines.

## Included examples

- **rnaseq-nextflow.yaml** – runs the nfcore/rnaseq pipeline via the `nextflow-launch` command.
- **crispr-nextflow.yaml** – example CRISPR‑screen pipeline using a placeholder nfcore/crispr pipeline.
- **scRNAseq-nextflow.yaml** – launches a single‑cell RNA‑seq analysis pipeline.
- **genomics-workflow.yaml** – a multi‑step workflow that combines literature lookup, experimental design, data analysis, and a design‑review command.

To execute a workflow:
```bash
opencode subagent general "run-workflow @workflows/<workflow‑file>.yaml"
```
Replace `<workflow‑file>` with the desired example.
