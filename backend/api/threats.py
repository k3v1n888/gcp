from fastapi import APIRouter, Depends
from backend.models import SessionLocal, ThreatLog
from backend.auth.rbac import get_current_user
from sqlalchemy.orm import Session

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/api/threats")
def get_threat_logs(user=Depends(get_current_user), db: Session = Depends(get_db)):
    logs = db.query(ThreatLog).filter(ThreatLog.tenant_id == user.tenant_id).order_by(ThreatLog.timestamp.desc()).limit(100).all()
    return [
        {
            "ip": log.ip,
            "threat": log.threat,
            "source": log.source,
            "timestamp": log.timestamp.isoformat()
        }
        for log in logs
    ]