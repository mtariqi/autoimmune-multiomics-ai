import numpy as np
import pandas as pd

from autoimmune_mo.ml import participant_folds


def _toy(n_people=40, visits=3, seed=0):
    rng = np.random.default_rng(seed)
    progressed = rng.integers(0, 2, n_people)
    rows = [
        {"participant_id": f"P{i:03d}", "visit": v, "progressed": progressed[i]}
        for i in range(n_people)
        for v in range(visits)
    ]
    return pd.DataFrame(rows)


def test_no_participant_leaks_across_folds():
    df = _toy()
    for train, test in participant_folds(df, n_splits=4):
        assert set(df.iloc[train].participant_id).isdisjoint(df.iloc[test].participant_id)


def test_every_row_tested_once():
    df = _toy()
    tested = np.concatenate([test for _, test in participant_folds(df, n_splits=4)])
    assert sorted(tested) == list(range(len(df)))
