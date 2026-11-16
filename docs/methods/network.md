# Network biology

**Code:** `autoimmune_mo.network` · **Rule:** `demo_network`

1. **Correlation network:** Spearman correlation for every feature pair; an edge is kept if |r| ≥ 0.3 and BH q ≤ 0.05.
2. **Hubs:** degree, weighted degree (strength) and eigenvector centrality, computed within each connected component.
3. **Modules:** greedy modularity maximization; modules smaller than 3 features are dropped.

This suits metabolite and protein networks (tens to hundreds of features). Genome-wide
co-expression modules (WGCNA) run in R in Phase 2. Protein-protein interaction context comes
from STRING, and Cytoscape can open `network_edges.tsv` directly.
