"""
API endpoints for Universal Data Connector System
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

from .. import database
from ..auth.rbac import get_current_user, require_role
from .manager import ConnectorManager
from .config import DEFAULT_CONFIG, DEV_CONFIG, PROD_CONFIG, get_connector_config
import os

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/connectors", tags=["connectors"])

# Global connector manager instance
connector_manager: Optional[ConnectorManager] = None


def require_admin():
    """Helper function for admin access - simplified for development"""
    return get_current_user


def get_connector_config():
    """Get configuration based on environment"""
    env = os.getenv('ENV', 'development')
    
    if env == 'production':
        return PROD_CONFIG
    elif env == 'development':
        return DEV_CONFIG
    else:
        return DEFAULT_CONFIG


def get_connector_manager() -> ConnectorManager:
    """Get or create connector manager instance"""
    global connector_manager
    
    if connector_manager is None:
        config = get_connector_config()
        connector_manager = ConnectorManager(config)
    
    return connector_manager


@router.get("/status")
async def get_connector_status(current_user: dict = Depends(require_admin)):
    """Get status of all connectors"""
    try:
        manager = get_connector_manager()
        status = manager.get_connector_status()
        
        # Add connection test results
        connection_status = manager.test_connections()
        
        for name, connector_info in status['connectors'].items():
            connector_info['connected'] = connection_status.get(name, False)
        
        return {
            "success": True,
            "data": status,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get connector status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test-connections")
async def test_all_connections(current_user: dict = Depends(require_admin)):
    """Test connections to all configured connectors"""
    try:
        manager = get_connector_manager()
        results = manager.test_connections()
        
        return {
            "success": True,
            "data": {
                "total_connectors": len(results),
                "successful_connections": sum(1 for connected in results.values() if connected),
                "results": results
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to test connections: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/collect-threats")
async def collect_threats(
    background_tasks: BackgroundTasks,
    hours_back: int = 1,
    connector_names: Optional[List[str]] = None,
    current_user: dict = Depends(require_admin)
):
    """Collect threats from connectors (runs in background)"""
    try:
        since = datetime.utcnow() - timedelta(hours=hours_back)
        
        def run_collection():
            manager = get_connector_manager()
            return manager.collect_threats(since, connector_names)
        
        background_tasks.add_task(run_collection)
        
        return {
            "success": True,
            "message": "Threat collection started in background",
            "since": since.isoformat(),
            "connectors": connector_names or "all active connectors"
        }
        
    except Exception as e:
        logger.error(f"Failed to start threat collection: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/run-pipeline")
async def run_full_pipeline(
    background_tasks: BackgroundTasks,
    hours_back: int = 1,
    connector_names: Optional[List[str]] = None,
    tenant_id: int = 1,
    current_user: dict = Depends(require_admin)
):
    """Run the complete threat analysis pipeline (background task)"""
    try:
        since = datetime.utcnow() - timedelta(hours=hours_back)
        
        def run_pipeline():
            manager = get_connector_manager()
            result = manager.run_full_pipeline(since, connector_names, tenant_id)
            logger.info(f"Pipeline result: {result}")
            return result
        
        background_tasks.add_task(run_pipeline)
        
        return {
            "success": True,
            "message": "Full threat analysis pipeline started",
            "since": since.isoformat(),
            "connectors": connector_names or "all active connectors",
            "tenant_id": tenant_id
        }
        
    except Exception as e:
        logger.error(f"Failed to start pipeline: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pipeline/run-sync")
async def run_pipeline_sync(
    hours_back: int = 1,
    connector_names: Optional[str] = None,
    tenant_id: int = 1,
    current_user: dict = Depends(require_admin)
):
    """Run the pipeline synchronously (for testing/manual execution)"""
    try:
        since = datetime.utcnow() - timedelta(hours=hours_back)
        connector_list = connector_names.split(',') if connector_names else None
        
        manager = get_connector_manager()
        result = manager.run_full_pipeline(since, connector_list, tenant_id)
        
        return {
            "success": True,
            "data": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/threats/recent")
async def get_recent_threats(
    hours_back: int = 24,
    limit: int = 100,
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(require_admin)
):
    """Get recently collected threats from database"""
    try:
        since = datetime.utcnow() - timedelta(hours=hours_back)
        
        # Query your existing ThreatLog table
        from .. import models
        
        threats = db.query(models.ThreatLog)\
                   .filter(models.ThreatLog.timestamp >= since)\
                   .order_by(models.ThreatLog.timestamp.desc())\
                   .limit(limit)\
                   .all()
        
        threat_data = []
        for threat in threats:
            threat_data.append({
                "id": threat.id,
                "ip": threat.ip,
                "threat": threat.threat,
                "source": threat.source,
                "severity": threat.severity,
                "timestamp": threat.timestamp.isoformat(),
                "tenant_id": threat.tenant_id,
                "ai_severity": getattr(threat, 'ai_severity', None),
                "confidence_score": getattr(threat, 'confidence_score', None),
                "impact_score": getattr(threat, 'impact_score', None)
            })
        
        return {
            "success": True,
            "data": {
                "threats": threat_data,
                "total_count": len(threat_data),
                "since": since.isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get recent threats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/config")
async def get_connector_config_api(current_user: dict = Depends(require_admin)):
    """Get current connector configuration (sanitized)"""
    try:
        config = get_connector_config()
        
        # Sanitize sensitive information
        sanitized_config = {}
        for section, values in config.items():
            if section == "connectors":
                sanitized_config[section] = {}
                for conn_name, conn_config in values.items():
                    sanitized_conn = conn_config.copy()
                    # Remove sensitive fields
                    for sensitive_field in ['password', 'client_secret', 'auth_token', 'api_key']:
                        if sensitive_field in sanitized_conn:
                            sanitized_conn[sensitive_field] = "***HIDDEN***"
                    sanitized_config[section][conn_name] = sanitized_conn
            else:
                sanitized_config[section] = values
        
        return {
            "success": True,
            "data": sanitized_config,
            "environment": os.getenv('ENV', 'development')
        }
        
    except Exception as e:
        logger.error(f"Failed to get config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reload")
async def reload_connector_manager(current_user: dict = Depends(require_admin)):
    """Reload the connector manager with updated configuration"""
    try:
        global connector_manager
        connector_manager = None  # Force recreation
        
        # Get new manager instance
        manager = get_connector_manager()
        status = manager.get_connector_status()
        
        return {
            "success": True,
            "message": "Connector manager reloaded successfully",
            "data": status
        }
        
    except Exception as e:
        logger.error(f"Failed to reload connector manager: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_connector_stats(
    hours_back: int = 24,
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(require_admin)
):
    """Get statistics about threat collection by source"""
    try:
        since = datetime.utcnow() - timedelta(hours=hours_back)
        
        from .. import models
        from sqlalchemy import func
        
        # Get threat counts by source
        source_stats = db.query(
            models.ThreatLog.source,
            func.count(models.ThreatLog.id).label('count'),
            func.max(models.ThreatLog.timestamp).label('latest')
        ).filter(
            models.ThreatLog.timestamp >= since
        ).group_by(models.ThreatLog.source).all()
        
        # Get severity distribution
        severity_stats = db.query(
            models.ThreatLog.severity,
            func.count(models.ThreatLog.id).label('count')
        ).filter(
            models.ThreatLog.timestamp >= since
        ).group_by(models.ThreatLog.severity).all()
        
        return {
            "success": True,
            "data": {
                "by_source": [
                    {
                        "source": stat.source,
                        "count": stat.count,
                        "latest": stat.latest.isoformat() if stat.latest else None
                    }
                    for stat in source_stats
                ],
                "by_severity": [
                    {
                        "severity": stat.severity,
                        "count": stat.count
                    }
                    for stat in severity_stats
                ],
                "total_threats": sum(stat.count for stat in source_stats),
                "time_period": f"{hours_back} hours",
                "since": since.isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get connector stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
