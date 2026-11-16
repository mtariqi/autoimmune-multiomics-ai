"""Machine learning: leakage-safe splits, model registry, nested CV and explanations."""

from .evaluate import calibration_table, nested_cv, summarize_metrics
from .explain import feature_importance, importance_stability
from .models import available_models, make_model
from .splits import participant_folds

__all__ = [
    "available_models",
    "calibration_table",
    "feature_importance",
    "importance_stability",
    "make_model",
    "nested_cv",
    "participant_folds",
    "summarize_metrics",
]
