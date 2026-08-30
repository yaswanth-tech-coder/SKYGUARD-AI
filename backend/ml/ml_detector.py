import math
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple


FEATURE_COLS = [
    "temperature_c",
    "humidity_pct",
    "pressure_hpa",
    "wind_speed_ms",
    "solar_radiation_wm2",
    "dew_point_c"
]


def c_factor(n: int) -> float:
    """Average path length of unsuccessful searches in a BST."""
    if n <= 1:
        return 1.0
    if n == 2:
        return 1.0
    euler_mascheroni = 0.5772156649
    return 2.0 * (math.log(n - 1) + euler_mascheroni) - (2.0 * (n - 1) / n)


class IsolationTreeNode:
    """Single node in an Isolation Tree."""
    def __init__(self, left=None, right=None, split_feature=None, split_value=None, size=0, is_leaf=False):
        self.left = left
        self.right = right
        self.split_feature = split_feature
        self.split_value = split_value
        self.size = size
        self.is_leaf = is_leaf


class IsolationTree:
    """Individual Isolation Tree trained on random subspace subsamples."""
    def __init__(self, max_height: int):
        self.max_height = max_height
        self.root = None

    def fit(self, X: np.ndarray, current_height: int = 0) -> IsolationTreeNode:
        n_samples, n_features = X.shape
        if current_height >= self.max_height or n_samples <= 1:
            return IsolationTreeNode(size=n_samples, is_leaf=True)

        # Randomly choose a feature
        feat_idx = np.random.randint(0, n_features)
        feat_min = X[:, feat_idx].min()
        feat_max = X[:, feat_idx].max()

        if math.isclose(feat_min, feat_max):
            return IsolationTreeNode(size=n_samples, is_leaf=True)

        # Random split point between min and max
        split_val = np.random.uniform(feat_min, feat_max)
        left_mask = X[:, feat_idx] < split_val
        right_mask = ~left_mask

        left_node = self.fit(X[left_mask], current_height + 1)
        right_node = self.fit(X[right_mask], current_height + 1)

        return IsolationTreeNode(
            left=left_node,
            right=right_node,
            split_feature=feat_idx,
            split_value=split_val,
            size=n_samples,
            is_leaf=False
        )

    def path_length(self, x: np.ndarray, node: IsolationTreeNode, current_height: int = 0) -> float:
        if node.is_leaf or node.left is None or node.right is None:
            return current_height + c_factor(node.size)

        if x[node.split_feature] < node.split_value:
            return self.path_length(x, node.left, current_height + 1)
        else:
            return self.path_length(x, node.right, current_height + 1)


class PureNumPyIsolationForest:
    """
    High-Performance, pure-NumPy Isolation Forest Anomaly Detector.
    Zero C-extension / OpenMP deadlock risk; sub-millisecond execution.
    """
    def __init__(self, n_trees: int = 50, sample_size: int = 64):
        self.n_trees = n_trees
        self.sample_size = sample_size
        self.trees: List[IsolationTree] = []
        self.n_samples_trained = 0

    def fit(self, X: np.ndarray):
        n_samples, _ = X.shape
        self.n_samples_trained = min(n_samples, self.sample_size)
        max_height = int(math.ceil(math.log2(max(self.n_samples_trained, 2))))

        self.trees = []
        for _ in range(self.n_trees):
            if n_samples > self.sample_size:
                sub_indices = np.random.choice(n_samples, size=self.sample_size, replace=False)
                X_sub = X[sub_indices]
            else:
                X_sub = X
            tree = IsolationTree(max_height=max_height)
            tree.root = tree.fit(X_sub)
            self.trees.append(tree)

    def score(self, x: np.ndarray) -> float:
        """Compute anomaly score s in [0, 1]. s > 0.6 indicates high anomaly probability."""
        if not self.trees:
            return 0.0
        avg_path = np.mean([tree.path_length(x, tree.root) for tree in self.trees])
        c = c_factor(self.n_samples_trained)
        if c == 0:
            return 0.0
        score_val = 2.0 ** (- (avg_path / c))
        return float(score_val)


