#!/usr/bin/env bash
# ────────────────────────────────────────────────────────────────────────────────
# run.sh: Start Nginx (listening on 8080) and then start Uvicorn (FastAPI) on 127.0.0.1:8000
# ────────────────────────────────────────────────────────────────────────────────

# 1) Start Nginx in the background (it will read /etc/nginx/conf.d/default.conf)
service nginx start

# 2) Start Uvicorn (FastAPI) bound to localhost:8000
uvicorn backend.main:app --host 127.0.0.1 --port 8000
