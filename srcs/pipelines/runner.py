import argparse
import json
import sys
from pathlib import Path
from typing import Any
from sklearn.base import BaseEstimator
import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml
from sklearn.model_selection import ParameterSampler, StratifiedKFold, learning_curve

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from srcs.data_preparation.category_encoding import CategoryEncoder
from srcs.evaluation import calibration_report, discrimination_report, find_thresholds, stability_report
from srcs.pipelines.data_pipeline import DataPipeline, RawDataBundle
from srcs.pipelines.model_pipeline import ModelPipeline

def load_yaml_config(file_path: Path) -> dict:
    with open(file_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def save_yaml(file_path: Path, data: dict) -> None:
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as file:
        yaml.safe_dump(data, file, sort_keys=False, allow_unicode=True)


def save_json(file_path: Path, data: dict) -> None:
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


class PipelineRunner:
    def __init__(self, mode: str, model_name: str = "lgbm", n_trials: int = 30, random_state: int = 42, n_splits: int = 5):

        self.mode = mode
        self.model_name = model_name
        self.n_trials = n_trials
        self.random_state = random_state
        self.n_splits = n_splits

        self.project_root = PROJECT_ROOT
        self.tuning_space_config = load_yaml_config(self.project_root / "config" / "model" / "tuning_space.yaml")
        self.path_config = load_yaml_config(self.project_root / "config" / "path.yaml")
        self.output_dir = self.project_root / "config" / "model"
        self.report_dir = self.project_root / "reports" / "model"

    def _data_dir(self) -> Path:
        return self.project_root / self.path_config.get("data_dir", "Home Credit Dataset")

    def _processed_path(self, split: str) -> Path:
        dirs = self.path_config["dirs"]
        filename = self.path_config["files"].get("main_table", "main_table.csv")
        return self._data_dir() / dirs[f"processed_{split}"] / filename

    def _raw_dir_for_split(self, split: str) -> Path:
        dirs = self.path_config["dirs"]
        if split == "raw":
            return self._data_dir() / dirs["raw"]
        if split == "train":
            return self._data_dir() / dirs.get("modelling_train", dirs["train"])
        if split == "valid":
            return self._data_dir() / dirs.get("modelling_test", dirs["test"])
        if split == "test":
            return self._data_dir() / dirs["test"]
        raise ValueError(f"Unknown split: {split}")

    def _resolve_table_path(self, directory: Path, file_key: str, split: str) -> Path:
        files = self.path_config["files"]
        filename = files[file_key]
        candidates = [directory / filename]

        if split == "train":
            candidates.append(directory / filename.replace(".csv", "_train.csv"))
            if file_key == "application":
                candidates.append(directory / "application_train.csv")
        elif split == "valid":
            candidates.append(directory / filename.replace(".csv", "_valid.csv"))
            if file_key == "application":
                candidates.append(directory / "application_train_valid.csv")
        elif split == "test":
            candidates.append(directory / filename.replace(".csv", "_test.csv"))
            if file_key == "application":
                candidates.append(directory / "application_train_test.csv")

        for path in candidates:
            if path.exists():
                return path

        raise FileNotFoundError(f"Could not find {file_key} for split '{split}' in {directory}")

    def _load_raw_bundle(self, split: str = "raw") -> RawDataBundle:
        directory = self._raw_dir_for_split(split)
        return RawDataBundle(
            application=pd.read_csv(self._resolve_table_path(directory, "application", split)),
            prev_application=pd.read_csv(
                self._resolve_table_path(directory, "previous_application", split)
            ),
            bureau=pd.read_csv(self._resolve_table_path(directory, "bureau", split)),
            bureau_balance=pd.read_csv(self._resolve_table_path(directory, "bureau_balance", split)),
            credit_card_balance=pd.read_csv(
                self._resolve_table_path(directory, "credit_card_balance", split)
            ),
            pos_cash_balance=pd.read_csv(self._resolve_table_path(directory, "pos_cash_balance", split)),
            instalments_payments=pd.read_csv(
                self._resolve_table_path(directory, "installments_payments", split)
            ),
        )

    def _dataset_from_raw(self, raw_data: RawDataBundle) -> tuple[pd.DataFrame, pd.Series, pd.DataFrame]:
        result = DataPipeline().run(raw_data)
        if not isinstance(result, tuple) or len(result) != 3:
            raise ValueError("DataPipeline output must contain X, y, and the full dataframe.")
        return result

    def _load_processed_dataset(self, split: str) -> tuple[pd.DataFrame, pd.Series, pd.DataFrame]:
        path = self._processed_path(split)
        if not path.exists():
            raise FileNotFoundError(f"Processed dataset not found: {path}")
        df = pd.read_csv(path)
        target_col = "TARGET"
        if target_col not in df.columns:
            raise ValueError(f"{path} does not contain '{target_col}'.")
        return df.drop(columns=[target_col]), df[target_col], df

    def _load_dataset(
        self,
        split: str,
        raw_data: RawDataBundle | None = None,
        prefer_processed: bool = True,
    ) -> tuple[pd.DataFrame, pd.Series, pd.DataFrame]:
        if raw_data is not None:
            return self._dataset_from_raw(raw_data)

        if prefer_processed:
            try:
                return self._load_processed_dataset(split)
            except FileNotFoundError:
                pass

        return self._dataset_from_raw(self._load_raw_bundle(split))

    def _build_preprocessors(self, X: pd.DataFrame) -> dict[str, BaseEstimator]:
        categorical_columns = X.select_dtypes(exclude=["number", "bool"]).columns.tolist()
        return {
            "woe": CategoryEncoder(categorical_columns, encoding_type="WOE"),
            "target_encoding": CategoryEncoder(categorical_columns, encoding_type="TE"),
        }

    def _build_model(self, X: pd.DataFrame, params: dict[str, Any] | None = None):
        config = {
            "model": {
                "name": self.model_name,
                "random_state": self.random_state,
                "n_jobs": -1,
            }
        }
        pipeline = ModelPipeline(config, self._build_preprocessors(X)).build()
        if params:
            pipeline.set_params(**params)
        return pipeline

    def _candidate_params(self) -> list[dict[str, Any]]:
        space = self.tuning_space_config.get(self.model_name)
        if not space:
            raise ValueError(
                f"No tuning space found for model '{self.model_name}'. "
                f"Available models: {list(self.tuning_space_config)}"
            )
        sampler = ParameterSampler(
            space,
            n_iter=min(self.n_trials, self._space_size(space)),
            random_state=self.random_state,
        )
        return list(sampler)

    @staticmethod
    def _space_size(space: dict[str, list]) -> int:
        size = 1
        for values in space.values():
            size *= len(values)
        return size

    @staticmethod
    def _predict_score(model, X: pd.DataFrame) -> np.ndarray:
        if hasattr(model, "predict_proba"):
            return model.predict_proba(X)[:, 1]
        return model.decision_function(X)

    def _plot_learning_curve(self, X: pd.DataFrame, y: pd.Series, best_params: dict[str, Any]) -> None:
        cv = StratifiedKFold(n_splits=self.n_splits, shuffle=True, random_state=self.random_state)
        estimator = self._build_model(X, best_params)
        train_sizes, train_scores, val_scores, _, _ = learning_curve(
            estimator=estimator,
            X=X,
            y=y,
            cv=cv,
            scoring="roc_auc",
            train_sizes=np.linspace(0.1, 1.0, 5),
            n_jobs=-1,
        )

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

        path = self.output_dir / f"{self.model_name}_learning_curve.png"
        path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(path, bbox_inches="tight")
        plt.close()

    def run_cv(self, raw_data: RawDataBundle | None = None) -> dict[str, Any]:
        X, y, _ = self._load_dataset("raw", raw_data=raw_data, prefer_processed=False)
        cv = StratifiedKFold(n_splits=self.n_splits, shuffle=True, random_state=self.random_state)

        rows = []
        for trial_id, params in enumerate(self._candidate_params(), start=1):
            fold_reports = []
            for fold_id, (train_idx, valid_idx) in enumerate(cv.split(X, y), start=1):
                X_train, X_valid = X.iloc[train_idx], X.iloc[valid_idx]
                y_train, y_valid = y.iloc[train_idx], y.iloc[valid_idx]
                model = self._build_model(X_train, params)
                model.fit(X_train, y_train)
                y_score = self._predict_score(model, X_valid)
                report = discrimination_report(y_valid, y_score)
                report["fold"] = fold_id
                fold_reports.append(report)

            mean_metrics = {
                metric: float(np.mean([fold[metric] for fold in fold_reports]))
                for metric in ["roc_auc", "f1", "precision", "recall", "average_precision", "ks"]
            }
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
        best_payload = {
            "model_name": self.model_name,
            "best_params": best["params"],
            "best_cv_metrics": best["mean_metrics"],
            "selection_metric": "roc_auc",
            "random_state": self.random_state,
            "n_splits": self.n_splits,
        }

        save_yaml(self.output_dir / "best_params.yaml", best_payload)
        save_json(self.report_dir / f"{self.model_name}_cv_report.json", {"trials": rows, "best": best_payload})
        self._plot_learning_curve(X, y, best["params"])
        return best_payload

    def _load_best_params(self) -> dict[str, Any]:
        path = self.output_dir / "best_params.yaml"
        if not path.exists():
            raise FileNotFoundError(f"Best params not found: {path}. Run mode=cv first.")
        payload = load_yaml_config(path)
        self.model_name = payload.get("model_name", self.model_name)
        return payload.get("best_params", payload)

    def run_valid(self, raw_train: RawDataBundle | None = None, raw_valid: RawDataBundle | None = None) -> dict:
        best_params = self._load_best_params()
        X_train, y_train, _ = self._load_dataset("train", raw_data=raw_train, prefer_processed=True)
        X_valid, y_valid, _ = self._load_dataset("valid", raw_data=raw_valid, prefer_processed=True)

        model = self._build_model(X_train, best_params)
        model.fit(X_train, y_train)
        train_score = self._predict_score(model, X_train)
        valid_score = self._predict_score(model, X_valid)
        thresholds = find_thresholds(y_valid, valid_score)
        selected_threshold = thresholds["best_f1"]

        report = {
            "model_name": self.model_name,
            "best_params": best_params,
            "thresholds": thresholds,
            "selected_threshold": selected_threshold,
            "discrimination": discrimination_report(y_valid, valid_score, selected_threshold),
            "calibration": calibration_report(y_valid, valid_score),
            "stability": stability_report(y_train, train_score, y_valid, valid_score),
        }

        save_yaml(self.output_dir / "thresholds.yaml", report["thresholds"] | {"selected": selected_threshold})
        save_json(self.report_dir / f"{self.model_name}_valid_report.json", report)
        joblib.dump(model, self.output_dir / f"{self.model_name}_model.joblib")
        return report

    def run_test(self, raw_train: RawDataBundle | None = None, raw_test: RawDataBundle | None = None) -> dict:
        best_params = self._load_best_params()
        threshold_path = self.output_dir / "thresholds.yaml"
        thresholds = load_yaml_config(threshold_path) if threshold_path.exists() else {"selected": 0.5}
        selected_threshold = float(thresholds.get("selected", 0.5))

        X_train, y_train, _ = self._load_dataset("train", raw_data=raw_train, prefer_processed=True)
        X_test, y_test, _ = self._load_dataset("test", raw_data=raw_test, prefer_processed=True)

        model_path = self.output_dir / f"{self.model_name}_model.joblib"
        if model_path.exists():
            model = joblib.load(model_path)
            train_score = self._predict_score(model, X_train)
        else:
            model = self._build_model(X_train, best_params)
            model.fit(X_train, y_train)
            train_score = self._predict_score(model, X_train)

        test_score = self._predict_score(model, X_test)
        report = {
            "model_name": self.model_name,
            "best_params": best_params,
            "selected_threshold": selected_threshold,
            "discrimination": discrimination_report(y_test, test_score, selected_threshold),
            "calibration": calibration_report(y_test, test_score),
            "stability": stability_report(y_train, train_score, y_test, test_score),
        }
        save_json(self.report_dir / f"{self.model_name}_test_report.json", report)
        return report

    def execute(self) -> dict[str, Any]:
        if self.mode == "cv":
            return self.run_cv()
        if self.mode == "valid":
            return self.run_valid()
        if self.mode == "test":
            return self.run_test()
        raise ValueError(f"Invalid mode: {self.mode}")
