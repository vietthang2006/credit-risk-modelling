from pathlib import Path
import sys
from typing import Any
import joblib
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator

PROJECT = Path(__file__).resolve().parents[2]
if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))

from srcs.evaluation import (
    calibration_report, 
    discrimination_report, 
    find_thresholds, 
    stability_report
)

from srcs.pipelines.core import (
    build_model,
    build_preprocessors,
    compute_space_size,
    load_yaml_config,
    predict_score,
    sample_candidate_params,
    save_json,
    save_yaml,
)
from srcs.pipelines.plots import (
    plot_calibration_curve,
    plot_cv_metric_comparison,
    plot_evaluation_suite,
    plot_ks_curve,
    plot_learning_curve,
    plot_pr_curve,
    plot_roc_curve,
    plot_score_distribution,
)
from srcs.pipelines.reporting import (
    aggregate_fold_metrics,
    build_cv_report,
    build_test_report,
    build_valid_report,
)


class PipelineRunner:
    def __init__(
        self,
        mode: str,
        model_name: str,
        n_trials: int = 30,
        random_state: int = 42,
        calibration: bool | str = False,
    ):
        self.mode = mode
        self.model_name = model_name
        self.random_state = random_state
        self.n_trials = n_trials
        self.calibration = calibration
        self.project_root = PROJECT
        self.tuning_space_config = load_yaml_config(
            self.project_root / "config" / "model" / "tuning_space.yaml"
        )
        self.output_dir = self.project_root / "config" / "model"
        self.report_dir = self.project_root / "reports" / "model"
        self.plots_dir = self.report_dir / "Images"
        self.plots_dir.mkdir(parents=True, exist_ok=True)


    def _build_preprocessors(self, X: pd.DataFrame) -> dict[str, BaseEstimator]:
        return build_preprocessors(X)

    def _build_model(self, X: pd.DataFrame, params: dict[str, Any] | None = None):
        return build_model(
            model_name=self.model_name,
            random_state=self.random_state,
            X=X,
            params=params,
            calibration=bool(self.calibration) if isinstance(self.calibration, str) else self.calibration,
        )

    def _candidate_params(self) -> list[dict[str, Any]]:
        return sample_candidate_params(
            tuning_space_config=self.tuning_space_config,
            model_name=self.model_name,
            n_trials=self.n_trials,
            random_state=self.random_state,
        )

    @staticmethod
    def _space_size(space: dict[str, list]) -> int:
        return compute_space_size(space)

    @staticmethod
    def _predict_score(model, X: pd.DataFrame) -> np.ndarray:
        return predict_score(model, X)

    def _plot_roc_curve(self, y_true: pd.Series | np.ndarray, y_score: np.ndarray, split: str = "valid") -> None:
        plot_roc_curve(y_true, y_score, self.model_name, self.plots_dir, split=split)

    def _plot_pr_curve(self, y_true: pd.Series | np.ndarray, y_score: np.ndarray, split: str = "valid") -> None:
        plot_pr_curve(y_true, y_score, self.model_name, self.plots_dir, split=split)

    def _plot_calibration_curve(self, y_true: pd.Series | np.ndarray, y_score: np.ndarray, split: str = "valid", n_bins: int = 10) -> None:
        plot_calibration_curve(y_true, y_score, self.model_name, self.plots_dir, split=split, n_bins=n_bins)

    def _plot_score_distribution(self, y_true: pd.Series | np.ndarray, y_score: np.ndarray, split: str = "valid", threshold: float | None = None) -> None:
        plot_score_distribution(y_true, y_score, self.model_name, self.plots_dir, split=split, threshold=threshold)

    def _plot_ks_curve(
        self, y_true: pd.Series | np.ndarray, y_score: np.ndarray, split: str = "valid"
    ) -> None:
        plot_ks_curve(y_true, y_score, self.model_name, self.plots_dir, split=split)

    def _plot_cv_metric_comparison(
        self, rows: list[dict], best_trial_id: int | None = None
    ) -> None:
        plot_cv_metric_comparison(rows, self.model_name, self.plots_dir, best_trial_id=best_trial_id)

    def _plot_evaluation_suite(
        self,
        y_true: pd.Series | np.ndarray,
        y_score: np.ndarray,
        split: str = "valid",
        threshold: float | None = None,
    ) -> None:
        plot_evaluation_suite(
            y_true, y_score, self.model_name, self.plots_dir, split=split, threshold=threshold
        )

    def _plot_learning_curve(self, folds: list[tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series]], best_params: dict[str, Any]) -> None:
        output_path = self.output_dir / f"{self.model_name}_learning_curve.png"
        plot_learning_curve(
            model_builder_fn=self._build_model,
            predict_score_fn=self._predict_score,
            folds=folds,
            best_params=best_params,
            model_name=self.model_name,
            output_path=output_path,
        )

    def run_cv(
        self, folds: list[tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series]]
    ) -> dict[str, Any]:
        """Function to run Cross-validation.

        Input:
            folds: (X_train, y_train, X_valid, y_valid)
                X_train and X_valid must be basically preprocessed (replace np.inf/-np.inf => 0 and drop 'TARGET')
        Output:
            best_payloads: A general report of model's performance
        """
        rows = []
        for trial_id, params in enumerate(self._candidate_params(), start=1):
            fold_reports = []

            for fold_id, (X_train, y_train, X_valid, y_valid) in enumerate(folds, start=1):
                model = self._build_model(X_train, params)
                model.fit(X_train, y_train)

                y_score = self._predict_score(model, X_valid)
                report = discrimination_report(y_valid, y_score)
                report["fold"] = fold_id
                fold_reports.append(report)

            mean_metrics = aggregate_fold_metrics(fold_reports)
            rows.append(
                {
                    "trial": trial_id,
                    "params": params,
                    "folds": fold_reports,
                    "mean_metrics": mean_metrics,
                }
            )
            print(f"Trial {trial_id}: ROC-AUC={mean_metrics['roc_auc']:.5f}, params={params}")

        best = max(rows, key=lambda row: row["mean_metrics"]["roc_auc"])
        best_payload = build_cv_report(
            model_name=self.model_name,
            best_params=best["params"],
            best_mean_metrics=best["mean_metrics"],
            random_state=self.random_state,
            n_splits=len(folds),
        )

        save_yaml(self.output_dir / "best_params.yaml", best_payload)
        save_json(
            self.report_dir / f"{self.model_name}_cv_report.json",
            {"trials": rows, "best": best_payload},
        )

        # Plot CV metrics progression across trials
        self._plot_cv_metric_comparison(rows=rows, best_trial_id=best.get("trial"))
        return best_payload

    def _load_best_params(self) -> dict[str, Any]:
        path = self.output_dir / "best_params.yaml"
        if not path.exists():
            raise FileNotFoundError(f"Best params not found: {path}. Run mode=cv first.")
        payload = load_yaml_config(path)
        self.model_name = payload.get("model_name", self.model_name)
        return payload.get("best_params", payload)

    def run_valid(self, X_train: pd.DataFrame, X_valid: pd.DataFrame, y_train: pd.Series, y_valid: pd.Series) -> dict[str, Any]:
        best_params = self._load_best_params()
        model = self._build_model(X_train, best_params)
        model.fit(X_train, y_train)
        train_score = self._predict_score(model, X_train)
        valid_score = self._predict_score(model, X_valid)
        thresholds = find_thresholds(y_valid, valid_score)
        selected_threshold = thresholds["youden_j"]

        report = build_valid_report(
            model_name=self.model_name,
            best_params=best_params,
            thresholds=thresholds,
            selected_threshold=selected_threshold,
            discrimination=discrimination_report(y_valid, valid_score, selected_threshold),
            calibration=calibration_report(y_valid, valid_score),
            stability=stability_report(y_train, train_score, y_valid, valid_score),
        )

        save_yaml(
            self.output_dir / "thresholds.yaml",
            report["thresholds"] | {"selected": selected_threshold},
        )
        save_json(self.report_dir / f"{self.model_name}_valid_report.json", report)
        joblib.dump(model, self.output_dir / f"{self.model_name}_model.joblib")

        # Plot evaluation suite for validation set
        self._plot_evaluation_suite(
            y_valid, valid_score, split="valid", threshold=selected_threshold
        )
        return report

    def run_test(self, X_train: pd.DataFrame, X_test: pd.DataFrame, y_train: pd.Series, y_test: pd.Series) -> dict[str, Any]:
        best_params = self._load_best_params()
        threshold_path = self.output_dir / "thresholds.yaml"
        thresholds = load_yaml_config(threshold_path) if threshold_path.exists() else {"selected": 0.5}
        selected_threshold = float(thresholds.get("selected", 0.5))

        model_path = self.output_dir / f"{self.model_name}_model.joblib"
        if model_path.exists():
            model = joblib.load(model_path)
            train_score = self._predict_score(model, X_train)
        else:
            model = self._build_model(X_train, best_params)
            model.fit(X_train, y_train)
            train_score = self._predict_score(model, X_train)

        test_score = self._predict_score(model, X_test)
        report = build_test_report(
            model_name=self.model_name,
            best_params=best_params,
            selected_threshold=selected_threshold,
            discrimination=discrimination_report(y_test, test_score, selected_threshold),
            calibration=calibration_report(y_test, test_score),
            stability=stability_report(y_train, train_score, y_test, test_score),
        )
        save_json(self.report_dir / f"{self.model_name}_test_report.json", report)

        # Plot evaluation suite for test set
        self._plot_evaluation_suite(
            y_test, test_score, split="test", threshold=selected_threshold
        )
        return report