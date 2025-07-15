from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
import logging
from datetime import datetime, timezone

from backend import models, database, schemas
from backend.app.websocket.threats import manager
# --- 1. Import the necessary enrichment functions ---
from backend.correlation_service import get_ip_reputation, find_cve_for_threat

logger = logging.getLogger(__name__)

class ThreatCreate(BaseModel):
    ip: str
    threat: str
    source: str
    tenant_id: int

router = APIRouter()

@router.post("/api/log_threat", response_model=schemas.ThreatLog, status_code=201)
async def log_threat_endpoint(request: Request, threat: ThreatCreate, db: Session = Depends(database.get_db)):
    predictor = request.app.state.predictor
    
    # --- 2. Gather all features before prediction ---
    ip_score = get_ip_reputation(threat.ip)
    cve_id = find_cve_for_threat(threat.threat)

    # --- 3. Call the predictor with ALL required arguments ---
    predicted_severity = predictor.predict(
        threat=threat.threat,
        source=threat.source,
        ip_reputation_score=ip_score,
        cve_id=cve_id
    )

    # Create the final log record with all data
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
    
    pydantic_log = schemas.ThreatLog.from_orm(db_log)
    await manager.broadcast_json(pydantic_log.dict())
    
    return db_log
