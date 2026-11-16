# ==============================================================================
# Project     : Autoimmune Multi-Omics AI (autoimmune-multiomics-ai)
# File        : workflow/scripts/train_models.py
# Purpose     : Nested participant-grouped CV for each available model, plus
#               feature importance and its stability across folds.
# Author      : Md Tariqul Islam
# Institution : Northeastern University | Bioinformatics Department
# License     : MIT (see LICENSE)
# ==============================================================================

"""Snakemake script: nested participant-grouped CV for each available model, plus
feature importance and its stability across folds."""

import warnings

import pandas as pd

from autoimmune_mo.ml import (available_models, feature_importance, importance_stability,
                              nested_cv, summarize_metrics)

warnings.filterwarnings("ignore", category=FutureWarning)
s = snakemake  # noqa: F821
samples = pd.read_csv(s.input.samples, sep="\t").set_index("sample_id")
X = pd.read_csv(s.input.features, sep="\t", index_col=0)
meta = samples.loc[X.index]

models = [m for m in s.params.models if m in available_models()]
skipped = sorted(set(s.params.models) - set(models))
metrics, preds, fitted = nested_cv(X, meta["progressed"].to_numpy(),
                                   meta["participant_id"].to_numpy(), models,
                                   s.params.outer, s.params.inner, s.params.seed)
metrics.to_csv(s.output.metrics, sep="\t", index=False)
summarize_metrics(metrics).round(4).to_csv(s.output.summary, sep="\t", index=False)
preds.to_csv(s.output.predictions, sep="\t", index=False)

y = meta["progressed"].to_numpy()
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
    fh.write(f"models run: {models}; skipped (library not installed): {skipped}\n")
