import numpy as np
import pandas as pd


def predict_score(model, X: pd.DataFrame) -> np.ndarray:
    """Predict risk probability/score from a fitted model or pipeline."""
    if hasattr(model, "predict_proba"):
        return model.predict_proba(X)[:, 1]
    return model.decision_function(X)
