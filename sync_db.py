from backend.database import SessionLocal
from backend.models import AnomalyEvent, Station

def sync_active_db():
    db = SessionLocal()
    # Reset all to RESOLVED first
    db.query(AnomalyEvent).update({AnomalyEvent.status: "RESOLVED"})
    
    # Activate anomalies for Delhi, Mumbai, Kolkata across code & ID mappings
    target_ids = ["AWS-IND-01", "AWS-IND-02", "AWS-IND-04", "AWS-IND-03", "AWS-IND-06", "AWS-IND-13"]
    for sid in target_ids:
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
