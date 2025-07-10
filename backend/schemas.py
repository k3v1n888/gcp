# backend/schemas.py

from pydantic import BaseModel, ConfigDict
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

    model_config = ConfigDict(from_attributes=True)


# --- ADD THIS NEW CLASS ---
# This is the Pydantic model for the SystemSettings API responses
class SystemSettings(BaseModel):
    id: int
    alert_severity: str

    model_config = ConfigDict(from_attributes=True)
