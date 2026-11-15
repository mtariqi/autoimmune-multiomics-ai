# Aim 1 preliminary: public PBMC scRNA-seq, fatty-acid / eicosanoid programs by cell type.
SC = config["scrnaseq"]


rule scrnaseq_all:
    input:
        expand("results/scrnaseq/program_scores_{dataset}.tsv", dataset=SC["datasets"]),


rule scrnaseq_qc:
    input:
        "data/external/scrnaseq/{dataset}.h5ad",
    output:
        "data/processed/scrnaseq/{dataset}_qc.h5ad",
    log:
        "logs/scrnaseq/qc_{dataset}.log",
    script:
        "../scripts/scrnaseq_qc.py"


rule scrnaseq_cluster_annotate:
    input:
        "data/processed/scrnaseq/{dataset}_qc.h5ad",
    output:
        "data/processed/scrnaseq/{dataset}_annotated.h5ad",
    log:
        "logs/scrnaseq/annotate_{dataset}.log",
    script:
        "../scripts/scrnaseq_annotate.py"


rule scrnaseq_program_scores:
    input:
        "data/processed/scrnaseq/{dataset}_annotated.h5ad",
    output:
        "results/scrnaseq/program_scores_{dataset}.tsv",
    log:
        "logs/scrnaseq/scores_{dataset}.log",
    script:
        "../scripts/scrnaseq_scores.py"
