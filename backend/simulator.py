import math
import random
import datetime
from typing import Dict, List, Any, Optional

from backend.ml.consistency import calculate_magnus_dew_point


# Stations Metadata Configuration
# Pan-India Automatic Weather Stations (AWS) Network Configuration
DEFAULT_STATIONS_CONFIG = [
    {
        "id": "AWS-IND-01",
        "code": "LEH-LADAKH",
        "name": "Ladakh High Altitude Cold Desert AWS",
        "latitude": 34.1526,
        "longitude": 77.5771,
        "elevation_m": 3500.0,
        "climate_zone": "Trans-Himalayan Cold Desert (Ladakh)",
        "base_temp": 8.5,
        "temp_amplitude": 12.0,
        "base_rh": 24.0,
        "base_press": 680.0,
        "base_wind": 7.5,
    },
    {
        "id": "AWS-IND-02",
        "code": "SHIMLA-HIMALAYA",
        "name": "Western Himalayan Highland AWS",
        "latitude": 31.1048,
        "longitude": 77.1734,
        "elevation_m": 2200.0,
        "climate_zone": "Western Himalayan Highland (Himachal)",
        "base_temp": 15.0,
        "temp_amplitude": 7.5,
        "base_rh": 60.0,
        "base_press": 785.0,
        "base_wind": 5.8,
    },
    {
        "id": "AWS-IND-03",
        "code": "DELHI-NCR",
        "name": "National Capital NCR Urban AWS",
        "latitude": 28.6139,
        "longitude": 77.2090,
        "elevation_m": 216.0,
        "climate_zone": "Northern Gangetic Plain (Delhi NCR)",
        "base_temp": 31.5,
        "temp_amplitude": 8.5,
        "base_rh": 55.0,
        "base_press": 992.0,
        "base_wind": 3.8,
    },
    {
        "id": "AWS-IND-04",
        "code": "PATNA-GANGA",
        "name": "Eastern Gangetic Floodplain AWS",
        "latitude": 25.5941,
        "longitude": 85.1376,
        "elevation_m": 53.0,
        "climate_zone": "Middle Gangetic Floodplain (Bihar)",
        "base_temp": 29.5,
        "temp_amplitude": 7.0,
        "base_rh": 72.0,
        "base_press": 1005.0,
        "base_wind": 3.2,
    },
    {
        "id": "AWS-IND-05",
        "code": "JAISALMER-THAR",
        "name": "Thar Desert Extreme Thermal AWS",
        "latitude": 26.9157,
        "longitude": 70.9083,
        "elevation_m": 225.0,
        "climate_zone": "Western Thar Desert (Rajasthan)",
        "base_temp": 36.0,
        "temp_amplitude": 14.5,
        "base_rh": 22.0,
        "base_press": 988.0,
        "base_wind": 7.8,
    },
    {
        "id": "AWS-IND-06",
        "code": "SURAT-GUJCOAST",
        "name": "Gulf of Khambhat Marine AWS",
        "latitude": 21.1702,
        "longitude": 72.8311,
        "elevation_m": 13.0,
        "climate_zone": "Gujarat Western Coastal Belt",
        "base_temp": 29.0,
        "temp_amplitude": 5.5,
        "base_rh": 78.0,
        "base_press": 1011.0,
        "base_wind": 5.4,
    },
    {
        "id": "AWS-IND-07",
        "code": "BHOPAL-VINDHYA",
        "name": "Central Vindhya Plateau AWS",
        "latitude": 23.2599,
        "longitude": 77.4126,
        "elevation_m": 527.0,
        "climate_zone": "Central Highlands & Vindhyas (MP)",
        "base_temp": 28.5,
        "temp_amplitude": 8.0,
        "base_rh": 62.0,
        "base_press": 955.0,
        "base_wind": 4.1,
    },
    {
        "id": "AWS-IND-08",
        "code": "MAHABALESHWAR-GHATS",
        "name": "Western Ghats Orographic High-Rainfall AWS",
        "latitude": 17.9237,
        "longitude": 73.6586,
        "elevation_m": 1353.0,
        "climate_zone": "Western Ghats High Escarpment (Maharashtra)",
        "base_temp": 20.5,
        "temp_amplitude": 6.0,
        "base_rh": 88.0,
        "base_press": 868.0,
        "base_wind": 8.2,
    },
    {
        "id": "AWS-IND-09",
        "code": "HYD-DECCAN",
        "name": "Telangana Deccan Plateau AWS",
        "latitude": 17.3850,
        "longitude": 78.4867,
        "elevation_m": 542.0,
        "climate_zone": "Central Deccan Plateau (Telangana)",
        "base_temp": 30.0,
        "temp_amplitude": 8.2,
        "base_rh": 58.0,
        "base_press": 952.0,
        "base_wind": 4.6,
    },
    {
        "id": "AWS-IND-10",
        "code": "BLR-MYSORE",
        "name": "South Deccan Mysore Plateau AWS",
        "latitude": 12.9716,
        "longitude": 77.5946,
        "elevation_m": 920.0,
        "climate_zone": "South Deccan Plateau (Karnataka)",
        "base_temp": 25.5,
        "temp_amplitude": 6.8,
        "base_rh": 66.0,
        "base_press": 915.0,
        "base_wind": 4.2,
    },
    {
        "id": "AWS-IND-11",
        "code": "CHENNAI-COROMANDEL",
        "name": "Coromandel Coastal Cyclone AWS",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "elevation_m": 6.0,
        "climate_zone": "Coromandel Coastal Belt (Tamil Nadu)",
        "base_temp": 31.0,
        "temp_amplitude": 4.8,
        "base_rh": 80.0,
        "base_press": 1012.0,
        "base_wind": 6.2,
    },
    {
        "id": "AWS-IND-12",
        "code": "KOCHI-MALABAR",
        "name": "Malabar Tropical Monsoon Coastal AWS",
        "latitude": 9.9312,
        "longitude": 76.2673,
        "elevation_m": 4.0,
        "climate_zone": "Malabar Tropical Coast (Kerala)",
        "base_temp": 28.5,
        "temp_amplitude": 4.2,
        "base_rh": 86.0,
        "base_press": 1013.0,
        "base_wind": 4.8,
    },
    {
        "id": "AWS-IND-13",
        "code": "KOLKATA-SUNDARBAN",
        "name": "Lower Gangetic Delta & Sundarbans AWS",
        "latitude": 22.5726,
        "longitude": 88.3639,
        "elevation_m": 9.0,
        "climate_zone": "Lower Gangetic Delta (West Bengal)",
        "base_temp": 29.5,
        "temp_amplitude": 6.2,
        "base_rh": 82.0,
        "base_press": 1012.0,
        "base_wind": 4.4,
    },
    {
        "id": "AWS-IND-14",
        "code": "SOHRA-CHERRAPUNJI",
        "name": "Meghalaya Hyper-Pluvial Highland AWS",
        "latitude": 25.2702,
        "longitude": 91.7323,
        "elevation_m": 1430.0,
        "climate_zone": "North-Eastern Khasi Hills (Meghalaya)",
        "base_temp": 18.5,
        "temp_amplitude": 5.5,
        "base_rh": 94.0,
        "base_press": 860.0,
        "base_wind": 6.5,
    },
    {
        "id": "AWS-IND-15",
        "code": "GUWAHATI-ASSAM",
        "name": "Brahmaputra Subtropical Valley AWS",
        "latitude": 26.1445,
        "longitude": 91.7362,
        "elevation_m": 55.0,
        "climate_zone": "Brahmaputra Subtropical Valley (Assam)",
        "base_temp": 27.5,
        "temp_amplitude": 6.5,
        "base_rh": 84.0,
        "base_press": 1006.0,
        "base_wind": 3.4,
    },
    {
        "id": "AWS-IND-16",
        "code": "PORTBLAIR-ANDAMAN",
        "name": "Andaman Maritime Tropical AWS",
        "latitude": 11.6234,
        "longitude": 92.7265,
        "elevation_m": 16.0,
        "climate_zone": "Andaman & Nicobar Islands (Bay of Bengal)",
        "base_temp": 28.0,
        "temp_amplitude": 3.8,
        "base_rh": 85.0,
        "base_press": 1011.0,
        "base_wind": 5.9,
    }
]



