"""
SkyGuard AI - Unified Multi-Tier AI/ML Anomaly Detection Orchestrator
Author: SkyGuard AI Development Team
Focus: Core Triad - Temperature (°C), Pressure (hPa), Relative Humidity (%)
"""

import datetime
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple

from backend.ml.thermodynamics import AtmosphericThermodynamics
from backend.ml.event_classifier import MeteorologicalEventClassifier
from backend.ml.imputer import PhysicsInformedImputer
from backend.ml.sensor_health import SensorHealthForecaster
from backend.ml.shap_explainer import SHAPExplainer
from backend.ml.wmo_rules import WMORulesValidator
from backend.ml.consistency import CrossSensorConsistencyValidator
from backend.ml.ml_detector import MLAnomalyDetector
from backend.ml.spatial import SpatialNeighborValidator
from backend.ml.explainer import AnomalyExplainer


class AnomalyEngine:
    """
    Unified Multi-Tier AI/ML Anomaly Detection & Self-Healing Pipeline.
    Integrates physics-based thermodynamic validation, meteorological event discrimination,
    unsupervised Isolation Forest + Mahalanobis ML, spatial IDW consensus,
    SHAP explainability, and self-healing data imputation.
    """

    def __init__(self):
        self.thermo = AtmosphericThermodynamics()
        self.event_classifier = MeteorologicalEventClassifier()
        self.imputer = PhysicsInformedImputer()
        self.health_forecaster = SensorHealthForecaster()
        self.shap_explainer = SHAPExplainer()
        self.wmo_validator = WMORulesValidator()
        self.consistency_validator = CrossSensorConsistencyValidator()
        self.ml_detector = MLAnomalyDetector(contamination=0.05)
        self.spatial_validator = SpatialNeighborValidator()
        self.explainer = AnomalyExplainer()

    def train_models(self, historical_df: pd.DataFrame) -> bool:
        """Train or calibrate unsupervised ML models and SHAP baseline on historical data."""
        self.shap_explainer.calibrate(historical_df)
        return self.ml_detector.fit(historical_df)

    def process_reading(
        self,
        station_meta: Dict[str, Any],
        current_reading: Dict[str, Any],
        recent_station_history: List[Dict[str, Any]],
        neighbor_stations_with_readings: Optional[List[Tuple[Dict[str, Any], Dict[str, Any]]]] = None
    ) -> Tuple[List[Dict[str, Any]], float, bool]:
        """
        Execute full multi-tier detection pipeline on an incoming sensor observation.
        Returns: (anomalies_list, composite_anomaly_score, is_flagged_as_anomaly)
        """
        detected_anomalies: List[Dict[str, Any]] = []

        # Ensure theoretical dew point and air density are calculated if missing
        temp = float(current_reading.get("temperature_c", 20.0))
        rh = float(current_reading.get("humidity_pct", 50.0))
        press = float(current_reading.get("pressure_hpa", 1013.0))

        reported_td = current_reading.get("dew_point_c")
        calc_td = AtmosphericThermodynamics.dew_point(temp, rh)
        if reported_td is None:
            current_reading["dew_point_c"] = calc_td
        current_reading["air_density_kg_m3"] = AtmosphericThermodynamics.moist_air_density(temp, press, rh)

        # Get last known clean reading to prevent recovery-step false alarms
        clean_prev = None
        for r in reversed(recent_station_history):
            if not r.get("is_anomaly", False):
                clean_prev = r
                break
        prev_reading = clean_prev or (recent_station_history[-1] if recent_station_history else None)

        # -------------------------------------------------------------
        # Step A: Meteorological Event vs Sensor Glitch Discrimination
        # -------------------------------------------------------------
        event_assessment = self.event_classifier.classify_event_or_fault(
            current=current_reading,
            previous=prev_reading,
            recent_window=recent_station_history
        )

        # If it's a genuine severe meteorological event (squall, downburst, front), DO NOT raise sensor alarms!
        is_genuine_weather = (event_assessment["classification"] == "GENUINE_METEOROLOGICAL_EVENT")

        # -------------------------------------------------------------
        # Tier 1: WMO-No. 8 Physical Bounds & Step Dynamic Limits & Flatline
        # -------------------------------------------------------------
        t1_bounds = self.wmo_validator.check_physical_bounds(current_reading)
        detected_anomalies.extend(t1_bounds)

        # Only check step rate-of-change if NOT a confirmed genuine severe storm
        if not is_genuine_weather:
            t1_roc = self.wmo_validator.check_rate_of_change(current_reading, prev_reading)
            detected_anomalies.extend(t1_roc)

        if len(recent_station_history) >= 3:
            all_history_window = recent_station_history + [current_reading]
            t1_flatline = self.wmo_validator.check_flatline(all_history_window, window_size=4)
            detected_anomalies.extend(t1_flatline)

        # -------------------------------------------------------------
        # Tier 2: Thermodynamic Consistency Checks
        # -------------------------------------------------------------
        thermo_check = AtmosphericThermodynamics.validate_thermodynamic_consistency(
            temp_c=temp,
            pressure_hpa=press,
            humidity_pct=rh,
            reported_dew_point=current_reading.get("dew_point_c")
        )
        if not thermo_check["is_consistent"]:
            for violation in thermo_check["violations"]:
                detected_anomalies.append({
                    "sensor": "cross_sensor:thermodynamic",
                    "anomaly_type": "CROSS_SENSOR_INCONSISTENCY",
                    "severity": "HIGH",
                    "confidence_score": 0.96,
                    "raw_value": temp,
                    "expected_range": "Thermodynamic Vapor Pressure Envelope",
                    "ml_model": "Tier-2:Magnus-Clausius-Clapeyron-Thermodynamics",
                    "explanation": violation
                })

        # Solar zenith check if solar radiation is present
        ts = current_reading.get("timestamp")
        if isinstance(ts, str):
            try:
                ts = datetime.datetime.fromisoformat(ts.replace("Z", "+00:00"))
            except Exception:
                ts = datetime.datetime.now(datetime.timezone.utc)
        elif not isinstance(ts, datetime.datetime):
            ts = datetime.datetime.now(datetime.timezone.utc)

        if "solar_radiation_wm2" in current_reading and current_reading["solar_radiation_wm2"] is not None:
            t2_solar = self.consistency_validator.check_solar_radiation_consistency(
                current_reading,
                station_lat=station_meta.get("latitude", 20.0),
                timestamp=ts
            )
            detected_anomalies.extend(t2_solar)

        # -------------------------------------------------------------
        # Tier 3: Unsupervised Multi-Variate ML (Isolation Forest + Mahalanobis)
        # -------------------------------------------------------------
        is_ml_anomaly, ml_score, ml_contribs = self.ml_detector.predict_multivariate(current_reading)
        
        # Suppress ML anomaly if confirmed genuine extreme weather
        if is_ml_anomaly and ml_score > 0.85 and not is_genuine_weather:
            top_feature = max(ml_contribs, key=ml_contribs.get) if ml_contribs else "multivariate_sensor_vector"
            detected_anomalies.append({
                "sensor": top_feature,
                "anomaly_type": "STATISTICAL_OUTLIER",
                "severity": "CRITICAL" if ml_score > 0.92 else "HIGH",
                "confidence_score": round(ml_score, 2),
                "raw_value": current_reading.get(top_feature),
                "expected_range": "Multivariate ML Norm Envelope",
                "ml_model": "Tier-3:IsolationForest-MultiVariate",
                "explanation": (
                    f"Multivariate AI outlier detected (Isolation Forest anomaly score: {ml_score:.2f}). "
                    f"Primary anomalous parameter: {top_feature} (deviation index: {ml_contribs.get(top_feature, 0):.2f})."
                )
            })

        # Dynamic rolling Z-scores
        if recent_station_history and not is_genuine_weather:
            t3_zscore = self.ml_detector.evaluate_rolling_zscores(current_reading, recent_station_history, z_threshold=3.6)
            detected_anomalies.extend(t3_zscore)

        # Drift detection over window
        if len(recent_station_history) >= 24 and not is_genuine_weather:
            drift_window = recent_station_history + [current_reading]
            t3_drift = self.ml_detector.detect_sensor_drift(drift_window, window_size=24)
            detected_anomalies.extend(t3_drift)

        # -------------------------------------------------------------
        # Tier 4: Spatial Neighbor Consistency (IDW)
        # -------------------------------------------------------------
        if neighbor_stations_with_readings and not is_genuine_weather:
            t4_spatial = self.spatial_validator.check_spatial_outlier(
                target_station=station_meta,
                target_reading=current_reading,
                neighbor_stations_with_readings=neighbor_stations_with_readings,
                max_search_radius_km=85.0
            )
            detected_anomalies.extend(t4_spatial)

        # -------------------------------------------------------------
        # Deduplication, Root-Cause Classification, and SHAP Attribution
        # -------------------------------------------------------------
        unique_anomalies = []
        seen_keys = set()
        flagged_sensors = []

        for a in detected_anomalies:
            key = (a["sensor"], a["anomaly_type"])
            if key not in seen_keys:
                seen_keys.add(key)
                flagged_sensors.append(a["sensor"])
                
                # Enrich with Root-Cause Diagnostics
                rca = self.explainer.classify_root_cause(
                    sensor=a["sensor"],
                    anomaly_type=a["anomaly_type"],
                    reading=current_reading,
                    explanation=a["explanation"]
                )
                a["root_cause"] = rca["root_cause"]
                a["action_required"] = rca["action_required"]
                a["maintenance_guide"] = rca["maintenance_guide"]

                unique_anomalies.append(a)

        # Calculate composite anomaly score
        if unique_anomalies:
            max_conf = max(a["confidence_score"] for a in unique_anomalies)
            composite_score = round(max(ml_score, max_conf), 3)
            is_flagged = True
        else:
            composite_score = round(ml_score, 3)
            is_flagged = False

        # Compute SHAP feature attribution
        shap_result = self.shap_explainer.compute_shapley_values(current_reading, composite_score)
        current_reading["shap_attribution"] = shap_result

        # -------------------------------------------------------------
        # Self-Healing Imputation (if flagged)
        # -------------------------------------------------------------
        if is_flagged and flagged_sensors:
            neighbor_readings_list = [r for _, r in neighbor_stations_with_readings] if neighbor_stations_with_readings else None
            imputation_output = self.imputer.impute_reading(
                corrupted_reading=current_reading,
                recent_history=recent_station_history,
                flagged_sensors=flagged_sensors,
                neighbor_readings=neighbor_readings_list
            )
            current_reading["imputed_data"] = imputation_output

        return unique_anomalies, composite_score, is_flagged
