#!/usr/bin/env bash
# ────────────────────────────────────────────────────────────────────────────────
# run.sh: Start Nginx (listening on 8080) and then exec Uvicorn on 127.0.0.1:8000
# ────────────────────────────────────────────────────────────────────────────────

set -e

# 1) Start Nginx in the background (reads /etc/nginx/conf.d/default.conf)
service nginx start

# 2) Exec Uvicorn (FastAPI) bound to localhost:8000
#    Using `exec` ensures Uvicorn becomes PID 1 so signals propagate correctly.
exec uvicorn backend.main:app --host 127.0.0.1 --port 8000
