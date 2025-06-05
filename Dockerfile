# ────────────────────────────────────────────────────────────────────────────────
# Stage 1: Build React frontend
# ────────────────────────────────────────────────────────────────────────────────
FROM node:18-alpine AS frontend-build

WORKDIR /app

#  1a) Copy only package.json to leverage cache
COPY frontend/package.json ./ 
# If you have a package-lock.json, copy it too (optional):
# COPY frontend/package-lock.json ./ 

#  1b) Install JS deps
RUN npm install

#  2) Copy all React source & produce a production build
COPY frontend/ ./
RUN npm run build




# ────────────────────────────────────────────────────────────────────────────────
# Stage 2: Build Python/FastAPI backend
# ────────────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim AS backend-build

WORKDIR /app

#  2a) Install system deps (for postgres, building wheels, etc.)
RUN apt-get update \
 && apt-get install -y \
      build-essential \
      libpq-dev \
      curl \
 && rm -rf /var/lib/apt/lists/*

#  2b) Copy only requirements.txt & install Python deps
COPY backend/requirements.txt ./
RUN pip install --upgrade pip setuptools wheel \
 && pip install --no-cache-dir -r requirements.txt

#  2c) Copy the backend source code
COPY backend/ ./backend/





# ────────────────────────────────────────────────────────────────────────────────
# Stage 3: Final image (Nginx + React build + Uvicorn)
# ────────────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim AS final

#  3a) Install Nginx
RUN apt-get update \
 && apt-get install -y nginx \
 && rm -rf /var/lib/apt/lists/*

#  3b) Copy our custom Nginx config (from local `nginx/default.conf`)
COPY nginx/default.conf /etc/nginx/conf.d/default.conf

#  3c) Copy React’s production build from stage1
COPY --from=frontend-build /app/build/ /usr/share/nginx/html/

#  3d) Copy Uvicorn binary and all site-packages from stage2
COPY --from=backend-build /usr/local/bin/uvicorn /usr/local/bin/uvicorn
COPY --from=backend-build /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/

#  3e) Copy the backend source code (so Uvicorn can import `backend.*`)
COPY --from=backend-build /app/backend/ /app/backend/

#  3f) Copy and mark `run.sh` executable
COPY run.sh /app/run.sh
RUN chmod +x /app/run.sh

WORKDIR /app

#  3g) Expose port 8080 (Cloud Run expects container LISTEN on 8080)
EXPOSE 8080

#  3h) Start Nginx+Uvicorn in one shot
CMD ["/app/run.sh"]
