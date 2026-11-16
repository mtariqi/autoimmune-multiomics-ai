# ==============================================================================
# Project     : Autoimmune Multi-Omics AI (autoimmune-multiomics-ai)
# File        : workflow/scripts/scrnaseq_annotate.py
# Purpose     : Automated cell-type annotation with CellTypist (majority vote
#               per cluster).
# Author      : Md Tariqul Islam
# Institution : Northeastern University | Bioinformatics Department
# License     : MIT (see LICENSE)
# ==============================================================================

"""Snakemake script: automated cell-type annotation with CellTypist (majority vote per cluster)."""

import celltypist
import scanpy as sc

s = snakemake  # noqa: F821
adata = sc.read_h5ad(s.input[0])
celltypist.models.download_models(model=[s.params.model], force_update=False)
pred = celltypist.annotate(adata, model=s.params.model, majority_voting=True,
                           over_clustering="leiden")
adata.obs["cell_type"] = pred.predicted_labels["majority_voting"].astype(str).values
adata.write_h5ad(s.output[0])
with open(s.log[0], "w") as fh:
    fh.write(adata.obs["cell_type"].value_counts().to_string() + "\n")
