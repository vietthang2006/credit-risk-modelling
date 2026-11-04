from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.calibration import calibration_curve
from sklearn.metrics import (
    auc,
    average_precision_score,
    precision_recall_curve,
    roc_curve,
)


def plot_roc_curve(
    y_true: pd.Series | np.ndarray,
    y_score: np.ndarray,
    model_name: str,
    output_dir: Path,
    split: str = "valid",
) -> Path:
    """Plot Receiver Operating Characteristic (ROC) curve and save to disk."""
    output_dir.mkdir(parents=True, exist_ok=True)
    y_true_arr = np.asarray(y_true).astype(int)
    fpr, tpr, _ = roc_curve(y_true_arr, y_score)
    roc_auc = auc(fpr, tpr)

    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, color="royalblue", lw=2, label=f"ROC Curve (AUC = {roc_auc:.4f})")
    plt.plot([0, 1], [0, 1], color="gray", linestyle="--", lw=1.5, label="Random (AUC = 0.5000)")
    plt.xlabel("False Positive Rate (1 - Specificity)")
    plt.ylabel("True Positive Rate (Sensitivity / Recall)")
    plt.title(f"ROC Curve - {model_name.upper()} ({split.capitalize()})")
    plt.legend(loc="lower right")
    plt.grid(True, alpha=0.3)

    path = output_dir / f"{model_name}_{split}_roc_curve.png"
    plt.savefig(path, bbox_inches="tight", dpi=300)
    plt.close()
    return path


def plot_pr_curve(
    y_true: pd.Series | np.ndarray,
    y_score: np.ndarray,
    model_name: str,
    output_dir: Path,
    split: str = "valid",
) -> Path:
    """Plot Precision-Recall (PR) curve and save to disk."""
    output_dir.mkdir(parents=True, exist_ok=True)
    y_true_arr = np.asarray(y_true).astype(int)
    precision, recall, _ = precision_recall_curve(y_true_arr, y_score)
    ap = average_precision_score(y_true_arr, y_score)
    baseline = float(np.mean(y_true_arr))

    plt.figure(figsize=(8, 6))
    plt.plot(recall, precision, color="darkorange", lw=2, label=f"PR Curve (AP = {ap:.4f})")
    plt.plot(
        [0, 1],
        [baseline, baseline],
        color="gray",
        linestyle="--",
        lw=1.5,
        label=f"Baseline (Prevalence = {baseline:.4f})",
    )
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.title(f"Precision-Recall Curve - {model_name.upper()} ({split.capitalize()})")
    plt.legend(loc="upper right")
    plt.grid(True, alpha=0.3)

    path = output_dir / f"{model_name}_{split}_pr_curve.png"
    plt.savefig(path, bbox_inches="tight", dpi=300)
    plt.close()
    return path


def plot_calibration_curve(
    y_true: pd.Series | np.ndarray,
    y_score: np.ndarray,
    model_name: str,
    output_dir: Path,
    split: str = "valid",
    n_bins: int = 10,
) -> Path:
    """Plot Calibration curve (Reliability Diagram) with prediction histogram and save to disk."""
    output_dir.mkdir(parents=True, exist_ok=True)
    y_true_arr = np.asarray(y_true).astype(int)
    prob_true, prob_pred = calibration_curve(y_true_arr, y_score, n_bins=n_bins, strategy="uniform")
    brier = float(np.mean((y_score - y_true_arr) ** 2))

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 8), gridspec_kw={"height_ratios": [3, 1]}, sharex=True)

    # Reliability curve
    ax1.plot(
        prob_pred,
        prob_true,
        marker="o",
        color="forestgreen",
        lw=2,
        label=f"{model_name.upper()} (Brier = {brier:.4f})",
    )
    ax1.plot([0, 1], [0, 1], linestyle="--", color="gray", lw=1.5, label="Perfectly Calibrated")
    ax1.set_ylabel("Fraction of Positives (Actual Risk)")
    ax1.set_title(f"Calibration Curve - {model_name.upper()} ({split.capitalize()})")
    ax1.legend(loc="upper left")
    ax1.grid(True, alpha=0.3)

    # Prediction probability distribution
    ax2.hist(y_score, bins=n_bins, range=(0, 1), color="forestgreen", edgecolor="black", alpha=0.6)
    ax2.set_xlabel("Mean Predicted Probability")
    ax2.set_ylabel("Count")
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    path = output_dir / f"{model_name}_{split}_calibration_curve.png"
    plt.savefig(path, bbox_inches="tight", dpi=300)
    plt.close()
    return path


