from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

# --- Adjust imports to match your project structure ---
from . import database, models, schemas
from .auth.rbac import get_current_user

router = APIRouter()

@router.get("/api/analytics/summary")
def get_analytics_summary(
    # --- Use a string forward reference for "User" ---
    current_user: "schemas.User" = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    # --- Fetch the full user object to get the tenant_id ---
    db_user = db.query(models.User).filter(models.User.id == current_user.id).first()
    if not db_user:
        return {"total": 0, "by_type": {}, "by_source": {}}

    # Query for threats by type
    by_type = (
        db.query(models.ThreatLog.threat, func.count(models.ThreatLog.threat))
        .filter(models.ThreatLog.tenant_id == db_user.tenant_id)
        .group_by(models.ThreatLog.threat)
        .all()
    )

    # Query for threats by source
    by_source = (
        db.query(models.ThreatLog.source, func.count(models.ThreatLog.source))
        .filter(models.ThreatLog.tenant_id == db_user.tenant_id)
        .group_by(models.ThreatLog.source)
        .all()
    )

    total = db.query(models.ThreatLog).filter(models.ThreatLog.tenant_id == db_user.tenant_id).count()

    return {
        "total": total,
        "by_type": dict(by_type),
        "by_source": dict(by_source),
    }
