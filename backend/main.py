# backend/main.py
import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse, FileResponse
from starlette.middleware.sessions import SessionMiddleware

# (We assume each of these modules defines `router = APIRouter()`.)
from backend.auth.auth import router as auth_router
from backend.threat_feed import router as feed_router
from backend.agents import router as agents_router
from backend.api.admin import router as admin_router
from backend.api.threats import router as threats_router
from backend.app.websocket.threats import router as ws_router
from backend.alerting import router as alert_router
from backend.analytics import router as analytics_router
from backend.slack_alert import router as slack_router

app = FastAPI()

# 1) SESSION + CORS (unchanged)
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET", "supersecretkey"))
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # in production, restrict to https://quantum-ai.asia
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2) Include your existing API routers under /api/...
app.include_router(auth_router, prefix="/api/auth")
app.include_router(feed_router, prefix="/api/threat_feed")
app.include_router(agents_router, prefix="/api/agents")
app.include_router(admin_router, prefix="/api/admin")
app.include_router(threats_router, prefix="/api/threats")
app.include_router(ws_router, prefix="/api/ws")
app.include_router(alert_router, prefix="/api/alerting")
app.include_router(analytics_router, prefix="/api/analytics")
app.include_router(slack_router, prefix="/api/slack")

# 3) (OPTIONAL) A “predictive AI” endpoint stub under /api/predict
from backend.predictive import router as predictive_router
app.include_router(predictive_router, prefix="/api/predict")

# 4) Serve static React build files
#    We assume that after you build React, all files live under `/app/frontend_build`
#    (we’ll show how to copy that folder into the container later).
app.mount("/static", StaticFiles(directory="frontend_build/static"), name="static")

# 5) Catch-all: for any path not starting with /api or /static, return index.html.
@app.get("/{full_path:path}", include_in_schema=False)
async def serve_spa(full_path: str):
    index_path = os.path.join("frontend_build", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    else:
        # If index.html is missing, return a 404
        raise HTTPException(status_code=404, detail="Frontend build not found")
