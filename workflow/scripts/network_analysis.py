"""Snakemake script: correlation network, hub features and modules."""

import pandas as pd

from autoimmune_mo.network import correlation_network, edge_table, hub_table

s = snakemake  # noqa: F821
X = pd.read_csv(s.input[0], sep="\t", index_col=0)
G = correlation_network(X, method=s.params.net["method"], min_abs_r=s.params.net["min_abs_r"],
                        max_q=s.params.net["max_q"])
hub_table(G).round(5).to_csv(s.output.hubs, sep="\t", index=False)
edge_table(G).round(5).to_csv(s.output.edges, sep="\t", index=False)
with open(s.log[0], "w") as fh:
    fh.write(f"{G.number_of_nodes()} nodes, {G.number_of_edges()} edges\n")
