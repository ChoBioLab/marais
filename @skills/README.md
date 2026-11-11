# Skills

The `@skills/` directory holds all reusable skill packs that agents can load at runtime. Each skill lives in its own sub‑directory with a `SKILL.md` file describing its purpose, steps, and any required tooling.

## Core skill packs (already shipped)



## Scientific skill suite (deprecated)

These scientific skill packs have been removed per system update and are no longer available.

## Matt Pocock engineering pack

- **setup‑matt‑pocock‑skills** – installs the full suite of Matt Pocock’s engineering skills (issue‑tracker setup, triage, domain docs, etc.).

### Adding a new skill

1. Create a directory `@skills/<skill-id>/`.
2. Add a `SKILL.md` file containing the required front‑matter (`name`, `description`) and a numbered step list.
3. Commit the new files and run `./setup‑opencode.sh` (or restart OpenCode) to make the skill discoverable.
