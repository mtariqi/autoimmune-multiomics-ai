# ==============================================================================
# Project     : Autoimmune Multi-Omics AI (autoimmune-multiomics-ai)
# File        : src/autoimmune_mo/ml/explain.py
# Purpose     : Model explanations: SHAP when installed, permutation importance
#               otherwise, plus a stability check across cross-validation folds.
# Author      : Md Tariqul Islam
# Institution : Northeastern University | Bioinformatics Department
# License     : MIT (see LICENSE)
# ==============================================================================

"""Model explanations: SHAP when installed, permutation importance otherwise,
plus a stability check across cross-validation folds."""

from __future__ import annotations

import importlib.util

import numpy as np
import pandas as pd
from sklearn.inspection import permutation_importance

TREE_MODELS = {"RandomForestClassifier", "XGBClassifier", "LGBMClassifier"}


def _make_explainer(shap, model, Xt, seed):
    """Exact explainers for tree and linear models; model-agnostic otherwise (e.g. MLP)."""
    name = type(model).__name__
    if name in TREE_MODELS:
        return shap.TreeExplainer(model)
    if name == "LogisticRegression":
        return shap.LinearExplainer(model, Xt)
    return shap.Explainer(lambda a: model.predict_proba(a)[:, 1], Xt, seed=seed)


def feature_importance(pipeline, X: pd.DataFrame, y=None, method: str = "auto",
                       seed: int = 2026) -> pd.Series:
    """Global importance per feature for a fitted sklearn Pipeline.

    ``method='shap'``: mean |SHAP value| (needs ``shap``).
    ``method='permutation'``: drop in ROC AUC when a feature is shuffled (needs ``y``).
    ``method='auto'``: SHAP if installed, otherwise permutation.
    """
    if method == "auto":
        method = "shap" if importlib.util.find_spec("shap") else "permutation"
    if method == "shap":
        import shap

        pre = pipeline[:-1]
        model = pipeline[-1]
        Xt = pd.DataFrame(pre.transform(X), index=X.index, columns=X.columns)
        explainer = _make_explainer(shap, model, Xt, seed)
        sv = explainer(Xt)
        vals = sv.values[..., 1] if sv.values.ndim == 3 else sv.values
        imp = np.abs(vals).mean(axis=0)
    elif method == "permutation":
        if y is None:
            raise ValueError("permutation importance needs y")
        r = permutation_importance(pipeline, X, y, scoring="roc_auc", n_repeats=10,
                                   random_state=seed, n_jobs=1)
        imp = r.importances_mean
    else:
        raise ValueError(f"unknown method '{method}'")
    s = pd.Series(imp, index=X.columns, name=method)
    return s.sort_values(ascending=False)


def importance_stability(per_fold: list[pd.Series], top_k: int = 10) -> pd.DataFrame:
    """How consistently each feature ranks across folds.

    Returns mean rank, SD of rank and the share of folds in which the feature is in the top ``k``.
    Only features that are stable across folds should be interpreted biologically.
    """
    ranks = pd.concat([s.rank(ascending=False) for s in per_fold], axis=1)
    out = pd.DataFrame({
        "mean_rank": ranks.mean(axis=1),
        "sd_rank": ranks.std(axis=1, ddof=1),
        f"top{top_k}_frequency": (ranks <= top_k).mean(axis=1),
        "mean_importance": pd.concat(per_fold, axis=1).mean(axis=1),
    })
    return out.sort_values("mean_rank")
