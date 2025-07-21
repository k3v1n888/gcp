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

    # Get enrichment and prediction data
    intel = get_intel_from_misp(threat.ip)
    ip_score = intel.get("ip_reputation_score", 0)
    cve_id = find_cve_for_threat(threat.threat)
    
    predicted_severity = predictor.predict(
        threat=threat.threat,
        source=threat.source,
        ip_reputation_score=ip_score,
        cve_id=cve_id
    )

    temp_log_for_check = {**threat.dict(), "ip_reputation_score": ip_score, "cve_id": cve_id}
    is_anomaly = anomaly_detector.check_for_anomaly(temp_log_for_check)
    
    # --- THIS IS THE FIX ---
    # Create the final log record with an explicit timestamp
    db_log = models.ThreatLog(
        **threat.dict(), 
        severity=predicted_severity,
        ip_reputation_score=ip_score,
        cve_id=cve_id,
        is_anomaly=is_anomaly,
        timestamp=datetime.now(timezone.utc) # <-- Set the timestamp here
    )
    
    db.add(db_log)
    db.commit()
    db.refresh(db_log)

    if predicted_severity == 'critical' and ip_score >= 90:
        block_ip_with_cloud_armor(db, db_log)
    
    # Broadcast the final record
    pydantic_log = schemas.ThreatLog.from_orm(db_log)
    await manager.broadcast_json(pydantic_log.dict())
    
    return db_log