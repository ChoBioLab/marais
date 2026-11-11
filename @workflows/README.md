# Example Workflows

This directory provides ready‑to‑run workflow descriptors (YAML) that can be executed with the generic `run-workflow` sub‑agent. Each workflow stitches together agents, commands, and/or Nextflow pipelines to illustrate common analyses in the lab.

## Included workflows

- **broad‑gene‑disease‑workflow.yaml** – Uses `biomcp` commands to gather gene‑disease association counts, gene information (pathways, druggability, CIViC), candidate drugs targeting the gene for the disease, recruiting clinical trials, and top‑cited articles.
- **genomics‑analysis‑workflow.yaml** – Demonstrates a full analysis loop: literature search via `@agents/literature`, experimental design via `@agents/designer`, bulk RNA‑seq differential expression via `@agents/analyst`, and a design‑review step.
- **rnaseq‑nextflow‑pipeline.yaml** – Launches the `nfcore/rnaseq` pipeline using the `nextflow‑launch` command with Docker profile and a parameter JSON file.
- **scRNAseq‑nextflow‑pipeline.yaml** – Runs the `nfcore/scrna` pipeline similarly, using its own config.
- **crispr‑nextflow‑pipeline.yaml** – Executes the `nfcore/crispr` pipeline via `nextflow‑launch`.
- **variant‑pathogenicity‑workflow.yaml** – Retrieves ClinVar predictions, CIViC CGI data, associated clinical trials, and relevant literature articles for a given variant using `biomcp`.

### How to run a workflow
```bash
opencode subagent general "run-workflow @workflows/<workflow‑file>.yaml"
```
Replace `<workflow‑file>` with the desired YAML file name (e.g., `genomics-analysis-workflow.yaml`).

Each workflow can be customized by editing the YAML (e.g., changing query parameters or pipeline profiles) before execution.
