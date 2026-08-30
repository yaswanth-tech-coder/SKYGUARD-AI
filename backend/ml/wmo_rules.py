from typing import Dict, List, Any, Optional
import numpy as np


# WMO-No. 8 physical limits
PHYSICAL_LIMITS = {
    "temperature_c": {"min": -60.0, "max": 60.0, "unit": "°C", "name": "Air Temperature"},
    "humidity_pct": {"min": 0.0, "max": 100.0, "unit": "%", "name": "Relative Humidity"},
    "pressure_hpa": {"min": 500.0, "max": 1090.0, "unit": "hPa", "name": "Atmospheric Pressure"},
    "wind_speed_ms": {"min": 0.0, "max": 75.0, "unit": "m/s", "name": "Wind Speed"},
    "wind_direction_deg": {"min": 0.0, "max": 360.0, "unit": "°", "name": "Wind Direction"},
    "solar_radiation_wm2": {"min": 0.0, "max": 1400.0, "unit": "W/m²", "name": "Solar Radiation"},
    "rain_rate_mmh": {"min": 0.0, "max": 300.0, "unit": "mm/h", "name": "Rainfall Rate"},
    "battery_v": {"min": 9.0, "max": 16.0, "unit": "V", "name": "Station Battery Voltage"},
}

# Max allowed 5-minute rate-of-change (step test)
MAX_STEP_CHANGE = {
    "temperature_c": {"max_delta": 6.0, "unit": "°C/step"},
    "humidity_pct": {"max_delta": 35.0, "unit": "%/step"},
    "pressure_hpa": {"max_delta": 5.0, "unit": "hPa/step"},
    "wind_speed_ms": {"max_delta": 25.0, "unit": "m/s/step"},
    "battery_v": {"max_delta": 2.5, "unit": "V/step"},
}


class WMORulesValidator:
    """
    Tier 1: WMO-No. 8 Physical Range, Step/Rate-of-Change, and Flatline Validator.
    """

    @staticmethod
    def check_physical_bounds(reading_dict: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check if any sensor reading violates global physical meteorological boundaries."""
        anomalies = []
        for param, limits in PHYSICAL_LIMITS.items():
            if param not in reading_dict or reading_dict[param] is None:
                continue
            val = float(reading_dict[param])
            if val < limits["min"] or val > limits["max"]:
                severity = "CRITICAL" if (val < limits["min"] - 5 or val > limits["max"] + 20) else "HIGH"
                anomalies.append({
                    "sensor": param,
                    "anomaly_type": "WMO_RANGE_VIOLATION",
                    "severity": severity,
                    "confidence_score": 0.99,
                    "raw_value": val,
                    "expected_range": f"{limits['min']} to {limits['max']} {limits['unit']}",
                    "ml_model": "Tier-1:WMO-No.8-PhysicalBounds",
                    "explanation": (
                        f"{limits['name']} value of {val:.2f}{limits['unit']} violates physical "
                        f"atmospheric boundaries [{limits['min']} to {limits['max']}{limits['unit']}]. "
                        f"Possible sensor hardware saturation or short circuit."
                    )
                })
        return anomalies

    @staticmethod
    def check_rate_of_change(current_reading: Dict[str, Any], previous_reading: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Check if instantaneous rate-of-change between consecutive readings exceeds physics limits."""
        if not previous_reading:
            return []
        
        anomalies = []
        for param, step_conf in MAX_STEP_CHANGE.items():
            if param not in current_reading or param not in previous_reading:
                continue
            curr_val = float(current_reading[param])
            prev_val = float(previous_reading[param])
            delta = abs(curr_val - prev_val)

            if delta > step_conf["max_delta"]:
                anomalies.append({
                    "sensor": param,
                    "anomaly_type": "SPIKE",
                    "severity": "HIGH" if delta > step_conf["max_delta"] * 1.5 else "MEDIUM",
                    "confidence_score": 0.92,
                    "raw_value": curr_val,
                    "expected_range": f"{prev_val - step_conf['max_delta']:.2f} to {prev_val + step_conf['max_delta']:.2f}",
                    "ml_model": "Tier-1:Dynamic-StepLimit",
                    "explanation": (
                        f"Abrupt step jump of {delta:.2f} detected on {param} (previous: {prev_val:.2f}, "
                        f"current: {curr_val:.2f}). Exceeds dynamic rate-of-change threshold "
                        f"({step_conf['max_delta']} {step_conf['unit']})."
                    )
                })
        return anomalies

    @staticmethod
    def check_flatline(recent_readings: List[Dict[str, Any]], window_size: int = 4) -> List[Dict[str, Any]]:
        """
        Check if sensor values have stayed completely constant (zero variance) over a sliding window.
        Indicates mechanical freeze, frozen vane, or stuck ADC register.
        """
        if len(recent_readings) < window_size:
            return []

        anomalies = []
        tracked_params = ["temperature_c", "humidity_pct", "pressure_hpa"]

        for param in tracked_params:
            values = [float(r[param]) for r in recent_readings[-window_size:] if param in r and r[param] is not None]
            if len(values) < window_size:
                continue

            # Skip boundary saturation for RH (e.g. persistent 100% fog/rain or extreme dry clamp)
            if param == "humidity_pct" and (values[-1] >= 95.0 or values[-1] <= 10.0):
                continue

            std_dev = float(np.std(values))

            # If variance is virtually 0 (e.g. identical repeating float)
            if std_dev < 1e-4:
                anomalies.append({
                    "sensor": param,
                    "anomaly_type": "FROZEN_SENSOR",
                    "severity": "HIGH",
                    "confidence_score": 0.95,
                    "raw_value": values[-1],
                    "expected_range": "Non-zero natural variance",
                    "ml_model": "Tier-1:ZeroVariance-Flatline",
                    "explanation": (
                        f"Sensor flatline / freeze detected on {param}. Value has remained unchanged "
                        f"({values[-1]:.2f}) for {window_size} consecutive observation steps "
                        f"(StdDev = {std_dev:.5f}). Suspected frozen vane, iced probe, or stalled ADC."
                    )
                })
        return anomalies
