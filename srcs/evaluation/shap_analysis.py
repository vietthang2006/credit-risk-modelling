from __future__ import annotations

import json
from pathlib import Path
from typing import Any
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap


def generate_lgbm_shap_analysis(
    lgbm_pipeline_or_calib: Any,
    X_raw: pd.DataFrame,
    output_dir: Path,
    n_sample: int = 3000,
    max_display: int = 20,
    random_state: int = 42,
) -> dict[str, Any]:
    """
    Compute SHAP values for LightGBM and generate:
      1. SHAP Summary Beeswarm Plot (directional impact on default log-odds)
      2. SHAP Bar Feature Importance Plot (mean absolute SHAP)
      3. Top Risk Drivers summary table
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    images_dir = output_dir / "Images"
    images_dir.mkdir(parents=True, exist_ok=True)

    # 1. Unwrap CalibratedClassifierCV if needed
    if hasattr(lgbm_pipeline_or_calib, "calibrated_classifiers_"):
        pipe = lgbm_pipeline_or_calib.calibrated_classifiers_[0].estimator
    else:
        pipe = lgbm_pipeline_or_calib

    preprocessor = pipe.named_steps["preprocessor"]
    imputer = pipe.named_steps["imputer"]
    selector = pipe.named_steps["selector"]
    lgbm_model = pipe.named_steps["model"]

    # 2. Subsample for fast, stable SHAP computation
    if len(X_raw) > n_sample:
        X_sub = X_raw.sample(n=n_sample, random_state=random_state).copy()
    else:
        X_sub = X_raw.copy()

    # Drop target column if present
    if "TARGET" in X_sub.columns:
        X_sub = X_sub.drop(columns=["TARGET"])

    # Align columns with model fit features
    if hasattr(imputer, "feature_names_in_"):
        expected_cols = [c for c in imputer.feature_names_in_ if c in X_sub.columns]
        X_sub = X_sub[expected_cols]

    # 3. Transform through pipeline steps up to model
    X_prep = preprocessor.transform(X_sub)
    X_imp = imputer.transform(X_prep)
    X_sel = selector.transform(X_imp)

    # 4. Resolve feature names
    if hasattr(imputer, "feature_names_in_") and hasattr(selector, "selected_indices_"):
        feature_names = [str(col) for col in imputer.feature_names_in_[selector.selected_indices_]]
    elif hasattr(selector, "selected_features_") and selector.selected_features_ is not None:
        feature_names = selector.selected_features_
    else:
        feature_names = [f"feature_{i}" for i in range(X_sel.shape[1])]

    X_df = pd.DataFrame(X_sel, columns=feature_names)

    # 5. TreeExplainer calculation
    explainer = shap.TreeExplainer(lgbm_model)
    raw_shap_values = explainer.shap_values(X_df)

    # For binary classification, shap_values can be a list of [neg_class, pos_class] or single matrix
    if isinstance(raw_shap_values, list) and len(raw_shap_values) == 2:
        shap_pos = raw_shap_values[1]
    elif isinstance(raw_shap_values, np.ndarray) and raw_shap_values.ndim == 3:
        shap_pos = raw_shap_values[:, :, 1]
    else:
        shap_pos = raw_shap_values

    # 6. Generate Beeswarm / Summary Plot
    summary_plot_path = images_dir / "lgbm_shap_summary_plot.png"
    plt.figure(figsize=(10, 8))
    shap.summary_plot(
        shap_pos,
        X_df,
        max_display=max_display,
        show=False,
        plot_type="dot",
    )
    plt.title(f"LightGBM SHAP Summary (Top {max_display} Risk Drivers)", fontsize=13, pad=15)
    plt.tight_layout()
    plt.savefig(summary_plot_path, bbox_inches="tight", dpi=300)
    plt.close()

    # 7. Generate Bar Feature Importance Plot
    bar_plot_path = images_dir / "lgbm_shap_bar_importance.png"
    plt.figure(figsize=(10, 8))
    shap.summary_plot(
        shap_pos,
        X_df,
        max_display=max_display,
        plot_type="bar",
        show=False,
    )
    plt.title(f"LightGBM Global Feature Importance (Mean |SHAP|)", fontsize=13, pad=15)
    plt.tight_layout()
    plt.savefig(bar_plot_path, bbox_inches="tight", dpi=300)
    plt.close()

    # 8. Create Top Risk Drivers Table
    mean_abs_shap = np.mean(np.abs(shap_pos), axis=0)
    ranking_df = pd.DataFrame({
        "Feature": feature_names,
        "Mean_Abs_SHAP": mean_abs_shap,
    }).sort_values(by="Mean_Abs_SHAP", ascending=False).reset_index(drop=True)

    ranking_df["Rank"] = range(1, len(ranking_df) + 1)
    ranking_top = ranking_df.head(max_display).copy()

    # Determine risk direction from correlation between feature value and SHAP value
    directions = []
    for feat in ranking_top["Feature"]:
        col_vals = X_df[feat].values
        feat_shap = shap_pos[:, X_df.columns.get_loc(feat)]
        corr = np.corrcoef(col_vals, feat_shap)[0, 1]
        if np.isnan(corr) or abs(corr) < 0.05:
            directions.append("Non-linear / Complex")
        elif corr > 0:
            directions.append("Higher value increases Default Risk (+)")
        else:
            directions.append("Higher value decreases Default Risk (-)")

    ranking_top["Business_Impact"] = directions
    ranking_top["Mean_Abs_SHAP"] = ranking_top["Mean_Abs_SHAP"].round(4)

    csv_path = output_dir / "lgbm_top_risk_drivers.csv"
    ranking_top.to_csv(csv_path, index=False)

    return {
        "summary_plot": summary_plot_path,
        "bar_plot": bar_plot_path,
        "risk_drivers_table": ranking_top,
        "csv_path": csv_path,
    }
