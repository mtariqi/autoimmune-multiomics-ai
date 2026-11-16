# ==============================================================================
# Project     : Autoimmune Multi-Omics AI (autoimmune-multiomics-ai)
# File        : workflow/scripts/demo_cv_folds.py
# Purpose     : Leakage-safe CV folds on the synthetic cohort, with a leak
#               check.
# Author      : Md Tariqul Islam
# Institution : Northeastern University | Bioinformatics Department
# License     : MIT (see LICENSE)
# ==============================================================================

"""Snakemake script: leakage-safe CV folds on the synthetic cohort, with a leak check."""

import pandas as pd

from autoimmune_mo.ml import participant_folds

s = snakemake  # noqa: F821
df = pd.read_csv(s.input.samples, sep="\t").query("group != 'qc_pool'").reset_index(drop=True)

records = []
for k, (train, test) in enumerate(participant_folds(df, n_splits=s.params.n_splits,
                                                     seed=s.params.seed)):
    tr, te = df.iloc[train], df.iloc[test]
    leaked = len(set(tr.participant_id) & set(te.participant_id))
    if leaked:
        raise RuntimeError(f"Fold {k}: {leaked} participants appear in train and test")
    records.append({"fold": k, "n_train_rows": len(tr), "n_test_rows": len(te),
                    "n_test_participants": te.participant_id.nunique(),
                    "test_progressor_share": round(
                        te.drop_duplicates("participant_id").progressed.mean(), 3),
                    "participants_leaked": leaked})

pd.DataFrame(records).to_csv(s.output[0], sep="\t", index=False)
with open(s.log[0], "w") as fh:
    fh.write(f"{len(records)} folds, no participant leakage\n")
