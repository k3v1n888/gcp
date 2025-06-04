#!/usr/bin/env bash
# ────────────────────────────────────────────────────────────────────────────────
# run.sh: Start Nginx on port 8080, then start Uvicorn on 127.0.0.1:8000
# ────────────────────────────────────────────────────────────────────────────────

set -x
echo ">>> run.sh: launching Nginx…"
service nginx start

echo ">>> run.sh: launching Uvicorn…"
ls -l /usr/local/bin/uvicorn

# The 'exec' ensures Uvicorn becomes PID 1 (so signals get forwarded correctly).
# Adjust the path if you installed Uvicorn somewhere else, but in our image it lives at /usr/local/bin/uvicorn
exec /usr/local/bin/uvicorn backend.main:app --host 127.0.0.1 --port 8000