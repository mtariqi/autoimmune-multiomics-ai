"""Leakage-safe cross-validation: all visits of a participant stay in one fold."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedGroupKFold


def participant_folds(
    df: pd.DataFrame,
    label: str = "progressed",
    group: str = "participant_id",
    n_splits: int = 5,
    seed: int = 2026,
):
    """Yield (train_idx, test_idx) with no participant in both sets.

    Stratifies on the participant-level label so each fold keeps a similar share of progressors.
    """
    cv = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    y = df[label].to_numpy()
    groups = df[group].to_numpy()
    yield from cv.split(np.zeros(len(df)), y, groups)
