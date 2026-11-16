# ==============================================================================
# Project     : Autoimmune Multi-Omics AI (autoimmune-multiomics-ai)
# File        : src/autoimmune_mo/stats.py
# Purpose     : Shared statistical helpers.
# Author      : Md Tariqul Islam
# Institution : Northeastern University | Bioinformatics Department
# License     : MIT (see LICENSE)
# ==============================================================================

"""Shared statistical helpers."""

from __future__ import annotations

import numpy as np


def bh_fdr(pvalues) -> np.ndarray:
    """Benjamini-Hochberg adjusted p-values (q-values). NaNs are kept as NaN."""
    p = np.asarray(pvalues, dtype=float)
    q = np.full_like(p, np.nan)
    ok = ~np.isnan(p)
    pv = p[ok]
    n = pv.size
    if n == 0:
        return q
    order = np.argsort(pv)
    ranked = pv[order] * n / np.arange(1, n + 1)
    ranked = np.minimum.accumulate(ranked[::-1])[::-1]
    out = np.empty(n)
    out[order] = np.clip(ranked, 0, 1)
    q[ok] = out
    return q
