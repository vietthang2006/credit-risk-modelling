from collections.abc import Callable
from pathlib import Path
from typing import Any
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score


def plot_learning_curve(
    model_builder_fn: Callable[[pd.DataFrame, dict[str, Any] | None], Any],
    predict_score_fn: Callable[[Any, pd.DataFrame], np.ndarray],
    folds: list[tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series]],
    best_params: dict[str, Any],
    model_name: str,
    output_path: Path,
) -> Path:
    """Compute and plot the learning curve across CV folds for the best model configuration."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    train_sizes = np.linspace(0.1, 1.0, 5)
    train_scores = np.zeros((len(train_sizes), len(folds)))
    val_scores = np.zeros((len(train_sizes), len(folds)))

    for fold_id, (X_train, y_train, X_valid, y_valid) in enumerate(folds):
        for size_id, fraction in enumerate(train_sizes):
            n_samples = max(1, int(len(X_train) * fraction))
            X_subset = X_train.iloc[:n_samples]
            y_subset = y_train.iloc[:n_samples]

            estimator = model_builder_fn(X_subset, best_params)
            estimator.fit(X_subset, y_subset)

            train_score = predict_score_fn(estimator, X_subset)
            val_score = predict_score_fn(estimator, X_valid)

            train_scores[size_id, fold_id] = roc_auc_score(y_subset, train_score)
            val_scores[size_id, fold_id] = roc_auc_score(y_valid, val_score)

    train_mean = train_scores.mean(axis=1)
    train_std = train_scores.std(axis=1)
    val_mean = val_scores.mean(axis=1)
    val_std = val_scores.std(axis=1)

    plt.figure(figsize=(10, 6))
    plt.plot(train_sizes, train_mean, "o-", label="Training ROC-AUC")
    plt.fill_between(train_sizes, train_mean - train_std, train_mean + train_std, alpha=0.15)
    plt.plot(train_sizes, val_mean, "o-", label="CV ROC-AUC")
    plt.fill_between(train_sizes, val_mean - val_std, val_mean + val_std, alpha=0.15)
    plt.title("Learning Curve")
    plt.xlabel("Training examples")
    plt.ylabel("ROC-AUC")
    plt.grid(True)
    plt.legend(loc="best")

    plt.savefig(output_path, bbox_inches="tight")
    plt.close()
    return output_path
