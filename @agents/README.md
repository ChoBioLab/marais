# Agents

This directory contains all built‑in agents that the Marais OpenCode configuration ships. Each markdown file defines an agent’s purpose, mode (primary or sub‑agent), and any permission overrides.

## Available agents

- **analyst** – primary agent for data processing, statistics and scripting.
- **designer** – primary read‑only agent for experimental design advice.
- **auditor** – sub‑agent that audits a single script or notebook.
- **literature** – sub‑agent that performs verified literature/database lookups.
- **scout** – sub‑agent for fast narrow file‑search queries.
- **nextflow‑runner** – agent that wraps the Nextflow CLI for reproducible pipeline execution.

To add a new agent, create a file `@agents/<name>.md` following the existing templates and run `./setup-opencode.sh` (or restart OpenCode) to make it available.
