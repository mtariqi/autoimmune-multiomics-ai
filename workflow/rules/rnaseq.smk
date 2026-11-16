# Bulk RNA-seq, Phase 2: FastQC -> Trim Galore -> STAR -> featureCounts -> DESeq2, plus MultiQC.
# Inputs: data/raw/rnaseq/{sample}_R1.fastq.gz and _R2.fastq.gz; samples listed in config.
# Tool versions are pinned in workflow/envs/rnaseq.yml and deseq2.yml.
RNA = config["rnaseq"]
RAW = "data/raw/rnaseq"
WD = "data/processed/rnaseq"


rule rnaseq_all:
    input:
        "results/rnaseq/deseq2_results.tsv",
        "results/rnaseq/multiqc_report.html",


rule rnaseq_fastqc:
    input:
        f"{RAW}/{{sample}}_{{read}}.fastq.gz",
    output:
        f"{WD}/fastqc/{{sample}}_{{read}}_fastqc.zip",
    params:
        outdir=f"{WD}/fastqc",
    wildcard_constraints:
        read="R[12]",
    threads: 2
    log:
        "logs/rnaseq/fastqc_{sample}_{read}.log",
    conda:
        "../envs/rnaseq.yml"
    shell:
        "fastqc -t {threads} -o {params.outdir} {input} > {log} 2>&1"


rule rnaseq_trim:
    input:
        r1=f"{RAW}/{{sample}}_R1.fastq.gz",
        r2=f"{RAW}/{{sample}}_R2.fastq.gz",
    output:
        r1=f"{WD}/trimmed/{{sample}}_R1_val_1.fq.gz",
        r2=f"{WD}/trimmed/{{sample}}_R2_val_2.fq.gz",
    params:
        outdir=f"{WD}/trimmed",
    threads: 4
    log:
        "logs/rnaseq/trim_{sample}.log",
    conda:
        "../envs/rnaseq.yml"
    shell:
        "trim_galore --paired --cores {threads} -o {params.outdir} {input.r1} {input.r2} > {log} 2>&1"


rule rnaseq_star:
    input:
        r1=rules.rnaseq_trim.output.r1,
        r2=rules.rnaseq_trim.output.r2,
        index=RNA["star_index"],
    output:
        f"{WD}/star/{{sample}}.Aligned.sortedByCoord.out.bam",
    params:
        prefix=f"{WD}/star/{{sample}}.",
    threads: 8
    log:
        "logs/rnaseq/star_{sample}.log",
    conda:
        "../envs/rnaseq.yml"
    shell:
        "STAR --runThreadN {threads} --genomeDir {input.index} "
        "--readFilesIn {input.r1} {input.r2} --readFilesCommand zcat "
        "--outSAMtype BAM SortedByCoordinate --outFileNamePrefix {params.prefix} > {log} 2>&1"


rule rnaseq_featurecounts:
    input:
        bams=expand(f"{WD}/star/{{sample}}.Aligned.sortedByCoord.out.bam", sample=RNA["samples"]),
        gtf=RNA["annotation_gtf"],
    output:
        f"{WD}/featurecounts/counts.txt",
    params:
        strand=RNA["strandedness"],
    threads: 8
    log:
        "logs/rnaseq/featurecounts.log",
    conda:
        "../envs/rnaseq.yml"
    shell:
        "featureCounts -p --countReadPairs -s {params.strand} -T {threads} "
        "-a {input.gtf} -o {output} {input.bams} > {log} 2>&1"


rule rnaseq_count_matrix:
    input:
        rules.rnaseq_featurecounts.output,
    output:
        f"{WD}/counts_matrix.tsv",
    log:
        "logs/rnaseq/count_matrix.log",
    script:
        "../scripts/rnaseq_count_matrix.py"


rule rnaseq_deseq2:
    input:
        counts=rules.rnaseq_count_matrix.output,
        samples=RNA["sample_sheet"],
    output:
        results="results/rnaseq/deseq2_results.tsv",
        vst=f"{WD}/vst_matrix.tsv",
    params:
        design=RNA["design"],
        contrast=RNA["contrast"],
    threads: 4
    log:
        "logs/rnaseq/deseq2.log",
    conda:
        "../envs/deseq2.yml"
    script:
        "../scripts/deseq2.R"


rule rnaseq_multiqc:
    input:
        expand(f"{WD}/fastqc/{{sample}}_{{read}}_fastqc.zip", sample=RNA["samples"],
               read=["R1", "R2"]),
        expand(f"{WD}/star/{{sample}}.Aligned.sortedByCoord.out.bam", sample=RNA["samples"]),
        rules.rnaseq_featurecounts.output,
    output:
        "results/rnaseq/multiqc_report.html",
    params:
        workdir=WD,
    log:
        "logs/rnaseq/multiqc.log",
    conda:
        "../envs/rnaseq.yml"
    shell:
        "multiqc --force -n multiqc_report.html -o results/rnaseq {params.workdir} logs/rnaseq > {log} 2>&1"
