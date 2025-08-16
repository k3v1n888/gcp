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

import os
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

# --- Import all application routers ---
from backend.auth.auth import router as auth_router
from backend.threat_feed import router as feed_router
from backend.agents import router as agents_router
from backend.api.admin import router as admin_router
from backend.api.threats import router as threats_router
from backend.api.incidents import router as incidents_router
from backend.api.ai_incidents import router as ai_incidents_router  # New AI incidents API
from backend.app.websocket.threats import router as ws_router
from backend.alerting import router as alert_router
from backend.analytics import router as analytics_router
from backend.slack_alert import router as slack_router
from backend.routers.log_receiver import router as log_receiver_router
from backend.routers.correlation import router as correlation_router
from backend.routers.predictive import router as predictive_router
from backend.routers.forecasting import router as forecasting_router
from backend.routers.chat import router as chat_router
from backend.routers.webhooks import router as webhook_router
from backend.api.graph import router as graph_router
from backend.api.hunting import router as hunting_router
from backend.api.health import router as health_router  # 🏥 System Health Monitoring
from backend.api.incident_aggregation import router as incident_aggregation_router  # 🔗 AI Incident Aggregation
from backend.connectors.api import router as connectors_router  # 🔌 Universal Data Connector API
from backend.routers.ai_routes import router as ai_routes_router  # 🤖 AI System Management API
# from backend.api.orchestrator import router as orchestrator_router  # 🎭 AI Orchestration Control API

# --- Import project components ---
from backend.models import Base, engine
from backend.database import SessionLocal
from backend.ml.prediction import SeverityPredictor
from backend.forecasting_service import ThreatForecaster
from backend.forecasting_service_safe import SafeThreatForecaster
from backend.anomaly_service import AnomalyDetector
from backend.graph_service import GraphService
from backend.threat_feed import fetch_and_save_threat_feed
from backend.wazuh_service import fetch_and_save_wazuh_alerts
from backend.threatmapper_service import fetch_and_save_threatmapper_vulns
from backend.incident_service import correlate_logs_into_incidents
from backend.ai_scheduler import start_ai_incident_scheduler, stop_ai_incident_scheduler  # AI orchestrator
from backend.ai_orchestrator import ai_orchestrator  # 🤖 AI System Orchestrator
from backend.connectors.scheduler import start_connector_scheduler, stop_connector_scheduler  # 🔌 Universal Data Connector Scheduler

# Create tables
Base.metadata.create_all(bind=engine)

