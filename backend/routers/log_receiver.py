from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
import logging
from datetime import datetime, timezone

from backend import models, database, schemas
from backend.app.websocket.threats import manager
from backend.correlation_service import get_ip_reputation, find_cve_for_threat

logger = logging.getLogger(__name__)

class ThreatCreate(BaseModel):
    ip: str
    threat: str
    source: str
    tenant_id: int

router = APIRouter()

# --- CHANGE: Remove the response_model for now to bypass validation ---
@router.post("/api/log_threat", status_code=201)
async def log_threat_endpoint(request: Request, threat: ThreatCreate, db: Session = Depends(database.get_db)):
    predictor = request.app.state.predictor
    
    ip_score = get_ip_reputation(threat.ip)
    cve_id = find_cve_for_threat(threat.threat)
    
    predicted_severity = predictor.predict(
        threat=threat.threat,
        source=threat.source,
        ip_reputation_score=ip_score,
        cve_id=cve_id
    )

    db_log = models.ThreatLog(
        **threat.dict(), 
        severity=predicted_severity,
        ip_reputation_score=ip_score,
        cve_id=cve_id,
        timestamp=datetime.now(timezone.utc)
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    
    # --- CHANGE: Manually build the response dictionary ---
    # This gives us full control over the data being sent.
    response_data = {
        "id": db_log.id,
        "ip": db_log.ip,
        "threat": db_log.threat,
        "source": db_log.source,
        "severity": db_log.severity,
        "timestamp": db_log.timestamp.isoformat(), # Use .isoformat() for JSON
        "tenant_id": db_log.tenant_id,
        "ip_reputation_score": db_log.ip_reputation_score,
        "cve_id": db_log.cve_id,
    }
    
    # Broadcast the clean dictionary
    await manager.broadcast_json(response_data)
    
    # Return the clean dictionary
    return response_data
