# ==============================================================================
# Project     : Autoimmune Multi-Omics AI (autoimmune-multiomics-ai)
# File        : workflow/scripts/demo_synthetic_data.py
# Purpose     : Synthetic at-risk cohort with serum fatty acids (no real data).
# Author      : Md Tariqul Islam
# Institution : Northeastern University | Bioinformatics Department
# License     : MIT (see LICENSE)
# ==============================================================================

"""Snakemake script: synthetic at-risk cohort with serum fatty acids (no real data).

Progressors get lower EPA/DHA and higher arachidonic acid. Omega-3 species share a latent factor,
so the network step has real structure to find. Includes pooled QC samples and some missingness.
"""

import numpy as np
import pandas as pd

p = snakemake.params  # noqa: F821
rng = np.random.default_rng(p.seed)

# typical serum concentrations (umol/L), purely illustrative
BASE = {"ALA": 60, "EPA": 50, "DPA": 25, "DHA": 120, "LA": 3000, "GLA": 40, "DGLA": 120,
        "AA": 800, "PA": 2500, "SA": 750, "OA": 2200, "C20_3n9": 8}
EFFECT = {"EPA": -0.25, "DHA": -0.2, "DPA": -0.1, "AA": 0.15}  # log-scale shift in progressors

samples, rows = [], []
for i in range(p.n_participants):
    pid = f"SYN{i:04d}"
    y = int(rng.random() < 0.25)
    sex = rng.choice(["F", "M"], p=[0.7, 0.3])
    age = round(float(rng.normal(52, 10)), 1)
    n3 = rng.normal(0, 0.25)  # person-level omega-3 status (diet)
    for v in range(p.visits):
        sid = f"{pid}_V{v}"
        samples.append({"sample_id": sid, "participant_id": pid, "visit": v,
                        "months_from_baseline": 6.0 * v, "group": "at_risk", "sex": sex,
                        "age": age + 0.5 * v, "progressed": y, "batch": f"plate{v + 1}"})
        conc = {}
        for fa, base in BASE.items():
            mu = np.log(base) + (n3 if fa in ("ALA", "EPA", "DPA", "DHA") else 0)
            mu += EFFECT.get(fa, 0) * y * (v + 1) / p.visits
            conc[fa] = float(np.exp(rng.normal(mu, 0.2)))
        rows.append({"sample_id": sid, **conc})

pool = pd.DataFrame(rows).drop(columns="sample_id").mean()
for q in range(p.n_qc):
    sid = f"QC{q:02d}"
    samples.append({"sample_id": sid, "participant_id": sid, "visit": 0,
                    "months_from_baseline": 0.0, "group": "qc_pool", "sex": "unknown",
                    "age": 0.0, "batch": "plate1"})
    noise = {fa: float(v * np.exp(rng.normal(0, 0.05))) for fa, v in pool.items()}
    noise["C20_3n9"] *= float(np.exp(rng.normal(0, 0.6)))  # an unreliable assay -> fails QC CV
    rows.append({"sample_id": sid, **noise})

met = pd.DataFrame(rows).set_index("sample_id")
mask = rng.random(met.shape) < 0.03  # sporadic missing values
met = met.mask(mask)
met.loc[met.sample(frac=0.4, random_state=p.seed).index, "GLA"] = np.nan  # too sparse -> dropped

pd.DataFrame(samples).to_csv(snakemake.output.samples, sep="\t", index=False)  # noqa: F821
met.round(4).to_csv(snakemake.output.metabolomics, sep="\t")  # noqa: F821
with open(snakemake.log[0], "w") as fh:  # noqa: F821
    fh.write(f"{len(samples)} samples ({p.n_qc} QC), {met.shape[1]} fatty acids\n")
