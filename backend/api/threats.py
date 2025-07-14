from fastapi import APIRouter, Depends, Response, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .. import models, database, schemas
from ..auth.rbac import get_current_user # This provides the basic auth user

router = APIRouter()

@router.get("/api/threats", response_model=List[schemas.ThreatLog])
def get_threat_logs(
    response: Response,
    # This dependency gets the authenticated user's basic info (like their ID)
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    
    response.headers["Cache-Control"] = "no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    # --- THIS IS THE FIX ---
    # Use the ID from the auth user to get the full user object from the database
    db_user = db.query(models.User).filter(models.User.id == current_user.id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Now, use the tenant_id from the full database user object
    logs = (
        db.query(models.ThreatLog)
        .filter(models.ThreatLog.tenant_id == db_user.tenant_id)
        .order_by(models.ThreatLog.timestamp.desc())
        .limit(100)
        .all()
    )
    
    return logs
