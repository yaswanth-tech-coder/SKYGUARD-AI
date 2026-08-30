"""
SkyGuard AI - Predictive Sensor Health & Degradation Forecaster
Author: SkyGuard AI Development Team
Focus: Continuous Health Index (0-100%), Drift Slope, and Remaining Useful Life (RUL)
"""

import math
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple


class SensorHealthForecaster:
    """
    Evaluates cumulative degradation, calibration drift trajectory, and Remaining Useful Life (RUL)
    for individual AWS transducers (Temperature, Pressure, Relative Humidity).
    """

    @classmethod
    def evaluate_sensor_health(
        cls,
        station_id: str,
        recent_history: List[Dict[str, Any]],
        recent_anomalies: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Compute holistic sensor health indices and predictive maintenance forecasts.
        """
        sensors = ["temperature_c", "humidity_pct", "pressure_hpa"]
        sensor_names = {
            "temperature_c": "Platinum Resistance Thermometer (Pt100/Pt1000)",
            "humidity_pct": "Capacitive Thin-Film Polymer Hygrometer",
            "pressure_hpa": "Piezoresistive Silicon Barometric Transducer"
        }

        health_profiles = {}
        overall_station_health = 100.0

        for s in sensors:
            # 1. Count recent anomalies on this channel
            s_anoms = [a for a in recent_anomalies if a.get("sensor") == s or s in str(a.get("sensor", ""))]
            crit_anoms = sum(1 for a in s_anoms if a.get("severity") == "CRITICAL")
            high_anoms = sum(1 for a in s_anoms if a.get("severity") == "HIGH")
            med_anoms = sum(1 for a in s_anoms if a.get("severity") == "MEDIUM")

            penalty = (crit_anoms * 18.0) + (high_anoms * 8.0) + (med_anoms * 3.0)

            # 2. Check drift slope over history
            drift_slope = 0.0
            r_squared = 0.0
            rul_days = 365  # default 1 year

            if recent_history and len(recent_history) >= 12:
                vals = [float(r[s]) for r in recent_history if s in r and r[s] is not None]
                if len(vals) >= 12:
                    x = np.arange(len(vals))
                    try:
                        slope, intercept = np.polyfit(x, vals, 1)
                        drift_slope = float(slope)
                        corr = np.corrcoef(x, vals)[0, 1] if np.std(vals) > 1e-4 else 0.0
                        r_squared = float(corr ** 2) if not np.isnan(corr) else 0.0

                        # If monotonic drift is prominent
                        if r_squared > 0.65 and abs(drift_slope) > 0.05:
                            penalty += min(35.0, abs(drift_slope) * 200.0)
                            # Estimate RUL based on slope reaching failure limit
                            drift_limit = 5.0 if s == "temperature_c" else 20.0 if s == "humidity_pct" else 15.0
                            steps_to_fail = max(10, int((drift_limit) / max(0.001, abs(drift_slope))))
                            # Assuming 15-min observation steps: 96 steps/day
                            rul_days = max(3, int(steps_to_fail / 96))
                    except Exception:
                        pass

            # Calculate continuous Health Index (0-100%)
            health_score = max(10.0, min(100.0, 100.0 - penalty))
            
            if health_score >= 85.0:
                status = "OPTIMAL_HEALTH"
                maintenance_rec = "Sensor operational; nominal calibration within WMO uncertainty limits."
            elif health_score >= 65.0:
                status = "DEGRADATION_DETECTED"
                maintenance_rec = f"Early calibration drift detected ({drift_slope:+.3f}/step). Schedule routine field inspection."
            else:
                status = "CRITICAL_MAINTENANCE_REQUIRED"
                maintenance_rec = f"Severe transducer degradation. Calibration drift R²={r_squared:.2f}. Immediate replacement required."

            health_profiles[s] = {
                "sensor_name": sensor_names.get(s, s),
                "health_score": round(health_score, 1),
                "status": status,
                "drift_slope_per_step": round(drift_slope, 4),
                "drift_r_squared": round(r_squared, 3),
                "estimated_rul_days": rul_days,
                "recent_fault_count": len(s_anoms),
                "maintenance_recommendation": maintenance_rec
            }

        # Station composite health is the weighted minimum of sensor healths
        scores = [p["health_score"] for p in health_profiles.values()]
        composite_health = round(float(np.mean(scores) * 0.4 + np.min(scores) * 0.6), 1)

        return {
            "station_id": station_id,
            "station_composite_health": composite_health,
            "status": "OPERATIONAL" if composite_health >= 80 else "DEGRADED" if composite_health >= 55 else "CRITICAL",
            "sensors": health_profiles
        }
