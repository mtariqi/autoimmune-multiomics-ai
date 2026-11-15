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
snakemake -n          # dry run of the pipeline
```

## Data policy

No individual-level participant data are ever committed. `data/raw/` is read-only input;
everything in `data/processed/` and `results/` must be reproducible from code.
See `data/README.md`.

## Citation

See `CITATION.cff`.

## License

Code: MIT. Documentation and figures: CC BY 4.0 unless stated otherwise.
