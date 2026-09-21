import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from lightgbm import LGBMClassifier


class ImportanceFeatureSelector(BaseEstimator, TransformerMixin):
    """
    Feature selector based on LightGBM feature importances.
    Suitable for use in a scikit-learn Pipeline.
    """

    def __init__(self, top_k=None, threshold=0.0):
        self.top_k = top_k
        self.threshold = threshold
        self.model = None
        self.selected_indices_ = None
        self.selected_features_ = None

    def fit(self, X, y=None):
        if y is None:
            raise ValueError("y must be provided to compute feature importances.")

        # Initialize the LightGBM model
        self.model = LGBMClassifier(n_estimators=200, random_state=42, n_jobs=-1, verbose=-1)

        # Fit the model to determine feature importances
        self.model.fit(X, y)
        importances = self.model.feature_importances_

        # Select features based on top_k or threshold
        if self.top_k is not None:
            k = min(self.top_k, len(importances))
            top_k_indices = np.argsort(importances)[-k:]
            self.selected_indices_ = np.sort(top_k_indices)
        else:
            self.selected_indices_ = np.where(importances > self.threshold)[0]

            # Fallback if no features selected
            if len(self.selected_indices_) == 0:
                self.selected_indices_ = np.argsort(importances)[-1:]

        # Store selected feature names if input is a DataFrame
        if isinstance(X, pd.DataFrame):
            self.selected_features_ = X.columns[self.selected_indices_].tolist()
        else:
            self.selected_features_ = [f"feature_{i}" for i in self.selected_indices_]

        return self

    def transform(self, X, y=None):
        if self.selected_indices_ is None:
            raise ValueError("The selector has not been fitted yet.")

        # SimpleImputer (upstream in Pipeline) converts DataFrame → numpy array,
        # so X may arrive as either type. Use numpy-style slicing for both.
        if isinstance(X, pd.DataFrame):
            return X.iloc[:, self.selected_indices_].reset_index(drop=True)

        return X[:, self.selected_indices_]

    def get_feature_names_out(self, input_features=None):
        return np.array(self.selected_features_)