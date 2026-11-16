# ==============================================================================
# Project     : Autoimmune Multi-Omics AI (autoimmune-multiomics-ai)
# File        : workflow/scripts/classifier_cv.py
# Purpose     : Nested CV on a secure fatty-acid table (one row per sample).
# Author      : Md Tariqul Islam
# Institution : Northeastern University | Bioinformatics Department
# License     : MIT (see LICENSE)
# ==============================================================================

"""Snakemake script: nested CV on a secure fatty-acid table (one row per sample).

The table needs the label column, an ID column (participant, used for grouping) and numeric
feature columns. Every other non-numeric column is ignored.
"""

import warnings

import numpy as np
import pandas as pd

from autoimmune_mo.ml import (available_models, feature_importance, importance_stability,
                              nested_cv, summarize_metrics)

warnings.filterwarnings("ignore", category=FutureWarning)
s = snakemake  # noqa: F821
c = s.params.clf
df = pd.read_csv(s.input[0])
y = df[c["label"]].map(dict(zip(c["label_values"], [0, 1]))).to_numpy()
if np.isnan(y.astype(float)).any():
    raise ValueError(f"label values must be {c['label_values']}")
groups = df[c["id_column"]].astype(str).to_numpy()
X = df.drop(columns=[c["label"], c["id_column"]]).select_dtypes("number")
X = np.log2(X.where(X > 0).fillna(X[X > 0].min() / 2)) if c.get("log2", True) else X

models = [m for m in c["models"] if m in available_models()]
metrics, preds, fitted = nested_cv(X, y, groups, models, s.params.outer, s.params.inner,
                                   s.params.seed)
metrics.to_csv(s.output.metrics, sep="\t", index=False)
summarize_metrics(metrics).round(4).to_csv(s.output.summary, sep="\t", index=False)
preds.to_csv(s.output.predictions, sep="\t", index=False)

tables = []
for name in models:
    per_fold = [feature_importance(est, X.iloc[te], y[te], method=s.params.method,
                                   seed=s.params.seed)
                for (m, _), (est, te) in fitted.items() if m == name]
    t = importance_stability(per_fold, top_k=5)
    t.insert(0, "model", name)
    tables.append(t.rename_axis("feature").reset_index())
pd.concat(tables).round(5).to_csv(s.output.importance, sep="\t", index=False)
with open(s.log[0], "w") as fh:
    fh.write(f"{len(df)} samples, {X.shape[1]} features, models {models}\n")
