"""Two-group differential abundance with Wilcoxon rank-sum tests and BH FDR."""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu

from ..stats import bh_fdr


def differential_abundance(X_log2: pd.DataFrame, groups, case, control) -> pd.DataFrame:
    """Compare ``case`` vs ``control`` for every feature of a log2-scale matrix.

    Returns one row per feature: medians, log2 fold change (difference of means on log2 scale),
    Wilcoxon p-value and BH q-value, sorted by p-value.
    """
    g = pd.Series(np.asarray(groups), index=X_log2.index)
    a, b = X_log2[g == case], X_log2[g == control]
    if len(a) < 3 or len(b) < 3:
        raise ValueError("need at least 3 samples per group")
    rows = []
    for f in X_log2.columns:
        x, y = a[f].dropna(), b[f].dropna()
        p = mannwhitneyu(x, y, alternative="two-sided").pvalue
        rows.append({"feature": f, "n_case": len(x), "n_control": len(y),
                     "log2_fc": x.mean() - y.mean(), "p": p})
    res = pd.DataFrame(rows)
    res["q"] = bh_fdr(res["p"])
    return res.sort_values("p").reset_index(drop=True)
