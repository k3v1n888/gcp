#!/usr/bin/env bash
# ───────────────────────────────────────────────────────────────────────────────
# run.sh: Start Nginx (port 80) and Uvicorn (port 8000)
# ───────────────────────────────────────────────────────────────────────────────

# 1) Start Nginx in the background
service nginx start

# 2) Start Uvicorn (FastAPI) bound to 127.0.0.1:8000
uvicorn backend.main:app --host 127.0.0.1 --port 8000
