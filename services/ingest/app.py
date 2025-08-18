
from fastapi import FastAPI, Body, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Union, Dict, Any
from schemas import FeatureVector
from normalizer import load_mapping, normalize
from enrichers import enrich_and_featureize
from app_router import r
import subprocess
import psutil
import time

app = FastAPI(title="Ingest Service (AI Router)", version="0.2.0")

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(r)

@app.post("/ingest/{source}", response_model=FeatureVector)
def ingest_and_transform(
    source: str,
    payload: Union[Dict[str, Any], str] = Body(..., description="JSON dict or raw syslog line"),
    ip_rep_score: int | None = Query(default=None),
    cvss_score: float | None = Query(default=None),
    asset_criticality: float | None = Query(default=None),
    anomaly_hint: int | None = Query(default=None)
) -> FeatureVector:
    mapping = load_mapping(source)
    ce = normalize(payload, mapping)
    fv = enrich_and_featureize(ce, ip_rep_score, cvss_score, asset_criticality, anomaly_hint)
    return fv

# Health endpoints for the dashboard
@app.get("/api/admin/health/docker")
async def get_docker_health():
    """Docker containers health status - Using Docker API for Mac Docker Desktop"""
    try:
        import aiohttp
        import json
        
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
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Docker health check failed: {e}")
        return {
            "status": "unavailable",
            "containers": [],
            "error": f"Docker API unavailable: {str(e)}",
            "suggestion": "Ensure Docker Desktop is running and socket is mounted"
        }

