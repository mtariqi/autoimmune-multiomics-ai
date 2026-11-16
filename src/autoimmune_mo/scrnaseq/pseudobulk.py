"""Pseudobulk aggregation and gene-program scoring (pure pandas; no Scanpy needed).

Case-control comparisons across donors use pseudobulk counts per donor and cell type, so that
the donor, not the cell, is the unit of replication.
"""

from __future__ import annotations

import pandas as pd

FATTY_ACID_PROGRAMS = {
    # Starter gene sets; curate against Reactome/KEGG before reporting results.
    "eicosanoid_synthesis": ["PLA2G4A", "PTGS1", "PTGS2", "ALOX5", "ALOX5AP", "ALOX15", "LTA4H",
                             "PTGES", "TBXAS1", "HPGDS"],
    "fatty_acid_metabolism": ["FADS1", "FADS2", "ELOVL5", "ELOVL2", "CPT1A", "ACADM", "FASN",
                              "SCD", "CD36", "FABP4"],
}


def pseudobulk(counts: pd.DataFrame, cells: pd.DataFrame, donor: str = "donor",
               cell_type: str = "cell_type", min_cells: int = 10) -> pd.DataFrame:
    """Sum raw counts (cells x genes) per donor and cell type.

    Returns a DataFrame indexed by (donor, cell_type) with an ``n_cells`` column first.
    Groups with fewer than ``min_cells`` cells are dropped.
    """
    if not counts.index.equals(cells.index):
        raise ValueError("counts and cell metadata must share the same index")
    keys = [cells[donor], cells[cell_type]]
    summed = counts.groupby(keys).sum()
    n = counts.groupby(keys).size().rename("n_cells")
    out = pd.concat([n, summed], axis=1)
    return out[out["n_cells"] >= min_cells]


def program_scores(expr: pd.DataFrame, programs: dict[str, list[str]] | None = None,
                   min_genes: int = 3) -> pd.DataFrame:
    """Mean z-score of each program's genes per row of a normalized expression matrix.

    Programs with fewer than ``min_genes`` genes present are skipped.
    """
    programs = programs or FATTY_ACID_PROGRAMS
    z = (expr - expr.mean()) / expr.std(ddof=1).replace(0, float("nan"))
    out = {}
    for name, genes in programs.items():
        present = [g for g in genes if g in z.columns]
        if len(present) >= min_genes:
            out[name] = z[present].mean(axis=1)
    return pd.DataFrame(out, index=expr.index)
