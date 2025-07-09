# backend/routers/log_receiver.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

# Adjust these imports to match your project structure
from .. import models, database
from ..ml.prediction import severity_predictor # We will use this later

class ThreatCreate(BaseModel):
    ip: str
    threat: str
    source: str
    tenant_id: int

router = APIRouter()

@router.post("/api/log_threat", response_model=models.ThreatLog, status_code=201)
def log_threat_endpoint(threat: ThreatCreate, db: Session = Depends(database.get_db)):
    # This is the logic that will eventually use the ML model
    db_log = models.ThreatLog(**threat.dict(), severity="unknown")
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log
