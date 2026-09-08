"""
Verification test for SIH Weather Anomaly Pipeline (Open-Meteo -> Isolation Forest -> InfluxDB/Cache -> FastAPI -> Frontend)
"""
import sys
from fastapi.testclient import TestClient
from api import app

def test_pipeline():
    client = TestClient(app)
    
    # 1. Test Root
    res_root = client.get("/")
    assert res_root.status_code == 200
    print("[PASS] Root Status Endpoint (200 OK):", res_root.json()["service"])
    
    # 2. Test Health
    res_health = client.get("/api/health")
    assert res_health.status_code == 200
    print("[PASS] Health Endpoint (200 OK):", res_health.json()["status"])
    
    # 3. Test /api/stations/latest
    res_latest = client.get("/api/stations/latest")
    assert res_latest.status_code == 200
    data = res_latest.json()
    stations = data.get("stations", [])
    
    print(f"[PASS] /api/stations/latest returned {len(stations)} stations (Source: {data.get('source')})")
    assert len(stations) == 16, f"Expected 16 stations, got {len(stations)}"
    
    print("\nSample Live Open-Meteo & Isolation Forest Anomaly Results:")
    for s in stations[:6]:
        status_tag = "ANOMALY" if s["is_anomaly"] else "NORMAL"
        print(f"  * {s['city']} ({s['station_id']}): {s['temperature']}°C, {s['windspeed']} km/h -> [{status_tag}] (Score: {s['anomaly_score']})")
    
    print("\nAll Real-Time Weather Pipeline Tests Passed Successfully!")

if __name__ == "__main__":
    test_pipeline()
