"""
SkyGuard AI - Meteorological Event vs Sensor Glitch Discrimination Engine
Author: SkyGuard AI Development Team
Focus: Distinguish genuine severe weather events from sensor faults using multi-channel physical coupling
"""

import math
from typing import Dict, List, Any, Optional, Tuple
from backend.ml.thermodynamics import AtmosphericThermodynamics


class MeteorologicalEventClassifier:
    """
    Discriminates between genuine extreme meteorological phenomena and sensor/data anomalies.
    Prevents false alarms during severe convective storms, squalls, frontal passages, and heatwaves.
    """

    @classmethod
    def classify_event_or_fault(
        cls,
        current: Dict[str, Any],
        previous: Optional[Dict[str, Any]],
        recent_window: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Analyze multi-channel covariance across Temperature, Pressure, and Humidity.
        Returns:
            classification: 'GENUINE_METEOROLOGICAL_EVENT' | 'SENSOR_FAULT' | 'NORMAL_VARIATION'
            event_type: Specific meteorological phenomenon or fault type
            confidence: float (0.0 to 1.0)
            is_anomaly: bool (True only if it's a sensor fault, False if genuine event)
            explanation: Detailed physical justification
        """
        if not previous:
            return {
                "classification": "NORMAL_VARIATION",
                "event_type": "BASELINE_OBSERVATION",
                "confidence": 0.95,
                "is_fault": False,
                "explanation": "Initial observation established."
            }

        curr_t = float(current.get("temperature_c", 25.0))
        prev_t = float(previous.get("temperature_c", 25.0))
        delta_t = curr_t - prev_t

        curr_p = float(current.get("pressure_hpa", 1013.0))
        prev_p = float(previous.get("pressure_hpa", 1013.0))
        delta_p = curr_p - prev_p

        curr_rh = float(current.get("humidity_pct", 50.0))
        prev_rh = float(previous.get("humidity_pct", 50.0))
        delta_rh = curr_rh - prev_rh

        # Calculate thermodynamic indicators
        thermo_curr = AtmosphericThermodynamics.validate_thermodynamic_consistency(curr_t, curr_p, curr_rh)
        dew_depr = thermo_curr["metrics"]["dew_point_depression_c"]

        # -------------------------------------------------------------
        # 1. Check for Genuine Convective Downburst / Thunderstorm Squall
        # Physical signature: Rapid temp drop (evaporative cooling from downdraft),
        # sharp humidity surge, and pressure surge/bubble (gust front micro-high).
        # -------------------------------------------------------------
        if (delta_t <= -1.8 and delta_rh >= 10.0) or (delta_t <= -2.5 and abs(delta_p) >= 0.5):
            return {
                "classification": "GENUINE_METEOROLOGICAL_EVENT",
                "event_type": "CONVECTIVE_DOWNDRAFT_SQUALL",
                "confidence": 0.96,
                "is_fault": False,
                "metrics": {"delta_t": delta_t, "delta_p": delta_p, "delta_rh": delta_rh},
                "explanation": (
                    f"Genuine meteorological event: Convective storm downburst / gust front detected. "
                    f"Multi-parameter coupling: Temp dropped {delta_t:.1f}°C, Humidity jumped {delta_rh:+.1f}%, "
                    f"and Pressure shifted {delta_p:+.1f} hPa. Physical relations are mutually coherent. "
                    f"ZERO hardware fault; suppressed false alarm."
                )
            }

        # -------------------------------------------------------------
        # 2. Check for Genuine Cold Front Passage
        # Physical signature: Sustained temperature drop, pressure rising (anticyclonic build),
        # dew point shift.
        # -------------------------------------------------------------
        if delta_t <= -3.0 and delta_p >= 1.2 and delta_rh <= 20.0:
            return {
                "classification": "GENUINE_METEOROLOGICAL_EVENT",
                "event_type": "COLD_FRONT_PASSAGE",
                "confidence": 0.94,
                "is_fault": False,
                "metrics": {"delta_t": delta_t, "delta_p": delta_p, "delta_rh": delta_rh},
                "explanation": (
                    f"Genuine meteorological event: Mesoscale cold front passage. "
                    f"Temp fell {delta_t:.1f}°C with barometric surge of {delta_p:+.1f} hPa. "
                    f"Atmospheric density increase consistent with cold air advection. No sensor fault."
                )
            }

        # -------------------------------------------------------------
        # 3. Check for Genuine Diurnal Heatwave Peak
        # High temperature (> 40°C), low humidity (< 25%), stable or slightly low pressure.
        # -------------------------------------------------------------
        if curr_t >= 42.0 and curr_rh <= 30.0 and abs(delta_t) < 4.0:
            return {
                "classification": "GENUINE_METEOROLOGICAL_EVENT",
                "event_type": "EXTREME_HEATWAVE_PEAK",
                "confidence": 0.93,
                "is_fault": False,
                "metrics": {"temperature_c": curr_t, "humidity_pct": curr_rh, "pressure_hpa": curr_p},
                "explanation": (
                    f"Genuine meteorological event: Extreme dry thermal heatwave condition. "
                    f"Air temp is {curr_t:.1f}°C with relative humidity at {curr_rh:.1f}%. "
                    f"Low humidity correctly balances high saturation vapor pressure ({thermo_curr['metrics']['saturation_vapor_pressure_hpa']:.1f} hPa)."
                )
            }

        # -------------------------------------------------------------
        # 4. Check for Sensor Fault: Isolated Temperature Spike / EMI Glitch
        # Physical signature: Huge step change in T, while P and RH are essentially uncoupled/static.
        # -------------------------------------------------------------
        if abs(delta_t) >= 6.0 and abs(delta_rh) < 5.0 and abs(delta_p) < 0.5:
            return {
                "classification": "SENSOR_FAULT",
                "event_type": "ISOLATED_TEMPERATURE_SPIKE",
                "confidence": 0.98,
                "is_fault": True,
                "metrics": {"delta_t": delta_t, "delta_p": delta_p, "delta_rh": delta_rh},
                "explanation": (
                    f"Sensor Fault Detected: Isolated temperature step anomaly of {delta_t:+.1f}°C. "
                    f"Neither humidity ({delta_rh:+.1f}%) nor atmospheric pressure ({delta_p:+.1f} hPa) show "
                    f"thermodynamic response. Indicates electrical transient, ADC glitch, or probe cable disconnect."
                )
            }

        # -------------------------------------------------------------
        # 5. Check for Sensor Fault: Isolated Pressure Step / Barometer Failure
        # -------------------------------------------------------------
        if abs(delta_p) >= 5.0 and abs(delta_t) < 1.0 and abs(delta_rh) < 5.0:
            return {
                "classification": "SENSOR_FAULT",
                "event_type": "BAROMETRIC_TRANSDUCER_FAULT",
                "confidence": 0.97,
                "is_fault": True,
                "metrics": {"delta_p": delta_p},
                "explanation": (
                    f"Sensor Fault Detected: Unphysical barometric pressure step jump of {delta_p:+.1f} hPa. "
                    f"No corresponding meteorological disturbance or temperature shift. Suspected piezoresistive transducer failure."
                )
            }

        # -------------------------------------------------------------
        # 6. Check for Sensor Fault: Thermodynamic Super-Saturation Inversion
        # -------------------------------------------------------------
        if not thermo_curr["is_consistent"]:
            return {
                "classification": "SENSOR_FAULT",
                "event_type": "THERMODYNAMIC_INCONSISTENCY",
                "confidence": 0.95,
                "is_fault": True,
                "metrics": thermo_curr["metrics"],
                "explanation": "; ".join(thermo_curr["violations"])
            }

        # -------------------------------------------------------------
        # 7. Check for Sensor Fault: Stuck / Flatlined Sensor
        # -------------------------------------------------------------
        if recent_window and len(recent_window) >= 10:
            t_vals = [float(r.get("temperature_c", 0)) for r in recent_window[-10:]]
            if len(set(t_vals)) == 1:
                return {
                    "classification": "SENSOR_FAULT",
                    "event_type": "FROZEN_TEMPERATURE_SENSOR",
                    "confidence": 0.99,
                    "is_fault": True,
                    "metrics": {"frozen_value": t_vals[-1]},
                    "explanation": f"Temperature sensor has been completely static at {t_vals[-1]:.2f}°C for 10 consecutive steps."
                }

        return {
            "classification": "NORMAL_VARIATION",
            "event_type": "STANDARD_ATMOSPHERIC_VARIATION",
            "confidence": 0.90,
            "is_fault": False,
            "metrics": {"delta_t": delta_t, "delta_p": delta_p, "delta_rh": delta_rh},
            "explanation": "Atmospheric parameters adhere to normal diurnal variations and thermodynamic constraints."
        }
