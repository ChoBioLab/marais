# Skills

The `@skills/` directory holds all reusable skill packs that agents can load at runtime. Each skill lives in its own sub‑directory with a `SKILL.md` file describing its purpose, steps, and any required tooling.

## Core skill packs (already shipped)



## Scientific skill suite (recommended for genetics/genomics)

These are curated from the K‑Dense‑AI scientific‑agent‑skills collection and provide guidance for common bio‑informatics tasks:

- `literature-review`
- `statistical-analysis`
- `scientific-visualization`
- `exploratory-data-analysis`
- `scanpy`
- `bulk-rnaseq`
- `deeptools`
- `genomic‑intelligence`
- `biopython`
- `scvi-tools`

## Matt Pocock engineering pack

- **setup‑matt‑pocock‑skills** – installs the full suite of Matt Pocock’s engineering skills (issue‑tracker setup, triage, domain docs, etc.).

### Adding a new skill

1. Create a directory `@skills/<skill-id>/`.
2. Add a `SKILL.md` file containing the required front‑matter (`name`, `description`) and a numbered step list.
3. Commit the new files and run `./setup‑opencode.sh` (or restart OpenCode) to make the skill discoverable.
