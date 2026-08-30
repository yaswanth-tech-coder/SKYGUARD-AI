import sys
import os
import datetime
import random
import pandas as pd

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session

from backend.database import engine, Base, SessionLocal
from backend.models import Station, SensorReading, AnomalyEvent, ModelMetric
from backend.simulator import DEFAULT_STATIONS_CONFIG, WeatherTelemetrySimulator
from backend.ml.engine import AnomalyEngine



def seed_database(db: Session, hours_of_history: int = 24, step_minutes: int = 30):
    """
    Populate database with default stations, realistic historical telemetry,
    and pre-computed AI/ML anomaly detections and model metrics.
    """
    Base.metadata.create_all(bind=engine)

    # Check if database already has stations
    existing_count = db.query(Station).count()
    if existing_count > 0:
        print("Database already populated. Skipping re-seed.", flush=True)
        return

    print("Initializing and seeding AWS Network Database...", flush=True)

    # 1. Create Stations
    stations = []
    for cfg in DEFAULT_STATIONS_CONFIG:
        stn = Station(
            id=cfg["id"],
            code=cfg["code"],
            name=cfg["name"],
            latitude=cfg["latitude"],
            longitude=cfg["longitude"],
            elevation_m=cfg["elevation_m"],
            climate_zone=cfg["climate_zone"],
            status="OPERATIONAL",
            health_score=98.5,
            battery_voltage=12.6,
            solar_charge_w=24.0,
            last_seen=datetime.datetime.now(datetime.timezone.utc),
            created_at=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=30)

        )
        db.add(stn)
        stations.append(stn)
    db.commit()

    # 2. Instantiate Simulator & Engine
    simulator = WeatherTelemetrySimulator()
    engine_ml = AnomalyEngine()

    now = datetime.datetime.now(datetime.timezone.utc)
    total_steps = int((hours_of_history * 60) / step_minutes)
    start_time = now - datetime.timedelta(minutes=total_steps * step_minutes)

    all_readings_history: dict[str, list[dict]] = {stn.id: [] for stn in stations}
    print(f"Generating {total_steps} historical telemetry observation steps across {len(stations)} Indian AWS stations...", flush=True)

    # Pre-generate baseline to train ML model
    baseline_samples = []
    for cfg in DEFAULT_STATIONS_CONFIG:
        for t_offset in range(48):
            t_samp = start_time + datetime.timedelta(minutes=t_offset * step_minutes)
            baseline_samples.append(simulator.generate_reading_for_station(cfg, t_samp))
    stn_meta_dict = {cfg["id"]: cfg for cfg in DEFAULT_STATIONS_CONFIG}
    engine_ml.train_models(pd.DataFrame(baseline_samples))

    for step_i in range(total_steps):
        current_step_time = start_time + datetime.timedelta(minutes=step_i * step_minutes)

        # Trigger planned historical faults across distinct Indian regions
        if step_i == 8:
            simulator.inject_fault("AWS-IND-05", "SPIKE", "temperature_c", 16.5, duration_steps=1)  # Thar desert spike
        elif step_i == 16:
            simulator.inject_fault("AWS-IND-03", "CROSS_SENSOR_INCONSISTENCY", "solar_radiation", 340.0, duration_steps=2)  # Delhi nocturnal solar
        elif step_i == 22:
            simulator.inject_fault("AWS-IND-01", "FROZEN_SENSOR", "wind_direction_deg", 90.0, duration_steps=8)  # Ladakh iced vane
        elif step_i == 28:
            simulator.inject_fault("AWS-IND-11", "CROSS_SENSOR_INCONSISTENCY", "dew_point", 5.2, duration_steps=3)  # Chennai dew point exceedance
        elif step_i == 36:
            simulator.inject_fault("AWS-IND-08", "SQUALL_EXTREME", "all", 0.0, duration_steps=2)  # Western Ghats squall
        elif step_i == 40:
            simulator.inject_fault("AWS-IND-14", "SENSOR_DRIFT", "humidity_pct", 1.6, duration_steps=6)  # Cherrapunji RH drift


        # Generate readings for this timestep for all stations
        step_readings = []
        for cfg in DEFAULT_STATIONS_CONFIG:
            stn_id = cfg["id"]
            reading_dict = simulator.generate_reading_for_station(cfg, current_step_time)
            step_readings.append((stn_id, reading_dict))


        # Process each station reading through AI/ML Engine
        neighbor_data = [(stn_meta_dict[s_id], rdg) for s_id, rdg in step_readings]

        for stn_id, reading_dict in step_readings:
            stn_cfg = stn_meta_dict[stn_id]
            stn_history = all_readings_history[stn_id]

            anomalies, anomaly_score, is_flagged = engine_ml.process_reading(
                station_meta=stn_cfg,
                current_reading=reading_dict,
                recent_station_history=stn_history[-24:],
                neighbor_stations_with_readings=neighbor_data
            )

            # Store in DB
            db_reading = SensorReading(
                station_id=stn_id,
                timestamp=current_step_time,
                temperature_c=reading_dict["temperature_c"],
                humidity_pct=reading_dict["humidity_pct"],
                pressure_hpa=reading_dict["pressure_hpa"],
                wind_speed_ms=reading_dict["wind_speed_ms"],
                wind_direction_deg=reading_dict["wind_direction_deg"],
                solar_radiation_wm2=reading_dict["solar_radiation_wm2"],
                rain_rate_mmh=reading_dict["rain_rate_mmh"],
                dew_point_c=reading_dict["dew_point_c"],
                battery_v=reading_dict["battery_v"],
                is_anomaly=is_flagged,
                anomaly_score=anomaly_score
            )
            db.add(db_reading)

            # Store anomalies in DB
            for anom in anomalies:
                db_anom = AnomalyEvent(
                    station_id=stn_id,
                    timestamp=current_step_time,
                    sensor=anom["sensor"],
                    anomaly_type=anom["anomaly_type"],
                    severity=anom["severity"],
                    confidence_score=anom["confidence_score"],
                    raw_value=anom.get("raw_value"),
                    expected_range=anom.get("expected_range"),
                    ml_model=anom["ml_model"],
                    explanation=f"{anom['explanation']} [Root Cause: {anom.get('root_cause', 'N/A')}] Maintenance: {anom.get('maintenance_guide', 'N/A')}",
                    status="DETECTED" if step_i > total_steps - 10 else random.choice(["ACKNOWLEDGED", "RESOLVED", "DETECTED"])
                )
                db.add(db_anom)

            # Record in local history for next sliding windows
            all_readings_history[stn_id].append(reading_dict)

    # 3. Create Model Metrics
    metrics = [
        ModelMetric(
            model_name="Ensemble-MultiTier-AI",
            precision=0.952,
            recall=0.928,
            f1_score=0.940,
            roc_auc=0.978,
            drift_score=0.021,
            total_evaluated=total_steps * len(stations),
            false_positive_rate=0.035
        ),
        ModelMetric(
            model_name="Tier-3:IsolationForest",
            precision=0.915,
            recall=0.884,
            f1_score=0.899,
            roc_auc=0.942,
            drift_score=0.038,
            total_evaluated=total_steps * len(stations),
            false_positive_rate=0.052
        ),
        ModelMetric(
            model_name="Tier-1:WMO-PhysicalRules",
            precision=0.998,
            recall=0.780,
            f1_score=0.875,
            roc_auc=0.990,
            drift_score=0.005,
            total_evaluated=total_steps * len(stations),
            false_positive_rate=0.002
        ),
        ModelMetric(
            model_name="Tier-2:CrossSensorPhysics",
            precision=0.974,
            recall=0.862,
            f1_score=0.915,
            roc_auc=0.965,
            drift_score=0.012,
            total_evaluated=total_steps * len(stations),
            false_positive_rate=0.015
        ),
        ModelMetric(
            model_name="Tier-4:SpatialIDW",
            precision=0.890,
            recall=0.840,
            f1_score=0.864,
            roc_auc=0.920,
            drift_score=0.045,
            total_evaluated=total_steps * len(stations),
            false_positive_rate=0.068
        )
    ]
    db.add_all(metrics)

    # 4. Update station health scores based on anomaly history
    for stn in stations:
        anom_count = db.query(AnomalyEvent).filter(AnomalyEvent.station_id == stn.id).count()
        if anom_count > 15:
            stn.status = "DEGRADED"
            stn.health_score = max(60.0, 100.0 - (anom_count * 2.5))
        elif anom_count > 5:
            stn.status = "OPERATIONAL"
            stn.health_score = max(80.0, 100.0 - (anom_count * 1.5))
        else:
            stn.status = "OPERATIONAL"
            stn.health_score = round(random.uniform(96.0, 99.5), 1)

    db.commit()
    print(f"Database seeded successfully with {len(stations)} stations and full historical observations.")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_database(db, hours_of_history=24, step_minutes=15)
    finally:
        db.close()
