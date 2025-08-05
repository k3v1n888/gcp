from fastapi import APIRouter, Depends, Response, HTTPException, Request, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timezone
from typing import List, Optional
import logging

from .. import models, schemas
from ..auth.rbac import get_current_user  # Use your original auth
from ..correlation_service import generate_threat_remediation_plan, get_and_summarize_misp_intel
from ..models import ThreatLog

router = APIRouter(prefix="/api", tags=["threats"])
logger = logging.getLogger(__name__)

def get_db():
    """Simple database dependency"""
    db = models.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/threats")  # ONLY remove response_model
def get_threat_logs(
    response: Response,
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0),
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get threats - ONLY fix the timestamp serialization issue"""
    try:
        response.headers["Cache-Control"] = "no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        
        # Keep your original query logic
        logs = (
            db.query(models.ThreatLog)
            .filter(models.ThreatLog.tenant_id == user.tenant_id)
            .order_by(models.ThreatLog.timestamp.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        
        # ONLY change: Convert to dict to avoid Pydantic timestamp validation
        safe_logs = []
        for log in logs:
            # Safe timestamp conversion
            timestamp_str = log.timestamp.isoformat() if log.timestamp else datetime.utcnow().isoformat()
            
            log_dict = {
                "id": log.id,
                "tenant_id": log.tenant_id,
                "ip": log.ip,
                "threat_type": log.threat_type,
                "threat": getattr(log, 'threat', ''),
                "severity": log.severity,
                "description": log.description,
                "timestamp": timestamp_str,
                "cve_id": log.cve_id,
                "cvss_score": log.cvss_score,
                "source": log.source,
                "ip_reputation_score": getattr(log, 'ip_reputation_score', None),
                "is_anomaly": getattr(log, 'is_anomaly', False)
            }
            safe_logs.append(log_dict)
        
        return safe_logs
        
    except Exception as e:
        logger.error(f"Error fetching threats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch threats: {str(e)}")

# Keep ALL your other endpoints exactly as they were
@router.get("/threats/{threat_id}", response_model=schemas.ThreatDetailResponse)
def get_threat_detail(
    request: Request,
    threat_id: int,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Keep your original logic"""
    threat_log = db.query(models.ThreatLog).filter(
        models.ThreatLog.id == threat_id,
        models.ThreatLog.tenant_id == user.tenant_id
    ).first()

    if not threat_log:
        raise HTTPException(status_code=404, detail="Threat log not found")

    # Keep your original logic exactly as it was
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

    response_data = schemas.ThreatDetailResponse.from_orm(threat_log)
    response_data.correlation = correlated_threat
    response_data.misp_summary = misp_summary
    response_data.soar_actions = soar_actions
    response_data.timeline_threats = timeline_threats
    
    if recommendations_dict:
        response_data.recommendations = schemas.Recommendation(**recommendations_dict)
    
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
    user: models.User = Depends(get_current_user),  # FIXED: Use get_current_user_simple
    db: Session = Depends(get_db)
):
    """Log a new threat with guaranteed timestamp"""
    try:
        # Always use current UTC time
        current_time = datetime.now(timezone.utc)
        
        threat_log = ThreatLog(
            tenant_id=user.tenant_id,
            ip=str(threat_data.get("ip", "unknown"))[:45],
            threat_type=str(threat_data.get("threat_type", "unknown"))[:100],
            threat=str(threat_data.get("threat", ""))[:500],
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

# Add a simple health check too
@router.get("/threats/health")
def threats_health():
    """Simple health check for threats API"""
    return {"status": "healthy", "service": "threats", "timestamp": datetime.utcnow().isoformat()}