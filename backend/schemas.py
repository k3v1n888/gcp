from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from pydantic import validator
import math

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
    shap_values: List[List[float]]
    features: Dict[str, Union[str, int, float]]
    
    @validator('base_value', pre=True)
    def validate_base_value(cls, v):
        if v is None or (isinstance(v, float) and (math.isnan(v) or not math.isfinite(v))):
            return 0.0
        return float(v)
    
    @validator('shap_values', pre=True)
    def validate_shap_values(cls, v):
        if not v:
            return [[]]
        
        # Ensure it's a nested list structure
        if isinstance(v, list):
            if len(v) > 0 and not isinstance(v[0], list):
                # Convert flat list to nested
                cleaned = []
                for val in v:
                    if val is None or (isinstance(val, float) and (math.isnan(val) or not math.isfinite(val))):
                        cleaned.append(0.0)
                    else:
                        cleaned.append(float(val))
                return [cleaned]
            else:
                # Already nested, just clean the values
                result = []
                for sublist in v:
                    if isinstance(sublist, list):
                        cleaned = []
                        for val in sublist:
                            if val is None or (isinstance(val, float) and (math.isnan(val) or not math.isfinite(val))):
                                cleaned.append(0.0)
                            else:
                                cleaned.append(float(val))
                        result.append(cleaned)
                    else:
                        result.append([float(sublist) if sublist is not None else 0.0])
                return result
        return [[]]
    
    @validator('features', pre=True)
    def validate_features(cls, v):
        if not v:
            return {}
        
        cleaned = {}
        for key, value in v.items():
            if isinstance(value, float) and (math.isnan(value) or not math.isfinite(value)):
                cleaned[key] = 0.0
            else:
                cleaned[key] = value
        return cleaned

class ThreatDetailResponse(ThreatLog):
    recommendations: Optional[Recommendation] = None
    correlation: Optional[CorrelatedThreat] = None
    anomaly_features: Optional[AnomalyFeatures] = None
    soar_actions: List[AutomationLog] = []
    misp_summary: Optional[str] = None
    timeline_threats: List[ThreatLog] = []
    xai_explanation: Optional[XAIExplanation] = None