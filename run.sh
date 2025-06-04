#!/usr/bin/env bash
################################################################################
# run.sh: start Nginx (listening on 8080) in the background, then exec Uvicorn
################################################################################

set -e

echo ">>> run.sh: launching Nginx..."
service nginx start

echo ">>> run.sh: launching Uvicorn..."
# Exec uvicorn so that signal handling is correct
exec /usr/local/bin/uvicorn backend.main:app --host 127.0.0.1 --port 8000