# Aim 3 preliminary: leakage-safe re-analysis of the serum fatty-acid classifier.
# Runs only where AMO_SECURE_DATA is set; the input path is never written into the repo.
import os

CLF = config["classifier"]
SECURE = os.environ.get("AMO_SECURE_DATA", "SECURE_DATA_NOT_SET")


rule classifier_all:
    input:
        "results/classifier/cv_metrics.tsv",
        "results/classifier/shap_importance.tsv",


rule classifier_cv:
    input:
        os.path.join(SECURE, CLF["input"]),
    output:
        metrics="results/classifier/cv_metrics.tsv",
        shap="results/classifier/shap_importance.tsv",
    params:
        seed=config["random_seed"],
    log:
        "logs/classifier/cv.log",
    script:
        "../scripts/classifier_cv.py"
