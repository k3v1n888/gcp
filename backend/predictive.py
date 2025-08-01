# backend/predictive.py

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter()

class ThreatSummary(BaseModel):
    source: str
    severity: float
    description: str

class PredictionResponse(BaseModel):
    correlated_score: float
    threats: List[ThreatSummary]

@router.get("/", response_model=PredictionResponse)
async def get_prediction():
    """
    Stub: Correlate threats from multiple sources and return a prediction.
    Replace with real AI/model logic in production.
    """
    sample_threats = [
        ThreatSummary(source="SIEM", severity=7.5, description="Suspicious login spike"),
        ThreatSummary(source="XDR", severity=5.2, description="Unusual process execution"),
        ThreatSummary(source="ASM", severity=6.0, description="Port scan detected"),
        ThreatSummary(source="Network", severity=4.3, description="Data exfiltration pattern"),
    ]
    correlated_score = 8.2  # Stubbed “AI result”

    return PredictionResponse(
        correlated_score=correlated_score,
        threats=sample_threats
    )