# backend/routers/log_receiver.py

from fastapi import APIRouter, Depends, Request # <-- CHANGE: Import Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
import logging

# --- CHANGE: The import path for models, etc., has been corrected, and the direct predictor import is removed ---
from backend import models, database, schemas

# --- Configure logging ---
logger = logging.getLogger(__name__)

class ThreatCreate(BaseModel):
    ip: str
    threat: str
    source: str
    tenant_id: int

router = APIRouter()

# --- CHANGE: Add `request: Request` to the function signature ---
@router.post("/api/log_threat", response_model=schemas.ThreatLog, status_code=201)
def log_threat_endpoint(request: Request, threat: ThreatCreate, db: Session = Depends(database.get_db)):
    # Create the initial log record
    db_log = models.ThreatLog(**threat.dict(), severity="unknown")
    db.add(db_log)
    db.commit()
    db.refresh(db_log)

    try:
        # --- CHANGE: Get the predictor from the application state ---
        predictor = request.app.state.predictor
        
        # Use the ML model to predict the severity
        predicted_severity = predictor.predict(
            threat=db_log.threat,
            source=db_log.source
        )

        # Update the log record with the model's prediction
        db_log.severity = predicted_severity
        db.commit()
        db.refresh(db_log)
        
    except Exception as e:
        # If prediction fails, log the error but don't crash the request
        logger.error(f"Failed to predict severity for log ID {db_log.id}: {e}")

    # Return the log record
    return db_log
