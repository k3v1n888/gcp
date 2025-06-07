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
app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET,
    https_only=False,  # <--- Make sure this is TRUE
    #samesite="none",  # <--- Make sure this is "none" (string literal)
    # If the issue persists, you *may* need to uncomment and adjust the domain.
    # For a Cloud Run managed domain like *.run.app, it might work without it.
    # If you use a custom domain like quantum-ai.asia, you might need:
    # domain=".quantum-ai.asia",
)

# 2) CORS middleware (only needed if front and API are on different origins during dev)
app.add_middleware(
    CORSMiddleware,
    # IMPORTANT: In production, specify your exact frontend URL(s)
    allow_origins=[
        "https://ai-cyber-fullstack-1020401092050.us-central1.run.app", # Your Cloud Run frontend URL
        "https://quantum-ai.asia" # Your custom domain, if applicable
    ],
    allow_credentials=True, # Allow cookies to be sent
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

# backend/main.py (add near the bottom)

@app.get("/_fastapi_health")
def fastapi_health():
    return {"status": "ok"}

# Local‐dev only: serve React’s static build if you want to run uvicorn directly.
# In production, Nginx already serves /usr/share/nginx/html.
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

# backend/main.py

# ... (existing code) ...

@app.get("/_debug_env")
def debug_env():
    """
    TEMPORARY DEBUG ENDPOINT: Dumps all environment variables.
    REMOVE IMMEDIATELY AFTER DEBUGGING.
    """
    return {"environment_variables": dict(os.environ)}

# ... (existing app.mount, etc.) ...

