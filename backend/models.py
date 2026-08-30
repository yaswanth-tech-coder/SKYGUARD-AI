import datetime
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, Index
)
from sqlalchemy.orm import relationship
from backend.database import Base


class Station(Base):
    __tablename__ = "stations"

    id = Column(String(50), primary_key=True, index=True)
    code = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    elevation_m = Column(Float, default=10.0)
    climate_zone = Column(String(50), default="Temperate")
    status = Column(String(20), default="OPERATIONAL")  # OPERATIONAL, DEGRADED, CRITICAL, OFFLINE
    health_score = Column(Float, default=100.0)  # 0 to 100
    battery_voltage = Column(Float, default=12.6)
    solar_charge_w = Column(Float, default=18.5)
    last_seen = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

    # Relationships
    readings = relationship("SensorReading", back_populates="station", cascade="all, delete-orphan")
    anomalies = relationship("AnomalyEvent", back_populates="station", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "elevation_m": self.elevation_m,
            "climate_zone": self.climate_zone,
            "status": self.status,
            "health_score": round(self.health_score, 1),
            "battery_voltage": round(self.battery_voltage, 2),
            "solar_charge_w": round(self.solar_charge_w, 2),
            "last_seen": self.last_seen.isoformat() if self.last_seen else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    station_id = Column(String(50), ForeignKey("stations.id"), nullable=False, index=True)
    timestamp = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), index=True)
    
    # Meteorological channels
    temperature_c = Column(Float, nullable=False)
    humidity_pct = Column(Float, nullable=False)
    pressure_hpa = Column(Float, nullable=False)
    wind_speed_ms = Column(Float, nullable=False)
    wind_direction_deg = Column(Float, nullable=False)
    solar_radiation_wm2 = Column(Float, nullable=False)
    rain_rate_mmh = Column(Float, default=0.0)
    dew_point_c = Column(Float, nullable=False)
    battery_v = Column(Float, default=12.5)

    # Anomaly flag for fast querying
    is_anomaly = Column(Boolean, default=False, index=True)
    anomaly_score = Column(Float, default=0.0)

    # Relationships
    station = relationship("Station", back_populates="readings")

    __table_args__ = (
        Index("idx_station_time", "station_id", "timestamp"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "station_id": self.station_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "temperature_c": round(self.temperature_c, 2),
            "humidity_pct": round(self.humidity_pct, 1),
            "pressure_hpa": round(self.pressure_hpa, 2),
            "wind_speed_ms": round(self.wind_speed_ms, 2),
            "wind_direction_deg": round(self.wind_direction_deg, 1),
            "solar_radiation_wm2": round(self.solar_radiation_wm2, 1),
            "rain_rate_mmh": round(self.rain_rate_mmh, 2),
            "dew_point_c": round(self.dew_point_c, 2),
            "battery_v": round(self.battery_v, 2),
            "is_anomaly": self.is_anomaly,
            "anomaly_score": round(self.anomaly_score, 3)
        }


class AnomalyEvent(Base):
    __tablename__ = "anomaly_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    station_id = Column(String(50), ForeignKey("stations.id"), nullable=False, index=True)
    timestamp = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), index=True)
    
    sensor = Column(String(50), nullable=False)  # temperature, humidity, pressure, wind_speed, solar, cross_sensor
    anomaly_type = Column(String(50), nullable=False)  # SPIKE, SENSOR_DRIFT, FROZEN_SENSOR, WMO_RANGE_VIOLATION, CROSS_SENSOR_INCONSISTENCY, SPATIAL_OUTLIER, SQUALL_EXTREME
    severity = Column(String(20), default="MEDIUM")  # CRITICAL, HIGH, MEDIUM, LOW
    confidence_score = Column(Float, default=0.85)  # 0.0 to 1.0
    
    raw_value = Column(Float, nullable=True)
    expected_range = Column(String(100), nullable=True)
    ml_model = Column(String(80), default="Ensemble-MultiTier-AI")
    explanation = Column(Text, nullable=False)
    
    status = Column(String(30), default="DETECTED")  # DETECTED, ACKNOWLEDGED, RESOLVED, FALSE_POSITIVE
    triage_notes = Column(Text, nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

    # Relationships
    station = relationship("Station", back_populates="anomalies")

    __table_args__ = (
        Index("idx_anomaly_station_time", "station_id", "timestamp"),
        Index("idx_anomaly_status_sev", "status", "severity"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "station_id": self.station_id,
            "station_name": self.station.name if self.station else None,
            "station_code": self.station.code if self.station else None,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "sensor": self.sensor,
            "anomaly_type": self.anomaly_type,
            "severity": self.severity,
            "confidence_score": round(self.confidence_score, 2),
            "raw_value": round(self.raw_value, 2) if self.raw_value is not None else None,
            "expected_range": self.expected_range,
            "ml_model": self.ml_model,
            "explanation": self.explanation,
            "status": self.status,
            "triage_notes": self.triage_notes,
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class ModelMetric(Base):
    __tablename__ = "model_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), index=True)
    model_name = Column(String(80), nullable=False)
    precision = Column(Float, default=0.94)
    recall = Column(Float, default=0.91)
    f1_score = Column(Float, default=0.925)
    roc_auc = Column(Float, default=0.965)
    drift_score = Column(Float, default=0.03)  # Kolmogorov-Smirnov / PSI drift
    total_evaluated = Column(Integer, default=1000)
    false_positive_rate = Column(Float, default=0.04)

    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "model_name": self.model_name,
            "precision": round(self.precision, 3),
            "recall": round(self.recall, 3),
            "f1_score": round(self.f1_score, 3),
            "roc_auc": round(self.roc_auc, 3),
            "drift_score": round(self.drift_score, 3),
            "total_evaluated": self.total_evaluated,
            "false_positive_rate": round(self.false_positive_rate, 3),
        }
