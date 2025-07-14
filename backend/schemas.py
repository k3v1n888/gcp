# backend/schemas.py

# --- CHANGE: Remove ConfigDict from the import ---
from pydantic import BaseModel
from datetime import datetime

# This is the Pydantic model for the ThreatLog API responses
class ThreatLog(BaseModel):
    id: int
    ip: str | None = None
    threat: str | None = None
    source: str | None = None
    severity: str
    timestamp: datetime
    tenant_id: int
    ip_reputation_score: int | None = None

    # --- CHANGE: Use Pydantic V1 Config style ---
    class Config:
        orm_mode = True


# This is the Pydantic model for the SystemSettings API responses
class SystemSettings(BaseModel):
    id: int
    alert_severity: str

    # --- CHANGE: Use Pydantic V1 Config style ---
    class Config:
        orm_mode = True
