# Dockerfile

# ───────────────────────────────────────────────────────────────────────────────
# Stage 1: Build React Frontend - FIXED
# ───────────────────────────────────────────────────────────────────────────────
FROM node:18-alpine AS frontend-build
WORKDIR /app

# Fix: Copy to correct paths
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install

# Fix: Copy frontend source correctly
COPY frontend/ ./
RUN npm run build


# ───────────────────────────────────────────────────────────────────────────────
# Stage 2: Build Python/FastAPI Backend
# ───────────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim AS backend-build
WORKDIR /app
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*
COPY backend/requirements.txt ./
RUN pip install --upgrade pip setuptools wheel cython \
 && pip install --no-cache-dir -r requirements.txt
COPY backend/ ./backend/


# ───────────────────────────────────────────────────────────────────────────────
# Stage 3 (Final): Combine Nginx + React Build + Uvicorn
# ───────────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim AS final

RUN apt-get update && apt-get install -y nginx gosu \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -r appgroup && useradd -r -g appgroup -s /sbin/nologin appuser

# Copy Nginx config
COPY nginx/default.conf /etc/nginx/conf.d/default.conf

# Copy React build from frontend stage
COPY --from=frontend-build /app/build/ /usr/share/nginx/html/

# Copy backend dependencies and source
COPY --from=backend-build /usr/local/bin/uvicorn /usr/local/bin/uvicorn
COPY --from=backend-build /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=backend-build /app/backend/ /app/backend/

# Copy and setup run script
COPY run.sh /app/run.sh
RUN chmod +x /app/run.sh

WORKDIR /app
RUN chown -R appuser:appgroup /app

EXPOSE 8080
CMD ["/app/run.sh"]
