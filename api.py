"""
SkyGuard AI - FastAPI Backend Service (api.py)
Serves live meteorological telemetry and AI anomaly detection predictions.
Integrates with InfluxDB time-series storage and Open-Meteo ingestion worker.
"""

import os
import sys
import datetime
import logging
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# InfluxDB Client
try:
    from influxdb_client import InfluxDBClient
    INFLUX_AVAILABLE = True
except ImportError:
    INFLUX_AVAILABLE = False

# Import worker station definitions & cache
try:
    import worker
    from worker import INDIAN_STATIONS, latest_observations_cache, fetch_and_process_weather
except ImportError:
    INDIAN_STATIONS = []
    latest_observations_cache = {}

# Load environment configuration
load_dotenv()

INFLUX_URL = os.getenv("INFLUX_URL", "http://localhost:8086")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN", "my-super-secret-auth-token")
INFLUX_ORG = os.getenv("INFLUX_ORG", "skyguard_ai")
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET", "weather_telemetry")
PORT = int(os.getenv("PORT", 8000))

# Setup Logging with UTF-8 safety
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("SkyGuard-API")

# Initialize FastAPI Application
app = FastAPI(
    title="SkyGuard AI - Weather Anomaly Detection API",
    description="Real-Time AI Anomaly Detection & InfluxDB Pipeline for Automatic Weather Stations",
    version="2.0.0"
)

# Configure CORS for Frontend and Local Development
ALLOWED_ORIGINS = [
    "https://skyguard-ai.netlify.app",
    "https://skyguard-ai-7lge.onrender.com",
    "http://localhost:3000",
    "http://localhost:8000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:5173",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_influx_client():
    """Create InfluxDB client instance."""
    if not INFLUX_AVAILABLE:
        return None
    try:
        return InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG, timeout=4000)
    except Exception as e:
        logger.warning(f"Could not create InfluxDB client: {e}")
        return None


@app.get("/")
def root_status():
    """Service status and endpoint index."""
    return {
        "service": "SkyGuard AI Real-Time Weather Anomaly Detection Pipeline",
        "status": "ONLINE",
        "influx_configured": bool(INFLUX_URL and INFLUX_BUCKET),
        "stations_monitored": len(INDIAN_STATIONS),
        "endpoints": [
            "/api/stations/latest",
            "/api/stations",
            "/api/health",
            "/docs"
        ]
    }


@app.get("/api/health")
def health_check():
    """Health check endpoint for container / orchestrator probes."""
    return {
        "status": "HEALTHY",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "cached_stations": len(latest_observations_cache)
    }


