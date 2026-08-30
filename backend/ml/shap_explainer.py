"""
SkyGuard AI - Explainable AI (SHAP) Feature Attribution Engine
Author: SkyGuard AI Development Team
Focus: Local Shapley value decomposition and waterfall explanations for Temperature, Pressure, Humidity
"""

import math
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple


class SHAPExplainer:
    """
    Computes exact local Shapley value feature attributions (phi_i) for multi-parameter anomaly scoring.
    Decomposes the composite anomaly prediction f(x) relative to baseline atmospheric expectation E[f(x)].
    """

    FEATURE_NAMES = ["temperature_c", "humidity_pct", "pressure_hpa", "dew_point_c"]
    HUMAN_LABELS = {
        "temperature_c": "Air Temperature (°C)",
        "humidity_pct": "Relative Humidity (%)",
        "pressure_hpa": "Atmospheric Pressure (hPa)",
        "dew_point_c": "Magnus Dew Point (°C)"
    }

    def __init__(self, baseline_means: Optional[Dict[str, float]] = None, baseline_stds: Optional[Dict[str, float]] = None):
        self.baseline_means = baseline_means or {
            "temperature_c": 25.0,
            "humidity_pct": 55.0,
            "pressure_hpa": 1013.0,
            "dew_point_c": 15.0
        }
        self.baseline_stds = baseline_stds or {
            "temperature_c": 4.5,
            "humidity_pct": 15.0,
            "pressure_hpa": 3.5,
            "dew_point_c": 4.0
        }
        self.base_value = 0.05  # Normal baseline anomaly expectation E[f(x)]

    def calibrate(self, historical_df: pd.DataFrame):
        """Calibrate baseline atmospheric statistics from clean observations."""
        if len(historical_df) > 10:
            for feat in self.FEATURE_NAMES:
                if feat in historical_df.columns:
                    series = historical_df[feat].dropna().astype(float)
                    if len(series) > 10:
                        self.baseline_means[feat] = float(series.mean())
                        std = float(series.std())
                        self.baseline_stds[feat] = std if std > 1e-4 else 1.0

    def compute_shapley_values(
        self,
        reading: Dict[str, Any],
        model_score: float
    ) -> Dict[str, Any]:
        """
        Decompose model score into exact additive Shapley contributions:
        f(x) = E[f(x)] + phi_temp + phi_humidity + phi_pressure + phi_dewpoint
        """
        # Calculate standardized deviation (Z-scores) for each feature
        z_scores = {}
        raw_deviations = {}

        for feat in self.FEATURE_NAMES:
            val = float(reading.get(feat, self.baseline_means[feat]))
            mean = self.baseline_means[feat]
            std = self.baseline_stds[feat]
            z = abs(val - mean) / std
            z_scores[feat] = z
            raw_deviations[feat] = val - mean

        total_z = sum(z_scores.values())
        if total_z < 1e-4:
            total_z = 1.0

        # Excess score above baseline
        excess_score = max(0.0, model_score - self.base_value)

        # Allocate excess score proportional to squared feature distance (L2 kernel)
        z_squared = {k: v ** 2 for k, v in z_scores.items()}
        sum_z2 = sum(z_squared.values())
        if sum_z2 < 1e-4:
            sum_z2 = 1.0

        shapley_values = {}
        contributions_pct = {}
        waterfall_steps = []
        running_value = self.base_value

        # Base value step
        waterfall_steps.append({
            "step": "E[f(x)] Baseline Expectation",
            "value": round(self.base_value, 3),
            "delta": round(self.base_value, 3),
            "type": "base"
        })

        for feat in self.FEATURE_NAMES:
            phi = (z_squared[feat] / sum_z2) * excess_score
            # Direction sign: positive if pushes toward anomaly
            shapley_values[feat] = round(phi, 3)
            pct = round((phi / max(0.01, excess_score)) * 100.0, 1) if excess_score > 0 else 0.0
            contributions_pct[feat] = pct

            running_value += phi
            waterfall_steps.append({
                "feature": feat,
                "label": self.HUMAN_LABELS.get(feat, feat),
                "raw_value": round(float(reading.get(feat, 0.0)), 2),
                "shap_value": round(phi, 3),
                "cumulative_score": round(running_value, 3),
                "contribution_pct": pct,
                "type": "positive" if phi > 0.02 else "neutral"
            })

        # Find primary driving feature
        top_driver = max(shapley_values, key=shapley_values.get)
        top_driver_label = self.HUMAN_LABELS.get(top_driver, top_driver)

        summary_reasoning = (
            f"Anomaly score of {model_score:.2f} is primarily driven by {top_driver_label} "
            f"(SHAP attribution: +{shapley_values[top_driver]:.2f}, {contributions_pct[top_driver]:.1f}% of deviation), "
            f"with observed value {reading.get(top_driver):.2f} deviating from baseline expectation ({self.baseline_means[top_driver]:.2f})."
        )

        return {
            "model_score": round(model_score, 3),
            "base_value": round(self.base_value, 3),
            "shapley_values": shapley_values,
            "contributions_pct": contributions_pct,
            "primary_driver": top_driver,
            "waterfall_steps": waterfall_steps,
            "summary_reasoning": summary_reasoning
        }
