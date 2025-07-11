from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from typing import List

# Adjust these imports to match your project structure
from .. import models, database, schemas
from ..auth.rbac import get_current_user
from ..models import User # <-- Import User directly

router = APIRouter()

@router.get("/api/threats", response_model=List[schemas.ThreatLog])
def get_threat_logs(
    response: Response,
    # --- THIS IS THE CORRECTED LINE ---
    # Use a string "User" as a forward reference to avoid the NameError
    user: "User" = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    
    # Add Cache-Control headers to prevent caching
    response.headers["Cache-Control"] = "no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    logs = (
        db.query(models.ThreatLog)
        .filter(models.ThreatLog.tenant_id == user.tenant_id)
        .order_by(models.ThreatLog.timestamp.desc())
        .limit(100)
        .all()
    )
    
    return logs
