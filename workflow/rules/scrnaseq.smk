# Single-cell RNA-seq on public PBMC data: QC + clustering -> CellTypist annotation ->
# pseudobulk per donor and cell type -> fatty-acid / eicosanoid program scores.
# Phase 2 cohort data enter the same rules after Cell Ranger at the sequencing core.
SC = config["scrnaseq"]
WSC = "data/processed/scrnaseq"


rule scrnaseq_all:
    input:
        expand("results/scrnaseq/program_scores_{dataset}.tsv", dataset=SC["datasets"]),


rule scrnaseq_qc_cluster:
    input:
        "data/external/scrnaseq/{dataset}.h5ad",
    output:
        f"{WSC}/{{dataset}}_clustered.h5ad",
    params:
        sc=SC,
        seed=config["random_seed"],
    threads: 4
    log:
        "logs/scrnaseq/qc_cluster_{dataset}.log",
    script:
        "../scripts/scrnaseq_qc.py"


rule scrnaseq_annotate:
    input:
        rules.scrnaseq_qc_cluster.output,
    output:
        f"{WSC}/{{dataset}}_annotated.h5ad",
    params:
        model=SC["celltypist_model"],
    log:
        "logs/scrnaseq/annotate_{dataset}.log",
    script:
        "../scripts/scrnaseq_annotate.py"


rule scrnaseq_program_scores:
    input:
        rules.scrnaseq_annotate.output,
    output:
        pseudobulk=f"{WSC}/{{dataset}}_pseudobulk.tsv",
        scores="results/scrnaseq/program_scores_{dataset}.tsv",
    params:
        donor=SC["donor_key"],
        min_cells=SC["min_cells_pseudobulk"],
    log:
        "logs/scrnaseq/scores_{dataset}.log",
    script:
        "../scripts/scrnaseq_scores.py"
