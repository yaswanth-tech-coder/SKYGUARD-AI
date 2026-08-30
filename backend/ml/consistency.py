import math
import datetime
from typing import Dict, List, Any, Optional, Tuple


def calculate_magnus_dew_point(temp_c: float, humidity_pct: float) -> float:
    """
    Calculate theoretical Dew Point using August-Roche-Magnus formula.
    Valid for -40°C <= T <= 50°C.
    """
    a = 17.27
    b = 237.7
    rh = max(0.01, min(100.0, humidity_pct))
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(rh / 100.0)
    dew_point = (b * alpha) / (a - alpha)
    return round(dew_point, 2)


def calculate_approx_solar_elevation(lat_deg: float, dt: datetime.datetime) -> float:
    """
    Approximate solar elevation angle in degrees for given latitude and UTC datetime.
    """
    day_of_year = dt.timetuple().tm_yday
    hour_utc = dt.hour + dt.minute / 60.0 + dt.second / 3600.0

    # Solar declination approximation (in radians)
    declination = 23.45 * math.sin(math.radians((360 / 365) * (day_of_year - 81)))
    decl_rad = math.radians(declination)
    lat_rad = math.radians(lat_deg)

    # Hour angle (solar noon approx at 12:00 local)
    hour_angle_deg = 15.0 * (hour_utc - 12.0)
    ha_rad = math.radians(hour_angle_deg)

    # Solar elevation angle (altitude)
    sin_elev = math.sin(lat_rad) * math.sin(decl_rad) + math.cos(lat_rad) * math.cos(decl_rad) * math.cos(ha_rad)
    sin_elev = max(-1.0, min(1.0, sin_elev))
    elev_deg = math.degrees(math.asin(sin_elev))
    return elev_deg


class CrossSensorConsistencyValidator:
    """
    Tier 2: Meteorological Cross-Sensor Consistency Engine.
    Validates physical correlations across multiple sensor parameters.
    """

    @staticmethod
    def check_dewpoint_consistency(reading: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Validate temperature vs humidity vs dew point consistency.
        Dew point cannot exceed dry-bulb temperature (Magnus-Tetens law).
        """
        anomalies = []
        temp = reading.get("temperature_c")
        rh = reading.get("humidity_pct")
        reported_dp = reading.get("dew_point_c")

        if temp is None or rh is None:
            return anomalies

        calc_dp = calculate_magnus_dew_point(temp, rh)

        # 1. Check if Dew Point exceeds Air Temp
        effective_dp = reported_dp if reported_dp is not None else calc_dp
        if effective_dp > temp + 0.3:
            anomalies.append({
                "sensor": "cross_sensor:temp_dewpoint",
                "anomaly_type": "CROSS_SENSOR_INCONSISTENCY",
                "severity": "HIGH",
                "confidence_score": 0.96,
                "raw_value": effective_dp,
                "expected_range": f"<= {temp:.1f}°C (Air Temp)",
                "ml_model": "Tier-2:Magnus-DewPoint-Consistency",
                "explanation": (
                    f"Thermodynamic violation: Dew point ({effective_dp:.2f}°C) exceeds dry-bulb "
                    f"ambient air temperature ({temp:.2f}°C). Supersaturation in ambient air is "
                    f"physically impossible for AWS surface observations; indicates relative humidity "
                    f"sensor calibration drift (+RH) or thermal lag on temp probe."
                )
            })

        # 2. Check if reported dew point severely deviates from theoretical Magnus formula
        if reported_dp is not None and abs(reported_dp - calc_dp) > 3.5:
            anomalies.append({
                "sensor": "dew_point_c",
                "anomaly_type": "CROSS_SENSOR_INCONSISTENCY",
                "severity": "MEDIUM",
                "confidence_score": 0.88,
                "raw_value": reported_dp,
                "expected_range": f"{calc_dp - 1.5:.2f}°C to {calc_dp + 1.5:.2f}°C",
                "ml_model": "Tier-2:Magnus-Tetens-Discrepancy",
                "explanation": (
                    f"Reported dew point ({reported_dp:.2f}°C) diverges by {abs(reported_dp - calc_dp):.2f}°C "
                    f"from theoretical Magnus-Tetens calculation ({calc_dp:.2f}°C) derived from "
                    f"Temp {temp:.1f}°C and RH {rh:.1f}%."
                )
            })

        return anomalies

    @staticmethod
    def check_solar_radiation_consistency(
        reading: Dict[str, Any],
        station_lat: float,
        timestamp: Optional[datetime.datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Validate solar radiation against diurnal solar zenith calculation.
        Flags nocturnal radiation (radiation > 0 W/m² at night) or dead pyranometer during midday.
        """
        anomalies = []
        solar_rad = reading.get("solar_radiation_wm2")
        if solar_rad is None:
            return anomalies

        dt = timestamp or datetime.datetime.utcnow()
        solar_elev = calculate_approx_solar_elevation(station_lat, dt)

        # Nocturnal radiation check: Sun well below horizon (< -6 deg astronomical night)
        if solar_elev < -6.0 and solar_rad > 15.0:
            anomalies.append({
                "sensor": "solar_radiation_wm2",
                "anomaly_type": "CROSS_SENSOR_INCONSISTENCY",
                "severity": "MEDIUM",
                "confidence_score": 0.94,
                "raw_value": solar_rad,
                "expected_range": "0.0 to 5.0 W/m² (Nighttime)",
                "ml_model": "Tier-2:Solar-Zenith-Gating",
                "explanation": (
                    f"Nocturnal solar radiation anomaly: Pyranometer reports {solar_rad:.1f} W/m² "
                    f"while astronomical solar elevation is {solar_elev:.1f}° (Sun below horizon). "
                    f"Suspected sensor zero-offset drift, artificial lighting reflection, or amplifier thermal bias."
                )
            })

        # Midday zero-radiation check: Sun high (> 35 deg) but solar rad is 0
        if solar_elev > 35.0 and solar_rad < 5.0:
            anomalies.append({
                "sensor": "solar_radiation_wm2",
                "anomaly_type": "FROZEN_SENSOR",
                "severity": "HIGH",
                "confidence_score": 0.91,
                "raw_value": solar_rad,
                "expected_range": "300.0 to 1100.0 W/m² (Midday)",
                "ml_model": "Tier-2:Solar-Zenith-Gating",
                "explanation": (
                    f"Pyranometer obscuration detected: Reading is {solar_rad:.1f} W/m² at solar "
                    f"elevation of {solar_elev:.1f}° (Midday clear sky expectation: 400-1000 W/m²). "
                    f"Sensor may be covered with debris, bird droppings, or sensor cable detached."
                )
            })

        return anomalies
