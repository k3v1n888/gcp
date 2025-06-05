#!/usr/bin/env bash
#
# run.sh: start nginx in the background, then run uvicorn in the foreground (PID 1).
#

# (1) Directly launch nginx (daemon off) so it runs as a background daemon.
#     We don’t invoke “service nginx start” because the slim image may not have full init scripts.
nginx

# (2) Exec Uvicorn (so that PID 1 is uvicorn).  Any crash in Uvicorn forces the container to exit.
#     We bind to 127.0.0.1:8000 because Nginx will proxy→loopback:8000 for “/api/…”.
exec uvicorn backend.main:app \
     --host 127.0.0.1 \
     --port 8000