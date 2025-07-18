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
    # ... (this function is correct and remains the same) ...
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

    correlated_threat = db.query(models.CorrelatedThreat).filter(
        models.CorrelatedThreat.title == f"Attack Pattern: {threat_log.threat}",
        models.CorrelatedThreat.tenant_id == user.tenant_id
    ).first()

    recommendations_dict = generate_threat_remediation_plan(threat_log)

    # Convert the base SQLAlchemy object to a Pydantic model
    response_data = schemas.ThreatDetailResponse.from_orm(threat_log)
    response_data.correlation = correlated_threat
    
    # --- THIS IS THE FIX ---
    # Create an instance of the Recommendation schema from the dictionary
    if recommendations_dict:
        response_data.recommendations = schemas.Recommendation(**recommendations_dict)
    
    if threat_log.is_anomaly:
        response_data.anomaly_features = schemas.AnomalyFeatures(
            text_feature=f"{threat_log.threat} {threat_log.source}",
            ip_reputation_score=threat_log.ip_reputation_score or 0,
            has_cve=1 if threat_log.cve_id else 0
        )
    
    return response_data
