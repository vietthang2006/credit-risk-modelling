from __future__ import annotations

import numpy as np
import pandas as pd


def _psi(expected, actual, bins: int = 10) -> float:
    expected = pd.Series(expected).astype(float)
    actual = pd.Series(actual).astype(float)
    edges = np.unique(np.quantile(expected, np.linspace(0, 1, bins + 1)))

    if len(edges) < 3:
        edges = np.linspace(min(expected.min(), actual.min()), max(expected.max(), actual.max()), bins + 1)

    edge_list = edges.tolist()
    expected_counts = pd.cut(expected, bins=edge_list, include_lowest=True).value_counts(sort=False)
    actual_counts = pd.cut(actual, bins=edge_list, include_lowest=True).value_counts(sort=False)
    expected_pct = (expected_counts / len(expected)).replace(0, 1e-6)
    actual_pct = (actual_counts / len(actual)).replace(0, 1e-6)

    return float(((actual_pct - expected_pct) * np.log(actual_pct / expected_pct)).sum())


def _score_summary(y_true, y_score) -> dict:
    y_true = pd.Series(y_true).astype(int)
    y_score = pd.Series(y_score).astype(float)

    return {
        "rows": int(len(y_score)),
        "target_rate": float(y_true.mean()),
        "score_mean": float(y_score.mean()),
        "score_std": float(y_score.std()),
        "score_min": float(y_score.min()),
        "score_p25": float(y_score.quantile(0.25)),
        "score_p50": float(y_score.quantile(0.50)),
        "score_p75": float(y_score.quantile(0.75)),
        "score_max": float(y_score.max()),
    }


def stability_report(reference_y, reference_score, current_y, current_score, bins: int = 10) -> dict:
    return {
        "score_psi": _psi(reference_score, current_score, bins=bins),
        "target_rate_delta": float(pd.Series(current_y).mean() - pd.Series(reference_y).mean()),
        "reference": _score_summary(reference_y, reference_score),
        "current": _score_summary(current_y, current_score),
    }
