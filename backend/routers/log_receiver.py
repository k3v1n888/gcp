# backend/routers/log_receiver.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
import logging # <-- Import the logging library

from backend import models, database, schemas
from backend.ml.prediction import severity_predictor

# --- Configure logging ---
logger = logging.getLogger(__name__)

class ThreatCreate(BaseModel):
    ip: str
    threat: str
    source: str
    tenant_id: int

router = APIRouter()

@router.post("/api/log_threat", response_model=schemas.ThreatLog, status_code=201)
def log_threat_endpoint(threat: ThreatCreate, db: Session = Depends(database.get_db)):
    # Create the initial log record
    db_log = models.ThreatLog(**threat.dict(), severity="unknown")
    db.add(db_log)
    db.commit()
    db.refresh(db_log)

    # --- NEW: Use a try/except block for the prediction ---
    try:
        # Use the ML model to predict the severity
        predicted_severity = severity_predictor.predict(
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

    # Return the log record (it will have "unknown" severity if prediction failed)
    return db_log
