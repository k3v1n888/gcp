from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from . import database, models, schemas
from .auth.rbac import get_current_user

router = APIRouter()

@router.get("/api/analytics/summary")
def get_analytics_summary(
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    tenant_id = current_user.tenant_id

    # --- CHANGE: Query for only the TOP 5 threats by type ---
    by_type = (
        db.query(models.ThreatLog.threat, func.count(models.ThreatLog.threat).label('count'))
        .filter(models.ThreatLog.tenant_id == tenant_id)
        .group_by(models.ThreatLog.threat)
        .order_by(func.count(models.ThreatLog.threat).desc())
        .limit(5)
        .all()
    )

    # --- CHANGE: Query for only the TOP 7 threats by source ---
    by_source = (
        db.query(models.ThreatLog.source, func.count(models.ThreatLog.source).label('count'))
        .filter(models.ThreatLog.tenant_id == tenant_id)
        .group_by(models.ThreatLog.source)
        .order_by(func.count(models.ThreatLog.source).desc())
        .limit(7)
        .all()
    )

    total = db.query(models.ThreatLog).filter(models.ThreatLog.tenant_id == tenant_id).count()

    return {
        "total": total,
        "by_type": dict(by_type),
        "by_source": dict(by_source),
    }