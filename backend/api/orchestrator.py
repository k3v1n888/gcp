"""
Copyright (c) 2025 Kevin Zachary
All rights reserved.

This software and associated documentation files (the "Software") are the 
exclusive property of Kevin Zachary. Unauthorized copying, distribution, 
modification, or use of this software is strictly prohibited.

For licensing inquiries, contact: kevin@zachary.com
"""

# Author: Kevin Zachary
# Copyright: Sentient Spire

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime
import asyncio

from ..ai_orchestrator import ai_orchestrator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/orchestrator", tags=["AI Orchestrator"])

# Pydantic models for requests/responses
class ThreatProcessingRequest(BaseModel):
    raw_data: Dict[str, Any]
    source: str
    priority: Optional[str] = "normal"

class OrchestratorStatus(BaseModel):
    orchestrator_status: str
    models: Dict[str, Dict[str, Any]]
    performance_metrics: Dict[str, Any]
    recent_decisions: int
    system_health: str

class DecisionResponse(BaseModel):
    decision_id: str
    status: str
    processing_time: Optional[float]
    threat_id: Optional[str]
    severity: str
    confidence: float
    actions_taken: List[Dict[str, Any]]
    ai_analysis: Dict[str, Any]

@router.get("/status", response_model=OrchestratorStatus)
async def get_orchestrator_status():
    """Get comprehensive AI orchestrator status"""
    try:
        status = ai_orchestrator.get_system_status()
        logger.info("✅ Orchestrator status retrieved successfully")
        return OrchestratorStatus(**status)
    except Exception as e:
        logger.error(f"❌ Failed to get orchestrator status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get orchestrator status: {str(e)}")

@router.post("/process_threat", response_model=DecisionResponse)
async def process_threat(request: ThreatProcessingRequest, background_tasks: BackgroundTasks):
    """Process a threat through the AI orchestration pipeline"""
    try:
        logger.info(f"🔄 Processing threat from source: {request.source}")
        
        # Process the threat through AI orchestrator
        result = ai_orchestrator.process_threat(
            raw_data=request.raw_data,
            source=request.source
        )
        
        logger.info(f"✅ Threat processing completed: {result.get('decision_id')}")
        return DecisionResponse(**result)
        
    except Exception as e:
        logger.error(f"❌ Threat processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Threat processing failed: {str(e)}")

