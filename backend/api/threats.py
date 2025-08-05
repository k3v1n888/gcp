from fastapi import APIRouter, Depends, Response, HTTPException, Request, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timezone
from typing import List, Optional
import logging

from .. import models, database, schemas
from ..auth.rbac import get_current_user
from ..correlation_service import generate_threat_remediation_plan, get_and_summarize_misp_intel
from ..database import get_db
from ..models import ThreatLog
from ..auth.auth import get_current_user, get_current_tenant

router = APIRouter(prefix="/api", tags=["threats"])
logger = logging.getLogger(__name__)

@router.get("/threats")  # Remove response_model completely
def get_threat_logs(
    response: Response,
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0),
    user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    """Get threats with safe timestamp handling"""
    try:
        response.headers["Cache-Control"] = "no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        
        logs = (
            db.query(models.ThreatLog)
            .filter(models.ThreatLog.tenant_id == user.tenant_id)
            .order_by(models.ThreatLog.timestamp.desc().nulls_last())  # Handle nulls
            .offset(offset)
            .limit(limit)
            .all()
        )
        
        # Convert to safe dict format
        safe_logs = []
        for log in logs:
            log_dict = {
                "id": log.id,
                "tenant_id": log.tenant_id,
                "ip": log.ip or "unknown",
                "threat_type": log.threat_type or "unknown",
                "threat": log.threat or "",
                "severity": log.severity or "medium",
                "description": log.description or "",
                "cve_id": log.cve_id,
                "cvss_score": log.cvss_score,
                "source": log.source or "api",
                "ip_reputation_score": log.ip_reputation_score,
                "is_anomaly": log.is_anomaly or False,
                # Safe timestamp handling
                "timestamp": log.timestamp.isoformat() if log.timestamp else datetime.utcnow().isoformat()
            }
            safe_logs.append(log_dict)
        
        return safe_logs
        
    except Exception as e:
        logger.error(f"Error fetching threats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch threats: {str(e)}")

@router.get("/threats/{threat_id}", response_model=schemas.ThreatDetailResponse)
def get_threat_detail(
    request: Request,
    threat_id: int,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    threat_log = db.query(models.ThreatLog).filter(
        models.ThreatLog.id == threat_id,
        models.ThreatLog.tenant_id == user.tenant_id
    ).first()

    if not threat_log:
        raise HTTPException(status_code=404, detail="Threat log not found")

    timeline_threats = []
    if threat_log.incidents:
        parent_incident = threat_log.incidents[0]
        timeline_threats = sorted(
            [t for t in parent_incident.threat_logs if t.timestamp], 
            key=lambda log: log.timestamp
        )

    correlated_threat = db.query(models.CorrelatedThreat).filter(
        models.CorrelatedThreat.title == f"Attack Pattern: {threat_log.threat}",
        models.CorrelatedThreat.tenant_id == user.tenant_id
    ).first()

    recommendations_dict = generate_threat_remediation_plan(threat_log)
    misp_summary = get_and_summarize_misp_intel(threat_log.ip)
    soar_actions = db.query(models.AutomationLog).filter(models.AutomationLog.threat_id == threat_id).order_by(models.AutomationLog.timestamp.desc()).all()

    threat_log_dict = schemas.ThreatLog.from_orm(threat_log).dict()
    if threat_log_dict.get('timestamp'):
        threat_log_dict['timestamp'] = threat_log_dict['timestamp'].isoformat()
    
    predictor = request.app.state.predictor
    xai_explanation_dict = predictor.explain_prediction(threat_log_dict)

    # Build the final, validated response
    response_data = schemas.ThreatDetailResponse.from_orm(threat_log)
    response_data.correlation = correlated_threat
    response_data.misp_summary = misp_summary
    response_data.soar_actions = soar_actions
    response_data.timeline_threats = timeline_threats
    
    if recommendations_dict:
        response_data.recommendations = schemas.Recommendation(**recommendations_dict)
    
    # --- THIS IS THE FIX ---
    # Create an instance of the XAIExplanation schema from the dictionary
    if xai_explanation_dict:
        response_data.xai_explanation = schemas.XAIExplanation(**xai_explanation_dict)
    
    if threat_log.is_anomaly:
        response_data.anomaly_features = schemas.AnomalyFeatures(
            text_feature=f"{threat_log.threat} {threat_log.source}",
            ip_reputation_score=threat_log.ip_reputation_score or 0,
            has_cve=1 if threat_log.cve_id else 0
        )
    
    return response_data

@router.post("/log_threat")
async def log_threat(
    threat_data: dict,
    tenant_id: int = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    """Log a new threat with guaranteed timestamp"""
    try:
        # Always use current UTC time
        current_time = datetime.now(timezone.utc)
        
        threat_log = ThreatLog(
            tenant_id=tenant_id,
            ip=str(threat_data.get("ip", "unknown"))[:45],
            threat_type=str(threat_data.get("threat_type", "unknown"))[:100],
            severity=str(threat_data.get("severity", "medium"))[:20],
            description=str(threat_data.get("description", ""))[:1000] if threat_data.get("description") else None,
            cve_id=str(threat_data.get("cve_id"))[:20] if threat_data.get("cve_id") else None,
            cvss_score=float(threat_data.get("cvss_score")) if threat_data.get("cvss_score") else None,
            source=str(threat_data.get("source", "api"))[:50],
            timestamp=current_time
        )
        
        db.add(threat_log)
        db.commit()
        db.refresh(threat_log)
        
        logger.info(f"Successfully logged threat with ID: {threat_log.id}")
        
        return {
            "success": True,
            "message": "Threat logged successfully",
            "threat_id": threat_log.id,
            "timestamp": threat_log.timestamp.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error logging threat: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to log threat: {str(e)}")

@router.get("/debug/threats-raw")
async def get_threats_raw(db: Session = Depends(get_db)):
    """Debug endpoint to check raw threat data"""
    try:
        threats = db.query(ThreatLog).order_by(desc(ThreatLog.timestamp)).limit(10).all()
        
        threats_data = []
        for threat in threats:
            threats_data.append({
                "id": threat.id,
                "ip": threat.ip,
                "threat_type": threat.threat_type,
                "tenant_id": threat.tenant_id,
                "timestamp": threat.timestamp.isoformat() if threat.timestamp else None,
                "timestamp_raw": str(threat.timestamp)
            })
        
        return {
            "total_threats": len(threats_data),
            "threats": threats_data,
            "success": True
        }
    except Exception as e:
        logger.error(f"Debug endpoint error: {e}")
        return {"error": str(e), "success": False}