@app.get("/api/admin/health/system")
def get_system_health():
    """System metrics and health - Real implementation"""
    try:
        # Calculate uptime (approximate - since app start)
        if not hasattr(get_system_health, 'start_time'):
            get_system_health.start_time = time.time()
        
        uptime_seconds = time.time() - get_system_health.start_time
        uptime_hours = int(uptime_seconds // 3600)
        uptime_minutes = int((uptime_seconds % 3600) // 60)
        uptime_str = f"{uptime_hours}h {uptime_minutes}m"
        
        # Get real system metrics
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
        return {
            "status": "error",
            "metrics": {},
            "error": f"Failed to get system metrics: {str(e)}"
        }

@app.get("/api/admin/health/apis")
def get_apis_health():
    """API endpoints health status - Real implementation"""
    import requests
    
    endpoints_to_check = [
        {"name": "Main API", "url": "http://localhost:8000/health"},
        {"name": "Threats API", "url": "http://ssai_postprocess:8000/api/threats"},
        {"name": "Incidents API", "url": "http://ssai_postprocess:8000/api/incidents"},
        {"name": "AI Service", "url": "http://ssai_threat_service:8002/health"},
    ]
    
    endpoints = []
    
    for endpoint in endpoints_to_check:
        try:
            start_time = time.time()
            response = requests.get(endpoint["url"], timeout=5)
            response_time = int((time.time() - start_time) * 1000)
            
            if response.status_code == 200:
                status = "online"
            elif 400 <= response.status_code < 500:
                status = "warning"
            else:
                status = "error"
            
            endpoints.append({
                "name": endpoint["name"],
                "url": endpoint["url"],
                "status": status,
                "response_time": f"{response_time}ms",
                "status_code": response.status_code
            })
            
        except requests.Timeout:
            endpoints.append({
                "name": endpoint["name"],
                "url": endpoint["url"],
                "status": "offline",
                "response_time": "timeout",
                "error": "Timeout"
            })
        except Exception as e:
            endpoints.append({
                "name": endpoint["name"],
                "url": endpoint["url"],
                "status": "offline",
                "response_time": "error",
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

@app.get("/health")
def health():
    """Basic health check"""
    return {"status": "ok", "service": "ingest-service"}

@app.get("/api/admin/health/system")
async def get_system_health():
    """System metrics and health - Real implementation"""
    try:
        # Calculate uptime (approximate - since app start)
        if not hasattr(get_system_health, 'start_time'):
            get_system_health.start_time = time.time()
        
        uptime_seconds = time.time() - get_system_health.start_time
        uptime_hours = int(uptime_seconds // 3600)
        uptime_minutes = int((uptime_seconds % 3600) // 60)
        uptime_str = f"{uptime_hours}h {uptime_minutes}m"
        
        # Get real system metrics
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
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"System health check failed: {e}")
        return {
            "status": "error",
            "metrics": {},
            "error": str(e)
        }

@app.get("/api/admin/health/apis")
async def get_api_health():
    """Test health of various API endpoints"""
    import aiohttp
    import asyncio
    
    endpoints_to_check = [
        {"name": "Main API", "url": "http://localhost:8000/health"},
        {"name": "Threats API", "url": "http://ssai_postprocess:8000/api/threats"}, 
        {"name": "Incidents API", "url": "http://ssai_postprocess:8000/api/incidents"},
        {"name": "AI Service", "url": "http://ssai_threat_service:8002/health"}
    ]
    
    endpoints = []
    
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
        for endpoint in endpoints_to_check:
            start_time = time.time()
            try:
                async with session.get(endpoint["url"]) as response:
                    response_time = f"{int((time.time() - start_time) * 1000)}ms"
                    
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

@app.get("/api/admin/health/ai-models")
async def get_ai_models_health():
    """Check AI model health status"""
    import aiohttp
    import asyncio
    
    models = []
    healthy_count = 0
    
    model_checks = [
        {"name": "Model A: Data Intake & Normalization AI", "url": "http://ssai_ingest:8000/health", "port": 8000},
        {"name": "Model B: Post-Processing & Enrichment AI", "url": "http://ssai_postprocess:8000/health", "port": 8001},
        {"name": "Model C: Sentient AI Predictive Security Engine", "url": "http://ssai_threat_model:8001/health", "port": 9000},
        {"name": "Threat Service", "url": "http://ssai_threat_service:8002/health", "port": 8002},
        {"name": "Orchestrator", "url": "http://ssai_orchestrator:8003/health", "port": 8003},
        {"name": "Console", "url": "http://ssai_console:8005/health", "port": 8005}
    ]
    
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
        for model in model_checks:
            try:
                async with session.get(model["url"]) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Special handling for Model C (Sentient AI Predictive Security Engine)
                        if "Sentient AI Predictive Security Engine" in model["name"]:
                            model_loaded = data.get("model_loaded", False)
                            preprocessor_loaded = data.get("preprocessor_loaded", False)
                            explainer_available = data.get("explainer_available", False)
                            
                            # All components must be loaded for healthy status
                            all_loaded = model_loaded and preprocessor_loaded and explainer_available
                            status = "healthy" if all_loaded else "degraded"
                            
                            models.append({
                                "name": model["name"],
                                "status": status,
                                "endpoint": model["url"],
                                "port": model["port"],
                                "sub_modules": {
                                    "RandomForest Model": "Loaded" if model_loaded else "Missing",
                                    "Preprocessor": "Loaded" if preprocessor_loaded else "Missing",
                                    "SHAP Explainer": "Loaded" if explainer_available else "Missing"
                                },
                                "model_loaded": model_loaded,
                                "preprocessor_loaded": preprocessor_loaded,
                                "explainer_available": explainer_available,
                                "features": "4,025 engineered features" if all_loaded else "N/A"
                            })
                            if all_loaded:
                                healthy_count += 1
                        else:
                            # Standard handling for other models
                            models.append({
                                "name": model["name"],
                                "status": "healthy",
                                "endpoint": model["url"],
                                "port": model["port"]
                            })
                            healthy_count += 1
                    else:
                        # Error response handling
                        if "Sentient AI Predictive Security Engine" in model["name"]:
                            models.append({
                                "name": model["name"],
                                "status": "degraded",
                                "endpoint": model["url"],
                                "error": f"HTTP {response.status}",
                                "sub_modules": {
                                    "RandomForest Model": "Missing",
                                    "Preprocessor": "Missing",
                                    "SHAP Explainer": "Missing"
                                }
                            })
                        else:
                            models.append({
                                "name": model["name"],
                                "status": "degraded",
                                "endpoint": model["url"],
                                "error": f"HTTP {response.status}"
                            })
            except Exception as e:
                # Exception handling
                if "Sentient AI Predictive Security Engine" in model["name"]:
                    models.append({
                        "name": model["name"],
                        "status": "offline",
                        "endpoint": model["url"],
                        "error": str(e),
                        "sub_modules": {
                            "RandomForest Model": "Missing",
                            "Preprocessor": "Missing",
                            "SHAP Explainer": "Missing"
                        }
                    })
                else:
                    models.append({
                        "name": model["name"],
                        "status": "offline",
                        "endpoint": model["url"],
                        "error": str(e)
                    })
    
    total_models = len(models)
    overall_status = "healthy" if healthy_count == total_models else "degraded" if healthy_count > 0 else "critical"
    
    return {
        "status": overall_status,
        "models": models,
        "healthy_count": healthy_count,
        "total_count": total_models
    }
