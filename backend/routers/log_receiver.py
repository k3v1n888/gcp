# log_Receiver.py

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

@router.post("/api/log_threat", response_model=schemas.ThreatLog, status_code=201)
async def log_threat_endpoint(request: Request, threat: ThreatCreate, db: Session = Depends(database.get_db)):
    predictor = request.app.state.predictor
    anomaly_detector = request.app.state.anomaly_detector
    graph_service = request.app.state.graph_service

    # Get enrichment and prediction data
    intel = get_intel_from_misp(threat.ip)
    ip_score = intel.get("ip_reputation_score", 0)
    cvss = intel.get("cvss_score", 0)
    crit_score = intel.get("criticality_score", 0)
    cve_id = find_cve_for_threat(threat.threat)

    predicted_severity = predictor.predict(
        threat=threat.threat,
        source=threat.source,
        ip_reputation_score=ip_score,
        cve_id=cve_id,
        cvss_score=cvss,
        criticality_score=crit_score
    )

    temp_log_for_check = {
        **threat.dict(),
        "ip_reputation_score": ip_score,
        "cve_id": cve_id,
        "cvss_score": cvss,
        "criticality_score": crit_score
    }
    is_anomaly = anomaly_detector.check_for_anomaly(temp_log_for_check)

    db_log = models.ThreatLog(
        **threat.dict(), 
        severity=predicted_severity,
        ip_reputation_score=ip_score,
        cve_id=cve_id,
        is_anomaly=is_anomaly,
        cvss_score=cvss,
        criticality_score=crit_score,
        timestamp=datetime.now(timezone.utc)
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)

    if predicted_severity == 'critical' and ip_score >= 90:
        block_ip_with_cloud_armor(db, db_log)

    # Add to graph DB
    graph_service.add_threat_to_graph(db_log)

    # Broadcast to clients
    pydantic_log = schemas.ThreatLog.from_orm(db_log)
    await manager.broadcast_json(pydantic_log.dict())

    return db_log