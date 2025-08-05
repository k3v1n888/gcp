from pydantic import BaseModel, ConfigDict, Field, validator
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
    cvss_score: Optional[float] = 0.0
    criticality_score: Optional[float] = 0.0
    ioc_risk_score: Optional[float] = 0.0
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

# --- THIS IS THE FIX ---
# Update the shap_values to expect a 3D list (List[List[List[float]]])
class XAIExplanation(BaseModel):
    base_value: float
    shap_values: List[List[List[float]]]
    features: Dict[str, Any]

class ThreatDetailResponse(ThreatLog):
    recommendations: Optional[Recommendation] = None
    correlation: Optional[CorrelatedThreat] = None
    anomaly_features: Optional[AnomalyFeatures] = None
    soar_actions: List[AutomationLog] = []
    misp_summary: Optional[str] = None
    timeline_threats: List[ThreatLog] = []
    xai_explanation: Optional[XAIExplanation] = None

class ThreatResponse(BaseModel):
    """Updated threat response model with proper timestamp handling"""
    id: int
    ip: str
    threat_type: str
    severity: str
    timestamp: Optional[datetime] = None  # Allow None values
    description: Optional[str] = None
    cve_id: Optional[str] = None
    cvss_score: Optional[float] = None
    source: Optional[str] = None
    tenant_id: int
    
    @validator('timestamp', pre=True)
    def validate_timestamp(cls, v):
        """Handle None timestamps and convert to datetime if needed"""
        if v is None:
            return datetime.utcnow()  # Use current time as fallback
        if isinstance(v, str):
            try:
                return datetime.fromisoformat(v.replace('Z', '+00:00'))
            except ValueError:
                return datetime.utcnow()
        return v
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

class ThreatListResponse(BaseModel):
    """Response model for threat list"""
    threats: List[ThreatResponse]
    total: int
    limit: int
    offset: int
    has_more: bool