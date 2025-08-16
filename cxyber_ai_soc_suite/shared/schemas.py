"""
Copyright (c) 2025 Kevin Zachary
All rights reserved.

This software and associated documentation files (the "Software") are the 
exclusive property of Kevin Zachary. Unauthorized copying, distribution, 
modification, or use of this software is strictly prohibited.

For licensing inquiries, contact: kevin@zachary.com
"""

# Author: Kevin Zachary
# Copyright: Sentient Spire


from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

class CanonicalEvent(BaseModel):
    timestamp: str
    vendor: Optional[str] = None
    product: Optional[str] = None
    event_type: str
    severity: Optional[str] = None
    src_ip: Optional[str] = None
    dst_ip: Optional[str] = None
    src_port: Optional[int] = None
    dst_port: Optional[int] = None
    http_method: Optional[str] = None
    url: Optional[str] = None
    user: Optional[str] = None
    host: Optional[str] = None
    bytes_in: Optional[int] = None
    bytes_out: Optional[int] = None
    process_name: Optional[str] = None
    file_hash: Optional[str] = None
    rule_name: Optional[str] = None
    rule_id: Optional[str] = None
    raw: Dict[str, Any] = Field(default_factory=dict)

class FeatureVector(BaseModel):
    ip_reputation: Optional[int] = None
    cvss_score: Optional[float] = None
    criticality_score: Optional[float] = None
    mitre_tactics: List[str] = []
    asset_criticality: Optional[float] = None
    bytes_received: Optional[int] = None
    bytes_sent: Optional[int] = None
    is_anomaly_hint: Optional[int] = None
    source: Optional[str] = None
    extra: Dict[str, Any] = Field(default_factory=dict)

class ThreatScoreRequest(BaseModel):
    feature_vector: FeatureVector
    canonical_event: CanonicalEvent
    context: Dict[str, Any] = Field(default_factory=dict)

class ThreatScoreResponse(BaseModel):
    case_id: str
    severity: str
    confidence: float
    findings: List[str]
    explanations: Dict[str, Any]
    recommendations: List[str]

class PolicyRequest(BaseModel):
    case_id: str
    severity: str
    confidence: float
    business_context: Dict[str, Any] = Field(default_factory=dict)
    controls: Dict[str, Any] = Field(default_factory=dict)

class ActionItem(BaseModel):
    action: str
    target: Optional[str] = None
    type: Optional[str] = None
    value: Optional[str] = None
    channel: Optional[str] = None
    priority: Optional[str] = None
    system: Optional[str] = None
    template: Optional[str] = None
    approval: Optional[str] = None

class PolicyResponse(BaseModel):
    action_plan: List[ActionItem]
    rollbacks: List[ActionItem]
    explain: str