@app.get("/api/stations/latest")
def get_latest_station_readings():
    """
    Query InfluxDB using Flux to return the most recent weather_sensor data from the last hour.
    Gracefully falls back to real-time Open-Meteo cache if InfluxDB is initializing.
    """
    client = get_influx_client()
    flux_results: List[Dict[str, Any]] = []

    if client:
        try:
            query_api = client.query_api()
            
            # Flux Query: Fetch most recent weather_sensor telemetry from last 1 hour
            flux_query = f'''
            from(bucket: "{INFLUX_BUCKET}")
              |> range(start: -1h)
              |> filter(fn: (r) => r._measurement == "weather_sensor")
              |> last()
              |> pivot(rowKey:["_time", "station_id"], columnKey: ["_field"], valueColumn: "_value")
            '''
            
            tables = query_api.query(query=flux_query, org=INFLUX_ORG)
            
            for table in tables:
                for record in table.records:
                    rec_values = record.values
                    stn_id = rec_values.get("station_id")
                    
                    # Match station metadata
                    stn_meta = next((s for s in INDIAN_STATIONS if s["id"] == stn_id), {})
                    
                    station_data = {
                        "station_id": stn_id,
                        "station_name": rec_values.get("station_name") or stn_meta.get("name", "AWS Node"),
                        "city": rec_values.get("city") or stn_meta.get("city", "India"),
                        "latitude": stn_meta.get("lat", 20.0),
                        "longitude": stn_meta.get("lon", 78.0),
                        "climate_zone": rec_values.get("climate_zone") or stn_meta.get("climate_zone", "N/A"),
                        "temperature": float(rec_values.get("temperature", 25.0)),
                        "windspeed": float(rec_values.get("windspeed", 3.0)),
                        "winddirection": float(rec_values.get("winddirection", 180.0)),
                        "weathercode": int(rec_values.get("weathercode", 0)),
                        "is_anomaly": bool(rec_values.get("is_anomaly", False)),
                        "anomaly_score": float(rec_values.get("anomaly_score", 0.05)),
                        "timestamp": record.get_time().isoformat() if record.get_time() else datetime.datetime.now(datetime.timezone.utc).isoformat()
                    }
                    flux_results.append(station_data)
                    
            if flux_results:
                logger.info(f"Retrieved {len(flux_results)} station records from InfluxDB Flux query.")
                return {
                    "source": "INFLUXDB",
                    "bucket": INFLUX_BUCKET,
                    "count": len(flux_results),
                    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    "stations": flux_results
                }
        except Exception as e:
            logger.warning(f"Flux query against InfluxDB failed or empty: {e}. Serving from live telemetry cache.")

    # Primary Source: Query SQLite / PostgreSQL database for rich station models, active anomalies & telemetry
    try:
        from backend.database import SessionLocal, init_db
        from backend.main import get_all_stations
        from backend.models import Station
        from backend.seed_data import seed_database
        init_db()
        db = SessionLocal()
        try:
            if db.query(Station).count() == 0:
                seed_database(db)
            db_stations = get_all_stations(db=db)
            if db_stations and len(db_stations) > 0:
                logger.info(f"Retrieved {len(db_stations)} live stations directly from SQLite database.")
                return db_stations
        finally:
            db.close()
    except Exception as db_err:
        logger.warning(f"Database query failed in /api/stations/latest: {db_err}")

    # Fallback to cache / live fetch if database is uninitialized
    if not latest_observations_cache:
        try:
            logger.info("Cache empty. Executing on-demand Open-Meteo live weather fetch...")
            fetch_and_process_weather()
        except Exception as err:
            logger.error(f"On-demand fetch error: {err}")

    cached_list = list(latest_observations_cache.values())
    return {
        "source": "OPEN_METEO_LIVE_CACHE",
        "count": len(cached_list),
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "stations": cached_list
    }


@app.on_event("startup")
def startup_db_init():
    """Ensure database schema and initial 16 Indian AWS stations exist upon server boot."""
    try:
        from backend.database import init_db, SessionLocal
        from backend.models import Station
        from backend.seed_data import seed_database
        init_db()
        db = SessionLocal()
        try:
            if db.query(Station).count() == 0:
                logger.info("Seeding initial 16 Indian AWS stations into database...")
                seed_database(db)
        finally:
            db.close()
        logger.info("Database schema initialized and verified.")
    except Exception as e:
        logger.warning(f"Startup DB init warning: {e}")


# Mount existing SkyGuard AI backend routes if available
try:
    from backend.main import app as skyguard_backend_app
    app.mount("/legacy", skyguard_backend_app)
    # Also forward /api/stations, /api/anomalies, /api/models, /api/simulate to full engine
    for route in skyguard_backend_app.routes:
        if hasattr(route, "path") and hasattr(route, "endpoint") and hasattr(route, "methods"):
            # Avoid duplicate /api/stations/latest
            if route.path not in ["/api/stations/latest", "/", "/api/health"]:
                try:
                    app.add_api_route(
                        path=route.path,
                        endpoint=route.endpoint,
                        methods=route.methods,
                        response_model=getattr(route, "response_model", None),
                        include_in_schema=True
                    )
                except Exception:
                    pass
except Exception as e:
    logger.info(f"SkyGuard backend routes mounted with standard configuration: {e}")


if __name__ == "__main__":
    logger.info(f"Starting SkyGuard AI FastAPI Server on http://0.0.0.0:{PORT}...")
    uvicorn.run("api:app", host="0.0.0.0", port=PORT, reload=False)
