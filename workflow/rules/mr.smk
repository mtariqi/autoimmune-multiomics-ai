# ==============================================================================
# Project     : Autoimmune Multi-Omics AI (autoimmune-multiomics-ai)
# File        : workflow/rules/mr.smk
# Purpose     : Aim 2 preliminary: two-sample Mendelian randomization, fatty
#               acids -> RA (and reverse).
# Author      : Md Tariqul Islam
# Institution : Northeastern University | Bioinformatics Department
# License     : MIT (see LICENSE)
# ==============================================================================

# Aim 2 preliminary: two-sample Mendelian randomization, fatty acids -> RA (and reverse).
MR = config["mr"]
GWAS = "data/external/gwas"


rule mr_all:
    input:
        "results/tables/mr_summary.tsv",


rule mr_harmonise:
    input:
        exposure=f"{GWAS}/{{exposure}}.tsv.gz",
        outcome=f"{GWAS}/{MR['outcome']}.tsv.gz",
    output:
        "data/processed/mr/harmonised_{exposure}.tsv",
    params:
        p=MR["instrument_p_threshold"],
        r2=MR["clump_r2"],
        kb=MR["clump_kb"],
    log:
        "logs/mr/harmonise_{exposure}.log",
    conda:
        "../envs/r-mr.yml"
    script:
        "../scripts/mr_harmonise.R"


rule mr_estimate:
    input:
        "data/processed/mr/harmonised_{exposure}.tsv",
    output:
        "results/mr/estimates_{exposure}.tsv",
    params:
        methods=MR["methods"],
    log:
        "logs/mr/estimate_{exposure}.log",
    conda:
        "../envs/r-mr.yml"
    script:
        "../scripts/mr_estimate.R"


rule mr_summary:
    input:
        expand("results/mr/estimates_{exposure}.tsv", exposure=MR["exposures"]),
    output:
        "results/tables/mr_summary.tsv",
    log:
        "logs/mr/summary.log",
    script:
        "../scripts/mr_summary.py"
