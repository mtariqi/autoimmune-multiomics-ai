# Explainable AI

**Code:** `autoimmune_mo.ml.explain`

- **SHAP** (when installed): mean absolute SHAP value per feature on each outer test fold. Tree and linear models use exact explainers; other models use a model-agnostic explainer.
- **Permutation importance** (fallback): drop in ROC AUC when a feature is shuffled, on held-out data.
- **Stability:** `importance_stability` reports each feature's mean rank, rank SD and the share of folds in which it is in the top *k*.

Only features that rank consistently across folds are interpreted biologically. Importance is
always computed on test folds, never on the data a model was trained on.
