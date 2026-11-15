"""Snakemake script: generate a small synthetic longitudinal cohort (no real data)."""

import numpy as np
import pandas as pd

p = snakemake.params  # noqa: F821  (injected by Snakemake)
rng = np.random.default_rng(p.seed)

people = [f"SYN{i:04d}" for i in range(p.n_participants)]
progressed = rng.binomial(1, 0.25, p.n_participants)

rows = []
for pid, y in zip(people, progressed):
    for visit in range(p.visits):
        feats = rng.normal(0.4 * y, 1.0, p.n_features)
        rows.append(
            {"participant_id": pid, "visit": visit, "progressed": int(y)}
            | {f"feature_{j:02d}": round(v, 5) for j, v in enumerate(feats)}
        )

pd.DataFrame(rows).to_csv(snakemake.output[0], sep="\t", index=False)  # noqa: F821
with open(snakemake.log[0], "w") as fh:  # noqa: F821
    fh.write(f"{len(rows)} rows, {p.n_participants} participants, seed {p.seed}\n")
