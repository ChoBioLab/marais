---
name: setup-matt-pocock-skills
description: "Configure this repo for the engineering skills: set up its issue tracker, triage label vocabulary, and domain doc layout. Run once before first use of the other engineering skills."
disable-model-invocation: true
---

# Setup Matt Pocock's Skills

Scaffold the per‑repo configuration that the engineering skills assume:

- **Issue tracker** – where issues live (GitHub by default; local markdown is also supported).
- **Triage labels** – the strings used for the five canonical triage roles.
- **Domain docs** – where `GLOSSARY.md` and ADRs live, and the consumer rules for reading them.

This skill is a prompt‑driven interaction that explores the repository, presents findings, and writes the required configuration files.

*See the original skill definition at https://github.com/mattpocock/skills/tree/main/skills/engineering/setup-matt-pocock-skills*