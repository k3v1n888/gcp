from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
import logging

# Use absolute imports to match your project structure
from backend import models, database, schemas

# Configure logging
logger = logging.getLogger(__name__)

# Defines the expected JSON data for incoming threats
class ThreatCreate(BaseModel):
    ip: str
    threat: str
    source: str
    tenant_id: int

router = APIRouter()

@router.post("/api/log_threat", response_model=schemas.ThreatLog, status_code=201)
def log_threat_endpoint(request: Request, threat: ThreatCreate, db: Session = Depends(database.get_db)):
    """
    Receives a new threat, saves it, uses the ML model to predict severity,
    updates the record, and returns the final result.
    """
    # 1. Create the initial log record with a default severity
    db_log = models.ThreatLog(**threat.dict(), severity="unknown")
    db.add(db_log)
    db.commit()
    db.refresh(db_log)

    # 2. Get the predictor instance from the application's state
    predictor = request.app.state.predictor

    # 3. Use the ML model to predict the actual severity
    predicted_severity = predictor.predict(
        threat=db_log.threat,
        source=db_log.source
    )
    
    # 4. Update the log record with the model's prediction
    db_log.severity = predicted_severity
    db.commit()
    db.refresh(db_log)
    
    # 5. Return the final, updated log record
    return db_log
