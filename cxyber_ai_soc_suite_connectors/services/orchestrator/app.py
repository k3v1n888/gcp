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
from fastapi import FastAPI, Body
from typing import Dict, Any

INGEST_URL = os.getenv("INGEST_URL", "http://localhost:8000/ingest_auto")
THREAT_URL = os.getenv("THREAT_URL", "http://localhost:8001/threat/score")
POLICY_URL = os.getenv("POLICY_URL", "http://localhost:8002/policy/decide")

app = FastAPI(title="Orchestrator", version="0.1.0")

@app.get("/health")
def health(): return {"ok": True}

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
