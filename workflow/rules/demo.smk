# End-to-end demo on synthetic data: data standards -> metabolomics -> ML + explanations -> network.
# Runs anywhere without real data. CI runs it on every push and checks the outputs are identical
# across two runs.
DEMO = config["demo"]
D = "data/processed/demo"
R = "results/demo"


rule demo_all:
    input:
        f"{R}/validation_report.txt",
        f"{R}/metabolomics_differential.tsv",
        f"{R}/fatty_acid_indices.tsv",
        f"{R}/cv_folds.tsv",
        f"{R}/model_summary.tsv",
        f"{R}/feature_importance_stability.tsv",
        f"{R}/network_hubs.tsv",


rule demo_synthetic_data:
    output:
        samples=f"{D}/samples.tsv",
        metabolomics=f"{D}/metabolomics_raw.tsv",
    params:
        seed=config["random_seed"],
        n_participants=DEMO["n_participants"],
        visits=DEMO["visits"],
        n_qc=DEMO["n_qc_samples"],
    log:
        "logs/demo/synthetic_data.log",
    script:
        "../scripts/demo_synthetic_data.py"


rule demo_validate:
    input:
        samples=f"{D}/samples.tsv",
        metabolomics=f"{D}/metabolomics_raw.tsv",
    output:
        f"{R}/validation_report.txt",
    log:
        "logs/demo/validate.log",
    script:
        "../scripts/validate_inputs.py"


rule demo_metabolomics:
    input:
        samples=f"{D}/samples.tsv",
        metabolomics=f"{D}/metabolomics_raw.tsv",
        report=f"{R}/validation_report.txt",
    output:
        log2=f"{D}/metabolomics_log2.tsv",
        indices=f"{R}/fatty_acid_indices.tsv",
        differential=f"{R}/metabolomics_differential.tsv",
    params:
        qc=config["metabolomics"],
    log:
        "logs/demo/metabolomics.log",
    script:
        "../scripts/metabolomics_preprocess.py"


rule demo_cv_folds:
    input:
        samples=f"{D}/samples.tsv",
    output:
        f"{R}/cv_folds.tsv",
    params:
        seed=config["random_seed"],
        n_splits=config["ml"]["cv_outer_folds"],
    log:
        "logs/demo/cv_folds.log",
    script:
        "../scripts/demo_cv_folds.py"


rule demo_models:
    input:
        samples=f"{D}/samples.tsv",
        features=f"{D}/metabolomics_log2.tsv",
    output:
        metrics=f"{R}/model_metrics.tsv",
        summary=f"{R}/model_summary.tsv",
        predictions=f"{R}/oof_predictions.tsv",
        importance=f"{R}/feature_importance_stability.tsv",
    params:
        seed=config["random_seed"],
        models=DEMO["models"],
        outer=config["ml"]["cv_outer_folds"],
        inner=config["ml"]["cv_inner_folds"],
        method=config["ml"]["importance_method"],
    log:
        "logs/demo/models.log",
    script:
        "../scripts/train_models.py"


rule demo_network:
    input:
        f"{D}/metabolomics_log2.tsv",
    output:
        hubs=f"{R}/network_hubs.tsv",
        edges=f"{R}/network_edges.tsv",
    params:
        net=config["network"],
    log:
        "logs/demo/network.log",
    script:
        "../scripts/network_analysis.py"
