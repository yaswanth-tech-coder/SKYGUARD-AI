"""
SkyGuard AI - Synthetic AWS Telemetry & Anomaly Benchmark Dataset Generator
Author: SkyGuard AI Development Team
Focus: Core Triad - Temperature (°C), Pressure (hPa), Relative Humidity (%)
"""

import os
import sys
import math
import random
import datetime
import numpy as np
import pandas as pd

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.ml.thermodynamics import AtmosphericThermodynamics

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))


def generate_benchmark_dataset(num_samples: int = 5000, anomaly_ratio: float = 0.08) -> pd.DataFrame:
    """
    Generate realistic multi-station AWS time-series telemetry with ground-truth anomaly annotations.
    """
    records = []
    start_time = datetime.datetime(2026, 8, 1, 0, 0, 0, tzinfo=datetime.timezone.utc)

    station_configs = [
        {"id": "AWS-01", "name": "Delhi NCR Urban", "base_t": 32.0, "amp_t": 8.0, "base_p": 994.0, "base_rh": 55.0},
        {"id": "AWS-02", "name": "Jaisalmer Desert", "base_t": 37.0, "amp_t": 13.0, "base_p": 988.0, "base_rh": 22.0},
        {"id": "AWS-03", "name": "Mumbai Marine Coast", "base_t": 29.0, "amp_t": 4.5, "base_p": 1012.0, "base_rh": 80.0},
        {"id": "AWS-04", "name": "Shimla Highland", "base_t": 16.0, "amp_t": 6.5, "base_p": 788.0, "base_rh": 62.0},
    ]

    current_time = start_time
    num_steps_per_station = num_samples // len(station_configs)

    for stn in station_configs:
        curr_t = stn["base_t"]
        curr_p = stn["base_p"]
        curr_rh = stn["base_rh"]

        active_drift = 0.0
        drift_slope = 0.0
        freeze_counter = 0
        frozen_val = 0.0

        for step in range(num_steps_per_station):
            t_hour = (step * 15 / 60.0) % 24.0
            
            # Realistic diurnal curve: Peak temp at 14:00 (14h), minimum at 05:00 (5h)
            diurnal_factor = math.sin((t_hour - 8.0) * math.pi / 12.0)
            
            # Baseline natural state
            temp = stn["base_t"] + stn["amp_t"] * diurnal_factor + random.gauss(0, 0.4)
            rh = max(10.0, min(95.0, stn["base_rh"] - (stn["amp_t"] * 1.6) * diurnal_factor + random.gauss(0, 1.2)))
            
            # Semi-diurnal atmospheric solar tide S_2(P) (peak at 10:00 and 22:00)
            tidal_p = 1.2 * math.cos(4.0 * math.pi * (t_hour - 10.0) / 24.0)
            press = stn["base_p"] + tidal_p + random.gauss(0, 0.3)

            is_anomaly = False
            ground_truth_label = "NORMAL"
            anomaly_type = "NONE"

            # Decide whether to inject an anomaly
            if random.random() < anomaly_ratio:
                anom_category = random.choice([
                    "SPIKE_TEMP", "SPIKE_PRESS", "DRIFT_HUMIDITY", 
                    "FROZEN_TEMP", "THERMODYNAMIC_INCONSISTENCY", "GENUINE_CONVECTIVE_STORM"
                ])

                if anom_category == "SPIKE_TEMP":
                    temp += random.choice([-15.0, 18.0, 24.0])
                    is_anomaly = True
                    ground_truth_label = "ANOMALY"
                    anomaly_type = "SPIKE"

                elif anom_category == "SPIKE_PRESS":
                    press += random.choice([-18.0, 22.0])
                    is_anomaly = True
                    ground_truth_label = "ANOMALY"
                    anomaly_type = "SPIKE"

                elif anom_category == "DRIFT_HUMIDITY":
                    drift_slope = random.choice([0.8, -0.7])
                    active_drift += drift_slope
                    rh = max(5.0, min(100.0, rh + active_drift))
                    is_anomaly = True
                    ground_truth_label = "ANOMALY"
                    anomaly_type = "SENSOR_DRIFT"

                elif anom_category == "FROZEN_TEMP":
                    freeze_counter = 8
                    frozen_val = temp
                    is_anomaly = True
                    ground_truth_label = "ANOMALY"
                    anomaly_type = "FROZEN_SENSOR"

                elif anom_category == "THERMODYNAMIC_INCONSISTENCY":
                    # Force dew point to exceed dry bulb (impossible super-saturation)
                    temp = 20.0
                    rh = 100.0
                    # reported dew point will be modified
                    is_anomaly = True
                    ground_truth_label = "ANOMALY"
                    anomaly_type = "CROSS_SENSOR_INCONSISTENCY"

                elif anom_category == "GENUINE_CONVECTIVE_STORM":
                    # Coherent severe weather: rapid temp drop + humidity surge + pressure wave
                    temp -= 5.5
                    rh += 28.0
                    press += 2.2
                    is_anomaly = False  # Genuine weather is NOT a sensor fault!
                    ground_truth_label = "GENUINE_WEATHER_EVENT"
                    anomaly_type = "GENUINE_WEATHER_EVENT"

            if freeze_counter > 0:
                temp = frozen_val
                freeze_counter -= 1
                is_anomaly = True
                ground_truth_label = "ANOMALY"
                anomaly_type = "FROZEN_SENSOR"

            # Derive physics
            dew_point = AtmosphericThermodynamics.dew_point(temp, rh)
            if anomaly_type == "CROSS_SENSOR_INCONSISTENCY":
                dew_point = temp + 3.5  # impossible violation

            step_time = start_time + datetime.timedelta(minutes=15 * step)
            records.append({
                "station_id": stn["id"],
                "station_name": stn["name"],
                "timestamp": step_time.isoformat(),
                "temperature_c": round(temp, 2),
                "pressure_hpa": round(press, 2),
                "humidity_pct": round(rh, 2),
                "dew_point_c": round(dew_point, 2),
                "wind_speed_ms": round(max(0.5, random.gauss(4.0, 1.5)), 2),
                "is_ground_truth_anomaly": is_anomaly,
                "ground_truth_label": ground_truth_label,
                "anomaly_type": anomaly_type
            })

    df = pd.DataFrame(records)
    return df


if __name__ == "__main__":
    print("Generating SkyGuard AI Benchmark Dataset (5,000 observations)...")
    df_data = generate_benchmark_dataset(num_samples=5000, anomaly_ratio=0.08)
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    csv_path = os.path.join(OUTPUT_DIR, "sample_aws_data.csv")
    df_data.to_csv(csv_path, index=False)
    
    print(f"Dataset generated successfully at: {csv_path}")
    print(f"Total Rows: {len(df_data)}")
    print(f"Anomalies Injected: {df_data['is_ground_truth_anomaly'].sum()} ({df_data['is_ground_truth_anomaly'].mean()*100:.1f}%)")
    print(f"Distribution of Types:\n{df_data['anomaly_type'].value_counts()}")
