#!/usr/bin/env bash

# 1) Start Nginx in the background
service nginx start

# 1.a) Debug: print out where uvicorn is (just for logs)
echo ">>> running which uvicorn: $(which uvicorn)"
echo ">>> uvicorn --version: $(uvicorn --version 2>&1)"

# 2) Start Uvicorn (FastAPI) bound to localhost:8000
exec uvicorn backend.main:app --host 127.0.0.1 --port 8000
