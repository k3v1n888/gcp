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
from backend.app.websocket.threats import router as ws_router
from backend.alerting import router as alert_router
from backend.analytics import router as analytics_router
from backend.slack_alert import router as slack_router
from backend.routers.log_receiver import router as log_receiver_router
from backend.routers.correlation import router as correlation_router
from backend.routers.predictive import router as predictive_router
from backend.routers.forecasting import router as forecasting_router
from backend.routers.chat import router as chat_router
# --- 1. Import the new webhook router ---
from backend.routers import webhooks as webhook_router

# --- Import project components ---
from backend.models import Base, engine
from backend.database import SessionLocal
from backend.ml.prediction import SeverityPredictor
from backend.forecasting_service import ThreatForecaster
from backend.anomaly_service import AnomalyDetector
from backend.threat_feed import fetch_and_save_threat_feed
# --- 2. REMOVE the old Wazuh and ThreatMapper service imports ---
# from backend.wazuh_service import fetch_and_save_wazuh_alerts
from backend.threatmapper_service import fetch_and_save_threatmapper_vulns

app = FastAPI()

# --- Updated background task (Wazuh call removed) ---
async def periodic_data_ingestion():
    """Runs data ingestion services on a schedule."""
    while True:
        db = SessionLocal()
        try:
            print("Running periodic data ingestion...")
            fetch_and_save_threat_feed(db)      # Maltiverse
            fetch_and_save_threatmapper_vulns(db) # ThreatMapper
            print("Data ingestion complete.")
        finally:
            db.close()
        await asyncio.sleep(3600)

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    app.state.predictor = SeverityPredictor()
    app.state.forecaster = ThreatForecaster()
    app.state.anomaly_detector = AnomalyDetector()
    asyncio.create_task(periodic_data_ingestion())

# --- Middleware configuration (no changes) ---
# ...

# --- Include all the routers ---
app.include_router(auth_router)
app.include_router(feed_router)
app.include_router(agents_router)
app.include_router(admin_router)
app.include_router(threats_router)
app.include_router(ws_router)
app.include_router(alert_router)
app.include_router(analytics_router)
app.include_router(slack_router)
app.include_router(log_receiver_router)
app.include_router(correlation_router)
app.include_router(predictive_router)
app.include_router(forecasting_router)
app.include_router(chat_router)
# --- 3. Include the new webhook router ---
app.include_router(webhook_router)

@app.get("/_fastapi_health")
def fastapi_health():
    return {"status": "ok"}