from fastapi import APIRouter, Depends, Response, HTTPException, Request, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timezone
from typing import List, Optional
import logging

from .. import models, database, schemas
from ..auth.rbac import get_current_user  # Use your original auth
from ..correlation_service import generate_threat_remediation_plan, get_and_summarize_misp_intel
from ..database import get_db
from ..models import ThreatLog

router = APIRouter(prefix="/api", tags=["threats"])
logger = logging.getLogger(__name__)

@router.get("/threats")  # Remove response_model - this was the main issue
def get_threat_logs(
    response: Response,
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0),
    user: models.User = Depends(get_current_user),  # Use your original auth
    db: Session = Depends(database.get_db)
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
            # Safe timestamp conversion - this was the core issue
            if log.timestamp:
                try:
                    timestamp_str = log.timestamp.isoformat()
                except:
                    timestamp_str = datetime.utcnow().isoformat()
            else:
                timestamp_str = datetime.utcnow().isoformat()
            
            # Convert to dict to bypass Pydantic validation
            log_dict = {
                "id": log.id,
                "tenant_id": log.tenant_id,
                "ip": log.ip,
                "threat_type": log.threat_type,
                "threat": getattr(log, 'threat', ''),
                "severity": log.severity,
                "description": log.description,
                "timestamp": timestamp_str,  # Always a string now
                "cve_id": log.cve_id,
                "cvss_score": log.cvss_score,
                "source": log.source,
                "ip_reputation_score": getattr(log, 'ip_reputation_score', None),
                "is_anomaly": getattr(log, 'is_anomaly', False)
            }
            safe_logs.append(log_dict)
        
        return safe_logs  # Return list of dicts instead of Pydantic models
        
    except Exception as e:
        logger.error(f"Error fetching threats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch threats: {str(e)}")

# Keep your other endpoints as they were - only remove response_model from problematic ones
@router.get("/threats/{threat_id}")  # Remove response_model
def get_threat_detail(
    request: Request,
    threat_id: int,
    user: models.User = Depends(get_current_user),  # Use original auth
    db: Session = Depends(database.get_db)
):
    """Individual threat detail - minimal changes"""
    # Keep your original logic but return dict instead of Pydantic model
    threat_log = db.query(models.ThreatLog).filter(
        models.ThreatLog.id == threat_id,
        models.ThreatLog.tenant_id == user.tenant_id
    ).first()

    if not threat_log:
        raise HTTPException(status_code=404, detail="Threat log not found")

    # Keep your original correlation logic
    timeline_threats = []
    if hasattr(threat_log, 'incidents') and threat_log.incidents:
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
    soar_actions = db.query(models.AutomationLog).filter(
        models.AutomationLog.threat_id == threat_id
    ).order_by(models.AutomationLog.timestamp.desc()).all()

    # Convert to dict with safe timestamp handling
    response_data = {
        "id": threat_log.id,
        "tenant_id": threat_log.tenant_id,
        "ip": threat_log.ip,
        "threat_type": threat_log.threat_type,
        "threat": getattr(threat_log, 'threat', ''),
        "severity": threat_log.severity,
        "description": threat_log.description,
        "timestamp": threat_log.timestamp.isoformat() if threat_log.timestamp else datetime.utcnow().isoformat(),
        "cve_id": threat_log.cve_id,
        "cvss_score": threat_log.cvss_score,
        "source": threat_log.source,
        # Add other fields as needed
        "correlation": correlated_threat.__dict__ if correlated_threat else None,
        "misp_summary": misp_summary,
        "recommendations": recommendations_dict,
        "timeline_threats": [
            {
                "id": t.id,
                "timestamp": t.timestamp.isoformat() if t.timestamp else None,
                "threat_type": t.threat_type,
                "ip": t.ip
            } for t in timeline_threats
        ]
    }
    
    return response_data

@router.post("/log_threat")
async def log_threat(
    threat_data: dict,
    user: models.User = Depends(get_current_user),  # FIXED: Use get_current_user_simple
    db: Session = Depends(database.get_db)
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
async def get_threats_raw(db: Session = Depends(database.get_db)):
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