# ==============================================================================
# Project     : Autoimmune Multi-Omics AI (autoimmune-multiomics-ai)
# File        : workflow/scripts/metabolomics_preprocess.py
# Purpose     : Metabolomics QC, fatty-acid indices and baseline differential
#               analysis.
# Author      : Md Tariqul Islam
# Institution : Northeastern University | Bioinformatics Department
# License     : MIT (see LICENSE)
# ==============================================================================

"""Snakemake script: metabolomics QC, fatty-acid indices and baseline differential analysis."""

import pandas as pd

from autoimmune_mo.metabolomics import differential_abundance, fatty_acid_indices, preprocess

s = snakemake  # noqa: F821
samples = pd.read_csv(s.input.samples, sep="\t").set_index("sample_id")
raw = pd.read_csv(s.input.metabolomics, sep="\t", index_col=0)
qc = samples.loc[raw.index, "group"].eq("qc_pool").to_numpy()

log2 = preprocess(raw, qc_mask=qc, max_missing=s.params.qc["max_missing"],
                  max_cv=s.params.qc["max_qc_cv"])
log2.to_csv(s.output.log2, sep="\t")

study = raw.loc[~qc]
fatty_acid_indices(study.fillna(study.min() / 2), total=study.sum(axis=1)).to_csv(
    s.output.indices, sep="\t")

# one sample per person: compare progressors vs non-progressors at baseline
base = samples.loc[log2.index].query("visit == 0")
res = differential_abundance(log2.loc[base.index], base["progressed"].map({1: "progressor",
                             0: "non_progressor"}), "progressor", "non_progressor")
res.to_csv(s.output.differential, sep="\t", index=False)

with open(s.log[0], "w") as fh:
    dropped = sorted(set(raw.columns) - set(log2.columns))
    fh.write(f"kept {log2.shape[1]} of {raw.shape[1]} features; dropped {dropped}\n")
