import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def rng():
    return np.random.default_rng(0)


@pytest.fixture
def cohort(rng):
    """60 participants x 2 visits, 8 features, first two informative."""
    n, visits = 60, 2
    y = rng.integers(0, 2, n)
    rows, X = [], []
    for i in range(n):
        for v in range(visits):
            rows.append({"participant_id": f"P{i:03d}", "y": y[i]})
            x = rng.normal(0, 1, 8)
            x[:2] += 1.5 * y[i]
            X.append(x)
    meta = pd.DataFrame(rows)
    X = pd.DataFrame(X, columns=[f"f{j}" for j in range(8)])
    return X, meta["y"].to_numpy(), meta["participant_id"].to_numpy()
