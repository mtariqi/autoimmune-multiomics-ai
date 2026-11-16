# Metabolomics

**Code:** `autoimmune_mo.metabolomics` · **Rules:** `demo_metabolomics` (synthetic), `classifier_cv` (secure)

Targeted fatty-acid data are processed in a fixed order:

1. **Missingness filter:** drop features missing in more than 20% of samples (`metabolomics.max_missing`).
2. **QC filter:** drop features whose coefficient of variation across pooled QC samples exceeds 30% (`max_qc_cv`). QC samples are then removed.
3. **Imputation:** half of each feature's minimum positive value, appropriate for values below the limit of detection.
4. **Transformation:** log2.
5. **Scaling (optional):** auto or Pareto scaling for multivariate methods.

**Fatty-acid indices:** total omega-3 (ALA, EPA, DPA, DHA), total omega-6 (LA, GLA, DGLA, AA), the omega-6:omega-3 ratio and, when total fatty acids are available, the omega-3 index (EPA + DHA as % of total).

**Differential analysis:** Wilcoxon rank-sum per feature with Benjamini-Hochberg FDR. Only one sample per participant enters a test (baseline visit), so observations are independent. Longitudinal comparisons use mixed models (planned).
