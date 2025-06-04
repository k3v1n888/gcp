# backend/main.py

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse

# Import routers
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

# 1) Session middleware (so that `request.session` works)
SESSION_SECRET = os.getenv("SESSION_SECRET_KEY", "change_this_in_prod")
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET)

# 2) CORS middleware (adjust “allow_origins” to your exact domain in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://quantum-ai.asia"],  # or ["*"] while testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3) Include routers
app.include_router(auth_router)
app.include_router(feed_router)
app.include_router(agents_router)
app.include_router(admin_router)
app.include_router(threats_router)
app.include_router(ws_router)
app.include_router(alert_router)
app.include_router(analytics_router)
app.include_router(slack_router)

# 4) Serve static React files (Nginx will handle this in production, but in development you can do this)
#commented to remove development 
#app.mount("/static", StaticFiles(directory="frontend_build/static"), name="static")

# 5) Catch-all for browser‐refresh on React routes
@app.get("/{full_path:path}", include_in_schema=False)
async def serve_spa(full_path: str):
    index_path = os.path.join("frontend_build", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"detail": "Not found"}, 404
