"""Snakemake script: pseudobulk counts per donor x cell type, then program scores on log-CPM."""

import pandas as pd
import scanpy as sc
from scipy import sparse

from autoimmune_mo.rnaseq import log_cpm
from autoimmune_mo.scrnaseq import program_scores, pseudobulk

s = snakemake  # noqa: F821
adata = sc.read_h5ad(s.input[0])
X = adata.layers["counts"]
X = X.toarray() if sparse.issparse(X) else X
counts = pd.DataFrame(X, index=adata.obs_names, columns=adata.var_names)
pb = pseudobulk(counts, adata.obs, donor=s.params.donor, cell_type="cell_type",
                min_cells=s.params.min_cells)
pb.to_csv(s.output.pseudobulk, sep="\t")

expr = log_cpm(pb.drop(columns="n_cells"))
scores = []
for ct, block in expr.groupby(level=1):  # z-score within each cell type, across donors
    sc_ct = program_scores(block)
    scores.append(sc_ct)
pd.concat(scores).round(5).to_csv(s.output.scores, sep="\t")
with open(s.log[0], "w") as fh:
    fh.write(f"{len(pb)} donor x cell-type groups\n")