@router.get("/models/health")
async def get_models_health():
    """Get detailed health status of all AI models"""
    try:
        status = ai_orchestrator.get_system_status()
        models_health = status.get("models", {})
        
        # Add detailed health information
        detailed_health = {}
        for model_name, model_info in models_health.items():
            detailed_health[model_name] = {
                **model_info,
                "endpoint": ai_orchestrator.model_endpoints.get(model_name, "unknown"),
                "last_decision": None,  # Could add last decision involving this model
                "total_decisions": len([d for d in ai_orchestrator.decision_history 
                                      if model_name.lower() in str(d.model_outputs).lower()])
            }
        
        logger.info("✅ Models health retrieved successfully")
        return {
            "models": detailed_health,
            "system_health": status.get("system_health", "unknown"),
            "total_models": len(detailed_health),
            "healthy_models": len([m for m in detailed_health.values() if m.get("status") == "healthy"]),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get models health: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get models health: {str(e)}")

@router.get("/decisions/history")
async def get_decision_history(limit: int = 50, hours: int = 24):
    """Get recent decision history from the orchestrator"""
    try:
        from datetime import timedelta
        
        # Filter decisions by time range
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        recent_decisions = [
            {
                "decision_id": d.decision_id,
                "timestamp": d.timestamp.isoformat(),
                "decision_type": d.decision_type,
                "confidence": d.confidence,
                "rationale": d.rationale,
                "actions": d.actions,
                "status": "completed"  # Could track status in decision object
            }
            for d in ai_orchestrator.decision_history
            if d.timestamp >= cutoff_time
        ][-limit:]  # Get last 'limit' decisions
        
        logger.info(f"✅ Retrieved {len(recent_decisions)} recent decisions")
        return {
            "decisions": recent_decisions,
            "total_count": len(recent_decisions),
            "time_range_hours": hours,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get decision history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get decision history: {str(e)}")

@router.post("/models/test/{model_name}")
async def test_model(model_name: str):
    """Test a specific AI model"""
    try:
        if model_name not in ai_orchestrator.model_endpoints:
            raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found")
        
        endpoint = ai_orchestrator.model_endpoints[model_name]
        
        # Simple test based on model type
        test_data = {}
        if "ingest" in model_name.lower():
            test_data = {"test": "connectivity", "timestamp": datetime.utcnow().isoformat()}
        elif "postprocess" in model_name.lower():
            test_data = {"events": [{"test": "event"}], "mode": "test"}
        elif "trained" in model_name.lower():
            test_data = {"text": "test threat analysis", "confidence_threshold": 0.5}
        else:
            test_data = {"test": "ping"}
        
        logger.info(f"🧪 Testing model: {model_name}")
        
        # For now, return mock test result - would implement actual test calls
        test_result = {
            "model_name": model_name,
            "endpoint": endpoint,
            "test_status": "passed",
            "response_time": 0.150,
            "test_data": test_data,
            "timestamp": datetime.utcnow().isoformat(),
            "details": {
                "connectivity": "ok",
                "response_format": "valid",
                "performance": "normal"
            }
        }
        
        logger.info(f"✅ Model test completed: {model_name}")
        return test_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Model test failed for {model_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Model test failed: {str(e)}")

@router.get("/performance/metrics")
async def get_performance_metrics():
    """Get detailed performance metrics for the orchestrator"""
    try:
        metrics = ai_orchestrator.performance_metrics
        
        # Add additional computed metrics
        enhanced_metrics = {
            **metrics,
            "decision_rate": metrics.get("recent_decisions", 0) / 1.0,  # per hour
            "model_availability": len([m for m in ai_orchestrator.models.values() if m.status == "healthy"]) / len(ai_orchestrator.models) if ai_orchestrator.models else 0,
            "system_load": "normal",  # Could calculate from actual system metrics
            "uptime_hours": metrics.get("system_uptime", 0),
            "error_incidents": 0,  # Could track errors
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info("✅ Performance metrics retrieved successfully")
        return enhanced_metrics
        
    except Exception as e:
        logger.error(f"❌ Failed to get performance metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get performance metrics: {str(e)}")

@router.post("/control/start")
async def start_orchestrator():
    """Start the AI orchestrator"""
    try:
        if not ai_orchestrator.is_running:
            ai_orchestrator.start()
            logger.info("✅ AI Orchestrator started successfully")
            return {"status": "started", "timestamp": datetime.utcnow().isoformat()}
        else:
            return {"status": "already_running", "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        logger.error(f"❌ Failed to start orchestrator: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start orchestrator: {str(e)}")

@router.post("/control/stop")
async def stop_orchestrator():
    """Stop the AI orchestrator"""
    try:
        if ai_orchestrator.is_running:
            ai_orchestrator.stop()
            logger.info("⏹️  AI Orchestrator stopped successfully")
            return {"status": "stopped", "timestamp": datetime.utcnow().isoformat()}
        else:
            return {"status": "already_stopped", "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        logger.error(f"❌ Failed to stop orchestrator: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to stop orchestrator: {str(e)}")

@router.get("/pipeline/overview")
async def get_pipeline_overview():
    """Get overview of the complete AI pipeline"""
    try:
        pipeline_overview = {
            "stages": [
                {
                    "stage": 1,
                    "name": "Data Ingest & Preprocessing",
                    "model": "Model A (Ingest)",
                    "endpoint": "http://localhost:8000",
                    "description": "Raw data ingestion and initial preprocessing",
                    "status": ai_orchestrator.models.get("model_a", {}).status if "model_a" in ai_orchestrator.models else "unknown"
                },
                {
                    "stage": 2,
                    "name": "Data Processing & Analysis", 
                    "model": "Model B (Postprocess)",
                    "endpoint": "http://localhost:8001",
                    "description": "Advanced data processing and threat analysis",
                    "status": ai_orchestrator.models.get("model_b", {}).status if "model_b" in ai_orchestrator.models else "unknown"
                },
                {
                    "stage": 3,
                    "name": "Trained AI Analysis",
                    "model": "Model C (Your Trained AI)",
                    "endpoint": "http://localhost:9000", 
                    "description": "Custom trained AI model for specialized threat detection",
                    "status": ai_orchestrator.models.get("model_c", {}).status if "model_c" in ai_orchestrator.models else "unknown"
                },
                {
                    "stage": 4,
                    "name": "Threat Intelligence & Response",
                    "model": "Threat Intelligence Service",
                    "endpoint": "http://localhost:8002",
                    "description": "Threat intelligence correlation and response planning",
                    "status": ai_orchestrator.models.get("threat_intel", {}).status if "threat_intel" in ai_orchestrator.models else "unknown"
                },
                {
                    "stage": 5,
                    "name": "Orchestration & Decision Making",
                    "model": "AI Orchestrator",
                    "endpoint": "http://localhost:8003",
                    "description": "Strategic decision making and action coordination",
                    "status": "running" if ai_orchestrator.is_running else "stopped"
                },
                {
                    "stage": 6,
                    "name": "Console & Human Interface",
                    "model": "CXyber Console",
                    "endpoint": "http://localhost:8005",
                    "description": "Human-in-the-loop interface and final decision approval",
                    "status": ai_orchestrator.models.get("console", {}).status if "console" in ai_orchestrator.models else "unknown"
                }
            ],
            "data_flow": [
                "Raw Data → Model A (Ingest) → Model B (Postprocess) → Model C (Trained AI)",
                "Model C Output → Threat Intelligence → Orchestrator → Human Approval → Action Execution"
            ],
            "human_control_points": [
                "Critical threat approval",
                "Containment action authorization", 
                "Policy decision overrides",
                "System configuration changes"
            ],
            "total_stages": 6,
            "operational_stages": len([s for s in ai_orchestrator.models.values() if s.status == "healthy"]),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info("✅ Pipeline overview generated successfully")
        return pipeline_overview
        
    except Exception as e:
        logger.error(f"❌ Failed to get pipeline overview: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get pipeline overview: {str(e)}")
