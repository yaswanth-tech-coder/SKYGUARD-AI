from typing import Dict, List, Any, Optional


def generate_alert_card(station: str, time: str, drift: str, slope: str, root_cause: str, action: str) -> str:
    """
    Using an HTML template string to create a clean key-value grid for the UI.
    
    In Streamlit, you would render this via:
    st.markdown(generate_alert_card(...), unsafe_allow_html=True)
    """
    html_card = f"""
    <div style="background-color: #1e2126; padding: 15px; border-radius: 8px; border-left: 4px solid #ff4b4b; margin-bottom: 10px;">
        <h4 style="margin-top: 0; color: #ffffff;">🚨 {station} <span style="font-size: 0.8em; color: #a0a0a0;">• {time}</span></h4>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 0.9em;">
            <div>
                <strong style="color: #a0a0a0;">Drift Amount:</strong><br>
                <span style="color: #ff4b4b;">{drift}</span>
            </div>


            <div>
                <strong style="color: #a0a0a0;">Linear Correlation (Slope):</strong><br>
                <span style="color: #ffffff;">{slope}</span>
            </div>
            <div>
                <strong style="color: #a0a0a0;">Root Cause:</strong><br>
                <span style="color: #ffffff;">{root_cause}</span>
            </div>
            <div>
                <strong style="color: #a0a0a0;">Recommended Action:</strong><br>
                <span style="color: #ffffff;">{action}</span>
            </div>
        </div>
    </div>
    """
    return html_card


class AnomalyExplainer:

    """
    Explainable AI (XAI) and Root Cause Diagnostic Generator for AWS Anomaly Detection.
    Synthesizes multi-tier alerts into operator-actionable maintenance guidance.
    """

    @staticmethod
    def classify_root_cause(
        sensor: str,
        anomaly_type: str,
        reading: Dict[str, Any],
        explanation: str
    ) -> Dict[str, str]:
        """
        Derive root cause category and actionable maintenance recommendation.
        """
        temp = reading.get("temperature_c", 0.0)
        wind = reading.get("wind_speed_ms", 0.0)
        rh = reading.get("humidity_pct", 0.0)
        press = reading.get("pressure_hpa", 1013.0)

        # Convective squall / real extreme
        if wind > 18.0 and anomaly_type in ["SPIKE", "STATISTICAL_OUTLIER"] and sensor == "wind_speed_ms":
            # If multiple conditions align (e.g. high wind with rain or pressure swing)
            if reading.get("rain_rate_mmh", 0) > 2.0 or press < 1005.0:
                return {
                    "root_cause": "GENUINE_METEOROLOGICAL_EVENT",
                    "action_required": "NO_HARDWARE_ACTION",
                    "maintenance_guide": "Valid convective storm / gust front passage detected. Sensor responses are physically coherent. Escalate to severe weather warning desk."
                }

        # Frozen Sensor
        if anomaly_type == "FROZEN_SENSOR":
            if sensor in ["wind_speed_ms", "wind_direction_deg"]:
                return {
                    "root_cause": "MECHANICAL_BEARING_STALL_OR_ICING",
                    "action_required": "FIELD_DISPATCH",
                    "maintenance_guide": "Check cup anemometer or wind vane bearings for mechanical seizure, dust binding, or rime icing. Replace bearing cartridge."
                }
            elif sensor == "solar_radiation_wm2":
                return {
                    "root_cause": "PYRANOMETER_OPTICAL_OBSCURATION",
                    "action_required": "CLEANING_INSPECTION",
                    "maintenance_guide": "Pyranometer glass dome is obscured. Inspect for bird droppings, fallen foliage, or dirt buildup; clean dome with isopropyl alcohol."
                }
            else:
                return {
                    "root_cause": "TRANSDUCER_ADC_STALL",
                    "action_required": "REMOTE_REBOOT_OR_REPLACE",
                    "maintenance_guide": "ADC register locked or digital transducer locked up. Attempt remote power cycle on data logger sensor bus."
                }

        # Sensor Drift
        if anomaly_type == "SENSOR_DRIFT":
            if sensor == "humidity_pct":
                return {
                    "root_cause": "CAPACITIVE_POLYMER_DEGRADATION",
                    "action_required": "SENSOR_RECALIBRATION",
                    "maintenance_guide": "Capacitive hygrometer polymer layer showing age degradation and offset drift. Schedule laboratory recalibration with salt chamber."
                }
            elif sensor == "solar_radiation_wm2":
                return {
                    "root_cause": "PHOTODIODE_SENSITIVITY_LOSS",
                    "action_required": "RECALIBRATION_OR_REPLACE",
                    "maintenance_guide": "Pyranometer responsivity constant drift. Compare against reference calibrated pyranometer."
                }

        # Cross sensor dew point violation
        if anomaly_type == "CROSS_SENSOR_INCONSISTENCY" and "dewpoint" in sensor.lower():
            return {
                "root_cause": "HYGROMETER_POSITIVE_BIAS_DRIFT",
                "action_required": "SENSOR_RECALIBRATION",
                "maintenance_guide": "RH sensor overestimating ambient humidity, driving theoretical dew point above dry-bulb temperature. Clean protective filter cap and recalibrate."
            }

        # WMO Range Violation
        if anomaly_type == "WMO_RANGE_VIOLATION":
            return {
                "root_cause": "ELECTRICAL_FAULT_OR_BROKEN_LEAD",
                "action_required": "EMERGENCY_REPAIR",
                "maintenance_guide": "Reading is outside physically permissible limits. Check sensor wiring for open circuit, short to ground, or lightning surge protector damage."
            }

        # Default Spike
        return {
            "root_cause": "ELECTROMAGNETIC_INTERFERENCE_OR_ADC_GLITCH",
            "action_required": "MONITOR_OR_FILTER",
            "maintenance_guide": "Single-step transient glitch. Check telemetry ground loop and verify if glitch repeats. AI has flagged reading for auto-filtering."
        }
