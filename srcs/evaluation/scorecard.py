from __future__ import annotations

from pathlib import Path
from typing import Any
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


class ScorecardScaler:
    def __init__(
        self,
        base_score: int = 600,
        base_odds: float = 50.0,
        pdo: int = 20,
    ):
        self.base_score = float(base_score)
        self.base_odds = float(base_odds)
        self.pdo = float(pdo)
        self.factor = self.pdo / np.log(2.0)
        self.offset = self.base_score - self.factor * np.log(self.base_odds)

    def prob_to_score(self, prob: np.ndarray | pd.Series | float) -> np.ndarray:
        """Convert predicted probability of default (PD) into credit score."""
        p = np.clip(np.asarray(prob, dtype=float), 1e-7, 1.0 - 1e-7)
        log_odds_bad = np.log(p / (1.0 - p))
        score = self.offset - self.factor * log_odds_bad
        return np.round(score).astype(int)

    def score_to_prob(self, score: np.ndarray | pd.Series | float) -> np.ndarray:
        """Convert credit score back into predicted probability of default (PD)."""
        s = np.asarray(score, dtype=float)
        log_odds_bad = (self.offset - s) / self.factor
        odds_bad = np.exp(np.clip(log_odds_bad, -30, 30))
        return odds_bad / (1.0 + odds_bad)

    def build_scorecard_table(
        self,
        lr_pipeline_or_calib,
        feature_names: list[str] | None = None,
        X_sample: pd.DataFrame | np.ndarray | None = None,
    ) -> pd.DataFrame:
        """
        Generate feature-level points contribution table from fitted Logistic Regression.
        """
        # Unwrap CalibratedClassifierCV if needed
        if hasattr(lr_pipeline_or_calib, "calibrated_classifiers_"):
            pipe = lr_pipeline_or_calib.calibrated_classifiers_[0].estimator
        else:
            pipe = lr_pipeline_or_calib

        lr_model = pipe.named_steps["model"]
        selector = pipe.named_steps.get("selector")
        imputer = pipe.named_steps.get("imputer")

        # Resolve selected feature names
        if feature_names is None:
            if hasattr(imputer, "feature_names_in_") and hasattr(selector, "selected_indices_"):
                feature_names = [str(col) for col in imputer.feature_names_in_[selector.selected_indices_]]
            elif hasattr(selector, "selected_features_") and selector.selected_features_ is not None:
                feature_names = selector.selected_features_
            else:
                feature_names = [f"feature_{i}" for i in range(len(lr_model.coef_[0]))]

        coefs = lr_model.coef_[0]
        intercept = float(lr_model.intercept_[0])
        m = len(coefs)

        scaler = pipe.named_steps.get("scaler")
        stds = scaler.scale_ if hasattr(scaler, "scale_") else np.ones(m)

        base_points_per_feat = (self.offset / m) - (self.factor * intercept / m)

        rows = []
        for feat, coef, std in zip(feature_names, coefs, stds):
            odds_ratio = np.exp(coef)
            # Point impact per 1 standard deviation increase in feature:
            # Score delta = - Factor * (coef * std)
            pts_per_std = - self.factor * (coef * (std if std != 0 else 1.0))

            direction = "High Risk (Decreases Score)" if coef > 0 else "Low Risk (Increases Score)"
            rows.append({
                "Feature": feat,
                "Coefficient (beta)": round(float(coef), 4),
                "Odds Ratio": round(float(odds_ratio), 4),
                "Std_Dev": round(float(std), 4),
                "Points_Delta_per_Std": round(float(pts_per_std), 1),
                "Risk_Direction": direction,
            })

        df_table = pd.DataFrame(rows)
        # Sort by absolute impact
        df_table["Abs_Impact"] = df_table["Coefficient (beta)"].abs()
        df_table = df_table.sort_values(by="Abs_Impact", ascending=False).drop(columns=["Abs_Impact"]).reset_index(drop=True)
        return df_table

    def create_rating_bands(
        self,
        y_true: pd.Series | np.ndarray,
        scores: pd.Series | np.ndarray,
        n_bands: int = 5,
    ) -> pd.DataFrame:
        """
        Group credit scores into Credit Rating Tiers (AAA, AA, A, BBB, Subprime)
        and compute actual default rates, population shares, and K-S stats per band.
        """
        y_true_arr = np.asarray(y_true).astype(int)
        scores_arr = np.asarray(scores).astype(int)

        df = pd.DataFrame({"score": scores_arr, "bad": y_true_arr})
        
        # Define clean score tier cutoffs (FICO-like convention)
        score_bins = [0, 580, 640, 700, 750, 1000]
        tier_names = [
            "Tier E: Very High Risk (<580)",
            "Tier D: High Risk (580-639)",
            "Tier C: Medium Risk (640-699)",
            "Tier B: Low Risk (700-749)",
            "Tier A: Prime (750+)",
        ]

        df["tier"] = pd.cut(df["score"], bins=score_bins, labels=tier_names, include_lowest=True, right=False)

        summary = (
            df.groupby("tier", observed=False)
            .agg(
                Total=("bad", "count"),
                Bad_Count=("bad", "sum"),
            )
            .reset_index()
        )

        total_obs = len(df)
        total_bads = df["bad"].sum()
        total_goods = total_obs - total_bads

        summary["Population_Pct"] = (summary["Total"] / total_obs * 100).round(2).astype(str) + "%"
        summary["Good_Count"] = summary["Total"] - summary["Bad_Count"]
        summary["Default_Rate (PD)"] = (summary["Bad_Count"] / summary["Total"] * 100).round(2).astype(str) + "%"

        # Cumulative distribution for K-S
        summary["Cum_Bad_Pct"] = (summary["Bad_Count"].cumsum() / total_bads * 100).round(2)
        summary["Cum_Good_Pct"] = (summary["Good_Count"].cumsum() / total_goods * 100).round(2)
        summary["KS_Separation"] = (summary["Cum_Bad_Pct"] - summary["Cum_Good_Pct"]).abs().round(2)

        return summary

    def plot_scorecard_distribution(
        self,
        y_true: pd.Series | np.ndarray,
        scores: pd.Series | np.ndarray,
        output_path: Path,
    ) -> Path:
        """Plot credit score distribution segmented by Default vs Non-Default."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        y_true_arr = np.asarray(y_true).astype(int)
        scores_arr = np.asarray(scores)

        scores_0 = scores_arr[y_true_arr == 0]
        scores_1 = scores_arr[y_true_arr == 1]

        plt.figure(figsize=(10, 6))
        bins = np.linspace(350, 850, 50)
        plt.hist(scores_0, bins=bins, density=True, alpha=0.55, color="steelblue", label=f"Non-Default (y=0, Mean={scores_0.mean():.0f})")
        plt.hist(scores_1, bins=bins, density=True, alpha=0.55, color="crimson", label=f"Default (y=1, Mean={scores_1.mean():.0f})")

        # Rating bands markers
        plt.axvline(580, color="darkred", linestyle=":", lw=1.5, label="Tier Cutoffs")
        plt.axvline(640, color="orange", linestyle=":", lw=1.5)
        plt.axvline(700, color="gold", linestyle=":", lw=1.5)
        plt.axvline(750, color="forestgreen", linestyle=":", lw=1.5)

        plt.xlabel("Credit Score (Points: 300 - 850)")
        plt.ylabel("Population Density")
        plt.title(f"Credit Scorecard Distribution (Base={int(self.base_score)}, PDO={int(self.pdo)})")
        plt.legend(loc="upper left")
        plt.grid(True, alpha=0.3)

        plt.savefig(output_path, bbox_inches="tight", dpi=300)
        plt.close()
        return output_path

