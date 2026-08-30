"""
SkyGuard AI - Pydantic Request & Response Schemas
Author: SkyGuard AI Development Team
Focus: Strict validation for telemetry, anomalies, sensor health, and self-healing imputation
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


# Reading schemas
class ReadingBase(BaseModel):
    station_id: str
    temperature_c: float
    humidity_pct: float
    pressure_hpa: float
    wind_speed_ms: Optional[float] = 3.5
    wind_direction_deg: Optional[float] = 180.0
    solar_radiation_wm2: Optional[float] = 0.0
    rain_rate_mmh: Optional[float] = 0.0
    dew_point_c: Optional[float] = None
    battery_v: Optional[float] = 12.5


class ReadingCreate(ReadingBase):
    timestamp: Optional[datetime] = None


class ReadingResponse(ReadingBase):
    id: int
    timestamp: str
    dew_point_c: float
    is_anomaly: bool
    anomaly_score: float

    class Config:
        from_attributes = True


# Station schemas
class StationBase(BaseModel):
    id: str
    code: str
    name: str
    latitude: float
    longitude: float
    elevation_m: float = 10.0
    climate_zone: str = "Temperate"


class StationCreate(StationBase):
    pass


class StationResponse(StationBase):
    status: str
    health_score: float
    battery_voltage: float
    solar_charge_w: float
    last_seen: Optional[str] = None
    created_at: Optional[str] = None

    class Config:
        from_attributes = True


# Anomaly schemas
class AnomalyResponse(BaseModel):
    id: int
    station_id: str
    station_name: Optional[str] = None
    station_code: Optional[str] = None
    timestamp: str
    sensor: str
    anomaly_type: str
    severity: str
    confidence_score: float
    raw_value: Optional[float] = None
    expected_range: Optional[str] = None
    ml_model: str
    explanation: str
    status: str
    triage_notes: Optional[str] = None
    acknowledged_at: Optional[str] = None
    created_at: Optional[str] = None

    class Config:
        from_attributes = True


class AnomalyTriageRequest(BaseModel):
    status: str = Field(..., description="ACKNOWLEDGED, RESOLVED, or FALSE_POSITIVE")
    triage_notes: Optional[str] = None


# Fault Injection schemas
class FaultInjectionRequest(BaseModel):
    station_id: str
    anomaly_type: str = Field(
        ...,
        description="SPIKE, SENSOR_DRIFT, FROZEN_SENSOR, CROSS_SENSOR_INCONSISTENCY, SQUALL_EXTREME, WMO_RANGE_VIOLATION"
    )
    sensor: str = Field(
        ...,
        description="temperature_c, humidity_pct, pressure_hpa, wind_speed_ms, solar_radiation_wm2, all"
    )
    magnitude: float = Field(
        ...,
        description="Magnitude of alteration (e.g. +15°C spike, or 1.4x drift factor, or stuck value)"
    )
    duration_steps: int = Field(default=5, description="Number of simulation timesteps the fault persists")


class SimulationStepResponse(BaseModel):
    timestamp: str
    readings_generated: int
    anomalies_detected: int
    details: List[Dict[str, Any]]


class EngineToggleRequest(BaseModel):
    enabled: Optional[bool] = None


# Self-Healing Imputation Schemas
class ImputationRequest(BaseModel):
    temperature_c: float
    humidity_pct: float
    pressure_hpa: float
    flagged_sensors: List[str]
    station_id: Optional[str] = None


class SensorHealthRequest(BaseModel):
    station_id: str
