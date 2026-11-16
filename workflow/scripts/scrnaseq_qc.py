# ==============================================================================
# Project     : Autoimmune Multi-Omics AI (autoimmune-multiomics-ai)
# File        : workflow/scripts/scrnaseq_qc.py
# Purpose     : Scanpy QC, normalization, HVGs, PCA, UMAP and Leiden clustering.
# Author      : Md Tariqul Islam
# Institution : Northeastern University | Bioinformatics Department
# License     : MIT (see LICENSE)
# ==============================================================================

"""Snakemake script: Scanpy QC, normalization, HVGs, PCA, UMAP and Leiden clustering."""

import scanpy as sc

from autoimmune_mo.scrnaseq import qc_and_cluster

s = snakemake  # noqa: F821
p = s.params.sc
adata = sc.read_h5ad(s.input[0])
n0 = adata.n_obs
adata = qc_and_cluster(adata, min_genes=p["min_genes"], max_pct_mito=p["max_pct_mito"],
                       n_top_genes=p["n_top_genes"], resolution=p["leiden_resolution"],
                       batch_key=p.get("batch_key"), seed=s.params.seed)
adata.write_h5ad(s.output[0])
with open(s.log[0], "w") as fh:
    fh.write(f"{n0} -> {adata.n_obs} cells; {adata.obs['leiden'].nunique()} clusters\n")
