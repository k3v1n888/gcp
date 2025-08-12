
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
