from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from typing import List

from .. import models, database, schemas
from ..auth.rbac import get_current_user

router = APIRouter()

@router.get("/api/threats", response_model=List[schemas.ThreatLog])
def get_threat_logs(
    response: Response,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    
    # Add headers to prevent browser caching
    response.headers["Cache-Control"] = "no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    # This query is now simple and reliable, as all data is already in the database.
    logs = (
        db.query(models.ThreatLog)
        .filter(models.ThreatLog.tenant_id == user.tenant_id)
        .order_by(models.ThreatLog.timestamp.desc())
        .limit(100)
        .all()
    )
    
    return logs
