"""Multi-omics integration.

* ``block_concat``: early integration. Scales each layer so no layer dominates by feature count.
* ``layer_pcs``: compresses each layer to principal components before integration.
* ``run_mofa``: MOFA+ factor analysis (optional dependency ``mofapy2``).

Late integration (one model per layer, then stacking) lives in ``autoimmune_mo.ml``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA


def _common_index(layers: dict[str, pd.DataFrame]) -> pd.Index:
    idx = None
    for X in layers.values():
        idx = X.index if idx is None else idx.intersection(X.index)
    if idx is None or len(idx) == 0:
        raise ValueError("layers share no samples")
    return idx


def block_concat(layers: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Z-score each feature, divide each layer by sqrt(n_features), concatenate on shared samples.

    Column names are prefixed with the layer name, e.g. ``metabolomics__DHA``.
    """
    idx = _common_index(layers)
    blocks = []
    for name, X in layers.items():
        X = X.loc[idx]
        z = (X - X.mean()) / X.std(ddof=1).replace(0, np.nan)
        z = z.dropna(axis=1, how="all") / np.sqrt(z.shape[1])
        blocks.append(z.add_prefix(f"{name}__"))
    return pd.concat(blocks, axis=1)


def layer_pcs(layers: dict[str, pd.DataFrame], n_components: int = 5, seed: int = 2026):
    """Top principal components of each z-scored layer, concatenated on shared samples."""
    idx = _common_index(layers)
    out = []
    for name, X in layers.items():
        z = ((X.loc[idx] - X.loc[idx].mean()) / X.loc[idx].std(ddof=1)).fillna(0)
        k = min(n_components, *z.shape)
        pcs = PCA(n_components=k, random_state=seed).fit_transform(z.values)
        out.append(pd.DataFrame(pcs, index=idx, columns=[f"{name}__PC{i + 1}" for i in range(k)]))
    return pd.concat(out, axis=1)


def run_mofa(layers: dict[str, pd.DataFrame], n_factors: int = 10, seed: int = 2026,
             outfile: str = "results/integration/mofa_model.hdf5"):
    """Fit MOFA+ on shared samples (requires ``pip install mofapy2``). Returns the output path."""
    from mofapy2.run.entry_point import entry_point

    idx = _common_index(layers)
    ent = entry_point()
    ent.set_data_options(scale_views=True)
    ent.set_data_matrix([[layers[k].loc[idx].values] for k in layers],
                        views_names=list(layers), samples_names=[list(idx)],
                        features_names=[list(layers[k].columns) for k in layers])
    ent.set_model_options(factors=n_factors)
    ent.set_train_options(seed=seed, convergence_mode="medium", verbose=False)
    ent.build()
    ent.run()
    ent.save(outfile)
    return outfile


__all__ = ["block_concat", "layer_pcs", "run_mofa"]
