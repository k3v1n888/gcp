# backend/schemas.py

from pydantic import BaseModel, ConfigDict
from datetime import datetime

# This is the Pydantic model for API responses
class ThreatLog(BaseModel):
    id: int
    ip: str | None = None
    threat: str | None = None
    source: str | None = None
    severity: str
    timestamp: datetime
    tenant_id: int

    # This special configuration tells Pydantic to read the data
    # from the SQLAlchemy object's attributes.
    model_config = ConfigDict(from_attributes=True)
