"""Standard targeted-metabolomics preprocessing on a samples x features matrix."""

from __future__ import annotations

import numpy as np
import pandas as pd


def filter_missing(X: pd.DataFrame, max_missing: float = 0.2) -> pd.DataFrame:
    """Drop features missing (NaN or <= 0) in more than ``max_missing`` of samples."""
    miss = (X.isna() | (X <= 0)).mean()
    return X.loc[:, miss <= max_missing]


def filter_qc_cv(X: pd.DataFrame, qc_mask, max_cv: float = 0.3) -> pd.DataFrame:
    """Drop features whose coefficient of variation in pooled QC samples exceeds ``max_cv``."""
    qc = X.loc[np.asarray(qc_mask, dtype=bool)]
    if len(qc) < 3:
        raise ValueError("Need at least 3 pooled QC samples to estimate CV")
    cv = qc.std(ddof=1) / qc.mean()
    return X.loc[:, cv <= max_cv]


def impute_half_min(X: pd.DataFrame) -> pd.DataFrame:
    """Replace missing / non-positive values with half the feature's smallest positive value."""
    X = X.where(X > 0)
    return X.fillna(X.min() / 2)


def log2_transform(X: pd.DataFrame) -> pd.DataFrame:
    if (X <= 0).any().any():
        raise ValueError("log2 requires positive values; impute first")
    return np.log2(X)


def scale(X: pd.DataFrame, method: str = "auto") -> pd.DataFrame:
    """Center and scale features: 'auto' (unit variance) or 'pareto' (sqrt of SD)."""
    centered = X - X.mean()
    sd = X.std(ddof=1).replace(0, np.nan)
    if method == "auto":
        return centered / sd
    if method == "pareto":
        return centered / np.sqrt(sd)
    raise ValueError(f"unknown scaling method '{method}'")


def preprocess(
    X: pd.DataFrame,
    qc_mask=None,
    max_missing: float = 0.2,
    max_cv: float = 0.3,
    scaling: str | None = None,
) -> pd.DataFrame:
    """Missingness filter -> QC CV filter -> half-min imputation -> log2 -> optional scaling.

    QC samples are used for filtering and then removed from the returned matrix.
    """
    X = filter_missing(X, max_missing)
    if qc_mask is not None:
        qc_mask = np.asarray(qc_mask, dtype=bool)
        X = filter_qc_cv(X, qc_mask, max_cv)
        X = X.loc[~qc_mask]
    X = log2_transform(impute_half_min(X))
    return scale(X, scaling) if scaling else X
