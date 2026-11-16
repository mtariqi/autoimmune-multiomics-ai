# ==============================================================================
# Project     : Autoimmune Multi-Omics AI (autoimmune-multiomics-ai)
# File        : workflow/rules/classifier.smk
# Purpose     : Aim 3 preliminary: leakage-safe re-analysis of the serum fatty-
#               acid classifier.
# Author      : Md Tariqul Islam
# Institution : Northeastern University | Bioinformatics Department
# License     : MIT (see LICENSE)
# ==============================================================================

# Aim 3 preliminary: leakage-safe re-analysis of the serum fatty-acid classifier.
# Runs only where AMO_SECURE_DATA is set; the input path is never written into the repo.
import os

CLF = config["classifier"]
SECURE = os.environ.get("AMO_SECURE_DATA", "SECURE_DATA_NOT_SET")


rule classifier_all:
    input:
        "results/classifier/model_summary.tsv",
        "results/classifier/feature_importance_stability.tsv",


rule classifier_cv:
    input:
        os.path.join(SECURE, CLF["input"]),
    output:
        metrics="results/classifier/model_metrics.tsv",
        summary="results/classifier/model_summary.tsv",
        predictions="results/classifier/oof_predictions.tsv",
        importance="results/classifier/feature_importance_stability.tsv",
    params:
        clf=CLF,
        seed=config["random_seed"],
        outer=config["ml"]["cv_outer_folds"],
        inner=config["ml"]["cv_inner_folds"],
        method=config["ml"]["importance_method"],
    log:
        "logs/classifier/cv.log",
    script:
        "../scripts/classifier_cv.py"
