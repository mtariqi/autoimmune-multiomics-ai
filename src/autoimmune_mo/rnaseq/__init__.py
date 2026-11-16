"""Bulk RNA-seq helpers for count matrices (samples x genes).

Read processing (FastQC, trimming, STAR, featureCounts) and DESeq2 run in
``workflow/rules/rnaseq.smk``; these helpers cover filtering and normalized expression for
machine learning and integration.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def filter_low_counts(counts: pd.DataFrame, min_count: int = 10, min_samples: int | None = None):
    """Keep genes with at least ``min_count`` reads in at least ``min_samples`` samples
    (default: the size of the smallest group would be ideal; here 10% of samples, minimum 3)."""
    if min_samples is None:
        min_samples = max(3, int(0.1 * len(counts)))
    keep = (counts >= min_count).sum() >= min_samples
    return counts.loc[:, keep]


def log_cpm(counts: pd.DataFrame, prior: float = 1.0) -> pd.DataFrame:
    """log2 counts-per-million with a prior count, for visualization and ML features."""
    lib = counts.sum(axis=1)
    return np.log2((counts.add(prior)).div(lib + 2 * prior, axis=0) * 1e6)


__all__ = ["filter_low_counts", "log_cpm"]
