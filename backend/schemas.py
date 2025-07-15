# backend/schemas.py

from pydantic import BaseModel
from datetime import datetime

class User(BaseModel):
    id: int
    username: str
    email: str
    role: str
    tenant_id: int

    class Config:
        orm_mode = True

class ThreatLog(BaseModel):
    id: int
    ip: str | None = None
    threat: str | None = None
    source: str | None = None
    severity: str
    timestamp: datetime
    tenant_id: int
    ip_reputation_score: int | None = None
    
    # --- ADD THIS NEW FIELD ---
    cve_id: str | None = None

    class Config:
        orm_mode = True

class SystemSettings(BaseModel):
    id: int
    alert_severity: str

    class Config:
        orm_mode = True
