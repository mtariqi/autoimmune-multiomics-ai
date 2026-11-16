"""Fatty-acid indices from absolute concentrations (same units across columns)."""

from __future__ import annotations

import numpy as np
import pandas as pd

OMEGA3 = ("ALA", "EPA", "DPA", "DHA")
OMEGA6 = ("LA", "GLA", "DGLA", "AA")


def fatty_acid_indices(
    conc: pd.DataFrame, omega3=OMEGA3, omega6=OMEGA6, total: pd.Series | None = None
) -> pd.DataFrame:
    """Total omega-3, total omega-6, omega-6:omega-3 ratio and (if ``total`` given) omega-3 index.

    The omega-3 index here is (EPA + DHA) as a percentage of ``total`` fatty acids.
    Columns not present in ``conc`` are ignored, and the columns used are recorded in ``.attrs``.
    """
    n3 = [c for c in omega3 if c in conc.columns]
    n6 = [c for c in omega6 if c in conc.columns]
    if not n3 or not n6:
        raise ValueError("need at least one omega-3 and one omega-6 column")
    out = pd.DataFrame(index=conc.index)
    out["omega3_total"] = conc[n3].sum(axis=1)
    out["omega6_total"] = conc[n6].sum(axis=1)
    out["omega6_omega3_ratio"] = out["omega6_total"] / out["omega3_total"].replace(0, np.nan)
    if total is not None:
        epa_dha = conc[[c for c in ("EPA", "DHA") if c in conc.columns]].sum(axis=1)
        out["omega3_index_pct"] = 100 * epa_dha / total
    out.attrs["omega3_columns"], out.attrs["omega6_columns"] = n3, n6
    return out
