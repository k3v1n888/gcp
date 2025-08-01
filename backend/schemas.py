# backend/schemas.py
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional, Dict, Any

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

class SecurityIncident(BaseModel):
    id: int
    title: str
    status: str
    severity: str
    start_time: datetime
    end_time: datetime
    threat_logs: List[ThreatLog] = []
    model_config = ConfigDict(from_attributes=True)

# --- NEW: Schema for the Explainable AI (XAI) response from your custom model ---
class XAIExplanation(BaseModel):
    base_value: float
    shap_values: List[List[float]]
    features: Dict[str, Any]

class ThreatDetailResponse(ThreatLog):
    recommendations: Optional[Recommendation] = None
    correlation: Optional[CorrelatedThreat] = None
    anomaly_features: Optional[AnomalyFeatures] = None
    soar_actions: List[AutomationLog] = []
    misp_summary: Optional[str] = None
    timeline_threats: List[ThreatLog] = []

    # --- ADD THIS NEW FIELD ---
    xai_explanation: Optional[XAIExplanation] = None