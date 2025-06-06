# backend/main.py

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
# We no longer need StaticFiles in production since Nginx serves /usr/share/nginx/html
from starlette.responses import FileResponse

# Routers
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

# 1) SessionMiddleware with SameSite=None, Secure=True
SESSION_SECRET = os.getenv("SESSION_SECRET_KEY", "change_this_in_prod")
app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET,
    session_cookie="session",     # you can leave this as default or name it "session"
    same_site="none",             # <─ allow cross‐site sending
    https_only=True               # <─ must be HTTPS
)

# 2) CORS: only allow your exact front‐end origin and credentials
FRONTEND_URL = "https://ai-cyber-fullstack-1020401092050.us-central1.run.app"  # or your Cloud Run URL if you haven’t switched to custom domain yet
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],   # no "*" here
    allow_credentials=True,         # must be True so browser will send session cookie
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3) Include all routers
app.include_router(auth_router)
app.include_router(feed_router)
app.include_router(agents_router)
app.include_router(admin_router)
app.include_router(threats_router)
app.include_router(ws_router)
app.include_router(alert_router)
app.include_router(analytics_router)
app.include_router(slack_router)

# 4) (removed) StaticFiles mount in production – Nginx serves /usr/share/nginx/html

# 5) Catch‐all for React routes (only used if Nginx isn't serving). 
#    In production, Nginx’s default.conf handles it.
@app.get("/{full_path:path}", include_in_schema=False)
async def serve_spa(full_path: str):
    index_path = os.path.join("frontend_build", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"detail": "Not found"}, 404
