from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from typing import List

# --- Adjust these imports to match your project structure ---
from .. import models, database, schemas
from ..auth.rbac import get_current_user
from ..correlation_service import get_ip_reputation # <-- Import the reputation function

router = APIRouter()

@router.get("/api/threats")
def get_threat_logs(
    response: Response,
    user: models.User = Depends(get_current_user),
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
    
    # --- NEW: Add IP reputation score to each log ---
    response_data = []
    for log in logs:
        # Convert the SQLAlchemy object to a dictionary
        log_data = schemas.ThreatLog.from_orm(log).dict()
        # Fetch the reputation score and add it to the dictionary
        log_data['ip_reputation_score'] = get_ip_reputation(log.ip)
        response_data.append(log_data)
        
    return response_data
