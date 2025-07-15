from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
import logging
from datetime import datetime, timezone

from backend import models, database, schemas
from backend.app.websocket.threats import manager

logger = logging.getLogger(__name__)

class ThreatCreate(BaseModel):
    ip: str
    threat: str
    source: str
    tenant_id: int

router = APIRouter()

@router.post("/api/log_threat", response_model=schemas.ThreatLog, status_code=201)
async def log_threat_endpoint(request: Request, threat: ThreatCreate, db: Session = Depends(database.get_db)):

    # --- TEMPORARY HARDCODED VALUES FOR DEBUGGING ---
    predicted_severity = "DEBUG_SUCCESS"
    ip_score = 999
    cve_id = "CVE-TEST-OK"

    print(f"--- DEBUGGING DEPLOYMENT: Saving threat with hardcoded severity: {predicted_severity} ---")

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
