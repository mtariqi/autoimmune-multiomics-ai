# ==============================================================================
# Project     : Autoimmune Multi-Omics AI (autoimmune-multiomics-ai)
# File        : src/autoimmune_mo/ml/evaluate.py
# Purpose     : Nested, participant-grouped cross-validation with discrimination
#               and calibration metrics.
# Author      : Md Tariqul Islam
# Institution : Northeastern University | Bioinformatics Department
# License     : MIT (see LICENSE)
# ==============================================================================

"""Nested, participant-grouped cross-validation with discrimination and calibration metrics."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score
from sklearn.model_selection import GridSearchCV, StratifiedGroupKFold

from .models import make_model


def nested_cv(X: pd.DataFrame, y, groups, model_names, outer_folds: int = 5,
              inner_folds: int = 3, seed: int = 2026):
    """Outer loop estimates performance; inner loop tunes hyperparameters.

    Both loops split by ``groups`` (participant), so no person is in train and test at once.
    Returns (metrics per model and fold, out-of-fold predictions, fitted models per fold).
    """
    y = np.asarray(y)
    groups = np.asarray(groups)
    outer = StratifiedGroupKFold(n_splits=outer_folds, shuffle=True, random_state=seed)
    metrics, preds, fitted = [], [], {}
    for name in model_names:
        est, grid = make_model(name, seed)
        for k, (tr, te) in enumerate(outer.split(X, y, groups)):
            inner = StratifiedGroupKFold(n_splits=inner_folds, shuffle=True, random_state=seed)
            search = GridSearchCV(clone(est), grid, scoring="roc_auc", cv=inner, n_jobs=1)
            search.fit(X.iloc[tr], y[tr], groups=groups[tr])
            p = search.best_estimator_.predict_proba(X.iloc[te])[:, 1]
            metrics.append({
                "model": name, "fold": k, "n_test": len(te),
                "roc_auc": roc_auc_score(y[te], p),
                "average_precision": average_precision_score(y[te], p),
                "brier": brier_score_loss(y[te], p),
                "best_params": str(search.best_params_),
            })
            preds.append(pd.DataFrame({"model": name, "fold": k, "row": X.index[te],
                                       "y_true": y[te], "y_prob": p}))
            fitted[(name, k)] = (search.best_estimator_, te)
    return pd.DataFrame(metrics), pd.concat(preds, ignore_index=True), fitted


def summarize_metrics(metrics: pd.DataFrame) -> pd.DataFrame:
    """Mean and SD across outer folds for each model."""
    cols = ["roc_auc", "average_precision", "brier"]
    s = metrics.groupby("model")[cols].agg(["mean", "std"])
    s.columns = [f"{m}_{a}" for m, a in s.columns]
    return s.reset_index().sort_values("roc_auc_mean", ascending=False)


def calibration_table(y_true, y_prob, n_bins: int = 10) -> pd.DataFrame:
    """Observed vs mean predicted risk in quantile bins of predicted risk."""
    df = pd.DataFrame({"y": np.asarray(y_true), "p": np.asarray(y_prob)})
    df["bin"] = pd.qcut(df["p"], q=min(n_bins, df["p"].nunique()), duplicates="drop")
    out = df.groupby("bin", observed=True).agg(n=("y", "size"), mean_predicted=("p", "mean"),
                                               observed=("y", "mean"))
    return out.reset_index(drop=True)
