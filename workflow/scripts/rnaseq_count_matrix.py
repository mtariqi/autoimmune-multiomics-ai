# ==============================================================================
# Project     : Autoimmune Multi-Omics AI (autoimmune-multiomics-ai)
# File        : workflow/scripts/rnaseq_count_matrix.py
# Purpose     : FeatureCounts output -> samples x genes count matrix.
# Author      : Md Tariqul Islam
# Institution : Northeastern University | Bioinformatics Department
# License     : MIT (see LICENSE)
# ==============================================================================

"""Snakemake script: featureCounts output -> samples x genes count matrix."""

import re

import pandas as pd

s = snakemake  # noqa: F821
fc = pd.read_csv(s.input[0], sep="\t", comment="#", index_col=0)
counts = fc.iloc[:, 5:]  # drop Chr, Start, End, Strand, Length
counts.columns = [re.sub(r"\.Aligned\.sortedByCoord\.out\.bam$", "", c.split("/")[-1])
                  for c in counts.columns]
counts.T.rename_axis("sample_id").to_csv(s.output[0], sep="\t")
with open(s.log[0], "w") as fh:
    fh.write(f"{counts.shape[1]} samples x {counts.shape[0]} genes\n")
