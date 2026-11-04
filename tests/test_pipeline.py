import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest

from srcs.pipelines.core.config_loader import load_yaml_config, save_json, save_yaml
from srcs.pipelines.core.model_factory import compute_space_size, sample_candidate_params
from srcs.pipelines.core.score_utils import predict_score
from srcs.pipelines.pipeline import PipelineRunner
from srcs.pipelines.plots.evaluation_plots import (
    plot_evaluation_suite,
)
from srcs.pipelines.reporting.report_builder import (
    aggregate_fold_metrics,
    build_cv_report,
    build_test_report,
    build_valid_report,
)


def test_config_loader(tmp_path: Path):
    test_yaml = tmp_path / "sub" / "test.yaml"
    data = {"model": "lgbm", "n_estimators": 100}
    save_yaml(test_yaml, data)
    assert test_yaml.exists()
    loaded = load_yaml_config(test_yaml)
    assert loaded == data

    test_json = tmp_path / "sub" / "test.json"
    save_json(test_json, data)
    assert test_json.exists()
    with open(test_json, "r", encoding="utf-8") as f:
        assert json.load(f) == data


def test_space_size():
    space = {"a": [1, 2, 3], "b": [10, 20]}
    assert compute_space_size(space) == 6


def test_sample_candidate_params():
    tuning_space = {"lgbm": {"learning_rate": [0.01, 0.05], "max_depth": [3, 5]}}
    candidates = sample_candidate_params(tuning_space, "lgbm", n_trials=2, random_state=42)
    assert len(candidates) == 2
    assert "learning_rate" in candidates[0]


def test_predict_score():
    class DummyModel:
        def predict_proba(self, X):
            return np.array([[0.8, 0.2], [0.3, 0.7]])

    df = pd.DataFrame({"col": [1, 2]})
    scores = predict_score(DummyModel(), df)
    np.testing.assert_array_equal(scores, np.array([0.2, 0.7]))


def test_report_builders():
    fold_reports = [
        {"roc_auc": 0.8, "f1": 0.6, "precision": 0.5, "recall": 0.7, "average_precision": 0.4, "ks": 0.3},
        {"roc_auc": 0.82, "f1": 0.64, "precision": 0.52, "recall": 0.72, "average_precision": 0.42, "ks": 0.32},
    ]
    aggregated = aggregate_fold_metrics(fold_reports)
    assert pytest.approx(aggregated["roc_auc"], 0.001) == 0.81

    cv_rep = build_cv_report("lgbm", {"n_estimators": 100}, aggregated, 42, 2)
    assert cv_rep["model_name"] == "lgbm"
    assert cv_rep["selection_metric"] == "roc_auc"

    val_rep = build_valid_report(
        "lgbm",
        {"n_estimators": 100},
        {"youden_j": 0.4},
        0.4,
        {"roc_auc": 0.8},
        {"brier_score": 0.1},
        {"psi": 0.02},
    )
    assert "discrimination" in val_rep
    assert val_rep["selected_threshold"] == 0.4


def test_plotting_suite(tmp_path: Path):
    y_true = np.array([0, 1, 0, 1, 0, 1, 0, 0, 1, 1])
    y_score = np.array([0.1, 0.9, 0.2, 0.8, 0.3, 0.7, 0.15, 0.4, 0.65, 0.85])
    plots_dir = tmp_path / "plots"

    paths = plot_evaluation_suite(y_true, y_score, "lgbm", plots_dir, split="valid", threshold=0.5)
    for key, p in paths.items():
        assert p.exists()


def test_pipeline_runner_init():
    runner = PipelineRunner(mode="valid", model_name="lr", n_trials=5, random_state=42)
    assert runner.model_name == "lr"
    assert runner.mode == "valid"
    assert runner.plots_dir.exists()


def test_load_best_params(tmp_path: Path):
    runner = PipelineRunner(mode="valid", model_name="lr", n_trials=5, random_state=42)
    runner.output_dir = tmp_path

    # Case 1: File not found
    with pytest.raises(FileNotFoundError):
        runner._load_best_params()

    # Case 2: File exists
    best_params_payload = {
        "model_name": "lgbm",
        "best_params": {"model__n_estimators": 100, "model__learning_rate": 0.05},
    }
    save_yaml(tmp_path / "best_params.yaml", best_params_payload)
    loaded = runner._load_best_params()
    assert runner.model_name == "lgbm"
    assert loaded == {"model__n_estimators": 100, "model__learning_rate": 0.05}


def test_run_valid_report_structure(tmp_path: Path):
    runner = PipelineRunner(mode="valid", model_name="lr", n_trials=5, random_state=42)
    runner.output_dir = tmp_path
    runner.report_dir = tmp_path / "reports"
    runner.plots_dir = runner.report_dir / "Images"

    best_params_payload = {
        "model_name": "lr",
        "best_params": {},
    }
    save_yaml(tmp_path / "best_params.yaml", best_params_payload)

    # Dummy dataset
    np.random.seed(42)
    X_train = pd.DataFrame({
        "num_1": np.random.randn(50),
        "cat_1": np.random.choice(["A", "B", "C"], size=50),
    })
    y_train = pd.Series(np.random.choice([0, 1], size=50, p=[0.8, 0.2]))

    X_valid = pd.DataFrame({
        "num_1": np.random.randn(20),
        "cat_1": np.random.choice(["A", "B", "C"], size=20),
    })
    y_valid = pd.Series(np.random.choice([0, 1], size=20, p=[0.8, 0.2]))

    report = runner.run_valid(X_train, X_valid, y_train, y_valid)

    # Check required keys
    expected_keys = [
        "model_name",
        "best_params",
        "thresholds",
        "selected_threshold",
        "discrimination",
        "calibration",
        "stability",
    ]
    for key in expected_keys:
        assert key in report

    assert (tmp_path / "thresholds.yaml").exists()
    assert (tmp_path / "reports" / "lr_valid_report.json").exists()
    assert (tmp_path / "lr_model.joblib").exists()
    assert (tmp_path / "reports" / "Images" / "lr_valid_roc_curve.png").exists()
    assert "cost_conservative" in report["thresholds"]
    assert "cost_balanced" in report["thresholds"]
    assert "cost_growth" in report["thresholds"]


def test_calibration_modes(tmp_path: Path):
    for calib_mode in ["sigmoid", "isotonic", True, False]:
        runner = PipelineRunner(mode="valid", model_name="lr", n_trials=5, random_state=42, calibration=calib_mode)
        runner.output_dir = tmp_path
        runner.report_dir = tmp_path / "reports"
        runner.plots_dir = runner.report_dir / "Images"

        save_yaml(tmp_path / "best_params.yaml", {"model_name": "lr", "best_params": {}})
        np.random.seed(42)
        X_train = pd.DataFrame({"num_1": np.random.randn(60), "cat_1": ["A"] * 30 + ["B"] * 30})
        y_train = pd.Series([0] * 50 + [1] * 10)
        X_valid = pd.DataFrame({"num_1": np.random.randn(20), "cat_1": ["A"] * 10 + ["B"] * 10})
        y_valid = pd.Series([0] * 16 + [1] * 4)

        report = runner.run_valid(X_train, X_valid, y_train, y_valid)
        assert "calibration" in report
        assert "brier_score" in report["calibration"]

