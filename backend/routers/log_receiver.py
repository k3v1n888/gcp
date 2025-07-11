# backend/routers/log_receiver.py

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
import logging

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
    predictor = request.app.state.predictor

    try:
        predicted_severity = predictor.predict(
            threat=threat.threat,
            source=threat.source
        )
    except Exception as e:
        logger.error(f"Prediction failed, defaulting to 'unknown': {e}")
        predicted_severity = "unknown"

    # --- FINGERPRINT LOG ---
    # This message can ONLY be printed by the new code.
    print(f"--- ATOMIC SAVE LOGIC: Saving threat with predicted severity: {predicted_severity} ---")

    db_log = models.ThreatLog(
        **threat.dict(), 
        severity=predicted_severity
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)

    pydantic_log = schemas.ThreatLog.from_orm(db_log)
    await manager.broadcast_json(pydantic_log.dict())

    return db_log
