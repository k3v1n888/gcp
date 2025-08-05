#!/usr/bin/env bash
#
# 1) Launch Nginx in the foreground. It will start as root and then
#    drop privileges for its worker processes as configured.
#
# 2) We then use 'gosu' to drop privileges from root to 'appuser'
#    before executing the uvicorn process.

set -eux

# Run timestamp fix before starting services
echo "Running timestamp fix..."
python3 backend/fix_timestamps.py || echo "Warning: Timestamp fix failed, continuing..."

# 1) Start Nginx in the foreground
nginx -g 'daemon off;' &

# 2) Give Nginx a second to bind port 8080 internally:
sleep 1

# 3) --- MODIFIED: Exec Uvicorn as the non-privileged 'appuser' ---
#    'gosu' is a lightweight tool to change user.
#    This ensures your Python application code does not run as root.
exec gosu appuser uvicorn backend.main:app --host 127.0.0.1 --port 8000
