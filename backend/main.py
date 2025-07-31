import os
import asyncio
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware

# --- Import all application routers ---
from backend.auth.auth import router as auth_router
from backend.threat_feed import router as feed_router
from backend.agents import router as agents_router
from backend.api.admin import router as admin_router
from backend.api.threats import router as threats_router
from backend.api.incidents import router as incidents_router
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
# --- THIS IS THE FIX: Correctly import the 'router' object from the modules ---
from backend.api.graph import router as graph_router
from backend.api.hunting import router as hunting_router

# --- Import project components ---
from backend.models import Base, engine
from backend.database import SessionLocal
from backend.ml.prediction import SeverityPredictor
from backend.forecasting_service import ThreatForecaster
from backend.anomaly_service import AnomalyDetector
from backend.graph_service import GraphService
from backend.threat_feed import fetch_and_save_threat_feed
from backend.wazuh_service import fetch_and_save_wazuh_alerts
from backend.threatmapper_service import fetch_and_save_threatmapper_vulns
from backend.incident_service import correlate_logs_into_incidents

app = FastAPI()

async def periodic_data_ingestion():
    """Runs all data ingestion and correlation services on a schedule."""
    while True:
        db = SessionLocal()
        try:
            print("Running periodic data ingestion and correlation...")
            fetch_and_save_threat_feed(db)
            fetch_and_save_wazuh_alerts(db)
            fetch_and_save_threatmapper_vulns(db)
            correlate_logs_into_incidents(db)
            print("Data ingestion and correlation complete.")
        finally:
            db.close()
        await asyncio.sleep(3600)

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    app.state.predictor = SeverityPredictor()
    app.state.forecaster = ThreatForecaster()
    app.state.anomaly_detector = AnomalyDetector()
    app.state.graph_service = GraphService()
    asyncio.create_task(periodic_data_ingestion())

@app.on_event("shutdown")
def on_shutdown():
    app.state.graph_service.close()

SESSION_SECRET = os.getenv("SESSION_SECRET_KEY", "change_this_in_prod")
app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET,
    https_only=True,
    same_site="none",
    max_age=86400
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://ai-cyber-fullstack-1020401092050.us-central1.run.app",
        "https://qai.quantum-ai.asia"
    ],
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

@app.get("/_fastapi_health")
def fastapi_health():
    return {"status": "ok"}