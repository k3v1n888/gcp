"""
Admin API endpoints for AI model testing and data generation
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
import json
import logging
import asyncio
import aiohttp
import random
import uuid
from datetime import datetime, timedelta
import os

from backend.database import get_db
from backend.models import ThreatLog, SecurityIncident, User
from backend.auth import require_admin

router = APIRouter(prefix="/api/admin", tags=["admin"])
logger = logging.getLogger(__name__)

# AI Model Test Configuration
AI_MODEL_ENDPOINTS = {
    "threat_scoring": {
        "name": "Threat Scoring Model",
        "endpoint": "/predict/threat_score",
        "method": "POST",
        "sample_data": {
            "source_ip": "192.168.1.100",
            "destination_ip": "10.0.0.50", 
            "protocol": "TCP",
            "port": 443,
            "threat_type": "malware_detection",
            "confidence_score": 0.85,
            "cvss_score": 7.5,
            "criticality_score": 0.8,
            "ioc_risk": 0.7
        }
    },
    "severity_prediction": {
        "name": "Severity Prediction Model",
        "endpoint": "/predict/severity", 
        "method": "POST",
        "sample_data": {
            "source_ip": "192.168.1.100",
            "threat_type": "phishing_attempt",
            "confidence_score": 0.9,
            "cvss_score": 8.0,
            "criticality_score": 0.85,
            "ioc_risk": 0.8
        }
    },
    "anomaly_detection": {
        "name": "Anomaly Detection Model",
        "endpoint": "/predict/anomaly",
        "method": "POST",
        "sample_data": {
            "source_ip": "203.0.113.45",
            "protocol": "UDP",
            "port": 53,
            "traffic_volume": 10000,
            "connection_count": 500
        }
    },
    "risk_assessment": {
        "name": "Risk Assessment Model", 
        "endpoint": "/predict/risk",
        "method": "POST",
        "sample_data": {
            "asset_value": "high",
            "vulnerability_score": 8.5,
            "threat_landscape": "active",
            "cvss_score": 9.0
        }
    },
    "shap_explanation": {
        "name": "SHAP Explainability",
        "endpoint": "/explain/shap",
        "method": "POST", 
        "sample_data": {
            "source_ip": "192.168.1.100",
            "threat_type": "ransomware",
            "confidence_score": 0.95,
            "cvss_score": 9.5
        }
    }
}

# Test data templates
THREAT_TYPES = [
    'malware_detection', 'phishing_attempt', 'brute_force_attack',
    'sql_injection', 'xss_attack', 'ddos_attack', 'privilege_escalation',
    'data_exfiltration', 'ransomware', 'lateral_movement'
]

SEVERITIES = ['low', 'medium', 'high', 'critical']

SAMPLE_IPS = [
    '192.168.1.100', '10.0.0.50', '172.16.0.25', '203.0.113.45',
    '198.51.100.78', '192.0.2.123', '185.199.108.153', '140.82.112.4'
]

@router.post("/generate-test-data")
async def generate_test_data(
    threat_logs_count: int = 100,
    incidents_count: int = 20,
    generate_iocs: bool = True,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """Generate comprehensive test data for AI model testing"""
    try:
        logger.info(f"Generating test data: {threat_logs_count} threats, {incidents_count} incidents")
        
        # Generate threat logs
        threat_logs_created = 0
        for i in range(threat_logs_count):
            threat_type = random.choice(THREAT_TYPES)
            severity = random.choice(SEVERITIES)
            
            # Generate realistic timestamps (last 30 days)
            base_time = datetime.now() - timedelta(days=random.randint(1, 30))
            
            threat_log = ThreatLog(
                tenant_id=1,
                timestamp=base_time,
                source_ip=random.choice(SAMPLE_IPS),
                destination_ip=random.choice(SAMPLE_IPS),
                protocol=random.choice(['TCP', 'UDP', 'HTTP', 'HTTPS']),
                port=random.choice([80, 443, 22, 3389, 8080, 25, 53]),
                threat_type=threat_type,
                severity=severity,
                confidence_score=round(random.uniform(0.1, 1.0), 3),
                status=random.choice(['active', 'resolved', 'investigating']),
                details=f"Generated test threat: {threat_type} from {random.choice(SAMPLE_IPS)}",
                mitre_technique=f"T{random.randint(1000, 1999)}.{random.randint(100, 999)}",
                rule_id=f"RULE_{random.randint(1000, 9999)}",
                analyst_notes=f"AI model test data for {threat_type}",
                is_false_positive=random.choice([True, False]) if random.random() < 0.1 else False,
                criticality_score=round(random.uniform(0.0, 1.0), 3),
                risk_score=round(random.uniform(0.0, 10.0), 2),
                cvss_score=round(random.uniform(0.0, 10.0), 1),
                ioc_count=random.randint(1, 10)
            )
            
            db.add(threat_log)
            threat_logs_created += 1
        
        # Generate security incidents
        incidents_created = 0
        for i in range(incidents_count):
            start_time = datetime.now() - timedelta(days=random.randint(1, 30))
            end_time = start_time + timedelta(hours=random.randint(1, 48)) if random.choice([True, False]) else None
            
            incident = SecurityIncident(
                title=f"AI Test Incident {i+1}: {random.choice(THREAT_TYPES).replace('_', ' ').title()}",
                status=random.choice(['open', 'investigating', 'resolved', 'closed']),
                severity=random.choice(SEVERITIES),
                start_time=start_time,
                end_time=end_time,
                tenant_id=1,
                created_at=start_time
            )
            
            db.add(incident)
            incidents_created += 1
        
        db.commit()
        
        # Get total counts
        total_threats = db.query(ThreatLog).count()
        total_incidents = db.query(SecurityIncident).count()
        
        logger.info(f"Successfully generated {threat_logs_created} threat logs and {incidents_created} incidents")
        
        return {
            "success": True,
            "threat_logs_inserted": threat_logs_created,
            "incidents_inserted": incidents_created,
            "total_threat_logs": total_threats,
            "total_incidents": total_incidents,
            "message": f"Generated {threat_logs_created} threat logs and {incidents_created} security incidents"
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error generating test data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating test data: {str(e)}"
        )

@router.post("/test-ai-models")
async def test_ai_models(
    test_type: str = "all",
    current_user: dict = Depends(require_admin)
):
    """Test all AI model endpoints with sample data"""
    try:
        ai_service_url = os.getenv("AI_SERVICE_URL", "http://ai-service:8001")
        logger.info(f"Testing AI models at {ai_service_url}")
        
        # Determine which tests to run
        if test_type == "all":
            tests_to_run = AI_MODEL_ENDPOINTS
        else:
            if test_type not in AI_MODEL_ENDPOINTS:
                raise HTTPException(status_code=400, detail=f"Invalid test type: {test_type}")
            tests_to_run = {test_type: AI_MODEL_ENDPOINTS[test_type]}
        
        test_results = {}
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
            for test_key, test_config in tests_to_run.items():
                test_start_time = datetime.now()
                
                try:
                    url = f"{ai_service_url}{test_config['endpoint']}"
                    logger.info(f"Testing {test_config['name']}: {url}")
                    
                    if test_config['method'] == 'GET':
                        async with session.get(url) as response:
                            response_data = await response.json() if response.content_type == 'application/json' else await response.text()
                            response_time = (datetime.now() - test_start_time).total_seconds()
                    else:
                        async with session.post(url, json=test_config['sample_data']) as response:
                            response_data = await response.json() if response.content_type == 'application/json' else await response.text()
                            response_time = (datetime.now() - test_start_time).total_seconds()
                    
                    test_results[test_key] = {
                        "name": test_config['name'],
                        "status": "success" if response.status == 200 else "failed",
                        "status_code": response.status,
                        "response_time": round(response_time * 1000, 2),  # Convert to ms
                        "endpoint": test_config['endpoint'],
                        "response": response_data,
                        "sample_data_used": test_config['sample_data']
                    }
                    
                    if response.status == 200:
                        logger.info(f"✅ {test_config['name']}: SUCCESS")
                    else:
                        logger.warning(f"❌ {test_config['name']}: FAILED (Status: {response.status})")
                
                except Exception as e:
                    test_results[test_key] = {
                        "name": test_config['name'],
                        "status": "error",
                        "error": str(e),
                        "endpoint": test_config['endpoint']
                    }
                    logger.error(f"❌ {test_config['name']}: ERROR - {e}")
        
        # Calculate summary
        summary = {
            "total": len(test_results),
            "passed": len([r for r in test_results.values() if r.get("status") == "success"]),
            "failed": len([r for r in test_results.values() if r.get("status") == "failed"]),
            "errors": len([r for r in test_results.values() if r.get("status") == "error"])
        }
        
        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "ai_service_url": ai_service_url,
            "test_type": test_type,
            "results": test_results,
            "summary": summary
        }
        
    except Exception as e:
        logger.error(f"Error testing AI models: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error testing AI models: {str(e)}"
        )

@router.get("/test-history")
async def get_test_history(
    limit: int = 10,
    current_user: dict = Depends(require_admin)
):
    """Get history of AI model test results"""
    # This would typically come from a database table storing test results
    # For now, return a placeholder response
    return {
        "success": True,
        "message": "Test history feature - would be implemented with persistent storage",
        "history": []
    }

@router.post("/clear-test-data")
async def clear_test_data(
    confirm: bool = False,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """Clear generated test data (use with caution)"""
    if not confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must confirm data deletion by setting confirm=true"
        )
    
    try:
        # Delete test threat logs (those with analyst_notes containing "AI model test")
        deleted_threats = db.query(ThreatLog).filter(
            ThreatLog.analyst_notes.like("%AI model test%")
        ).delete(synchronize_session=False)
        
        # Delete test incidents (those with title containing "AI Test")
        deleted_incidents = db.query(SecurityIncident).filter(
            SecurityIncident.title.like("%AI Test%")
        ).delete(synchronize_session=False)
        
        db.commit()
        
        logger.info(f"Cleared {deleted_threats} test threat logs and {deleted_incidents} test incidents")
        
        return {
            "success": True,
            "deleted_threat_logs": deleted_threats,
            "deleted_incidents": deleted_incidents,
            "message": f"Cleared {deleted_threats} test threat logs and {deleted_incidents} test incidents"
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error clearing test data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error clearing test data: {str(e)}"
        )

@router.get("/ai-models/status")
async def get_ai_models_status(current_user: dict = Depends(require_admin)):
    """Get status of all AI model endpoints"""
    ai_service_url = os.getenv("AI_SERVICE_URL", "http://ai-service:8001")
    
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
            # Test health endpoint
            try:
                async with session.get(f"{ai_service_url}/health") as response:
                    health_status = "healthy" if response.status == 200 else "unhealthy"
                    health_response = await response.json() if response.content_type == 'application/json' else await response.text()
            except Exception as e:
                health_status = "error"
                health_response = str(e)
            
            # Test individual model endpoints
            model_statuses = {}
            for model_key, model_config in AI_MODEL_ENDPOINTS.items():
                try:
                    url = f"{ai_service_url}{model_config['endpoint']}"
                    async with session.post(url, json=model_config['sample_data']) as response:
                        model_statuses[model_key] = {
                            "name": model_config['name'],
                            "status": "available" if response.status == 200 else "unavailable",
                            "endpoint": model_config['endpoint']
                        }
                except Exception as e:
                    model_statuses[model_key] = {
                        "name": model_config['name'],
                        "status": "error",
                        "endpoint": model_config['endpoint'],
                        "error": str(e)
                    }
        
        return {
            "success": True,
            "ai_service_url": ai_service_url,
            "overall_health": health_status,
            "health_response": health_response,
            "models": model_statuses,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error checking AI models status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking AI models status: {str(e)}"
        )
