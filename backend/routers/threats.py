# backend/routers/threats.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

# Adjust these imports to match your project structure
from .. import models, database

# This is the Pydantic model that defines the shape of the incoming JSON data
class ThreatCreate(BaseModel):
    ip: str
    threat: str
    source: str
    tenant_id: int

# Create a new router instance
router = APIRouter()

# Define the endpoint for logging a new threat
@router.post("/api/log_threat", response_model=models.ThreatLog, status_code=201)
def log_threat_endpoint(threat: ThreatCreate, db: Session = Depends(database.get_db)):
    """
    Receives new threat data, saves it to the database with a default
    severity, and returns the created record.
    """
    # We will add the ML prediction logic here in a later step.
    db_log = models.ThreatLog(**threat.dict(), severity="unknown")
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log