async def periodic_data_ingestion():
    """Runs all data ingestion and correlation services on a schedule."""
    while True:
        db = SessionLocal()
        try:
            print("Running periodic data ingestion and correlation...")
            fetch_and_save_threat_feed(db)
            fetch_and_save_wazuh_alerts(db)
            fetch_and_save_threatmapper_vulns(db)
            # Legacy basic correlation - AI orchestrator now handles advanced incident creation
            correlate_logs_into_incidents(db)
            print("Data ingestion and correlation complete.")
        finally:
            db.close()
        await asyncio.sleep(3600)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting Sentient AI Threat Detection System...")
    
    try:
        # Initialize services with safe error handling
        app.state.predictor = SeverityPredictor()
        
        # Use safe forecaster that won't break the app
        app.state.safe_forecaster = SafeThreatForecaster()
        
        # Keep the original forecaster for backward compatibility (optional)
        try:
            app.state.forecaster = ThreatForecaster()
        except Exception as e:
            print(f"⚠️ Original forecaster unavailable: {e}")
            app.state.forecaster = None
        
        app.state.anomaly_detector = AnomalyDetector()
        app.state.graph_service = GraphService()
        
        # 🚀 Start AI Incident Orchestration Scheduler
        try:
            start_ai_incident_scheduler()
            print("🤖 AI Incident Orchestration Scheduler started (using Sentient AI)")
        except Exception as scheduler_error:
            print(f"⚠️ AI Scheduler initialization failed: {scheduler_error}")
        
        # 🔌 Start Universal Data Connector Scheduler
        try:
            start_connector_scheduler()
            print("🔌 Universal Data Connector Scheduler started")
        except Exception as connector_error:
            print(f"⚠️ Connector Scheduler initialization failed: {connector_error}")
        
        # 🤖 Start AI Orchestrator
        try:
            ai_orchestrator.start()
            print("🤖 AI Orchestration System started")
        except Exception as orchestrator_error:
            print(f"⚠️ AI Orchestrator initialization failed: {orchestrator_error}")
        
        # Start the periodic data ingestion
        asyncio.create_task(periodic_data_ingestion())
        print("✅ Services initialized")
    except Exception as e:
        print(f"⚠️ Warning: Could not initialize services: {e}")
        # Ensure at least the safe forecaster is available
        try:
            app.state.safe_forecaster = SafeThreatForecaster()
            print("✅ Safe forecaster initialized as fallback")
        except Exception as fallback_error:
            print(f"❌ Critical: Could not initialize fallback services: {fallback_error}")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down...")
    
    # Stop AI Incident Scheduler
    try:
        stop_ai_incident_scheduler()
        print("🤖 AI Incident Scheduler stopped")
    except Exception as e:
        print(f"⚠️ Error stopping AI scheduler: {e}")
    
    # Stop Universal Data Connector Scheduler
    try:
        stop_connector_scheduler()
        print("🔌 Universal Data Connector Scheduler stopped")
    except Exception as e:
        print(f"⚠️ Error stopping connector scheduler: {e}")
    
    # Stop AI Orchestrator
    try:
        ai_orchestrator.stop()
        print("🤖 AI Orchestration System stopped")
    except Exception as e:
        print(f"⚠️ Error stopping AI orchestrator: {e}")
    
    if hasattr(app.state, 'graph_service'):
        app.state.graph_service.close()

app = FastAPI(lifespan=lifespan)

SESSION_SECRET = os.getenv("SESSION_SECRET_KEY", "change_this_in_prod")
app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET,
    https_only=False,  # Allow HTTP in development
    same_site="lax",   # More permissive for development
    max_age=86400
)

# Development-aware CORS configuration
allowed_origins = [
    "https://ai-cyber-fullstack-1020401092050.us-central1.run.app",
    "https://qai.quantum-ai.asia"
]

# Add development origins if in development mode
if os.getenv("DEV_MODE") == "true" or os.getenv("DISABLE_GOOGLE_AUTH") == "true":
    dev_origins = [
        "http://192.168.64.13:3000",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://0.0.0.0:3000"
    ]
    allowed_origins.extend(dev_origins)
    print("🔧 Development mode: Added dev origins to CORS:", dev_origins)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(feed_router)
app.include_router(agents_router)
app.include_router(admin_router)
app.include_router(threats_router)
app.include_router(incidents_router)
app.include_router(ai_incidents_router)  # 🤖 AI-powered incident management
app.include_router(ws_router)
app.include_router(alert_router)
app.include_router(analytics_router)
app.include_router(slack_router)
app.include_router(log_receiver_router)
app.include_router(correlation_router)
app.include_router(predictive_router)
app.include_router(forecasting_router)
app.include_router(chat_router)
app.include_router(webhook_router)
app.include_router(graph_router)
app.include_router(hunting_router)
app.include_router(health_router)  # 🏥 System Health Monitoring
app.include_router(incident_aggregation_router)  # 🔗 AI Incident Aggregation
app.include_router(connectors_router)  # 🔌 Universal Data Connector System
app.include_router(ai_routes_router)  # 🤖 AI System Management API
# app.include_router(orchestrator_router)  # 🎭 AI Orchestration Control API

@app.get("/_fastapi_health")
def fastapi_health():
    return {"status": "ok"}

@app.get("/api/health")
def api_health():
    return {"status": "ok", "environment": "development" if os.getenv("DEV_MODE") == "true" else "production"}

@app.get("/")
def root():
    return {"message": "Sentient AI Security Platform API", "status": "operational"}