#!/usr/bin/env bash
#
# Simplified startup without timestamp fix
#

set -eux

echo "Starting Quantum AI Platform..."

# 1) Start Nginx in the foreground
nginx -g 'daemon off;' &

# 2) Give Nginx a second to bind port 8080 internally:
sleep 1

# 3) Start the FastAPI application
echo "Starting FastAPI application..."
exec gosu appuser uvicorn backend.main:app --host 127.0.0.1 --port 8000 --log-level info