def plot_score_distribution(
    y_true: pd.Series | np.ndarray,
    y_score: np.ndarray,
    model_name: str,
    output_dir: Path,
    split: str = "valid",
    threshold: float | None = None,
) -> Path:
    """Plot predicted score distribution for default vs non-default classes and save to disk."""
    output_dir.mkdir(parents=True, exist_ok=True)
    y_true_arr = np.asarray(y_true).astype(int)
    y_score_arr = np.asarray(y_score)

    scores_0 = y_score_arr[y_true_arr == 0]
    scores_1 = y_score_arr[y_true_arr == 1]
    bins = list(np.linspace(0, 1, 50))

    plt.figure(figsize=(8, 6))
    plt.hist(
        scores_0,
        bins=bins,
        density=True,
        alpha=0.55,
        color="steelblue",
        label=f"Non-Default (y=0, n={len(scores_0):,})",
    )
    plt.hist(
        scores_1,
        bins=bins,
        density=True,
        alpha=0.55,
        color="crimson",
        label=f"Default (y=1, n={len(scores_1):,})",
    )

    if threshold is not None:
        plt.axvline(threshold, color="black", linestyle="--", lw=2, label=f"Threshold = {threshold:.4f}")

    plt.xlabel("Predicted Default Probability")
    plt.ylabel("Density")
    plt.title(f"Predicted Score Distribution - {model_name.upper()} ({split.capitalize()})")
    plt.legend(loc="upper right")
    plt.grid(True, alpha=0.3)

    path = output_dir / f"{model_name}_{split}_score_distribution.png"
    plt.savefig(path, bbox_inches="tight", dpi=300)
    plt.close()
    return path


def plot_ks_curve(
    y_true: pd.Series | np.ndarray,
    y_score: np.ndarray,
    model_name: str,
    output_dir: Path,
    split: str = "valid",
) -> Path:
    """Plot Kolmogorov-Smirnov (KS) curve and save to disk."""
    output_dir.mkdir(parents=True, exist_ok=True)
    y_true_arr = np.asarray(y_true).astype(int)
    y_score_arr = np.asarray(y_score)

    fpr, tpr, thresholds = roc_curve(y_true_arr, y_score_arr)
    clean_thresholds = np.clip(thresholds, 0.0, 1.0)
    ks_diff = tpr - fpr
    ks_idx = int(np.argmax(ks_diff))
    ks_stat = float(ks_diff[ks_idx])
    ks_threshold = float(clean_thresholds[ks_idx])

    plt.figure(figsize=(8, 6))
    plt.plot(clean_thresholds, tpr, color="crimson", lw=2, label="Cumulative Defaults (TPR / Sensitivity)")
    plt.plot(clean_thresholds, fpr, color="steelblue", lw=2, label="Cumulative Non-Defaults (FPR / 1-Specificity)")
    plt.plot(clean_thresholds, ks_diff, color="forestgreen", linestyle=":", lw=2, label="K-S Distance")

    plt.vlines(
        x=ks_threshold,
        ymin=fpr[ks_idx],
        ymax=tpr[ks_idx],
        color="black",
        linestyle="--",
        lw=2,
        label=f"Max KS = {ks_stat*100:.2f}% @ Cutoff = {ks_threshold:.4f}",
    )
    plt.xlabel("Score / Probability Cutoff")
    plt.ylabel("Cumulative Proportion")
    plt.title(f"Kolmogorov-Smirnov (K-S) Curve - {model_name.upper()} ({split.capitalize()})")
    plt.legend(loc="upper right")
    plt.grid(True, alpha=0.3)

    path = output_dir / f"{model_name}_{split}_ks_curve.png"
    plt.savefig(path, bbox_inches="tight", dpi=300)
    plt.close()
    return path


def plot_evaluation_suite(
    y_true: pd.Series | np.ndarray,
    y_score: np.ndarray,
    model_name: str,
    output_dir: Path,
    split: str = "valid",
    threshold: float | None = None,
) -> dict[str, Path]:
    """Generate and save all standard credit risk evaluation plots."""
    return {
        "roc_curve": plot_roc_curve(y_true, y_score, model_name, output_dir, split=split),
        "pr_curve": plot_pr_curve(y_true, y_score, model_name, output_dir, split=split),
        "calibration_curve": plot_calibration_curve(y_true, y_score, model_name, output_dir, split=split),
        "score_distribution": plot_score_distribution(
            y_true, y_score, model_name, output_dir, split=split, threshold=threshold
        ),
        "ks_curve": plot_ks_curve(y_true, y_score, model_name, output_dir, split=split),
    }
