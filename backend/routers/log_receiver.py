from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
import logging

from backend import models, database, schemas
# --- 1. Import the WebSocket manager ---
from backend.app.websocket.threats import manager

logger = logging.getLogger(__name__)

class ThreatCreate(BaseModel):
    ip: str
    threat: str
    source: str
    tenant_id: int

router = APIRouter()

# --- 2. Make the function async ---
@router.post("/api/log_threat", response_model=schemas.ThreatLog, status_code=201)
async def log_threat_endpoint(request: Request, threat: ThreatCreate, db: Session = Depends(database.get_db)):
    # ... (code to create initial log and run prediction is the same) ...
    db_log = models.ThreatLog(**threat.dict(), severity="unknown")
    db.add(db_log)
    db.commit()
    db.refresh(db_log)

    predictor = request.app.state.predictor
    predicted_severity = predictor.predict(
        threat=db_log.threat,
        source=db_log.source
    )

    db_log.severity = predicted_severity
    db.commit()
    db.refresh(db_log)
    
    # --- 3. Broadcast the FINAL result ---
    # Convert the SQLAlchemy object to a Pydantic model, then to a dict
    pydantic_log = schemas.ThreatLog.from_orm(db_log)
    await manager.broadcast_json(pydantic_log.dict())
    
    return db_log
