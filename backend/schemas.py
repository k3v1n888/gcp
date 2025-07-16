# backend/schemas.py

from pydantic import BaseModel, ConfigDict # <-- 1. Import ConfigDict
from typing import List
from datetime import datetime

class User(BaseModel):
    id: int
    username: str
    email: str
    role: str
    tenant_id: int

    # --- 2. Use the new model_config syntax ---
    model_config = ConfigDict(from_attributes=True)

class ThreatLog(BaseModel):
    id: int
    ip: str | None = None
    threat: str | None = None
    source: str | None = None
    severity: str
    timestamp: datetime
    tenant_id: int
    ip_reputation_score: int | None = None
    cve_id: str | None = None

    # --- 2. Use the new model_config syntax ---
    model_config = ConfigDict(from_attributes=True)

class SystemSettings(BaseModel):
    id: int
    alert_severity: str

    # --- 2. Use the new model_config syntax ---
    model_config = ConfigDict(from_attributes=True)

# --- NEW: Schema for the AI-generated recommendations ---
class Recommendation(BaseModel):
    explanation: str
    impact: str
    mitigation: List[str]

# --- NEW: Schema for the full threat detail response ---
class ThreatDetailResponse(ThreatLog):
    recommendations: Recommendation | None = None
