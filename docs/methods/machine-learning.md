# Machine learning

**Code:** `autoimmune_mo.ml` · **Rules:** `demo_models`, `classifier_cv`

## Models

| Name | Family | Tuned in inner CV |
| --- | --- | --- |
| `logistic_elastic_net` | Penalized logistic regression (baseline) | C, L1 ratio |
| `random_forest` | Tree ensemble | max features |
| `xgboost` | Gradient boosting (optional install) | max depth |
| `lightgbm` | Gradient boosting (optional install) | number of leaves |
| `mlp` | Small neural network | L2 penalty |

Every model is a scikit-learn pipeline: median imputation, scaling where needed, then the model,
so preprocessing is fitted inside each training fold.

## Validation

- **Nested cross-validation:** the outer loop (5 folds) estimates performance; the inner loop tunes hyperparameters.
- **Grouped by participant:** repeated visits of one person never appear in both training and test data (`StratifiedGroupKFold`).
- **Metrics:** ROC AUC, average precision (AUPRC) and Brier score per fold; calibration tables from out-of-fold predictions.
- **Reporting:** TRIPOD+AI.

## Why no PyTorch or TensorFlow yet

With about 100 expected events, deep networks are unlikely to beat penalized regression or tree
models, and they add a large software stack. The `mlp` model is the neural-network baseline. A
deep-learning framework (PyTorch, one only) is added if and when the simpler models are clearly
outperformed on held-out data.
