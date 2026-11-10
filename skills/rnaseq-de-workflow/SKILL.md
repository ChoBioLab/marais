---
name: rnaseq-de-workflow
description: Bulk RNA-seq differential expression workflow conventions from counts to DE results to enrichment, with QC gates. Use when planning or analysing RNA-seq count data.
---
1. Inputs: raw counts (not TPM/FPKM), sample sheet (condition, batch, replicate), organism and annotation version. Check sample names match and are unique. Warn if fewer than 3 replicates per group.
2. QC before modelling: library sizes, detected genes, PCA/sample distances. Check clustering by batch vs condition. Flag swaps (for example XIST/Y-gene expression vs recorded sex). Never drop samples silently.
3. Model: design formula with batch covariates (~ batch + condition), explicit contrasts, low-count filter. Use DESeq2 (R) or PyDESeq2 (Python; see `pydeseq2` skill if installed).
4. Outputs: gene ID, symbol, baseMean, shrunken log2FC (state method), padj. MA and volcano plots. Up/down counts at stated thresholds.
5. Enrichment: background = expressed genes, not the whole genome. State database versions.
6. Save session info, seeds, scripts and results/. Send scripts to @auditor before reporting.
