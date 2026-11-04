from typing import Any
import numpy as np


def aggregate_fold_metrics(fold_reports: list[dict[str, Any]]) -> dict[str, float]:
    """Calculate mean metrics across cross-validation folds."""
    metrics_to_aggregate = ["roc_auc", "f1", "precision", "recall", "average_precision", "ks"]
    return {
        metric: float(np.mean([fold[metric] for fold in fold_reports]))
        for metric in metrics_to_aggregate
    }


def build_cv_report(
    model_name: str,
    best_params: dict[str, Any],
    best_mean_metrics: dict[str, float],
    random_state: int,
    n_splits: int,
) -> dict[str, Any]:
    """Construct the payload dictionary for the best cross-validation model result."""
    return {
        "model_name": model_name,
        "best_params": best_params,
        "best_cv_metrics": best_mean_metrics,
        "selection_metric": "roc_auc",
        "random_state": random_state,
        "n_splits": n_splits,
    }


def build_valid_report(
    model_name: str,
    best_params: dict[str, Any],
    thresholds: dict[str, float],
    selected_threshold: float,
    discrimination: dict[str, Any],
    calibration: dict[str, Any],
    stability: dict[str, Any],
) -> dict[str, Any]:
    """Construct the validation report dictionary."""
    return {
        "model_name": model_name,
        "best_params": best_params,
        "thresholds": thresholds,
        "selected_threshold": selected_threshold,
        "discrimination": discrimination,
        "calibration": calibration,
        "stability": stability,
    }


def build_test_report(
    model_name: str,
    best_params: dict[str, Any],
    selected_threshold: float,
    discrimination: dict[str, Any],
    calibration: dict[str, Any],
    stability: dict[str, Any],
) -> dict[str, Any]:
    """Construct the test evaluation report dictionary."""
    return {
        "model_name": model_name,
        "best_params": best_params,
        "selected_threshold": selected_threshold,
        "discrimination": discrimination,
        "calibration": calibration,
        "stability": stability,
    }
