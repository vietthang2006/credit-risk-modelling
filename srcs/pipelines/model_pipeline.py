import pandas as pd
import numpy as np

from typing import Any

from sklearn.pipeline import Pipeline
from sklearn.base import BaseEstimator

from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier

from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier

from srcs.data_preparation.feature_selection import ImportanceFeatureSelector

class ModelPipeline:
    def __init__(self, config: dict[str, Any], preprocessors: dict[str, BaseEstimator]):
        self.config = config
        self.preprocessors = preprocessors

    def build(self) -> Pipeline:
        """
        Build the configured model pipeline. 

        Returns: A configured scikit-learn Pipeline. 
        Raises: 
            ValueError: If the model name is unsupported.
        """
        model_name = self.config["model"]["name"]
        builders = {
            'lr': self._build_lr,
            'xgb': self._build_xgb,
            'lgbm': self._build_lgbm,
            'rf': self._build_rf
        }

        if model_name not in builders:
            raise ValueError(f"Unsupported model: {model_name}. " f"Supported models: {list(builders)}")

        return builders[model_name]()

    def _build_rf(self) -> Pipeline:
        """
        Pipeline for Random Forest Model
        """
        config = self.config["model"]
        return Pipeline(
            steps=[
                ("preprocessor", self.preprocessors["target_encoding"]),
                ("imputer", SimpleImputer(strategy="constant", fill_value=0)),
                ("selector", ImportanceFeatureSelector(top_k=config.get("top_k", 100))),
                ("model", RandomForestClassifier(
                    n_estimators=config.get("n_estimators", 500),
                    random_state=config.get("random_state", 42),
                    n_jobs=config.get("n_jobs", -1)
                )),
            ]
        )

    def _build_lr(self) -> Pipeline:
        """
        Pipeline for Logistic Regression with L2 penalty
        """
        config = self.config['model']
        return Pipeline(
            steps=[
                ('preprocessor', self.preprocessors['woe']),
                ('imputer', SimpleImputer(strategy='constant', fill_value=0)),
                ('selector', ImportanceFeatureSelector(top_k=config.get("top_k", 100))),
                ('scaler', StandardScaler()),
                ('model', LogisticRegression(
                    class_weight='balanced',
                    penalty=config.get("penalty", "l2"),
                    solver=config.get("solver", "lbfgs"),
                    max_iter=config.get("max_iter", 1000),
                    random_state=config.get("random_state", 42)
                )),
            ]
        )

    def _build_xgb(self) -> Pipeline:
        """
        Pipeline for XGBoost Model
        """
        config = self.config['model']
        return Pipeline(
            steps=[
                ('preprocessor', self.preprocessors['woe']),
                ('imputer', SimpleImputer(strategy="constant", fill_value=0)),
                ('selector', ImportanceFeatureSelector(top_k=config.get("top_k", 100))),
                ('model', XGBClassifier(
                    n_estimators=config.get("n_estimators", 500),
                    max_depth=config.get("max_depth", 6),
                    learning_rate=config.get("learning_rate", 0.05),
                    random_state=config.get("random_state", 42),
                    n_jobs=config.get("n_jobs", -1),
                    eval_metric=config.get("eval_metric", "logloss")
                ))
            ]
        )

    def _build_lgbm(self) -> Pipeline:
        """
        Pipeline for LightGBM Model
        """

        config = self.config['model']
        return Pipeline(
            steps=[
                ('preprocessor', self.preprocessors['woe']),
                ('imputer', SimpleImputer(strategy="constant", fill_value=0)),
                ('selector', ImportanceFeatureSelector(top_k=config.get("top_k", 100))),
                ('model', LGBMClassifier(
                    n_estimators=config.get("n_estimators", 500),
                    max_depth=config.get("max_depth", -1),
                    learning_rate=config.get('learning_rate', 0.05),
                    random_state=config.get("random_state", 42),
                    n_jobs=config.get("n_jobs", -1),
                    verbosity=config.get("verbosity", -1)
                ))
            ]
        )