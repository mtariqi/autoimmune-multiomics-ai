# ==============================================================================
# Project     : Autoimmune Multi-Omics AI (autoimmune-multiomics-ai)
# File        : tests/test_ml_network.py
# Purpose     : Unit tests: ml network.
# Author      : Md Tariqul Islam
# Institution : Northeastern University | Bioinformatics Department
# License     : MIT (see LICENSE)
# ==============================================================================

import pandas as pd
import pytest

from autoimmune_mo.ml import (
    available_models,
    calibration_table,
    feature_importance,
    importance_stability,
    nested_cv,
    summarize_metrics,
)
from autoimmune_mo.network import correlation_network, hub_table


def test_registry_has_core_models():
    assert {"logistic_elastic_net", "random_forest", "mlp"} <= set(available_models())


def test_nested_cv_learns_signal_without_leakage(cohort):
    X, y, groups = cohort
    metrics, preds, fitted = nested_cv(X, y, groups, ["logistic_elastic_net"], 3, 3)
    assert metrics["roc_auc"].mean() > 0.75
    for (_, te) in fitted.values():
        test_people = set(groups[te])
        train_people = set(groups) - test_people
        assert test_people.isdisjoint(train_people)
    assert len(preds) == len(X)
    assert "roc_auc_mean" in summarize_metrics(metrics).columns


@pytest.mark.parametrize("name", ["xgboost", "lightgbm"])
def test_boosting_models_when_installed(cohort, name):
    pytest.importorskip(name)
    X, y, groups = cohort
    metrics, _, _ = nested_cv(X, y, groups, [name], 3, 2)
    assert metrics["roc_auc"].mean() > 0.6


def test_permutation_importance_ranks_informative_first(cohort):
    X, y, groups = cohort
    _, _, fitted = nested_cv(X, y, groups, ["random_forest"], 3, 2)
    per_fold = [feature_importance(m, X.iloc[te], y[te], method="permutation")
                for (m, te) in fitted.values()]
    stab = importance_stability(per_fold, top_k=2)
    assert set(stab.index[:2]) == {"f0", "f1"}


def test_shap_when_installed(cohort):
    pytest.importorskip("shap")
    X, y, groups = cohort
    _, _, fitted = nested_cv(X, y, groups, ["random_forest"], 3, 2)
    m, te = next(iter(fitted.values()))
    imp = feature_importance(m, X.iloc[te], method="shap")
    assert set(imp.index[:2]) == {"f0", "f1"}


def test_calibration_table(cohort):
    _, y, _ = cohort
    t = calibration_table(y, y * 0.8 + 0.1, n_bins=2)
    assert t["n"].sum() == len(y)


def test_network_recovers_module(rng):
    base = rng.normal(size=100)
    X = pd.DataFrame({f"m{i}": base + rng.normal(0, 0.3, 100) for i in range(4)})
    X["noise"] = rng.normal(size=100)
    G = correlation_network(X, min_abs_r=0.5)
    hubs = hub_table(G)
    assert G.degree("noise") == 0 and hubs.iloc[0]["feature"].startswith("m")
    assert hubs.loc[hubs.feature.str.startswith("m"), "module"].nunique() == 1
