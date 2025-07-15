from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

# --- Adjust imports to match your project structure ---
from . import database, models, schemas
from .auth.rbac import get_current_user

router = APIRouter()

@router.get("/api/analytics/summary")
def get_analytics_summary(
    # --- CHANGE: Use the Pydantic schema for the user dependency ---
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    
    # The 'current_user' object now reliably has an 'id' and 'tenant_id'
    # because it's validated by the schemas.User Pydantic model.
    # We no longer need a second database query to get the user.

    # Query for threats by type
    by_type = (
        db.query(models.ThreatLog.threat, func.count(models.ThreatLog.threat))
        .filter(models.ThreatLog.tenant_id == current_user.tenant_id)
        .group_by(models.ThreatLog.threat)
        .all()
    )

    # Query for threats by source
    by_source = (
        db.query(models.ThreatLog.source, func.count(models.ThreatLog.source))
        .filter(models.ThreatLog.tenant_id == current_user.tenant_id)
        .group_by(models.ThreatLog.source)
        .all()
    )

    total = db.query(models.ThreatLog).filter(models.ThreatLog.tenant_id == current_user.tenant_id).count()

    return {
        "total": total,
        "by_type": dict(by_type),
        "by_source": dict(by_source),
    }
