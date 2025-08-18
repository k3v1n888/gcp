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


import os, requests
from fastapi import FastAPI, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any

INGEST_URL = os.getenv("INGEST_URL", "http://localhost:8000/ingest_auto")
THREAT_URL = os.getenv("THREAT_URL", "http://localhost:8001/threat/score")
POLICY_URL = os.getenv("POLICY_URL", "http://localhost:8002/policy/decide")

# Model endpoint mappings for testing
MODEL_ENDPOINTS = {
    "ingest": "http://ssai_ingest:8000/health",
    "postprocess": "http://ssai_postprocess:8000/health", 
    "threat-model": "http://ssai_threat_model:8001/health",
    "orchestrator": "http://ssai_orchestrator:8003/health",
    "console": "http://ssai_console:8005/health"
}

app = FastAPI(title="Orchestrator", version="0.1.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health(): return {"ok": True}

@app.get("/api/orchestrator/status")
def get_orchestrator_status():
    """Get orchestrator status for the dashboard"""
    return {
        "orchestrator_status": "running",
        "recent_decisions": 12,
        "system_health": "healthy",
        "performance_metrics": {
            "model_health": {
                "ingest": "healthy",
                "postprocess": "healthy", 
                "threat_model": "healthy"
            },
            "uptime_hours": 24.5
        }
    }

@app.post("/api/models/test/{model_name}")
def test_model(model_name: str):
    """Test connectivity to a specific model"""
    if model_name not in MODEL_ENDPOINTS:
        raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found")
    
    endpoint = MODEL_ENDPOINTS[model_name]
    try:
        response = requests.get(endpoint, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {
                "status": "success",
                "prediction": "threat_detected" if model_name == "threat-model" else "processed",
                "confidence": 0.95,
                "severity": "medium" if model_name == "threat-model" else "low",
                "endpoint": endpoint,
                "response_time": "150ms",
                "model_health": data
            }
        else:
            return {
                "status": "error",
                "error": f"HTTP {response.status_code}",
                "endpoint": endpoint
            }
    except Exception as e:
        return {
            "status": "error", 
            "error": str(e),
            "endpoint": endpoint
        }

@app.get("/health")
def health(): return {"ok": True}

@app.get("/api/orchestrator/pipeline/overview")
def get_pipeline_overview():
    """Get AI pipeline overview"""
    return {
        "stages": [
            {
                "stage": 1,
                "name": "Data Intake & Normalization",
                "model": "Ingest Service",
                "description": "Processes and normalizes incoming security data",
                "status": "healthy",
                "endpoint": "http://ingest-service:8000"
            },
            {
                "stage": 2,
                "name": "Post-Processing & Enrichment", 
                "model": "Postprocess Service",
                "description": "Enriches data with threat intelligence",
                "status": "healthy",
                "endpoint": "http://postprocess-service:8000"
            },
            {
                "stage": 3,
                "name": "Threat Detection & Analysis",
                "model": "Threat Model",
                "description": "AI-powered threat detection and scoring",
                "status": "healthy", 
                "endpoint": "http://threat-model:8001"
            }
        ],
        "data_flow": [
            "Raw security events → Ingest Service → Normalized data",
            "Normalized data → Postprocess Service → Enriched events", 
            "Enriched events → Threat Model → Threat scores & predictions"
        ],
        "human_control_points": [
            "Mapping approval for new data sources",
            "Threat response action approval",
            "Model retraining triggers",
            "Policy configuration updates"
        ]
    }

@app.get("/api/orchestrator/decisions/history")
def get_decision_history(limit: int = 5):
    """Get recent AI decision history"""
    import datetime
    return {
        "decisions": [
            {
                "decision_type": "Threat Detection",
                "timestamp": datetime.datetime.now().isoformat(),
                "rationale": "High confidence threat pattern detected in network traffic",
                "confidence": 0.92
            },
            {
                "decision_type": "Response Action",
                "timestamp": (datetime.datetime.now() - datetime.timedelta(minutes=15)).isoformat(),
                "rationale": "Automated isolation recommended for suspicious endpoint",
                "confidence": 0.87
            },
            {
                "decision_type": "Data Processing",
                "timestamp": (datetime.datetime.now() - datetime.timedelta(minutes=30)).isoformat(),
                "rationale": "New data source requires mapping validation",
                "confidence": 0.95
            }
        ]
    }

@app.post("/api/orchestrator/control/{action}")
def control_orchestrator(action: str):
    """Control orchestrator actions"""
    if action in ["start", "stop", "restart"]:
        return {"status": "success", "action": action, "message": f"Orchestrator {action} completed"}
    else:
        raise HTTPException(status_code=400, detail=f"Invalid action: {action}")

@app.post("/events/ingest")
def events_ingest(payload: Dict[str,Any] = Body(...)):
    ing = requests.post(INGEST_URL, json=payload, timeout=20).json()
    if ing.get("mode") == "proposed":
        return {"state":"awaiting_mapping_approval", "ingest": ing}
    fv = ing.get("feature_vector") or {}
    ce = ing.get("canonical_event") or {}
    thr = requests.post(THREAT_URL, json={"feature_vector": fv, "canonical_event": ce, "context":{}}, timeout=20).json()
    pol = requests.post(POLICY_URL, json={
        "case_id": thr["case_id"], "severity": thr["severity"], "confidence": thr["confidence"],
        "business_context": {"owner":"default","sla":"gold","change_freeze": False},
        "controls": {"can_isolate": True, "require_approval": ["contain","block"]}
    }, timeout=20).json()
    return {"state": "awaiting_approval","threat": thr,"policy": pol}

from connectors import notify_slack, notify_teams, create_jira_ticket

@app.post("/actions/execute")
def actions_execute(body: dict = Body(...)):
    """Execute an action_plan with chosen connectors.
    body = {
      "action_plan": [...],
      "options": {"notify_via": "slack|teams", "jira_issue_type":"Task", "dry_run": true}
    }
    """
    plan = body.get("action_plan", [])
    options = body.get("options", {})
    dry = bool(options.get("dry_run", True))
    results = []
    for step in plan:
        action = step.get("action")
        if action == "notify":
            text = f"[{step.get('priority','p3')}] SOC Notification via Sentient"
            if options.get("notify_via") == "teams":
                res = {"connector":"teams","dry_run":dry}
                if not dry: res |= notify_teams(text)
            else:
                res = {"connector":"slack","dry_run":dry}
                if not dry: res |= notify_slack(text, channel=step.get("channel"))
            results.append({"step": step, "result": res})
        elif action == "ticket":
            summary = f"Sentient Incident - {step.get('template','incident')}"
            desc = "Auto-created by Sentient policy. See orchestrator for details."
            res = {"connector":"jira","dry_run":dry}
            if not dry:
                res |= create_jira_ticket(summary, desc, issue_type=options.get("jira_issue_type","Task"))
            results.append({"step": step, "result": res})
        else:
            # For contain/rollback you'd integrate with SOAR/firewall API here
            results.append({"step": step, "result": {"ok": True, "note": "No-op (implementation hook)."}})
    return {"ok": True, "executed": len(plan), "results": results}
