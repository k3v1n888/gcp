from fastapi import APIRouter, Depends, Response, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .. import models, database, schemas
from ..auth.rbac import get_current_user
from ..correlation_service import generate_threat_remediation_plan

router = APIRouter()

@router.get("/api/threats", response_model=List[schemas.ThreatLog])
def get_threat_logs(
    response: Response,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
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

# --- NEW: Endpoint for a single threat's details ---
@router.get("/api/threats/{threat_id}", response_model=schemas.ThreatDetailResponse)
def get_threat_detail(
    threat_id: int,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    threat_log = db.query(models.ThreatLog).filter(
        models.ThreatLog.id == threat_id,
        models.ThreatLog.tenant_id == user.tenant_id
    ).first()

    if not threat_log:
        raise HTTPException(status_code=404, detail="Threat log not found")

    recommendations = generate_threat_remediation_plan(threat_log)

    # Convert the SQLAlchemy object to a dictionary for modification
    response_data = schemas.ThreatLog.from_orm(threat_log).dict()
    # Add the recommendations
    response_data['recommendations'] = recommendations
    
    return response_data
