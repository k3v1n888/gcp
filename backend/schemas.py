# backend/schemas.py

from pydantic import BaseModel, ConfigDict
from datetime import datetime

class ThreatLog(BaseModel):
    id: int
    ip: str | None = None
    threat: str | None = None
    source: str | None = None
    severity: str
    timestamp: datetime
    tenant_id: int
    
    # --- ADD THIS NEW FIELD ---
    ip_reputation_score: int | None = None

    model_config = ConfigDict(from_attributes=True)

class SystemSettings(BaseModel):
    id: int
    alert_severity: str

    model_config = ConfigDict(from_attributes=True)
