#!/usr/bin/env bash
#
# 1) Launch Nginx in the foreground, then immediately launch Uvicorn (so that
#    both processes run under the same container, and if either quits, the container dies).
#
# 2) We use "nginx -g 'daemon off;'" so Nginx does NOT daemonize itself.
#    Then we exec uvicorn as the final PID 1-ish process.

set -eux

# 1) Start Nginx in the foreground ( “daemon off” means “don’t background” )
nginx -g 'daemon off;' &

# 2) Give Nginx a second to bind port 8080 internally:
sleep 1

# 3) Exec Uvicorn so that if it dies, the container dies too
exec uvicorn backend.main:app --host 127.0.0.1 --port 8000
