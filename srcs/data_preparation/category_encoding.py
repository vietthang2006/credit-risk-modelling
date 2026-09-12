import numpy as np
import pandas as pd

from sklearn.base import BaseEstimator, TransformerMixin


class CategoryEncoder(BaseEstimator, TransformerMixin):
    """
    Categorical Encoder for WoE and Target Encoding.
    Only columns specified in categorical_columns are encoded.
    WoE: Suitable for Logistic Regression / Scorecard models.
    Target Encoding:
        Suitable for tree-based models such as
        Random Forest / XGBoost / LightGBM.
    """

    def __init__(self, categorical_columns: list, encoding_type: str = "WOE", alpha: float = 0.5):
        self.categorical_columns = categorical_columns
        self.encoding_type = encoding_type
        self.alpha = alpha

    def fit(self, X, y):
        X = self._validate_X(X)
        y = pd.Series(y, index=X.index, name="TARGET")

        if self.encoding_type not in ["WOE", "TE"]:
            raise ValueError("encoding_type must be either 'WOE' or 'TE'.")

        if y.isna().any():
            raise ValueError("y contains missing values.")

        if not set(y.unique()).issubset({0, 1}):
            raise ValueError("y must contain only 0 and 1.")

        missing_columns = [column for column in self.categorical_columns if column not in X.columns]

        if missing_columns:
            raise ValueError(f"Columns not found in X: {missing_columns}")

        self.mappings_ = {}

        if self.encoding_type == "WOE":
            self._fit_woe(X, y)

        elif self.encoding_type == "TE":
            self._fit_te(X, y)

        return self

    def _fit_woe(self, X, y):
        self.global_good_ = (y == 0).sum() + self.alpha
        self.global_bad_ = (y == 1).sum() + self.alpha

        for column in self.categorical_columns:
            stats = (
                pd.DataFrame({"feature": X[column], "target": y})
                .assign(feature=lambda df: df["feature"].astype(object).where(df["feature"].notna(), "__MISSING__"))
                .groupby("feature")["target"]
                .agg(total="count", bad="sum")
            )

            stats["good"] = stats["total"] - stats["bad"]
            stats["good"] += self.alpha
            stats["bad"] += self.alpha
            stats["dist_good"] = stats["good"] / stats["good"].sum()
            stats["dist_bad"] = stats["bad"] / stats["bad"].sum()
            stats["woe"] = np.log(stats["dist_good"] / stats["dist_bad"])

            self.mappings_[column] = stats["woe"].to_dict()

    def _fit_te(self, X, y):
        self.global_mean_ = y.mean()

        for column in self.categorical_columns:
            data = pd.DataFrame({"feature": X[column], "target": y})
            data["feature"] = data["feature"].astype(object).where(data["feature"].notna(), "__MISSING__" )
            stats = data.groupby("feature")["target"].agg(count="count", mean="mean")
            stats["te"] = (stats["count"] * stats["mean"] + self.alpha * self.global_mean_) / (stats["count"] + self.alpha)
            self.mappings_[column] = stats["te"].to_dict()

    def transform(self, X):
        X = self._validate_X(X)
        X_encoded = X.copy()

        for column in self.categorical_columns:
            values = X[column].astype(object).where(X[column].notna(), "__MISSING__")

            if self.encoding_type == "WOE":
                global_value = np.log(self.global_good_ / self.global_bad_)

            else:
                global_value = self.global_mean_

            X_encoded[column] = values.map(self.mappings_[column]).fillna(global_value)

        return X_encoded

    @staticmethod
    def _validate_X(X):
        if not isinstance(X, pd.DataFrame):
            raise TypeError("X must be a pandas DataFrame.")

        return X