from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional

class User(BaseModel):
    id: int
    username: str
    email: str
    role: str
    tenant_id: int
    model_config = ConfigDict(from_attributes=True)

class ThreatLog(BaseModel):
    id: int
    ip: Optional[str] = None
    threat: Optional[str] = None
    source: Optional[str] = None
    severity: str
    timestamp: datetime
    tenant_id: int
    ip_reputation_score: Optional[int] = None
    cve_id: Optional[str] = None
    is_anomaly: bool = False
    model_config = ConfigDict(from_attributes=True)

class SystemSettings(BaseModel):
    id: int
    alert_severity: str
    model_config = ConfigDict(from_attributes=True)

# --- NEW: Schema for the user invitation request ---
class UserInviteRequest(BaseModel):
    email: str
    role: str

class Recommendation(BaseModel):
    explanation: str
    impact: str
    mitigation: List[str]

class CorrelatedThreat(BaseModel):
    title: str
    summary: Optional[str] = None
    cve_id: Optional[str] = None
    risk_score: int
    model_config = ConfigDict(from_attributes=True)
    
class AnomalyFeatures(BaseModel):
    text_feature: str
    ip_reputation_score: int
    has_cve: int

class AutomationLog(BaseModel):
    action_type: str
    timestamp: datetime
    details: str
    model_config = ConfigDict(from_attributes=True)

class ThreatDetailResponse(ThreatLog):
    recommendations: Optional[Recommendation] = None
    correlation: Optional[CorrelatedThreat] = None
    anomaly_features: Optional[AnomalyFeatures] = None
    soar_actions: List[AutomationLog] = []
