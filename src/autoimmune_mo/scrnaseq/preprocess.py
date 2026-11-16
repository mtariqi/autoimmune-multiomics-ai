# ==============================================================================
# Project     : Autoimmune Multi-Omics AI (autoimmune-multiomics-ai)
# File        : src/autoimmune_mo/scrnaseq/preprocess.py
# Purpose     : Scanpy preprocessing. Scanpy is imported lazily so the rest of
#               the package works without it.
# Author      : Md Tariqul Islam
# Institution : Northeastern University | Bioinformatics Department
# License     : MIT (see LICENSE)
# ==============================================================================

"""Scanpy preprocessing. Scanpy is imported lazily so the rest of the package works without it."""

from __future__ import annotations


def qc_and_cluster(adata, min_genes: int = 200, max_pct_mito: float = 15,
                   n_top_genes: int = 3000, resolution: float = 1.0, batch_key: str | None = None,
                   seed: int = 2026):
    """QC filter, normalize, select HVGs, PCA, neighbours, UMAP and Leiden clustering.

    Raw counts are kept in ``adata.layers['counts']`` for pseudobulk analysis.
    """
    import scanpy as sc

    adata = adata.copy()
    adata.var["mt"] = adata.var_names.str.upper().str.startswith("MT-")
    sc.pp.calculate_qc_metrics(adata, qc_vars=["mt"], inplace=True, percent_top=None)
    sc.pp.filter_cells(adata, min_genes=min_genes)
    adata = adata[adata.obs["pct_counts_mt"] <= max_pct_mito].copy()
    sc.pp.filter_genes(adata, min_cells=3)
    adata.layers["counts"] = adata.X.copy()
    sc.pp.normalize_total(adata, target_sum=1e4)
    sc.pp.log1p(adata)
    sc.pp.highly_variable_genes(adata, n_top_genes=n_top_genes, batch_key=batch_key,
                                flavor="seurat_v3", layer="counts")
    sc.pp.pca(adata, mask_var="highly_variable", random_state=seed)
    sc.pp.neighbors(adata, random_state=seed)
    sc.tl.umap(adata, random_state=seed)
    sc.tl.leiden(adata, resolution=resolution, random_state=seed, flavor="igraph",
                 n_iterations=2, directed=False)
    return adata