DEFAULT_CORE_FEATURES = [
    "temperature_c",
    "humidity_pct",
    "pressure_hpa",
    "dew_point_c"
]


class MLAnomalyDetector:
    """
    Tier 3: Unsupervised Multi-Variate ML Anomaly Detector.
    Employs Pure-NumPy Isolation Forest, Mahalanobis Distance, and Adaptive Rolling Z-Score.
    Specialized for the core atmospheric triad (Temp, Pressure, RH).
    """

    def __init__(self, contamination: float = 0.05):
        self.contamination = contamination
        self.feature_cols = DEFAULT_CORE_FEATURES
        self.mean_vector = None
        self.std_vector = None
        self.cov_inv = None
        self.iso_forest = PureNumPyIsolationForest(n_trees=40, sample_size=64)
        self.is_fitted = False

    def fit(self, historical_df: pd.DataFrame) -> bool:
        """Fit Isolation Forest and Covariance on historical clean observations."""
        if len(historical_df) < 15:
            return False

        # Select available features (prioritizing core triad)
        avail_features = [c for c in DEFAULT_CORE_FEATURES if c in historical_df.columns]
        for opt in ["wind_speed_ms", "solar_radiation_wm2"]:
            if opt in historical_df.columns:
                avail_features.append(opt)

        if len(avail_features) < 3:
            return False

        self.feature_cols = avail_features
        df_clean = historical_df[self.feature_cols].dropna()
        if len(df_clean) < 15:
            return False

        try:
            X = df_clean.values.astype(float)
            self.mean_vector = np.mean(X, axis=0)
            self.std_vector = np.std(X, axis=0)
            self.std_vector[self.std_vector < 1e-4] = 1.0  # avoid div by zero

            # Scaled data
            X_scaled = (X - self.mean_vector) / self.std_vector
            
            # Robust Covariance Inverse for Mahalanobis
            cov = np.cov(X_scaled, rowvar=False) + np.eye(X.shape[1]) * 1e-3
            self.cov_inv = np.linalg.pinv(cov)

            # Fit Isolation Forest
            self.iso_forest.fit(X_scaled)
            self.is_fitted = True
            return True
        except Exception as e:
            print(f"Error fitting ML anomaly detector: {e}")
            return False

    def predict_multivariate(self, reading_dict: Dict[str, Any]) -> Tuple[bool, float, Dict[str, float]]:
        """
        Evaluate single reading with Isolation Forest and Mahalanobis distance.
        Returns (is_anomaly, anomaly_score_0_to_1, feature_contributions).
        """
        if not self.is_fitted:
            return False, 0.0, {}

        try:
            x_raw = np.array([float(reading_dict.get(col, self.mean_vector[i])) for i, col in enumerate(self.feature_cols)])
            x_scaled = (x_raw - self.mean_vector) / self.std_vector

            # 1. Isolation Forest score (0.0 to 1.0)
            if_score = self.iso_forest.score(x_scaled)

            # 2. Mahalanobis distance
            diff = x_scaled.reshape(1, -1)
            mahal_dist = float(np.sqrt(np.dot(np.dot(diff, self.cov_inv), diff.T)[0, 0]))
            
            # Normalize Mahalanobis distance to [0, 1] probability
            mahal_score = float(1.0 - math.exp(- (mahal_dist / 4.0)**2))

            # Composite ML score
            combined_score = float(0.6 * if_score + 0.4 * mahal_score)
            is_anomaly = bool(combined_score > 0.65 or if_score > 0.72)

            # Feature attribution (individual z-score distance)
            contributions = {}
            for idx, col in enumerate(self.feature_cols):
                contributions[col] = round(float(abs(x_scaled[idx])), 2)

            return is_anomaly, round(combined_score, 3), contributions
        except Exception as e:
            print(f"Prediction error in ML Anomaly Detector: {e}")
            return False, 0.0, {}

    @staticmethod
    def evaluate_rolling_zscores(
        current_reading: Dict[str, Any],
        recent_readings: List[Dict[str, Any]],
        z_threshold: float = 3.0
    ) -> List[Dict[str, Any]]:
        """
        Evaluate adaptive rolling Z-Score for individual sensor channels over historical window.
        """
        if len(recent_readings) < 6:
            return []

        anomalies = []
        df_recent = pd.DataFrame(recent_readings)

        for col in ["temperature_c", "humidity_pct", "pressure_hpa", "wind_speed_ms"]:
            if col not in df_recent.columns or col not in current_reading:
                continue

            series = df_recent[col].dropna().astype(float)
            if len(series) < 6:
                continue

            mean = series.mean()
            std = series.std()

            if std < 1e-4:
                continue

            curr_val = float(current_reading[col])
            z_score = abs(curr_val - mean) / std

            if z_score > z_threshold:
                severity = "CRITICAL" if z_score > 4.5 else "HIGH" if z_score > 3.8 else "MEDIUM"
                confidence = min(0.98, round(0.70 + (z_score / 15.0), 2))
                lower_bound = round(mean - 2.5 * std, 2)
                upper_bound = round(mean + 2.5 * std, 2)

                anomalies.append({
                    "sensor": col,
                    "anomaly_type": "SPIKE" if z_score > 4.0 else "STATISTICAL_OUTLIER",
                    "severity": severity,
                    "confidence_score": confidence,
                    "raw_value": curr_val,
                    "expected_range": f"{lower_bound} to {upper_bound}",
                    "ml_model": "Tier-3:Adaptive-Rolling-ZScore",
                    "explanation": (
                        f"Statistical anomaly on {col}: Reading ({curr_val:.2f}) deviates by "
                        f"{z_score:.2f} standard deviations from rolling local mean ({mean:.2f}, "
                        f"σ = {std:.2f}). Exceeds dynamic Z-score threshold (Z > {z_threshold})."
                    )
                })

        return anomalies

    @staticmethod
    def detect_sensor_drift(
        recent_readings: List[Dict[str, Any]],
        window_size: int = 24
    ) -> List[Dict[str, Any]]:
        """
        Detect progressive calibration degradation / sensor drift.
        Examines monotonic slope and cumulative baseline bias over a sliding window.
        """
        if len(recent_readings) < window_size:
            return []

        anomalies = []
        df_window = pd.DataFrame(recent_readings[-window_size:])

        for col, drift_threshold in [("humidity_pct", 22.0), ("temperature_c", 5.0), ("pressure_hpa", 6.0), ("solar_radiation_wm2", 90.0)]:
            if col not in df_window.columns:
                continue

            series = df_window[col].dropna().astype(float).values
            if len(series) < window_size:
                continue

            x = np.arange(len(series))
            slope, intercept = np.polyfit(x, series, 1)
            total_drift = slope * len(series)

            corr = np.corrcoef(x, series)[0, 1] if np.std(series) > 1e-4 else 0.0

            if abs(corr) > 0.88 and abs(total_drift) > drift_threshold:
                direction = "upward (+bias)" if total_drift > 0 else "downward (-bias)"
                anomalies.append({
                    "sensor": col,
                    "anomaly_type": "SENSOR_DRIFT",
                    "severity": "HIGH" if abs(total_drift) > drift_threshold * 1.4 else "MEDIUM",
                    "confidence_score": round(min(0.95, abs(corr)), 2),
                    "raw_value": series[-1],
                    "expected_range": f"Baseline drift < ±{drift_threshold:.1f}",
                    "ml_model": "Tier-3:Monotonic-Drift-Estimator",
                    "explanation": (
                        f"Progressive sensor drift detected on {col}: Continuous {direction} drift of "
                        f"{total_drift:+.2f} over past {window_size} observation timesteps (Slope = {slope:+.3f}/step, "
                        f"Linear Correlation R² = {corr**2:.2f}). Indicates aging sensor element, dust accumulation, "
                        f"or uncalibrated ADC drift."
                    )
                })

        return anomalies
