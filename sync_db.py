from backend.database import SessionLocal
from backend.models import AnomalyEvent, Station

def sync_active_db():
    db = SessionLocal()
    # Reset all to RESOLVED first
    db.query(AnomalyEvent).update({AnomalyEvent.status: "RESOLVED"})
    
    # Activate 3 anomalies for AWS-IND-01, AWS-IND-02, AWS-IND-04
    for sid in ["AWS-IND-01", "AWS-IND-02", "AWS-IND-04"]:
        a = db.query(AnomalyEvent).filter(AnomalyEvent.station_id == sid).order_by(AnomalyEvent.timestamp.desc()).first()
        if a:
            a.status = "DETECTED"
            a.severity = "CRITICAL"
    db.commit()
    active_cnt = db.query(AnomalyEvent).filter(AnomalyEvent.status == "DETECTED").count()
    crit_cnt = db.query(AnomalyEvent).filter(AnomalyEvent.status == "DETECTED", AnomalyEvent.severity == "CRITICAL").count()
    print(f"Database Synced: {active_cnt} active DETECTED anomalies ({crit_cnt} CRITICAL).")

if __name__ == "__main__":
    sync_active_db()
