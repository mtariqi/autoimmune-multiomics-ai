import numpy as np
import pandas as pd

from autoimmune_mo.integration import block_concat, layer_pcs
from autoimmune_mo.microbiome import aitchison_distance, clr, filter_prevalence, shannon
from autoimmune_mo.rnaseq import filter_low_counts, log_cpm
from autoimmune_mo.scrnaseq import program_scores, pseudobulk


def test_clr_rows_sum_to_zero(rng):
    c = pd.DataFrame(rng.poisson(20, (5, 6)))
    assert np.allclose(clr(c).sum(axis=1), 0)


def test_shannon_even_vs_dominated():
    c = pd.DataFrame([[10, 10, 10, 10], [37, 1, 1, 1]])
    h = shannon(c)
    assert np.isclose(h[0], np.log(4)) and h[1] < h[0]


def test_aitchison_symmetric_zero_diagonal(rng):
    d = aitchison_distance(pd.DataFrame(rng.poisson(5, (4, 6))))
    assert np.allclose(d, d.T) and np.allclose(np.diag(d), 0)


def test_prevalence_filter():
    c = pd.DataFrame({"common": [1, 2, 3, 4], "rare": [0, 0, 0, 1]})
    assert list(filter_prevalence(c, 0.5).columns) == ["common"]


def test_rnaseq_filter_and_logcpm(rng):
    counts = pd.DataFrame(rng.poisson(50, (6, 4)), columns=list("abcd"))
    counts["zero"] = 0
    kept = filter_low_counts(counts)
    assert "zero" not in kept.columns
    cpm = 2 ** log_cpm(kept, prior=0)
    assert np.allclose(cpm.sum(axis=1), 1e6)


def test_pseudobulk_sums_by_donor_and_type():
    counts = pd.DataFrame({"g1": [1] * 30, "g2": [2] * 30})
    cells = pd.DataFrame({"donor": ["d1"] * 15 + ["d2"] * 15,
                          "cell_type": (["mono"] * 10 + ["b"] * 5) * 2})
    pb = pseudobulk(counts, cells, min_cells=10)
    assert len(pb) == 2 and pb.loc[("d1", "mono"), "g2"] == 20


def test_program_scores_skip_small_programs(rng):
    expr = pd.DataFrame(rng.normal(0, 1, (5, 4)), columns=["FADS1", "FADS2", "SCD", "X"])
    out = program_scores(expr, {"fa": ["FADS1", "FADS2", "SCD"], "tiny": ["X"]})
    assert list(out.columns) == ["fa"]


def test_block_concat_and_pcs(rng):
    a = pd.DataFrame(rng.normal(size=(10, 50)), index=range(10))
    b = pd.DataFrame(rng.normal(size=(8, 4)), index=range(2, 10))
    X = block_concat({"rna": a, "met": b})
    assert X.shape == (8, 54) and X.columns[0].startswith("rna__")
    # each layer contributes equal total variance
    assert np.isclose(X.filter(like="rna__").var().sum(), X.filter(like="met__").var().sum())
    assert layer_pcs({"rna": a, "met": b}, n_components=3).shape == (8, 6)
