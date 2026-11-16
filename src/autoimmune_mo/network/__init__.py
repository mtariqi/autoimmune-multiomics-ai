"""Network biology: correlation networks, hub features and modules (networkx).

Use for metabolite, protein or gene co-variation networks. Large gene co-expression analyses
(WGCNA) run in R; this module covers the moderate-size networks used in this project.
"""

from __future__ import annotations

import networkx as nx
import numpy as np
import pandas as pd
from networkx.algorithms.community import greedy_modularity_communities

from ..stats import bh_fdr


def correlation_network(X: pd.DataFrame, method: str = "spearman", min_abs_r: float = 0.3,
                        max_q: float = 0.05) -> nx.Graph:
    """Edges between features with |r| >= ``min_abs_r`` and BH q <= ``max_q``.

    Edge attributes: ``r`` (signed) and ``weight`` (|r|).
    """
    from scipy.stats import pearsonr, spearmanr

    test = spearmanr if method == "spearman" else pearsonr
    cols = list(X.columns)
    pairs, rs, ps = [], [], []
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            ok = X[[cols[i], cols[j]]].dropna()
            if len(ok) < 5:
                continue
            r, p = test(ok.iloc[:, 0], ok.iloc[:, 1])
            pairs.append((cols[i], cols[j]))
            rs.append(r)
            ps.append(p)
    q = bh_fdr(ps)
    G = nx.Graph()
    G.add_nodes_from(cols)
    for (a, b), r, qq in zip(pairs, rs, q):
        if abs(r) >= min_abs_r and qq <= max_q:
            G.add_edge(a, b, r=float(r), weight=float(abs(r)))
    return G


def hub_table(G: nx.Graph) -> pd.DataFrame:
    """Degree, weighted degree (strength) and eigenvector centrality per node."""
    if G.number_of_edges() == 0:
        return pd.DataFrame(columns=["feature", "degree", "strength", "eigenvector", "module"])
    eig = {}
    for comp in nx.connected_components(G):  # centrality is only defined within a component
        if len(comp) > 2:
            eig.update(nx.eigenvector_centrality_numpy(G.subgraph(comp), weight="weight"))
    mods = {n: k for k, comm in enumerate(network_modules(G)) for n in comm}
    rows = [{"feature": n, "degree": G.degree(n), "strength": G.degree(n, weight="weight"),
             "eigenvector": eig.get(n, np.nan), "module": mods.get(n, -1)} for n in G.nodes]
    return pd.DataFrame(rows).sort_values("strength", ascending=False).reset_index(drop=True)


def network_modules(G: nx.Graph, min_size: int = 3) -> list[set]:
    """Modules by greedy modularity maximization; singletons and small groups are dropped."""
    comms = greedy_modularity_communities(G, weight="weight") if G.number_of_edges() else []
    return [set(c) for c in comms if len(c) >= min_size]


def edge_table(G: nx.Graph) -> pd.DataFrame:
    return pd.DataFrame([{"source": a, "target": b, **d} for a, b, d in G.edges(data=True)])


__all__ = ["correlation_network", "edge_table", "hub_table", "network_modules"]
