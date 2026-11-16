# Multi-omics integration

**Code:** `autoimmune_mo.integration`

| Strategy | Function | When to use |
| --- | --- | --- |
| Early integration | `block_concat` | Few layers, moderate features. Each layer is scaled so it contributes equal total variance, whatever its number of features. |
| Compressed early integration | `layer_pcs` | Many features per layer; top principal components per layer are concatenated. |
| Factor analysis | `run_mofa` (MOFA+) | Discovering shared and layer-specific sources of variation; inputs to endotyping. |
| Late integration | `autoimmune_mo.ml` | One model per layer, combined by stacking. Usually the most robust with about 100 events. |

All integration uses only samples present in every layer. Feature scaling is learned on training
data only when integration feeds a prediction model.
