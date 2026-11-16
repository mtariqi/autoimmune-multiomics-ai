"""Snakemake script: species-level MetaPhlAn table -> alpha diversity, CLR, Aitchison distance."""

import pandas as pd

from autoimmune_mo.microbiome import aitchison_distance, clr, filter_prevalence, shannon

s = snakemake  # noqa: F821
tab = pd.read_csv(s.input[0], sep="\t", comment="#", index_col=0)
tab = tab.drop(columns=[c for c in tab.columns if c.upper() == "NCBI_TAX_ID"], errors="ignore")
species = tab[tab.index.str.contains(r"\|s__") & ~tab.index.str.contains(r"\|t__")]
X = species.T / 100.0  # samples x species, relative abundance 0-1
X.columns = [c.split("|s__")[-1] for c in X.columns]
X = filter_prevalence(X, s.params.min_prevalence)

pseudo = X[X > 0].min().min() / 2  # zero handling on relative abundances
alpha = pd.concat([shannon(X), (X > 0).sum(axis=1).rename("richness")], axis=1)
alpha.rename_axis("sample_id").to_csv(s.output.alpha, sep="\t")
clr(X, pseudocount=pseudo).rename_axis("sample_id").to_csv(s.output.clr, sep="\t")
aitchison_distance(X, pseudocount=pseudo).to_csv(s.output.dist, sep="\t")
with open(s.log[0], "w") as fh:
    fh.write(f"{X.shape[0]} samples x {X.shape[1]} species after prevalence filter\n")
