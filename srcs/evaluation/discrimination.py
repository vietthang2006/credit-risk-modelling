from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)


def _find_cost_optimal_threshold(
    y_true: pd.Series, y_score: pd.Series, cost_fn: float = 5.0, cost_fp: float = 1.0, grid_size: int = 100
) -> float:
    """Find threshold that minimizes total business expected cost: Cost = Cost_FN * FN + Cost_FP * FP."""
    grid = np.linspace(0.01, 0.99, grid_size)
    costs = []
    for threshold in grid:
        y_pred = (y_score >= threshold).astype(int)
        fn = int(np.sum((y_true == 1) & (y_pred == 0)))
        fp = int(np.sum((y_true == 0) & (y_pred == 1)))
        total_cost = cost_fn * fn + cost_fp * fp
        costs.append(total_cost)
    return float(grid[int(np.argmin(costs))])


def find_thresholds(y_true, y_score) -> dict[str, float]:
    y_true = pd.Series(y_true).astype(int)
    y_score = pd.Series(y_score, index=y_true.index).astype(float)

    grid = np.linspace(0.01, 0.99, 99)
    f1_values = np.array([f1_score(y_true, y_score >= threshold, zero_division=0) for threshold in grid])
    best_f1_threshold = float(grid[int(np.argmax(f1_values))])

    fpr, tpr, thresholds = roc_curve(y_true, y_score)
    youden_index = int(np.argmax(tpr - fpr))
    youden_threshold = float(thresholds[youden_index])

    # Cost-based thresholds for 3 business credit risk strategies:
    # 1. Conservative (Giảm nợ xấu tối đa): C(FN) / C(FP) = 10:1
    cost_conservative = _find_cost_optimal_threshold(y_true, y_score, cost_fn=10.0, cost_fp=1.0)
    # 2. Balanced (Cân bằng rủi ro và lợi nhuận): C(FN) / C(FP) = 5:1
    cost_balanced = _find_cost_optimal_threshold(y_true, y_score, cost_fn=5.0, cost_fp=1.0)
    # 3. Growth (Mở rộng thị phần & Doanh thu): C(FN) / C(FP) = 2:1
    cost_growth = _find_cost_optimal_threshold(y_true, y_score, cost_fn=2.0, cost_fp=1.0)

    return {
        "default_0_50": 0.5,
        "best_f1": best_f1_threshold,
        "youden_j": youden_threshold,
        "cost_conservative": cost_conservative,
        "cost_balanced": cost_balanced,
        "cost_growth": cost_growth,
    }


def _ks_statistic(y_true, y_score) -> float:
    fpr, tpr, _ = roc_curve(y_true, y_score)
    return float(np.max(tpr - fpr))


def discrimination_report(y_true, y_score, threshold: float = 0.5) -> dict:
    y_true = pd.Series(y_true).astype(int)
    y_score = pd.Series(y_score, index=y_true.index).astype(float)
    y_pred = (y_score >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    auc = roc_auc_score(y_true, y_score)

    return {
        "threshold": float(threshold),
        "roc_auc": float(auc),
        "auc": float(auc),
        "roc-auc": float(auc),
        "average_precision": float(average_precision_score(y_true, y_score)),
        "gini": float(2 * auc - 1),
        "ks": _ks_statistic(y_true, y_score),
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "confusion_matrix": {
            "tn": int(tn),
            "fp": int(fp),
            "fn": int(fn),
            "tp": int(tp),
        },
    }
