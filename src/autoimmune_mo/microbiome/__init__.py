# ==============================================================================
# Project     : Autoimmune Multi-Omics AI (autoimmune-multiomics-ai)
# File        : src/autoimmune_mo/microbiome/__init__.py
# Purpose     : Microbiome: compositional transforms and diversity for taxa
#               tables (samples x taxa).
# Author      : Md Tariqul Islam
# Institution : Northeastern University | Bioinformatics Department
# License     : MIT (see LICENSE)
# ==============================================================================

"""Microbiome: compositional transforms and diversity for taxa tables (samples x taxa)."""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.spatial.distance import pdist, squareform


def filter_prevalence(counts: pd.DataFrame, min_prevalence: float = 0.1) -> pd.DataFrame:
    """Keep taxa present (>0) in at least ``min_prevalence`` of samples."""
    return counts.loc[:, (counts > 0).mean() >= min_prevalence]


def relative_abundance(counts: pd.DataFrame) -> pd.DataFrame:
    return counts.div(counts.sum(axis=1), axis=0)


def clr(counts: pd.DataFrame, pseudocount: float = 0.5) -> pd.DataFrame:
    """Centred log-ratio transform (handles zeros with a pseudocount)."""
    logx = np.log(counts + pseudocount)
    return logx.sub(logx.mean(axis=1), axis=0)


def shannon(counts: pd.DataFrame) -> pd.Series:
    p = relative_abundance(counts)
    with np.errstate(divide="ignore", invalid="ignore"):
        h = -(p * np.log(p)).where(p > 0, 0).sum(axis=1)
    return h.rename("shannon")


def observed_richness(counts: pd.DataFrame) -> pd.Series:
    return (counts > 0).sum(axis=1).rename("richness")


def aitchison_distance(counts: pd.DataFrame, pseudocount: float = 0.5) -> pd.DataFrame:
    """Euclidean distance on CLR-transformed data (Aitchison distance), samples x samples."""
    z = clr(counts, pseudocount)
    d = squareform(pdist(z.values, metric="euclidean"))
    return pd.DataFrame(d, index=counts.index, columns=counts.index)


__all__ = ["aitchison_distance", "clr", "filter_prevalence", "observed_richness",
           "relative_abundance", "shannon"]
