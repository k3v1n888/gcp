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


import uuid
from fastapi import FastAPI, Body
from shared.schemas import ThreatScoreRequest, ThreatScoreResponse
from model.loader import predict_severity

app = FastAPI(title="Threat Service", version="0.1.0")

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/threat/score", response_model=ThreatScoreResponse)
def score(req: ThreatScoreRequest = Body(...)):
    sev, conf, findings, shap = predict_severity(req.feature_vector.model_dump(), req.canonical_event.model_dump(), req.context)
    recs = []
    if "SQLi" in findings or (sev in ["high","critical"] and conf >= 0.7):
        recs = ["Block source IP", "Patch related CVEs", "Add WAF rule"]
    case_id = "c-" + str(uuid.uuid4())
    return ThreatScoreResponse(
        case_id=case_id,
        severity=sev,
        confidence=conf,
        findings=findings,
        explanations={"shap": shap},
        recommendations=recs
    )
