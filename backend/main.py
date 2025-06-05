# backend/main.py

import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
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

# 1) Session middleware (for request.session)
SESSION_SECRET = os.getenv("SESSION_SECRET_KEY", "change_this_in_prod")
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET)

# 2) CORS middleware (only needed if front and API are on different origins during dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # in production you can lock this to ["https://quantum-ai.asia"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3) Include all the routers
app.include_router(auth_router)
app.include_router(feed_router)
app.include_router(agents_router)
app.include_router(admin_router)
app.include_router(threats_router)
app.include_router(ws_router)
app.include_router(alert_router)
app.include_router(analytics_router)
app.include_router(slack_router)

# 4) Local‐dev only: serve React’s static build if you want to run uvicorn directly.
#    In production, Nginx already serves /usr/share/nginx/html.
# Uncomment the following when testing locally (and ensure that you have built React into "frontend/build").
#
# from fastapi.staticfiles import StaticFiles
# app.mount("/static", StaticFiles(directory="frontend/build/static"), name="static")
#
# @app.get("/{full_path:path}", include_in_schema=False)
# async def serve_spa(full_path: str):
#     # This finds "frontend/build/index.html" and returns it for any unrecognized path.
#     index_path = os.path.join("frontend", "build", "index.html")
#     if os.path.exists(index_path):
#         return FileResponse(index_path)
#     raise HTTPException(status_code=404, detail="Not Found")

# 5) If you do NOT want local‐dev fallback, you can remove the above block entirely.
