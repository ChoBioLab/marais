# Lab rules (functional genomics / genetics)

## Data and privacy
- Do not read, print or transmit API keys or anything under ~/.config/opencode/secrets.
- No PHI, patient-level genotypes or identifiable data in prompts or files.
- biomcp sends queries to public third‑party APIs. Query only with public identifiers (gene symbols, rsIDs, PMIDs, disease terms). Never with unpublished sequences or patient variants.

## Scientific honesty
- Never invent citations, PMIDs, DOIs, accessions, gene IDs, rsIDs or numbers. A citation counts only if a tool returned it this session and you show its PMID/DOI.
- Separate: (1) what the data show, (2) what the literature says (cited), (3) your inference. Label uncertainty.
- If inputs look wrong (sample swap, batch confounded with condition), say so before analysing.

## Genomics hygiene
- State organism, genome build and annotation version for every analysis. Never mix builds. Ask if unknown.
- BED is 0‑based half‑open. VCF, GFF and GTF are 1‑based inclusive. Convert explicitly.
- Key genes on stable IDs (Ensembl ID, version handling stated). Symbols are for display only.
- Replication unit = independent biological replicate (not reads, cells or wells). Report effect size, n, model/design formula, and multiple‑testing correction (FDR).
- Never modify raw data. Write outputs to new files.

## Reproducibility and compute
- Prefer scripts to one‑offs. Record versions, seeds and exact commands. Outputs go in results/ with a README line on how they were made.
- On Minerva, do not run heavy jobs on login nodes. Write the LSF (bsub) script and ask the user to submit it.

## Working style
- Ask one clarifying question when organism, build, replicate structure or goal is ambiguous. Otherwise proceed.

## Delegation
- Pass subagents exact file paths. Do not paraphrase or pre‑read the files they will read.
- Treat subagent output as unverified: check each quoted line against the file before reporting it.
- Before merging, compare subagent findings with your own and list real disagreements.

## API Health Checks
- Run `/biomcp-health` regularly. If any API shows **error** or is **excluded**, address the issue (network, missing key, etc.) before using related commands.
