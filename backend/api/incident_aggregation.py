"""
API endpoints for AI-powered incident aggregation
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

from .. import database
from ..auth.rbac import require_role
from ..incident_aggregation import incident_aggregator
from ..models import ThreatLog, SecurityIncident

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/incidents", tags=["incident-aggregation"])

def require_admin():
    """Helper function for admin access - simplified for development"""
    return lambda: True

@router.post("/aggregate-threats")
async def aggregate_threats_into_incidents(
    background_tasks: BackgroundTasks,
    hours_back: int = 24,
    min_threats: int = 3,
    tenant_id: int = 1,
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(require_admin)
):
    """Aggregate recent threats into comprehensive incidents"""
    try:
        # Run aggregation in background
        background_tasks.add_task(
            run_threat_aggregation,
            db=db,
            hours_back=hours_back,
            min_threats=min_threats,
            tenant_id=tenant_id
        )
        
        return {
            "success": True,
            "message": "Threat aggregation started",
            "parameters": {
                "hours_back": hours_back,
                "min_threats": min_threats,
                "tenant_id": tenant_id
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to start threat aggregation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def run_threat_aggregation(db: Session, hours_back: int, min_threats: int, tenant_id: int):
    """Background task to run threat aggregation"""
    try:
        incidents = incident_aggregator.auto_aggregate_recent_threats(
            db=db,
            hours_back=hours_back,
            min_threats=min_threats,
            tenant_id=tenant_id
        )
        
        logger.info(f"Successfully created {len(incidents)} incidents from threat aggregation")
        
    except Exception as e:
        logger.error(f"Threat aggregation failed: {e}")

@router.post("/create-from-threats")
async def create_incident_from_threat_list(
    threat_ids: List[int],
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(require_admin)
):
    """Create a comprehensive incident from a specific list of threats"""
    try:
        # Get threats by IDs
        threats = db.query(ThreatLog).filter(ThreatLog.id.in_(threat_ids)).all()
        
        if not threats:
            raise HTTPException(status_code=404, detail="No threats found with provided IDs")
        
        # Create incident
        incident = incident_aggregator.create_incident_from_threats(
            threats=threats,
            db=db,
            tenant_id=1
        )
        
        return {
            "success": True,
            "incident_id": incident.id,
            "incident_title": incident.title,
            "threats_count": len(threats),
            "severity": incident.severity
        }
        
    except Exception as e:
        logger.error(f"Failed to create incident from threats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/aggregation-candidates")
async def get_aggregation_candidates(
    hours_back: int = 24,
    min_threats: int = 2,
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(require_admin)
):
    """Get threats that are candidates for aggregation into incidents"""
    try:
        # Get recent threats not already in incidents
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
        
        unassigned_threats = db.query(ThreatLog).filter(
            ThreatLog.timestamp >= cutoff_time,
            ~ThreatLog.incidents.any()  # Not already in an incident
        ).all()
        
        # Group by IP for analysis
        ip_groups = {}
        for threat in unassigned_threats:
            ip = threat.ip or 'unknown'
            if ip not in ip_groups:
                ip_groups[ip] = []
            ip_groups[ip].append({
                "id": threat.id,
                "title": threat.threat,
                "severity": threat.severity,
                "timestamp": threat.timestamp.isoformat() if threat.timestamp else None,
                "source": threat.source
            })
        
        # Filter groups that meet minimum threshold
        candidates = []
        for ip, threats in ip_groups.items():
            if len(threats) >= min_threats:
                candidates.append({
                    "ip": ip,
                    "threat_count": len(threats),
                    "threats": threats,
                    "severity_distribution": {
                        sev: len([t for t in threats if t["severity"] == sev])
                        for sev in set(t["severity"] for t in threats)
                    }
                })
        
        return {
            "success": True,
            "total_unassigned_threats": len(unassigned_threats),
            "candidate_groups": len(candidates),
            "candidates": candidates
        }
        
    except Exception as e:
        logger.error(f"Failed to get aggregation candidates: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/comprehensive/{incident_id}")
async def get_comprehensive_incident_details(
    incident_id: int,
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(require_admin)
):
    """Get comprehensive incident details with full investigation data"""
    try:
        # Get incident with related threats
        incident = db.query(SecurityIncident).filter(SecurityIncident.id == incident_id).first()
        
        if not incident:
            raise HTTPException(status_code=404, detail="Incident not found")
        
        # Get all related threats
        related_threats = []
        for threat in incident.threat_logs:
            related_threats.append({
                "id": threat.id,
                "title": threat.threat,
                "severity": threat.severity,
                "ip": threat.ip,
                "source": threat.source,
                "timestamp": threat.timestamp.isoformat() if threat.timestamp else None,
                "cve_id": threat.cve_id,
                "cvss_score": threat.cvss_score,
                "criticality_score": threat.criticality_score,
                "is_anomaly": threat.is_anomaly
            })
        
        # Analyze patterns in threats
        patterns = incident_aggregator.analyze_threat_patterns(incident.threat_logs)
        
        # Prepare comprehensive response
        response = {
            "incident": {
                "id": incident.id,
                "title": incident.title,
                "description": incident.description,
                "severity": incident.severity,
                "status": incident.status,
                "created_at": incident.created_at.isoformat() if incident.created_at else None,
                "ai_summary": incident.ai_summary,
                "confidence_score": incident.confidence_score
            },
            "threats": {
                "total_count": len(related_threats),
                "threats": related_threats,
                "severity_distribution": patterns["severity_distribution"],
                "source_distribution": patterns["source_analysis"]
            },
            "analysis": {
                "ip_clusters": {
                    ip: len(threats) for ip, threats in patterns["ip_clusters"].items()
                },
                "attack_chains": len(patterns["attack_chains"]),
                "time_span": {
                    "start": min(t["timestamp"] for t in related_threats if t["timestamp"]),
                    "end": max(t["timestamp"] for t in related_threats if t["timestamp"])
                } if related_threats else None
            },
            "investigation": {
                "indicators_of_compromise": incident.indicators_of_compromise,
                "affected_assets": incident.affected_assets,
                "recommended_actions": [
                    "Investigate all IP addresses involved",
                    "Block malicious IPs immediately", 
                    "Review logs for additional indicators",
                    "Implement additional monitoring",
                    f"Consider incident response for {incident.severity} severity"
                ]
            }
        }
        
        return {"success": True, "data": response}
        
    except Exception as e:
        logger.error(f"Failed to get comprehensive incident details: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reanalyze/{incident_id}")
async def reanalyze_incident_with_ai(
    incident_id: int,
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(require_admin)
):
    """Reanalyze an incident with updated AI analysis"""
    try:
        # Get incident with related threats
        incident = db.query(SecurityIncident).filter(SecurityIncident.id == incident_id).first()
        
        if not incident:
            raise HTTPException(status_code=404, detail="Incident not found")
        
        # Regenerate analysis
        patterns = incident_aggregator.analyze_threat_patterns(incident.threat_logs)
        new_summary = incident_aggregator.generate_incident_summary(incident.threat_logs, patterns)
        
        # Update incident with new analysis
        incident.ai_summary = new_summary
        incident.updated_at = datetime.utcnow()
        
        db.commit()
        
        return {
            "success": True,
            "incident_id": incident.id,
            "message": "Incident reanalyzed successfully",
            "updated_summary": new_summary
        }
        
    except Exception as e:
        logger.error(f"Failed to reanalyze incident: {e}")
        raise HTTPException(status_code=500, detail=str(e))
