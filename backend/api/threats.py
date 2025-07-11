from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from typing import List

# --- 1. Import necessary modules ---
# Adjust these imports to match your project structure
from .. import models, database, schemas
from ..auth.rbac import get_current_user

router = APIRouter()

# --- 2. Define the endpoint with the corrected signature and response model ---
@router.get("/api/threats", response_model=List[schemas.ThreatLog])
def get_threat_logs(
    response: Response,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    
    # --- 3. Add Cache-Control headers to prevent caching ---
    response.headers["Cache-Control"] = "no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    # Query the database for the logs
    logs = db.query(models.ThreatLog)\
             .filter(models.ThreatLog.tenant_id == user.tenant_id)\
             .order_by(models.ThreatLog.timestamp.desc())\
             .limit(1
