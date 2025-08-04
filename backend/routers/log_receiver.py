import os
import requests
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
import logging
from datetime import datetime, timezone

from backend import models, database, schemas
from backend.app.websocket.threats import manager
from backend.correlation_service import get_intel_from_misp, find_cve_for_threat
from backend.soar_service import block_ip_with_cloud_armor

logger = logging.getLogger(__name__)

class ThreatCreate(BaseModel):
    ip: str
    threat: str
    source: str
    tenant_id: int

router = APIRouter()

def get_cvss_score(cve_id: str) -> float:
    if not cve_id:
        return 0.0

    url = f"https://www.cve.org/api/cve/{cve_id}"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        score = data.get("cvssMetrics", [{}])[0].get("cvssData", {}).get("baseScore", 0.0)
        return float(score or 0.0)
    except Exception as e:
        print(f"⚠️ Could not fetch CVSS score for {cve_id}: {e}")
        return 0.0

@router.post("/api/log_threat", response_model=schemas.ThreatLog, status_code=201)
async def log_threat_endpoint(request: Request, threat: ThreatCreate, db: Session = Depends(database.get_db)):
    predictor = request.app.state.predictor
    anomaly_detector = request.app.state.anomaly_detector
    graph_service = request.app.state.graph_service

    intel = get_intel_from_misp(threat.ip)
    ip_score = intel.get("ip_reputation_score", 0)
    cve_id = find_cve_for_threat(threat.threat)
    cvss_score = get_cvss_score(cve_id)
    criticality_score = 0.9  # placeholder logic

    predicted_severity = predictor.predict(
        threat=threat.threat,
        source=threat.source,
        ip_reputation_score=ip_score,
        cve_id=cve_id,
        cvss_score=cvss_score,
        criticality_score=criticality_score
    )

    enriched_log = {
        **threat.dict(),
        "ip_reputation_score": ip_score,
        "cve_id": cve_id,
        "cvss_score": cvss_score,
        "criticality_score": criticality_score
    }
    is_anomaly = anomaly_detector.check_for_anomaly(enriched_log)

    db_log = models.ThreatLog(
        **threat.dict(),
        severity=predicted_severity,
        ip_reputation_score=ip_score,
        cve_id=cve_id,
        cvss_score=cvss_score,
        criticality_score=criticality_score,
        ioc_risk_score=(ip_score / 100.0),
        is_anomaly=is_anomaly,
        timestamp=datetime.now(timezone.utc)
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)

    if predicted_severity == 'critical' and ip_score >= 90:
        block_ip_with_cloud_armor(db, db_log)

    graph_service.add_threat_to_graph(db_log)
    pydantic_log = schemas.ThreatLog.from_orm(db_log)
    await manager.broadcast_json(pydantic_log.dict())
    return db_log