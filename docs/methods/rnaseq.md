# Bulk RNA-seq

**Rules:** `workflow/rules/rnaseq.smk` · **Status:** ready for Phase 2 data, not yet run on real reads.

| Step | Tool | Output |
| --- | --- | --- |
| Read QC | FastQC | `data/processed/rnaseq/fastqc/` |
| Adapter and quality trimming | Trim Galore | trimmed FASTQ |
| Alignment | STAR (sorted BAM) | `star/{sample}.Aligned.sortedByCoord.out.bam` |
| Gene counts | featureCounts (paired, strandedness from config) | `counts_matrix.tsv` |
| Differential expression | DESeq2, design and contrast from config | `results/rnaseq/deseq2_results.tsv` |
| Report | MultiQC | `results/rnaseq/multiqc_report.html` |

DESeq2 also writes a variance-stabilized matrix for integration and machine learning. Before
the first run, build the STAR index and set `rnaseq.samples`, `star_index`, `annotation_gtf`,
`strandedness`, `design` and `contrast` in `config/config.yaml`.
