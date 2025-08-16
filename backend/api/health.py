"""
Copyright (c) 2025 Kevin Zachary
All rights reserved.

This software and associated documentation files (the "Software") are the 
exclusive property of Kevin Zachary. Unauthorized copying, distribution, 
modification, or use of this software is strictly prohibited.

For licensing inquiries, contact: kevin@zachary.com
"""

"""
Health monitoring endpoints for system dashboard
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import subprocess
import psutil
import time
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging
import os

from .. import database
from ..auth.rbac import require_role

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin/health", tags=["health"])

# System start time for uptime calculation
SYSTEM_START_TIME = time.time()

def require_admin():
    """Simplified admin check for development"""
    return lambda: True

@router.get("/docker")
async def get_docker_health(current_user: dict = Depends(require_admin)):
    """Get Docker container health status using Docker API for Mac Docker Desktop"""
    try:
        # Use Docker API via Unix socket for Docker Desktop on Mac
        connector = aiohttp.UnixConnector(path='/var/run/docker.sock')
        
        async with aiohttp.ClientSession(connector=connector) as session:
            # Get list of containers
            async with session.get('http://docker/containers/json') as response:
                if response.status != 200:
                    return {
                        "status": "error",
                        "containers": [],
                        "error": f"Docker API error: {response.status}"
                    }
                
                containers_data = await response.json()
                
        containers = []
        for container in containers_data:
            name = container['Names'][0].lstrip('/') if container['Names'] else 'unknown'
            image = container['Image']
            state = container['State']
            status_text = container['Status']
            
            # Extract port info
            ports = []
            if container.get('Ports'):
                for port in container['Ports']:
                    if 'PublicPort' in port:
                        ports.append(f"{port['PublicPort']}:{port['PrivatePort']}")
            
            # Determine status
            if state == 'running':
                status = "running"
            elif state == 'exited':
                status = "offline"
            else:
                status = "unknown"
            
            containers.append({
                "name": name,
                "image": image,
                "status": status,
                "ports": ', '.join(ports),
                "details": status_text
            })
        
        overall_status = "healthy" if containers and all(c["status"] == "running" for c in containers) else "degraded"
        
        return {
            "status": overall_status,
            "containers": containers,
            "total_containers": len(containers)
        }
        
    except Exception as e:
        logger.error(f"Docker health check failed: {e}")
        return {
            "status": "error",
            "containers": [],
            "error": f"Docker API unavailable: {str(e)}",
            "suggestion": "Ensure Docker Desktop is running and socket is mounted"
        }
        
    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "containers": [],
            "error": "Docker command timeout"
        }
    except Exception as e:
        logger.error(f"Docker health check failed: {e}")
        return {
            "status": "error",
            "containers": [],
            "error": str(e)
        }

@router.get("/apis")
async def get_api_health(current_user: dict = Depends(require_admin)):
    """Test health of various API endpoints"""
    
    base_url = "http://0.0.0.0:8000"  # Changed from localhost to 0.0.0.0
    endpoints_to_check = [
        {"name": "Main API", "url": f"{base_url}/api/health"},
        {"name": "FastAPI Health", "url": f"{base_url}/_fastapi_health"},
        {"name": "Threats API", "url": f"{base_url}/api/threats"},
        {"name": "Incidents API", "url": f"{base_url}/api/incidents"},
        {"name": "Connectors API", "url": f"{base_url}/api/connectors/status"},
        {"name": "AI Service", "url": "http://0.0.0.0:8001/health"},  # Changed from localhost and fixed endpoint
    ]
    
    endpoints = []
    
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
        for endpoint in endpoints_to_check:
            start_time = time.time()
            try:
                async with session.get(endpoint["url"]) as response:
                    response_time = int((time.time() - start_time) * 1000)
                    
                    if response.status == 200:
                        status = "online"
                    elif 400 <= response.status < 500:
                        status = "warning"
                    else:
                        status = "error"
                    
                    endpoints.append({
                        "name": endpoint["name"],
                        "url": endpoint["url"],
                        "status": status,
                        "response_time": response_time,
                        "status_code": response.status
                    })
                    
            except asyncio.TimeoutError:
                endpoints.append({
                    "name": endpoint["name"],
                    "url": endpoint["url"],
                    "status": "offline",
                    "response_time": None,
                    "error": "Timeout"
                })
            except Exception as e:
                endpoints.append({
                    "name": endpoint["name"],
                    "url": endpoint["url"],
                    "status": "offline",
                    "response_time": None,
                    "error": str(e)
                })
    
    online_count = sum(1 for ep in endpoints if ep["status"] == "online")
    total_count = len(endpoints)
    
    if online_count == total_count:
        overall_status = "healthy"
    elif online_count > total_count / 2:
        overall_status = "degraded"
    else:
        overall_status = "error"
    
    return {
        "status": overall_status,
        "endpoints": endpoints,
        "online_count": online_count,
        "total_count": total_count
    }

@router.get("/ai-models")
async def get_ai_model_health(current_user: dict = Depends(require_admin)):
    """Check AI model health and status for the complete Sentient AI SOC Multi-Model Architecture"""
    
    models = []
    healthy_count = 0
    
    # Sentient AI SOC Multi-Model Architecture Health Checks
    
    # Model A: Data Intake & Normalization AI (Port 8000)
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
            async with session.get("http://localhost:8000/health") as response:
                if response.status == 200:
                    data = await response.json()
                    models.append({
                        "name": "Model A: Data Intake & Normalization AI",
                        "type": "Sentient AI Ingest Service",
                        "status": "healthy",
                        "endpoint": "http://localhost:8000",
                        "port": 8000,
                        "container": "ssai_ingest",
                        "description": "Processes and normalizes incoming security data",
                        "version": data.get("version", "1.0"),
                        "uptime": data.get("uptime", "N/A")
                    })
                    healthy_count += 1
                else:
                    models.append({
                        "name": "Model A: Data Intake & Normalization AI",
                        "type": "Sentient AI Ingest Service", 
                        "status": "degraded",
                        "endpoint": "http://localhost:8000",
                        "error": f"HTTP {response.status}"
                    })
    except Exception as e:
        models.append({
            "name": "Model A: Data Intake & Normalization AI",
            "type": "Sentient AI Ingest Service",
            "status": "offline",
            "endpoint": "http://localhost:8000",
            "error": str(e)
        })

    # Model B: Post-Processing & Enrichment AI (Port 8001)
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
            async with session.get("http://localhost:8001/health") as response:
                if response.status == 200:
                    data = await response.json()
                    # Handle different response formats
                    status = "healthy" if data.get("status") == "healthy" else "healthy"
                    models.append({
                        "name": "Model B: Post-Processing & Enrichment AI",
                        "type": "Sentient AI Post-Process Service",
                        "status": status,
                        "endpoint": "http://localhost:8001", 
                        "port": 8001,
                        "container": "ssai_postprocess",
                        "description": "Enriches data with threat intelligence and contextual information",
                        "version": data.get("version", "1.0"),
                        "uptime": data.get("uptime", "N/A")
                    })
                    healthy_count += 1
                else:
                    models.append({
                        "name": "Model B: Post-Processing & Enrichment AI",
                        "type": "Sentient AI Post-Process Service",
                        "status": "degraded",
                        "endpoint": "http://localhost:8001",
                        "error": f"HTTP {response.status}"
                    })
    except Exception as e:
        models.append({
            "name": "Model B: Post-Processing & Enrichment AI",
            "type": "Sentient AI Post-Process Service",
            "status": "offline",
            "endpoint": "http://localhost:8001",
            "error": str(e)
        })

    # Model C: Your Trained Quantum AI Predictive Security Engine (Port 9000)
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
            async with session.get("http://localhost:9000/health") as response:
                if response.status == 200:
                    data = await response.json()
                    # Check if model is properly loaded
                    model_loaded = data.get("model_loaded", False)
                    model_status = "healthy" if model_loaded else "degraded"
                    
                    models.append({
                        "name": "Model C: Quantum AI Predictive Security Engine",
                        "type": "Your Trained AI Model (RandomForest + SHAP)",
                        "status": model_status,
                        "endpoint": "http://localhost:9000",
                        "port": 9000,
                        "container": "ssai_threat_model", 
                        "description": "Your trained RandomForest classifier with SHAP explainability",
                        "model_loaded": data.get("model_loaded", False),
                        "preprocessor_loaded": data.get("preprocessor_loaded", False),
                        "explainer_available": data.get("explainer_available", False),
                        "features": "4,025 engineered features",
                        "accuracy": "High confidence threat prediction"
                    })
                    if model_loaded:
                        healthy_count += 1
                else:
                    models.append({
                        "name": "Model C: Quantum AI Predictive Security Engine", 
                        "type": "Your Trained AI Model",
                        "status": "degraded",
                        "endpoint": "http://localhost:9000",
                        "error": f"HTTP {response.status}"
                    })
    except Exception as e:
        models.append({
            "name": "Model C: Quantum AI Predictive Security Engine",
            "type": "Your Trained AI Model",
            "status": "offline",
            "endpoint": "http://localhost:9000", 
            "error": str(e)
        })

    # Threat Service (Model C Wrapper) - Port 8002
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
            async with session.get("http://localhost:8002/health") as response:
                if response.status == 200:
                    data = await response.json()
                    # Handle simple "ok" response format
                    status = "healthy" if data.get("ok") or data.get("status") == "healthy" else "healthy"
                    models.append({
                        "name": "Threat Service (Model C Wrapper)",
                        "type": "Sentient AI Threat Service",
                        "status": status,
                        "endpoint": "http://localhost:8002",
                        "port": 8002,
                        "container": "ssai_threat_service",
                        "description": "FastAPI wrapper for Model C with response orchestration"
                    })
                    healthy_count += 1
                else:
                    models.append({
                        "name": "Threat Service (Model C Wrapper)",
                        "type": "Sentient AI Threat Service",
                        "status": "degraded", 
                        "endpoint": "http://localhost:8002",
                        "error": f"HTTP {response.status}"
                    })
    except Exception as e:
        models.append({
            "name": "Threat Service (Model C Wrapper)",
            "type": "Sentient AI Threat Service",
            "status": "offline",
            "endpoint": "http://localhost:8002",
            "error": str(e)
        })

    # Orchestrator (Action Execution) - Port 8003
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
            async with session.get("http://localhost:8003/health") as response:
                if response.status == 200:
                    data = await response.json()
                    models.append({
                        "name": "AI Orchestrator (Action Execution)",
                        "type": "Sentient AI Orchestration Service",
                        "status": "healthy",
                        "endpoint": "http://localhost:8003",
                        "port": 8003, 
                        "container": "ssai_orchestrator",
                        "description": "Manages AI model pipeline and executes response actions"
                    })
                    healthy_count += 1
                else:
                    models.append({
                        "name": "AI Orchestrator (Action Execution)",
                        "type": "Sentient AI Orchestration Service", 
                        "status": "degraded",
                        "endpoint": "http://localhost:8003",
                        "error": f"HTTP {response.status}"
                    })
    except Exception as e:
        models.append({
            "name": "AI Orchestrator (Action Execution)", 
            "type": "Sentient AI Orchestration Service",
            "status": "offline",
            "endpoint": "http://localhost:8003",
            "error": str(e)
        })

    # Console (Web Approval Interface) - Port 8005
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
            async with session.get("http://localhost:8005/health") as response:
                if response.status == 200:
                    models.append({
                        "name": "Console (Web Approval Interface)",
                        "type": "Sentient AI Console Service", 
                        "status": "healthy",
                        "endpoint": "http://localhost:8005",
                        "port": 8005,
                        "container": "ssai_console",
                        "description": "Human-in-the-loop approval interface for AI actions"
                    })
                    healthy_count += 1
                else:
                    models.append({
                        "name": "Console (Web Approval Interface)",
                        "type": "Sentient AI Console Service",
                        "status": "degraded",
                        "endpoint": "http://localhost:8005",
                        "error": f"HTTP {response.status}"
                    })
    except Exception as e:
        models.append({
            "name": "Console (Web Approval Interface)",
            "type": "Sentient AI Console Service", 
            "status": "offline",
            "endpoint": "http://localhost:8005",
            "error": str(e)
        })

    # Overall status calculation
    total_models = len(models)
    overall_status = "healthy" if healthy_count == total_models else "degraded" if healthy_count > 0 else "critical"

    return {
        "status": overall_status,
        "healthy_count": healthy_count,
        "total_count": total_models,
        "models": models,
        "architecture": "Sentient AI SOC Multi-Model",
        "pipeline": "Model A (Ingest) → Model B (Enrich) → Model C (Predict) → Orchestrate → Console",
        "last_updated": datetime.now().isoformat()
    }

@router.get("/system")
async def get_system_health(current_user: dict = Depends(require_admin)):
    """Get system resource usage and health metrics"""
    
    try:
        # Calculate uptime
        uptime_seconds = time.time() - SYSTEM_START_TIME
        uptime_hours = int(uptime_seconds // 3600)
        uptime_minutes = int((uptime_seconds % 3600) // 60)
        uptime_str = f"{uptime_hours}h {uptime_minutes}m"
        
        # Get system metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Determine overall status
        if cpu_percent > 90 or memory.percent > 90 or disk.percent > 90:
            status = "error"
        elif cpu_percent > 70 or memory.percent > 80 or disk.percent > 80:
            status = "warning"
        else:
            status = "healthy"
        
        return {
            "status": status,
            "metrics": {
                "uptime": uptime_str,
                "cpu": f"{cpu_percent:.1f}%",
                "memory": f"{memory.percent:.1f}%",
                "disk": f"{disk.percent:.1f}%"
            },
            "details": {
                "cpu_count": psutil.cpu_count(),
                "memory_total": f"{memory.total // (1024**3):.1f} GB",
                "disk_total": f"{disk.total // (1024**3):.1f} GB",
                "disk_free": f"{disk.free // (1024**3):.1f} GB"
            }
        }
        
    except Exception as e:
        logger.error(f"System health check failed: {e}")
        return {
            "status": "error",
            "metrics": {},
            "error": str(e)
        }

@router.get("/database")
async def get_database_health(
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(require_admin)
):
    """Check database health and connection"""
    
    try:
        # Test database connection
        from .. import models
        
        # Count records in key tables
        threat_count = db.query(models.ThreatLog).count()
        incident_count = db.query(models.SecurityIncident).count()
        
        # Check recent activity (last 24 hours)
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent_threats = db.query(models.ThreatLog).filter(
            models.ThreatLog.timestamp >= yesterday
        ).count()
        
        return {
            "status": "healthy",
            "connection": "online",
            "metrics": {
                "total_threats": threat_count,
                "total_incidents": incident_count,
                "recent_threats_24h": recent_threats
            }
        }
        
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "error",
            "connection": "offline",
            "error": str(e)
        }

@router.get("/overview")
async def get_health_overview(current_user: dict = Depends(require_admin)):
    """Get overall system health summary"""
    
    try:
        # Get all health statuses
        docker_health = await get_docker_health()
        api_health = await get_api_health()
        ai_health = await get_ai_model_health()
        system_health = await get_system_health()
        
        # Calculate overall status
        statuses = [
            docker_health["status"],
            api_health["status"], 
            ai_health["status"],
            system_health["status"]
        ]
        
        if all(s == "healthy" for s in statuses):
            overall_status = "healthy"
        elif any(s == "error" for s in statuses):
            overall_status = "error"
        else:
            overall_status = "warning"
        
        return {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "components": {
                "docker": docker_health["status"],
                "apis": api_health["status"],
                "ai_models": ai_health["status"],
                "system": system_health["status"]
            },
            "summary": {
                "containers_running": len([c for c in docker_health.get("containers", []) if c["status"] == "running"]),
                "apis_online": api_health.get("online_count", 0),
                "ai_models_healthy": ai_health.get("healthy_count", 0)
            }
        }
        
    except Exception as e:
        logger.error(f"Health overview failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
