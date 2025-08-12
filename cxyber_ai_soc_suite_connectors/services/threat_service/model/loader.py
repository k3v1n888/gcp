
import os
from typing import Tuple, List, Dict, Any

REMOTE_URL = os.getenv("REMOTE_MODEL_URL")

def _remote_predict(fv: Dict[str,Any]) -> Tuple[str, float, List[str], Dict[str,Any]]:
    import requests
    resp = requests.post(REMOTE_URL, json={"features": fv}, timeout=10)
    resp.raise_for_status()
    r = resp.json()
    severity = r.get("severity","medium")
    confidence = float(r.get("confidence",0.6))
    findings = r.get("findings", ["AI-Classification"])
    shap = r.get("shap", {})
    return severity, confidence, findings, shap

def _heuristic_predict(fv: Dict[str,Any], ce: Dict[str,Any]) -> Tuple[str, float, List[str], Dict[str,Any]]:
    crit = fv.get("criticality_score") or 0.0
    ipr = (fv.get("ip_reputation") or 0)/100.0
    sev_score = max(crit, ipr)
    if sev_score >= 0.8: sev = "critical"
    elif sev_score >= 0.6: sev = "high"
    elif sev_score >= 0.3: sev = "medium"
    else: sev = "low"
    findings = []
    if ce.get("event_type") == "waf" and "union select" in (ce.get("url","").lower()):
        findings.append("SQLi")
    if fv.get("is_anomaly_hint") == 1:
        findings.append("Anomaly")
    shap = {"criticality_score": float(crit), "ip_reputation": float(fv.get("ip_reputation") or 0)}
    conf = float(min(0.95, 0.5 + sev_score/2))
    return sev, conf, findings or ["Baseline-Heuristic"], shap

def predict_severity(fv: Dict[str,Any], ce: Dict[str,Any], ctx: Dict[str,Any]):
    if REMOTE_URL:
        try:
            return _remote_predict(fv)
        except Exception:
            pass
    return _heuristic_predict(fv, ce)
