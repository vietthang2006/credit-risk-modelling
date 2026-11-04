from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def plot_cv_metric_comparison(
    rows: list[dict],
    model_name: str,
    output_dir: Path,
    best_trial_id: int | None = None,
) -> Path | None:
    """Plot Cross-Validation metric comparison across all Optuna / ParameterSampler trials."""
    if not rows:
        return None

    output_dir.mkdir(parents=True, exist_ok=True)
    trials = [r["trial"] for r in rows]
    mean_aucs = [r["mean_metrics"]["roc_auc"] for r in rows]
    fold_std = [
        float(np.std([f.get("roc_auc", f.get("auc", 0)) for f in r["folds"]]))
        if "folds" in r and r["folds"]
        else 0.0
        for r in rows
    ]

    mean_aucs_arr = np.array(mean_aucs)
    fold_std_arr = np.array(fold_std)

    plt.figure(figsize=(10, 6))
    plt.plot(trials, mean_aucs_arr, marker="o", color="royalblue", lw=2, label="Trial Mean ROC-AUC")
    plt.fill_between(
        trials,
        mean_aucs_arr - fold_std_arr,
        mean_aucs_arr + fold_std_arr,
        alpha=0.2,
        color="royalblue",
        label="Fold Std Dev",
    )

    if best_trial_id is not None and best_trial_id in trials:
        best_idx = trials.index(best_trial_id)
        best_auc = mean_aucs_arr[best_idx]
        plt.scatter(
            [best_trial_id],
            [best_auc],
            color="crimson",
            s=120,
            zorder=5,
            label=f"Best Trial #{best_trial_id} (AUC = {best_auc:.4f})",
        )
        plt.axhline(best_auc, color="crimson", linestyle="--", alpha=0.6, lw=1.2)

    plt.xlabel("Trial Number")
    plt.ylabel("Mean CV ROC-AUC")
    plt.title(f"Cross-Validation Hyperparameter Tuning Progression - {model_name.upper()}")
    plt.legend(loc="best")
    plt.grid(True, alpha=0.3)

    path = output_dir / f"{model_name}_cv_metrics_comparison.png"
    plt.savefig(path, bbox_inches="tight", dpi=300)
    plt.close()
    return path
