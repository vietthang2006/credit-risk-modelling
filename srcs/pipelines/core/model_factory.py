from typing import Any
import pandas as pd
from sklearn.base import BaseEstimator
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import ParameterSampler

from srcs.data_preparation.category_encoding import CategoryEncoder
from srcs.pipelines.model_pipeline import ModelPipeline


def build_preprocessors(X: pd.DataFrame) -> dict[str, BaseEstimator]:
    """Identify categorical columns and build WoE & Target Encoding preprocessors."""
    category_cols = X.select_dtypes(exclude=["number", "bool"]).columns.tolist()
    return {
        "woe": CategoryEncoder(categorical_columns=category_cols, encoding_type="WOE"),
        "target_encoding": CategoryEncoder(categorical_columns=category_cols, encoding_type="TE"),
    }


def build_model(
    model_name: str,
    random_state: int,
    X: pd.DataFrame,
    params: dict[str, Any] | None = None,
    calibration: bool = False,
) -> Any:
    """Build and configure a model pipeline with optional hyperparameters and calibration."""
    config = {
        "model": {
            "name": model_name,
            "random_state": random_state,
        }
    }

    pipeline = ModelPipeline(config, build_preprocessors(X)).build()
    if params:
        pipeline.set_params(**params)

    if calibration:
        method = "sigmoid" if isinstance(calibration, str) and calibration.lower() in ["sigmoid", "platt"] else "isotonic"
        pipeline = CalibratedClassifierCV(
            estimator=pipeline,
            method=method,
            cv=3,
        )

    return pipeline


def compute_space_size(space: dict[str, list]) -> int:
    """Calculate the total number of combinations in a discrete parameter grid."""
    size = 1
    for values in space.values():
        size *= len(values)
    return size


def sample_candidate_params(
    tuning_space_config: dict[str, Any],
    model_name: str,
    n_trials: int,
    random_state: int,
) -> list[dict[str, Any]]:
    """Sample hyperparameter candidates for a model from the tuning space configuration."""
    space = tuning_space_config.get(model_name)
    if not space:
        raise ValueError(
            f"No tuning space found for model '{model_name}'. "
            f"Available models: {list(tuning_space_config)}"
        )
    sampler = ParameterSampler(
        space,
        n_iter=min(n_trials, compute_space_size(space)),
        random_state=random_state,
    )
    return list(sampler)
