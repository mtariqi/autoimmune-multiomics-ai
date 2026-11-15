# autoimmune-multiomics-ai

Reproducible multi-omics and explainable machine-learning platform for studying the
pre-clinical phase of autoimmune disease, starting with rheumatoid arthritis (RA).

**Research question:** Do serum fatty-acid disturbances precede and contribute to RA, and can
integrated multi-omics predict who among at-risk individuals will progress?

## Status

| Analysis | Aim | Data | Status |
| --- | --- | --- | --- |
| Two-sample Mendelian randomization: fatty acids → RA (and reverse) | Aim 2 | Public GWAS summary statistics | Planned |
| PBMC single-cell re-analysis: fatty-acid / eicosanoid programs in RA | Aim 1 | Public scRNA-seq (GEO, CELLxGENE) | Planned |
| Leakage-safe re-analysis of serum fatty-acid classifier | Aim 3 | Existing metabolomics data (not public) | Planned |

## Repository layout

```
config/             all parameters and paths (config.yaml)
data/               NOT version-controlled except README and metadata templates
docs/               methods notes and manuscript drafts
notebooks/          exploration only (see notebooks/README.md)
results/            generated figures, tables, models
src/autoimmune_mo/  tested Python package: all analysis logic
workflow/           Snakemake pipeline: rules/, scripts/, envs/
tests/              unit tests (pytest)
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for the data flow, layer rules and naming conventions.

## Quick start

```bash
conda env create -f environment.yml
conda activate autoimmune-mo
pip install -e .
pytest
snakemake all            # runs the synthetic demo end to end
```

## Reproducing results

All results are produced by the Snakemake pipeline in `workflow/`. Settings (cores, conda
environments, rerun triggers) come from `workflow/profiles/default/config.yaml`.

| Target | What it runs | Data needed |
| --- | --- | --- |
| `snakemake all` | Environment check + synthetic demo | None |
| `snakemake mr_all` | Mendelian randomization | Public GWAS in `data/external/gwas/` |
| `snakemake scrnaseq_all` | Single-cell re-analysis | Public `.h5ad` files in `data/external/scrnaseq/` |
| `snakemake classifier_all` | Fatty-acid classifier | `AMO_SECURE_DATA` set (secure machine only) |

Useful commands:

```bash
snakemake -n mr_all                                   # dry run: list jobs without running
snakemake --dag mr_all | dot -Tsvg > results/figures/dag_mr.svg   # pipeline diagram
snakemake --report results/report.html                # HTML report with provenance
snakemake --summary                                   # status and code version of every output
```

**Software versions.** `environment.yml` pins major versions. After creating the environment,
record the exact versions and commit the file:

```bash
conda env export --no-builds -n autoimmune-mo > environment.lock.yml
```

To rebuild the exact environment later: `conda env create -f environment.lock.yml`.

**Determinism.** Every stochastic step reads `random_seed` from `config/config.yaml`. CI runs the
demo twice from scratch and fails if the outputs differ.

## Data policy

No individual-level participant data are ever committed. `data/raw/` is read-only input;
everything in `data/processed/` and `results/` must be reproducible from code.
See `data/README.md`.

## Citation

See `CITATION.cff`.

## License

Code: MIT. Documentation and figures: CC BY 4.0 unless stated otherwise.
