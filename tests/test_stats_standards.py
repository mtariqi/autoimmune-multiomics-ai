import numpy as np
import pandas as pd

from autoimmune_mo.standards import (SAMPLE_SHEET, check_matrix_matches_samples, validate_table)
from autoimmune_mo.stats import bh_fdr


def test_bh_matches_known_values():
    q = bh_fdr([0.01, 0.04, 0.03, 0.2])
    assert np.allclose(q, [0.04, 0.0533333, 0.0533333, 0.2])


def test_bh_keeps_nan():
    q = bh_fdr([0.01, np.nan])
    assert np.isnan(q[1]) and q[0] == 0.01


def _sheet():
    return pd.DataFrame({
        "sample_id": ["S1", "S2"], "participant_id": ["P1", "P1"], "visit": [0, 1],
        "months_from_baseline": [0, 6], "group": ["at_risk", "at_risk"],
        "sex": ["F", "F"], "age": [50, 50.5]})


def test_valid_sheet_passes():
    assert validate_table(_sheet(), SAMPLE_SHEET) == []


def test_invalid_sheet_reports_each_problem():
    df = _sheet()
    df.loc[1, "sample_id"] = "S1"
    df.loc[0, "group"] = "patient"
    df.loc[0, "age"] = 150
    probs = " | ".join(validate_table(df.drop(columns="sex"), SAMPLE_SHEET))
    for expected in ["missing required column 'sex'", "'group'", "above 120", "duplicated"]:
        assert expected in probs


def test_matrix_sample_mismatch():
    m = pd.DataFrame({"a": [1, 2]}, index=["S1", "S9"])
    assert len(check_matrix_matches_samples(m, _sheet())) == 2