class WeatherTelemetrySimulator:
    """
    Simulates high-fidelity meteorological diurnal cycles across AWS network,
    with an interactive real-time fault injection subsystem.
    """

    def __init__(self):
        # Active fault injections: station_id -> list of active faults
        # Each fault: {type, sensor, magnitude, remaining_steps, initial_magnitude, step_count}
        self.active_faults: Dict[str, List[Dict[str, Any]]] = {}
        # Track last values to simulate frozen state
        self.frozen_cache: Dict[str, Dict[str, float]] = {}

    def inject_fault(
        self,
        station_id: str,
        anomaly_type: str,
        sensor: str,
        magnitude: float,
        duration_steps: int = 5
    ) -> Dict[str, Any]:
        """Register a new synthetic fault to be injected into future simulation timesteps."""
        if station_id not in self.active_faults:
            self.active_faults[station_id] = []

        fault_entry = {
            "anomaly_type": anomaly_type,
            "sensor": sensor,
            "magnitude": magnitude,
            "remaining_steps": duration_steps,
            "initial_magnitude": magnitude,
            "current_step": 0
        }
        self.active_faults[station_id].append(fault_entry)
        return {
            "status": "INJECTED",
            "station_id": station_id,
            "fault": fault_entry
        }

    def clear_faults(self, station_id: Optional[str] = None):
        """Clear active fault injections."""
        if station_id:
            self.active_faults.pop(station_id, None)
            self.frozen_cache.pop(station_id, None)
        else:
            self.active_faults.clear()
            self.frozen_cache.clear()

    def generate_reading_for_station(
        self,
        station_cfg: Dict[str, Any],
        sim_time: datetime.datetime
    ) -> Dict[str, Any]:
        """
        Generate physically coherent baseline meteorological observations for a given station & time,
        then superimpose any active synthetic fault injections.
        """
        stn_id = station_cfg["id"]
        hour = sim_time.hour + sim_time.minute / 60.0 + sim_time.second / 3600.0

        # Diurnal solar cycle (peak at 12:30, 0 at night)
        solar_peak = max(0.0, math.sin(math.pi * (hour - 6.0) / 12.0)) if 6.0 <= hour <= 18.0 else 0.0
        max_solar = 950.0 if station_cfg["elevation_m"] < 1000 else 1150.0
        solar_rad = round(solar_peak * max_solar + random.uniform(-5.0, 5.0), 1) if solar_peak > 0 else 0.0
        solar_rad = max(0.0, solar_rad)

        # Diurnal temperature cycle (lagged peak around 14:30)
        temp_phase = math.sin(math.pi * (hour - 8.5) / 12.0)
        temperature = station_cfg["base_temp"] + (station_cfg["temp_amplitude"] * temp_phase) + random.gauss(0, 0.4)

        # Diurnal relative humidity (inversely correlated with temperature)
        rh_offset = - (temperature - station_cfg["base_temp"]) * 3.2
        humidity = station_cfg["base_rh"] + rh_offset + random.gauss(0, 1.2)
        humidity = max(10.0, min(99.0, humidity))

        # Semi-diurnal atmospheric pressure tide (~1.5 hPa wave)
        pressure_tide = 1.2 * math.cos(math.pi * (hour - 9.0) / 6.0)
        pressure = station_cfg["base_press"] + pressure_tide + random.gauss(0, 0.25)

        # Wind speed & direction
        wind_gust_factor = 1.0 + (0.4 * solar_peak)  # stronger thermal wind in afternoon
        wind_speed = max(0.2, (station_cfg["base_wind"] * wind_gust_factor) + random.weibullvariate(1.5, 1.2))
        wind_direction = (random.gauss(220.0, 15.0) + (hour * 4.0)) % 360.0

        # Precipitation chance (mostly dry with occasional light rain)
        rain_rate = 0.0
        if station_cfg["climate_zone"] == "Subtropical Wetland" and random.random() < 0.08:
            rain_rate = round(random.uniform(1.2, 14.5), 1)

        # Battery voltage (charges during solar day, slight drain at night)
        battery_v = 12.4 + (0.8 * solar_peak) + random.uniform(-0.05, 0.05)

        # Baseline Dew Point
        dew_point = calculate_magnus_dew_point(temperature, humidity)

        reading = {
            "station_id": stn_id,
            "timestamp": sim_time.isoformat(),
            "temperature_c": round(temperature, 2),
            "humidity_pct": round(humidity, 1),
            "pressure_hpa": round(pressure, 2),
            "wind_speed_ms": round(wind_speed, 2),
            "wind_direction_deg": round(wind_direction, 1),
            "solar_radiation_wm2": round(solar_rad, 1),
            "rain_rate_mmh": round(rain_rate, 2),
            "dew_point_c": round(dew_point, 2),
            "battery_v": round(battery_v, 2),
        }

        # -------------------------------------------------------------
        # Apply Active Fault Injections
        # -------------------------------------------------------------
        if stn_id in self.active_faults and self.active_faults[stn_id]:
            active_list = self.active_faults[stn_id]
            retained_faults = []

            for fault in active_list:
                f_type = fault["anomaly_type"]
                f_sensor = fault["sensor"]
                f_mag = fault["magnitude"]
                fault["current_step"] += 1
                fault["remaining_steps"] -= 1

                # Apply fault modification based on type
                if f_type == "SPIKE":
                    # Instantaneous spike
                    if f_sensor in reading:
                        reading[f_sensor] += f_mag
                    elif f_sensor == "all":
                        reading["temperature_c"] += 14.0
                        reading["pressure_hpa"] -= 12.0

                elif f_type == "SENSOR_DRIFT":
                    # Cumulative drift factor per step
                    step_drift = (fault["current_step"] * f_mag)
                    if f_sensor in reading:
                        reading[f_sensor] += step_drift

                elif f_type == "FROZEN_SENSOR":
                    # Lock reading to cached value or fixed value
                    if stn_id not in self.frozen_cache:
                        self.frozen_cache[stn_id] = {}
                    if f_sensor not in self.frozen_cache[stn_id]:
                        self.frozen_cache[stn_id][f_sensor] = reading.get(f_sensor, f_mag)
                    
                    target_frozen_val = self.frozen_cache[stn_id][f_sensor]
                    if f_sensor in reading:
                        reading[f_sensor] = target_frozen_val

                elif f_type == "CROSS_SENSOR_INCONSISTENCY":
                    # Violate dew point > temp or night solar radiation
                    if f_sensor == "temperature" or f_sensor == "humidity" or f_sensor == "dew_point":
                        reading["dew_point_c"] = reading["temperature_c"] + abs(f_mag)
                    elif f_sensor == "solar_radiation":
                        reading["solar_radiation_wm2"] = 350.0  # e.g. nocturnal radiation

                elif f_type == "WMO_RANGE_VIOLATION":
                    # Impossible physical bounds
                    if f_sensor in reading:
                        reading[f_sensor] = f_mag

                elif f_type == "SQUALL_EXTREME":
                    # Coherent extreme meteorological event (Severe Storm)
                    reading["wind_speed_ms"] = max(24.5, reading["wind_speed_ms"] + 18.0)
                    reading["rain_rate_mmh"] = 42.0
                    reading["pressure_hpa"] -= 7.5
                    reading["temperature_c"] -= 4.2
                    reading["humidity_pct"] = 96.0

            self.active_faults[stn_id] = retained_faults

        elif getattr(self, 'enable_live_stream_anomalies', True):
            # Dynamic realistic background anomaly generation during continuous live stream
            # ~12% stochastic chance per station per step to simulate real-world sensor faults
            if random.random() < 0.12:
                anom_choice = random.choice([
                    ("SPIKE", "temperature_c", round(random.uniform(18.0, 26.0), 1)),
                    ("SENSOR_DRIFT", "humidity_pct", round(random.uniform(22.0, 35.0), 1)),
                    ("FROZEN_SENSOR", "wind_speed_ms", 0.0),
                    ("CROSS_SENSOR_INCONSISTENCY", "dew_point_c", round(reading["temperature_c"] + random.uniform(3.5, 7.5), 1)),
                    ("RATE_OF_CHANGE", "pressure_hpa", - round(random.uniform(8.0, 14.0), 1))
                ])
                f_type, f_sensor, f_val = anom_choice
                if f_type == "SPIKE":
                    reading[f_sensor] += f_val
                elif f_type == "SENSOR_DRIFT":
                    reading[f_sensor] = min(99.5, reading[f_sensor] + f_val)
                elif f_type == "FROZEN_SENSOR":
                    reading[f_sensor] = 0.0
                elif f_type == "CROSS_SENSOR_INCONSISTENCY":
                    reading["dew_point_c"] = f_val
                elif f_type == "RATE_OF_CHANGE":
                    reading[f_sensor] += f_val

        return reading

