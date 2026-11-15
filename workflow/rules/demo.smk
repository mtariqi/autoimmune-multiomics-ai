# End-to-end demo on synthetic data. Proves the pipeline runs and is deterministic,
# without any real data. CI runs this on every push.
DEMO = config["demo"]


rule demo_all:
    input:
        "results/demo/cv_folds.tsv",


rule demo_synthetic_data:
    output:
        "data/processed/demo/synthetic_cohort.tsv",
    params:
        seed=config["random_seed"],
        n_participants=DEMO["n_participants"],
        visits=DEMO["visits"],
        n_features=DEMO["n_features"],
    log:
        "logs/demo/synthetic_data.log",
    script:
        "../scripts/demo_synthetic_data.py"


rule demo_cv:
    input:
        "data/processed/demo/synthetic_cohort.tsv",
    output:
        "results/demo/cv_folds.tsv",
    params:
        seed=config["random_seed"],
        n_splits=config["ml"]["cv_outer_folds"],
    log:
        "logs/demo/cv.log",
    script:
        "../scripts/demo_cv.py"
