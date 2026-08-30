import sys
import os
import uvicorn

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.database import init_db, SessionLocal
from backend.seed_data import seed_database


def main():
    print("=" * 70)
    print("  AWS Intelligent AI/ML Anomaly Detection System")
    print("  Automatic Weather Stations Telemetry Quality Control Console")
    print("=" * 70)
    
    # 1. Initialize SQLite database & Seed baseline if empty
    print("\n[1/2] Verifying database and ML baseline...")
    init_db()
    db = SessionLocal()
    try:
        seed_database(db, hours_of_history=24, step_minutes=30)
    finally:
        db.close()

    # 2. Start FastAPI Server
    port = 8000
    host = "127.0.0.1"
    print(f"\n[2/2] Launching Web Operations Console at: http://{host}:{port}")
    print("  -> Interactive Dashboard: http://localhost:8000")
    print("  -> API OpenAPI Docs:     http://localhost:8000/docs\n")
    print("Press Ctrl+C to terminate the server.\n" + "=" * 70 + "\n")

    uvicorn.run(
        "backend.main:app",
        host=host,
        port=port,
        log_level="info"
    )


if __name__ == "__main__":
    main()
