# backend/main.py

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
from starlette.middleware.sessions import SessionMiddleware

# Import each router (must define `router = APIRouter()` inside)
from backend.auth.auth import router as auth_router
from backend.threat_feed import router as feed_router
from backend.agents import router as agents_router
from backend.api.admin import router as admin_router
from backend.api.threats import router as threats_router
from backend.app.websocket.threats import router as ws_router
from backend.alerting import router as alert_router
from backend.analytics import router as analytics_router
from backend.slack_alert import router as slack_router

# Import the predictive AI stub router
from backend.predictive import router as predictive_router

app = FastAPI()

# 1) Session + CORS middleware
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET", "supersecretkey"))
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://quantum-ai.asia"],  # Production: restrict to your custom domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2) Include your API routers under /api/... prefixes
app.include_router(auth_router, prefix="/api/auth")
app.include_router(feed_router, prefix="/api/threat_feed")
app.include_router(agents_router, prefix="/api/agents")
app.include_router(admin_router, prefix="/api/admin")
app.include_router(threats_router, prefix="/api/threats")
app.include_router(ws_router, prefix="/api/ws")
app.include_router(alert_router, prefix="/api/alerting")
app.include_router(analytics_router, prefix="/api/analytics")
app.include_router(slack_router, prefix="/api/slack")
app.include_router(predictive_router, prefix="/api/predict")

# 3) Mount static React build files under /static
#    (When building, the Dockerfile will copy React’s `build/` → /usr/share/nginx/html,
#     and Nginx will serve `/static/*` from there.)
app.mount("/static", StaticFiles(directory="frontend_build/static"), name="static")

# 4) Catch‐all: any route not under /api or /static → return index.html
@app.get("/{full_path:path}", include_in_schema=False)
async def serve_spa(full_path: str):
    index_path = os.path.join("frontend_build", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    raise HTTPException(status_code=404, detail="Frontend build not found")
