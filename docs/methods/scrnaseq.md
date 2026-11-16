# Single-cell RNA-seq

**Code:** `autoimmune_mo.scrnaseq` · **Rules:** `workflow/rules/scrnaseq.smk`

1. **QC and clustering (Scanpy):** cells with fewer than 200 genes or more than 15% mitochondrial reads are removed; raw counts are kept; normalization, 3,000 highly variable genes, PCA, neighbours, UMAP, Leiden clustering.
2. **Annotation:** CellTypist (`Immune_All_Low.pkl`) with majority voting per cluster.
3. **Pseudobulk:** raw counts summed per donor and cell type (groups with fewer than 10 cells dropped). The donor, not the cell, is the unit of replication in case-control tests.
4. **Program scores:** mean z-score of fatty-acid-metabolism and eicosanoid-synthesis gene sets on log-CPM pseudobulk, within each cell type.

The starter gene sets in `pseudobulk.py` must be curated against Reactome or KEGG before results are reported.
