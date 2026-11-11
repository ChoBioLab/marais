# Agents

This directory contains all built‑in agents that the Marais OpenCode configuration ships. Each markdown file defines an agent’s purpose, mode (primary or sub‑agent), and any permission overrides.

## Available agents

- **analyst** – primary agent that orchestrates data processing pipelines, statistical analyses, and script generation for genomics projects. It can design experiments, query literature, write R/Python scripts, audit them, and produce a final report.
- **designer** – read‑only sub‑agent providing experimental design guidance and scientific reasoning. It suggests study layouts, replication strategies, and assay choices without modifying files.
- **auditor** – sub‑agent that performs a focused audit of a single script or notebook, checking for code bugs, reproducibility issues, and methodological pitfalls (e.g., genome‑build mismatches, missing multiple‑testing correction).
- **literature** – sub‑agent that conducts verified literature and database lookups (PubMed, Semantic Scholar, UniProt, ClinVar, etc.) and returns structured, cited evidence tables.
- **scout** – sub‑agent for fast, read‑only queries about specific files or directories, returning concise answers with file:line citations.
- **nextflow‑runner** – primary agent that wraps the `nextflow run` CLI, executing nfcore pipelines with full provenance logging (pipeline version, parameters, timestamps) for reproducible analyses.

To add a new agent, create a file `@agents/<name>.md` following the existing templates and run `./setup-opencode.sh` (or restart OpenCode) to make it available.
