# Skills

The `@skills/` directory holds all reusable skill packs that agents can load at runtime. Each skill lives in its own sub‑directory with a `SKILL.md` file describing its purpose, steps, and any required tooling.

## Core skill packs (already shipped)

- **bulk‑rnaseq** – end‑to‑end bulk RNA‑seq processing and handoff to downstream analysis.
- **scanpy** – single‑cell RNA‑seq preprocessing, clustering, and marker discovery.
- **genomic‑intelligence** – DNA‑sequence‑based predictions (promoters, enhancers, expression, etc.).
- **exploratory‑data‑analysis** – quick profiling of tabular and image data with missingness and leakage audits.
- **statistical‑analysis** – hypothesis testing, effect size, power analysis, and APA‑style reporting.
- **deeptools** – NGS QC, normalization, and heatmap/profile generation.
- **biopython** – sequence I/O, BLAST automation, phylogenetics, and more.
- **literature** – literature lookup and citation extraction.
- **literature‑review** – systematic review scaffolding and citation management.
- **scvi‑tools** – multimodal single‑cell generative modeling.
- **scientific‑visualization** – publication‑ready figures with Matplotlib/Seaborn/Plotly.
- **setup‑matt‑pocock‑skills** – engineering utilities pack.



## Matt Pocock engineering pack

- **setup‑matt‑pocock‑skills** – installs the full suite of Matt Pocock’s engineering skills (issue‑tracker setup, triage, domain docs, etc.).

### Adding a new skill

1. Create a directory `@skills/<skill-id>/`.
2. Add a `SKILL.md` file containing the required front‑matter (`name`, `description`) and a numbered step list.
3. Commit the new files and run `./setup‑opencode.sh` (or restart OpenCode) to make the skill discoverable.
