"""Snakemake script: leakage-safe CV folds on the synthetic cohort, with a leak check."""

import pandas as pd

from autoimmune_mo.ml import participant_folds

df = pd.read_csv(snakemake.input[0], sep="\t")  # noqa: F821
p = snakemake.params  # noqa: F821

records = []
for k, (train, test) in enumerate(participant_folds(df, n_splits=p.n_splits, seed=p.seed)):
    tr, te = df.iloc[train], df.iloc[test]
    leaked = len(set(tr.participant_id) & set(te.participant_id))
    if leaked:
        raise RuntimeError(f"Fold {k}: {leaked} participants appear in train and test")
    records.append(
        {
            "fold": k,
            "n_train_rows": len(tr),
            "n_test_rows": len(te),
            "n_test_participants": te.participant_id.nunique(),
            "test_progressor_share": round(te.drop_duplicates("participant_id").progressed.mean(), 3),
            "participants_leaked": leaked,
        }
    )

pd.DataFrame(records).to_csv(snakemake.output[0], sep="\t", index=False)  # noqa: F821
with open(snakemake.log[0], "w") as fh:  # noqa: F821
    fh.write(f"{len(records)} folds, no participant leakage\n")
