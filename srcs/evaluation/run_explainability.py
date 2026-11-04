from pathlib import Path
import sys
import joblib
import pandas as pd
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from srcs.evaluation.scorecard import ScorecardScaler
from srcs.evaluation.shap_analysis import generate_lgbm_shap_analysis
from srcs.pipelines.core.config_loader import load_yaml_config


def df_to_markdown(df: pd.DataFrame) -> str:
    headers = [str(c) for c in df.columns]
    lines = ["| " + " | ".join(headers) + " |"]
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for _, row in df.iterrows():
        vals = [str(x) for x in row.values]
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def run_all_explainability():
    print("=" * 70)
    print("CREDIT RISK MODEL EXPLAINABILITY & SCORECARD SUITE")
    print("=" * 70)

    config_path = PROJECT_ROOT / "config" / "path.yaml"
    paths = load_yaml_config(config_path)
    output_dir = PROJECT_ROOT / "reports" / "model"
    images_dir = output_dir / "Images"
    images_dir.mkdir(parents=True, exist_ok=True)

    # 1. Load Validation Data
    valid_path = PROJECT_ROOT / paths.get("data_dir", "Home Credit Dataset") / paths["dirs"]["processed_valid"] / paths["files"]["main_table"]
    print(f"\n[1/3] Loading Validation Data from: {valid_path}")
    if not valid_path.exists():
        raise FileNotFoundError(f"Validation dataset not found at {valid_path}")

    df_valid = pd.read_csv(valid_path).replace([np.inf, -np.inf], np.nan)
    y_valid = df_valid["TARGET"]
    X_valid = df_valid.drop(columns=["TARGET"])
    print(f"Validation samples: {len(df_valid):,} | Default Rate: {y_valid.mean()*100:.2f}%")

    # 2. LOGISTIC REGRESSION SCORECARD SCALING & POINTS TABLE
    print("\n[2/3] Generating FICO-style Credit Scorecard (Logistic Regression)...")
    lr_model_path = PROJECT_ROOT / "config" / "model" / "lr_model.joblib"
    if lr_model_path.exists():
        lr_model = joblib.load(lr_model_path)
        scaler = ScorecardScaler(base_score=600, base_odds=50.0, pdo=20)

        # Build feature scorecard points table
        scorecard_df = scaler.build_scorecard_table(lr_model)
        scorecard_csv = output_dir / "lr_scorecard_points_table.csv"
        scorecard_md = output_dir / "lr_scorecard_points_table.md"
        scorecard_df.to_csv(scorecard_csv, index=False)
        with open(scorecard_md, "w", encoding="utf-8") as f:
            f.write("# Credit Scorecard Scaling Table (Logistic Regression)\n\n")
            f.write(f"**Parameters**: Base Score = 600 points @ Odds 50:1 (Good:Bad) | PDO = 20 points\n\n")
            f.write(df_to_markdown(scorecard_df.head(25)))

        # Predict scores on validation dataset (aligned with model columns)
        lr_pipe = lr_model.calibrated_classifiers_[0].estimator if hasattr(lr_model, "calibrated_classifiers_") else lr_model
        expected_lr_cols = [c for c in lr_pipe.named_steps["imputer"].feature_names_in_ if c in X_valid.columns]
        X_valid_lr = X_valid[expected_lr_cols]
        prob_valid = lr_model.predict_proba(X_valid_lr)[:, 1]
        scores_valid = scaler.prob_to_score(prob_valid)

        # Rating tiers
        rating_bands = scaler.create_rating_bands(y_valid, scores_valid)
        rating_csv = output_dir / "lr_scorecard_rating_bands.csv"
        rating_md = output_dir / "lr_scorecard_rating_bands.md"
        rating_bands.to_csv(rating_csv, index=False)
        with open(rating_md, "w", encoding="utf-8") as f:
            f.write("# Credit Rating Tiers & Risk Profile\n\n")
            f.write(df_to_markdown(rating_bands))

        # Plot Score Distribution
        score_plot = images_dir / "lr_scorecard_distribution.png"
        scaler.plot_scorecard_distribution(y_valid, scores_valid, score_plot)

        print(f"  -> Scorecard points table saved: {scorecard_csv.name}")
        print(f"  -> Rating tiers table saved: {rating_csv.name}")
        print(f"  -> Score distribution plot saved: {score_plot.name}")
        print("\n--- TOP 10 RISK FACTORS IN SCORECARD ---")
        print(df_to_markdown(scorecard_df.head(10)[["Feature", "Coefficient (beta)", "Odds Ratio", "Points_Delta_per_Std", "Risk_Direction"]]))
        print("\n--- CREDIT RATING TIERS (VALIDATION DATA) ---")
        print(df_to_markdown(rating_bands))
    else:
        print(f"  [!] lr_model.joblib not found at {lr_model_path}. Skipping LR scorecard.")

    # 3. LIGHTGBM SHAP SUMMARY & FEATURE IMPORTANCE
    print("\n[3/3] Generating SHAP Analysis for LightGBM (TreeExplainer)...")
    lgbm_model_path = PROJECT_ROOT / "config" / "model" / "lgbm_model.joblib"
    if lgbm_model_path.exists():
        lgbm_model = joblib.load(lgbm_model_path)
        shap_res = generate_lgbm_shap_analysis(
            lgbm_pipeline_or_calib=lgbm_model,
            X_raw=X_valid,
            output_dir=output_dir,
            n_sample=2500,
            max_display=20,
            random_state=42,
        )
        print(f"  -> SHAP summary beeswarm plot saved: {shap_res['summary_plot'].name}")
        print(f"  -> SHAP bar importance plot saved: {shap_res['bar_plot'].name}")
        print(f"  -> Top risk drivers saved: {shap_res['csv_path'].name}")
        print("\n--- TOP 10 LIGHTGBM RISK DRIVERS (SHAP) ---")
        print(df_to_markdown(shap_res["risk_drivers_table"].head(10)[["Rank", "Feature", "Mean_Abs_SHAP", "Business_Impact"]]))
    else:
        print(f"  [!] lgbm_model.joblib not found at {lgbm_model_path}. Skipping LightGBM SHAP.")

    print("\n" + "=" * 70)
    print("SUCCESS: Model explainability artifacts generated successfully!")
    print("=" * 70)


if __name__ == "__main__":
    run_all_explainability()
