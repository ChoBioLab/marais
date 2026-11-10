---
name: design-review
description: Critique experimental design for genetics and functional-genomics experiments - replication, controls, batch effects, power, confounding, analysis plan. Use before data collection or when results look surprising.
---
1. Elicit: hypothesis, organism/strain/cell line, perturbation (KO, KD, CRISPR, drug), assay/readout, conditions, planned n.
2. Define the experimental unit (independent biological replicate). Flag pseudoreplication: technical replicates, cells/wells/reads, one animal/litter/passage counted as independent.
3. Controls: vehicle/non-targeting, positive, rescue or orthogonal validation, isogenic background. For CRISPR, multiple independent guides and off-target risk.
4. Confounding: batch, date, operator, plate position, lane, passage, sex/age. Confirm condition is not collinear with batch. Propose randomization and a balanced layout.
5. Power: state expected effect size, variance source, alpha, replicates needed. If unknown, say so and propose a pilot. Use the `statistical-power` skill if installed.
6. Fix the analysis plan before seeing data: model/design formula, contrasts, normalization, filters, multiple testing, outlier rules.
7. Output sections: Hypothesis / Design table (sample, condition, batch, replicate) / Controls / Confounders / Power / Analysis plan / Top risks (ranked) / Open questions. Mark assumptions.
