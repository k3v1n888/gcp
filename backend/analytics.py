# backend/analytics.py

from fastapi import APIRouter, Depends
from sqlalchemy import func
from backend.models import SessionLocal, ThreatLog, User
# This line is corrected to use a dot instead of a slash
from backend.auth.rbac import get_current_user

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/api/analytics/summary")
def analytics_summary(db: SessionLocal = Depends(get_db), current_user: User = Depends(get_current_user)):
    tenant_id = current_user.tenant_id

    total = db.query(func.count(ThreatLog.id)).filter(ThreatLog.tenant_id == tenant_id).scalar()

    threats_by_type = db.query(ThreatLog.threat, func.count(ThreatLog.id))\
        .filter(ThreatLog.tenant_id == tenant_id)\
        .group_by(ThreatLog.threat).all()

    threats_by_source = db.query(ThreatLog.source, func.count(ThreatLog.id))\
        .filter(ThreatLog.tenant_id == tenant_id)\
        .group_by(ThreatLog.source).all()

    return {
        "total": total,
        "by_type": dict(threats_by_type),
        "by_source": dict(threats_by_source)
    }
