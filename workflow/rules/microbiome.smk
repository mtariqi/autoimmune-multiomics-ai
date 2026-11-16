# Shotgun metagenomics, Phase 2: MetaPhlAn (taxonomy) + HUMAnN (pathways) -> diversity and CLR.
# Inputs: data/raw/microbiome/{sample}_R1.fastq.gz and _R2.fastq.gz. Host reads should already be
# removed by the sequencing core (human DNA must not leave the secure environment).
MB = config["microbiome"]
RAWMB = "data/raw/microbiome"
WMB = "data/processed/microbiome"


rule microbiome_all:
    input:
        "results/microbiome/alpha_diversity.tsv",
        "results/microbiome/aitchison_distance.tsv",
        "results/microbiome/pathabundance_relab.tsv",


rule microbiome_concat:
    input:
        r1=f"{RAWMB}/{{sample}}_R1.fastq.gz",
        r2=f"{RAWMB}/{{sample}}_R2.fastq.gz",
    output:
        temp(f"{WMB}/concat/{{sample}}.fastq.gz"),
    shell:
        "cat {input.r1} {input.r2} > {output}"


rule microbiome_metaphlan:
    input:
        reads=rules.microbiome_concat.output,
        db=MB["metaphlan_db"],
    output:
        profile=f"{WMB}/metaphlan/{{sample}}_profile.tsv",
        mapout=f"{WMB}/metaphlan/{{sample}}.mapout.bz2",
    threads: 8
    log:
        "logs/microbiome/metaphlan_{sample}.log",
    conda:
        "../envs/microbiome.yml"
    shell:
        "metaphlan {input.reads} --input_type fastq --bowtie2db {input.db} --nproc {threads} "
        "--mapout {output.mapout} -o {output.profile} > {log} 2>&1"


rule microbiome_merge_taxa:
    input:
        expand(f"{WMB}/metaphlan/{{sample}}_profile.tsv", sample=MB["samples"]),
    output:
        f"{WMB}/metaphlan_merged.tsv",
    log:
        "logs/microbiome/merge_taxa.log",
    conda:
        "../envs/microbiome.yml"
    shell:
        "merge_metaphlan_tables.py {input} > {output} 2> {log}"


rule microbiome_humann:
    input:
        reads=rules.microbiome_concat.output,
        taxa=rules.microbiome_metaphlan.output.profile,
    output:
        f"{WMB}/humann/{{sample}}_pathabundance.tsv",
    params:
        outdir=f"{WMB}/humann",
        nuc=MB["humann_nucleotide_db"],
        prot=MB["humann_protein_db"],
    threads: 8
    log:
        "logs/microbiome/humann_{sample}.log",
    conda:
        "../envs/microbiome.yml"
    shell:
        "humann --input {input.reads} --output {params.outdir} --output-basename {wildcards.sample} "
        "--threads {threads} --taxonomic-profile {input.taxa} "
        "--nucleotide-database {params.nuc} --protein-database {params.prot} > {log} 2>&1"


rule microbiome_merge_pathways:
    input:
        expand(f"{WMB}/humann/{{sample}}_pathabundance.tsv", sample=MB["samples"]),
    output:
        "results/microbiome/pathabundance_relab.tsv",
    params:
        indir=f"{WMB}/humann",
        joined=f"{WMB}/pathabundance_joined.tsv",
    log:
        "logs/microbiome/merge_pathways.log",
    conda:
        "../envs/microbiome.yml"
    shell:
        "(humann_join_tables -i {params.indir} -o {params.joined} --file_name pathabundance && "
        "humann_renorm_table -i {params.joined} -o {output} --units relab) > {log} 2>&1"


rule microbiome_diversity:
    input:
        rules.microbiome_merge_taxa.output,
    output:
        alpha="results/microbiome/alpha_diversity.tsv",
        dist="results/microbiome/aitchison_distance.tsv",
        clr=f"{WMB}/species_clr.tsv",
    params:
        min_prevalence=MB["min_prevalence"],
    log:
        "logs/microbiome/diversity.log",
    script:
        "../scripts/microbiome_diversity.py"
