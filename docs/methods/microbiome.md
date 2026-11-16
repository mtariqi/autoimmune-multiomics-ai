# Microbiome

**Code:** `autoimmune_mo.microbiome` · **Rules:** `workflow/rules/microbiome.smk` · **Status:** ready for Phase 2 data.

| Step | Tool |
| --- | --- |
| Taxonomic profiling | MetaPhlAn 4.1 |
| Functional profiling | HUMAnN 3.9 (pathway abundance, renormalized to relative abundance) |
| Prevalence filter | species present in at least 10% of samples |
| Alpha diversity | Shannon index, observed richness |
| Compositional transform | centred log-ratio (CLR) with a pseudocount of half the smallest non-zero value |
| Beta diversity | Aitchison distance (Euclidean distance on CLR) |

Microbiome data are compositional, so differential abundance uses compositional methods
(ANCOM-BC2 and MaAsLin2; only features found by both are reported). Host reads must be removed
before data leave the sequencing core.
