# Commands

Command markdown files live in `@commands/` and define reusable CLI‑style shortcuts that invoke agents or sub‑tasks. Each file includes a front‑matter block with a description, the target agent, and optional sub‑task flag.

## Available commands

- **/lit** – literature lookup via the `literature` agent.
- **/audit** – audit a script via the `auditor` agent.
- **/new-analysis** – scaffold a reproducible analysis folder (uses `analyst`).
- **/biomcp-health** – run `biomcp health --apis-only` and highlight errors/exclusions.
- **/nextflow-launch** – launch an nfcore/Nextflow pipeline via the `nextflow-runner` agent.

To create a new command, add a file `@commands/<name>.md` with the appropriate front‑matter and template, then restart OpenCode or run `./setup-opencode.sh`.
