# ==============================================================================
# Project     : Autoimmune Multi-Omics AI (autoimmune-multiomics-ai)
# File        : tests/test_metabolomics.py
# Purpose     : Unit tests: metabolomics.
# Author      : Md Tariqul Islam
# Institution : Northeastern University | Bioinformatics Department
# License     : MIT (see LICENSE)
# ==============================================================================

import numpy as np
import pandas as pd
import pytest

from autoimmune_mo.metabolomics import (
    differential_abundance,
    fatty_acid_indices,
    filter_missing,
    filter_qc_cv,
    impute_half_min,
    preprocess,
)


def test_filter_missing_drops_sparse_feature():
    X = pd.DataFrame({"a": [1, 2, 3, 4, 5], "b": [1, np.nan, np.nan, 0, 2]})
    assert list(filter_missing(X, 0.2).columns) == ["a"]


def test_qc_cv_filter(rng):
    X = pd.DataFrame({"stable": [10, 10.1, 9.9, 5, 6], "noisy": [1, 10, 5, 3, 3]})
    assert list(filter_qc_cv(X, [1, 1, 1, 0, 0], 0.3).columns) == ["stable"]


def test_half_min_imputation():
    X = pd.DataFrame({"a": [4.0, np.nan, 2.0]})
    assert impute_half_min(X)["a"].tolist() == [4.0, 1.0, 2.0]


def test_preprocess_removes_qc_and_logs(rng):
    X = pd.DataFrame(rng.lognormal(2, 0.1, (10, 3)), columns=list("abc"))
    qc = [1, 1, 1] + [0] * 7
    out = preprocess(X, qc_mask=qc)
    assert len(out) == 7 and out.max().max() < 10


def test_fatty_acid_indices():
    c = pd.DataFrame({"EPA": [1.0], "DHA": [3.0], "LA": [20.0], "AA": [8.0]})
    out = fatty_acid_indices(c, total=pd.Series([100.0]))
    assert out.loc[0, "omega3_total"] == 4 and out.loc[0, "omega6_omega3_ratio"] == 7
    assert out.loc[0, "omega3_index_pct"] == 4


def test_differential_finds_shifted_feature(rng):
    X = pd.DataFrame(rng.normal(0, 1, (40, 5)), columns=list("abcde"))
    g = np.array(["case"] * 20 + ["ctrl"] * 20)
    X.loc[:19, "a"] += 2
    res = differential_abundance(X, g, "case", "ctrl")
    assert res.iloc[0]["feature"] == "a" and res.iloc[0]["q"] < 0.01


def test_differential_needs_samples():
    X = pd.DataFrame({"a": [1, 2, 3, 4]})
    with pytest.raises(ValueError):
        differential_abundance(X, ["case", "case", "ctrl", "ctrl"], "case", "ctrl")
