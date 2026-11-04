from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.calibration import calibration_curve
from sklearn.metrics import brier_score_loss, log_loss


def _expected_calibration_error(y_true, y_score, n_bins: int) -> float:
    data = pd.DataFrame({"y": y_true, "score": y_score})
    data["bin"] = pd.cut(data["score"], bins=list(np.linspace(0, 1, n_bins + 1)), include_lowest=True)

    ece = 0.0
    for _, group in data.groupby("bin", observed=False):
        if group.empty:
            continue
        weight = len(group) / len(data)
        ece += weight * abs(group["y"].mean() - group["score"].mean())

    return float(ece)


def calibration_report(y_true, y_score, n_bins: int = 10) -> dict:
    y_true = pd.Series(y_true).astype(int)
    y_score = pd.Series(y_score, index=y_true.index).clip(1e-15, 1 - 1e-15).astype(float)
    prob_true, prob_pred = calibration_curve(y_true, y_score, n_bins=n_bins, strategy="quantile")

    return {
        "brier_score": float(brier_score_loss(y_true, y_score)),
        "log_loss": float(log_loss(y_true, y_score)),
        "expected_calibration_error": _expected_calibration_error(y_true, y_score, n_bins),
        "curve": [
            {"predicted": float(predicted), "observed": float(observed)}
            for predicted, observed in zip(prob_pred, prob_true)
        ],
    }
