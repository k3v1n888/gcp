from fastapi import APIRouter, Depends, Response, HTTPException, Request, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timezone
from typing import List, Optional
import logging

from .. import models, database, schemas
from ..correlation_service import generate_threat_remediation_plan, get_and_summarize_misp_intel
from ..database import get_db
from ..models import ThreatLog

router = APIRouter(prefix="/api", tags=["threats"])
logger = logging.getLogger(__name__)

# Simple auth dependency for now
def get_current_user_simple(db: Session = Depends(get_db)) -> models.User:
    """Simplified auth - returns default user for testing"""
    # For now, return a default user or create one
    # This is a temporary fix - replace with proper auth later
    user = db.query(models.User).first()
    if not user:
        # Create a default user for testing
        user = models.User(
            id=1,
            email="test@quantum-ai.asia",
            tenant_id=1,
            is_admin=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

@router.get("/threats")
def get_threat_logs(
    response: Response,
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0),
    user: models.User = Depends(get_current_user_simple),  # Use simple auth
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
            .order_by(models.ThreatLog.timestamp.desc().nulls_last())
            .offset(offset)
            .limit(limit)
            .all()
        )
        
        # Convert to safe dict format
        safe_logs = []
        for log in logs:
            timestamp_str = log.timestamp.isoformat() if log.timestamp else datetime.utcnow().isoformat()
            
            log_dict = {
                "id": log.id,
                "tenant_id": log.tenant_id,
                "ip": log.ip or "unknown",
                "threat_type": log.threat_type or "unknown",
                "threat": log.threat or "",
                "severity": log.severity or "medium",
                "description": log.description or "",
                "cve_id": log.cve_id,
                "cvss_score": float(log.cvss_score) if log.cvss_score else None,
                "source": log.source or "api",
                "ip_reputation_score": log.ip_reputation_score or 0,
                "is_anomaly": log.is_anomaly or False,
                "timestamp": timestamp_str
            }
            safe_logs.append(log_dict)
        
        logger.info(f"Returning {len(safe_logs)} threats for tenant {user.tenant_id}")
        return safe_logs
        
    except Exception as e:
        logger.error(f"Error fetching threats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch threats: {str(e)}")

@router.get("/threats/{threat_id}")  # Remove response_model to avoid validation issues
def get_threat_detail(
    request: Request,
    threat_id: int,
    user: models.User = Depends(get_current_user_simple),
    db: Session = Depends(database.get_db)
):
    """Individual threat detail - fixed for simplified models"""
    try:
        threat_log = db.query(models.ThreatLog).filter(
            models.ThreatLog.id == threat_id,
            models.ThreatLog.tenant_id == user.tenant_id
        ).first()

        if not threat_log:
            raise HTTPException(status_code=404, detail="Threat log not found")

        # Remove the incidents relationship access since it's causing issues
        timeline_threats = []
        
        # Get correlated threats safely
        correlated_threat = None
        try:
            correlated_threat = db.query(models.CorrelatedThreat).filter(
                models.CorrelatedThreat.title == f"Attack Pattern: {threat_log.threat}",
                models.CorrelatedThreat.tenant_id == user.tenant_id
            ).first()
        except Exception as e:
            logger.warning(f"Could not fetch correlated threat: {e}")

        # Get automation logs safely
        soar_actions = []
        try:
            soar_actions = db.query(models.AutomationLog).filter(
                models.AutomationLog.threat_id == threat_id
            ).order_by(models.AutomationLog.timestamp.desc()).all()
        except Exception as e:
            logger.warning(f"Could not fetch automation logs: {e}")

        # Build safe response
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
            "ip_reputation_score": getattr(threat_log, 'ip_reputation_score', 0),
            "is_anomaly": getattr(threat_log, 'is_anomaly', False),
            "correlation": correlated_threat.__dict__ if correlated_threat else None,
            "soar_actions": [
                {
                    "id": action.id,
                    "action": action.action,
                    "timestamp": action.timestamp.isoformat() if action.timestamp else None
                } for action in soar_actions
            ],
            "timeline_threats": timeline_threats
        }
        
        return response_data
        
    except Exception as e:
        logger.error(f"Error fetching threat detail: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch threat detail: {str(e)}")

@router.post("/log_threat")
async def log_threat(
    threat_data: dict,
    user: models.User = Depends(get_current_user_simple),  # FIXED: Use get_current_user_simple
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