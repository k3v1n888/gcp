from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.auth.rbac import require_role
from backend.models import SessionLocal, SystemSettings

router = APIRouter()

@router.get("/api/admin/settings")
def get_settings(user=Depends(require_role(["admin"])), db: Session = Depends(SessionLocal)):
    settings = db.query(SystemSettings).first()
    if not settings:
        settings = SystemSettings(alert_severity="critical")
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return {"alert_severity": settings.alert_severity}

@router.post("/api/admin/settings")
def update_settings(payload: dict, user=Depends(require_role(["admin"])), db: Session = Depends(SessionLocal)):
    alert_severity = payload.get("alert_severity")
    if alert_severity not in ["low", "medium", "high", "critical"]:
        raise HTTPException(status_code=400, detail="Invalid severity level")
    settings = db.query(SystemSettings).first()
    if not settings:
        settings = SystemSettings(alert_severity=alert_severity)
        db.add(settings)
    else:
        settings.alert_severity = alert_severity
    db.commit()
    return {"alert_severity": settings.alert_severity}