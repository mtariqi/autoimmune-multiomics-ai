# Roadmap to grant readiness

Target: within 12 to 18 months, this repository is evidence that the team can run the
computational program in the grant. The table tracks each deliverable honestly.

| Deliverable | What "done" means | Status | Target |
| --- | --- | --- | --- |
| Multi-omics datasets | Public datasets (GWAS, PBMC scRNA-seq) downloaded by the pipeline and logged in `sources.csv`; secure data referenced, never committed | Not started | Month 3 |
| Reproducible workflows | Snakemake rules for every layer; CI runs the demo and checks determinism | **Done** (RNA-seq and microbiome await real data) | Month 0 |
| Machine-learning models | Nested, participant-grouped CV; five model families | **Done** on synthetic data | Month 0 |
| SHAP interpretation framework | SHAP with permutation fallback; fold-stability report | **Done** on synthetic data | Month 0 |
| scRNA-seq pipeline | QC, annotation, pseudobulk, program scores run on one public RA dataset | Code written; not yet run on real data | Month 4 |
| Documentation | Docs website with methods per layer | **Done**; update as analyses land | Ongoing |
| Preliminary results | MR estimates; public scRNA-seq program scores; leakage-safe classifier re-analysis | Not started | Months 2 to 9 |
| Publication draft | Methods and results drafted in `docs/manuscript/` from pipeline outputs | Template in place | Month 12 |
| Grant proposal | Proposal in a private repository, preliminary-data section citing this repo | Draft exists | Month 12 to 18 |

## Next three analyses, in order

1. **Mendelian randomization** (Aim 2): public data only, fastest route to a real result.
2. **Public PBMC single-cell re-analysis** (Aim 1): choose one RA dataset with donor-level metadata.
3. **Classifier re-analysis** (Aim 3): run `classifier_all` on the secure machine; publish only summary results.

## Grant proposal (kept private)

The proposal never goes in this public repository. Keep it in `docs/grant/` (ignored by Git) as
its own private repository:

```bash
cd docs/grant
git init -b main
gh repo create autoimmune-multiomics-grant --private --source=. --push
```
