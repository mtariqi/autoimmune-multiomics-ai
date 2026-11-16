# Reproducibility

Every result in `results/` is produced by the Snakemake pipeline from code, configuration and
input data. Nothing is edited by hand.

## Guarantees and how they are enforced

| Guarantee | Mechanism |
| --- | --- |
| Same software | `environment.yml` (pinned major versions), `environment.lock.yml` (exact), per-rule conda envs in `workflow/envs/` |
| Same parameters | All parameters in `config/config.yaml`; none hard-coded |
| Same randomness | Every stochastic step reads `random_seed` |
| Rebuild when anything changes | Profile rerun triggers: file times, parameters, inputs, software environment, code |
| Runs on a clean machine | CI builds the environment and runs the demo pipeline on every push |
| Deterministic | CI runs the demo twice from scratch and fails if any output differs |
| Provenance | `snakemake --report` and `snakemake --summary` record code version, inputs and parameters per output |

## Pipeline targets

| Target | Runs | Data needed |
| --- | --- | --- |
| `demo_all` | Standards check, metabolomics, ML, explanations, network on synthetic data | None |
| `mr_all` | Mendelian randomization | Public GWAS summary statistics |
| `scrnaseq_all` | Single-cell QC, annotation, pseudobulk, program scores | Public `.h5ad` files |
| `classifier_all` | Fatty-acid classifier with nested CV | `AMO_SECURE_DATA` |
| `rnaseq_all` | FastQC, Trim Galore, STAR, featureCounts, DESeq2, MultiQC | FASTQ (Phase 2) |
| `microbiome_all` | MetaPhlAn, HUMAnN, diversity | FASTQ (Phase 2) |

```bash
snakemake -n rnaseq_all              # dry run
snakemake rnaseq_all                 # run with the default profile
snakemake --report results/report.html
```
