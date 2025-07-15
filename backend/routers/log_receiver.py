from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
import logging
from datetime import datetime, timezone # <-- 1. Import datetime and timezone

from backend import models, database, schemas
from backend.app.websocket.threats import manager
from backend.correlation_service import get_ip_reputation

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
    
    predicted_severity = predictor.predict(
        threat=threat.threat,
        source=threat.source
    )
    ip_score = get_ip_reputation(threat.ip)

    # --- 2. Create the final log record with an explicit timestamp ---
    db_log = models.ThreatLog(
        **threat.dict(), 
        severity=predicted_severity,
        ip_reputation_score=ip_score,
        timestamp=datetime.now(timezone.utc) # <-- Set the timestamp here
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    
    pydantic_log = schemas.ThreatLog.from_orm(db_log)
    await manager.broadcast_json(pydantic_log.dict())
    
    return db_log
