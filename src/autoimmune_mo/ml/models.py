"""Model registry. Each entry returns (estimator pipeline, hyperparameter grid).

Gradient-boosting libraries are optional: a model is available only if its library is installed.
"""

from __future__ import annotations

import importlib.util

import sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


_SKLEARN = tuple(int(x) for x in sklearn.__version__.split(".")[:2])


def _pipe(model, scale=True):
    steps = [("impute", SimpleImputer(strategy="median"))]
    if scale:
        steps.append(("scale", StandardScaler()))
    steps.append(("model", model))
    return Pipeline(steps)


def _logistic(seed):
    kw = dict(solver="saga", l1_ratio=0.5, C=1.0, max_iter=5000, random_state=seed)
    if _SKLEARN < (1, 8):  # older versions need the penalty named explicitly
        kw["penalty"] = "elasticnet"
    m = LogisticRegression(**kw)
    return _pipe(m), {"model__C": [0.01, 0.1, 1.0], "model__l1_ratio": [0.2, 0.8]}


def _random_forest(seed):
    m = RandomForestClassifier(n_estimators=300, min_samples_leaf=5, random_state=seed, n_jobs=1)
    return _pipe(m, scale=False), {"model__max_features": ["sqrt", 0.3]}


def _xgboost(seed):
    from xgboost import XGBClassifier

    m = XGBClassifier(n_estimators=300, learning_rate=0.05, subsample=0.8, colsample_bytree=0.8,
                      eval_metric="logloss", random_state=seed, n_jobs=1)
    return _pipe(m, scale=False), {"model__max_depth": [2, 4]}


def _lightgbm(seed):
    from lightgbm import LGBMClassifier

    m = LGBMClassifier(n_estimators=300, learning_rate=0.05, subsample=0.8, subsample_freq=1,
                       colsample_bytree=0.8, random_state=seed, n_jobs=1, verbose=-1)
    return _pipe(m, scale=False), {"model__num_leaves": [7, 15]}


def _mlp(seed):
    # Small neural-network baseline. Deep learning frameworks are added only if this and the
    # tree models are clearly outperformed on held-out data.
    m = MLPClassifier(hidden_layer_sizes=(32,), alpha=1e-2, max_iter=2000, early_stopping=True,
                      random_state=seed)
    return _pipe(m), {"model__alpha": [1e-3, 1e-1]}


_REGISTRY = {
    "logistic_elastic_net": (_logistic, None),
    "random_forest": (_random_forest, None),
    "xgboost": (_xgboost, "xgboost"),
    "lightgbm": (_lightgbm, "lightgbm"),
    "mlp": (_mlp, None),
}


def available_models() -> list[str]:
    return [n for n, (_, lib) in _REGISTRY.items()
            if lib is None or importlib.util.find_spec(lib) is not None]


def make_model(name: str, seed: int = 2026):
    if name not in _REGISTRY:
        raise KeyError(f"unknown model '{name}'; choose from {list(_REGISTRY)}")
    if name not in available_models():
        raise ImportError(f"model '{name}' needs '{_REGISTRY[name][1]}' installed")
    return _REGISTRY[name][0](seed)
