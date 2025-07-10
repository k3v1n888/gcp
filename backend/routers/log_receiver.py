# backend/routers/log_receiver.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

# --- IMPORTS ADJUSTED TO MATCH YOUR PROJECT STRUCTURE ---
from backend import models, database, schemas
from backend.ml.prediction import severity_predictor

class ThreatCreate(BaseModel):
    ip: str
    threat: str
    source: str
    tenant_id: int

router = APIRouter()

@router.post("/api/log_threat", response_model=schemas.ThreatLog, status_code=201)
def log_threat_endpoint(threat: ThreatCreate, db: Session = Depends(database.get_db)):
    # Create the initial log with a default severity
    db_log = models.ThreatLog(**threat.dict(), severity="unknown")
    db.add(db_log)
    db.commit()
    db.refresh(db_log)

    # Use the ML model to predict the severity
    predicted_severity = severity_predictor.predict(
        threat=db_log.threat, 
        source=db_log.source
    )

    # Update the log with the model's prediction
    db_log.severity = predicted_severity
    db.commit()
    db.refresh(db_log)
    
    # Return the final, updated log record
    return db_log
