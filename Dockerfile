# ───────────────────────────────────────────────────────────────────────────────
# Stage 1: Build React frontend
# ───────────────────────────────────────────────────────────────────────────────
FROM node:20-alpine AS frontend-build
WORKDIR /app

# Copy package.json (no lockfile). We’ll run `npm install`.
COPY frontend/package.json ./

# Install dependencies
RUN npm install

# Copy the rest of the frontend code and build it
COPY frontend/ ./
RUN npm run build

# ───────────────────────────────────────────────────────────────────────────────
# Stage 2: Build (and cache) Python dependencies
# ───────────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim AS backend-build
WORKDIR /app

# Install system libs needed for some Python packages (e.g. asyncpg, psycopg2, etc.)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt and install into this build stage 
COPY backend/requirements.txt .
RUN pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

# Copy all backend source code (so that cached Python deps + code coexist)
COPY backend/ ./backend

# ───────────────────────────────────────────────────────────────────────────────
# Stage 3: Final image (Nginx + Uvicorn)
# ───────────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim
WORKDIR /app

# Install Nginx
RUN apt-get update && apt-get install -y nginx \
    && rm -rf /var/lib/apt/lists/*

# 1) Copy installed Python packages (including 'uvicorn') from backend-build
COPY --from=backend-build /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/

# 2) Copy the uvicorn binary itself so `run.sh` can call it
COPY --from=backend-build /usr/local/bin/uvicorn /usr/local/bin/uvicorn

# (If you need gunicorn, you can add a similar line—without "|| true"—only if it actually exists:)
# COPY --from=backend-build /usr/local/bin/gunicorn /usr/local/bin/gunicorn

# 3) Copy your backend source code
COPY --from=backend-build /app/backend /app/backend

# 4) Copy React build into Nginx’s html folder
COPY --from=frontend-build /app/build /usr/share/nginx/html

# 5) Copy the Nginx config (now listening on port 8080)
COPY nginx/default.conf /etc/nginx/conf.d/default.conf

# 6) Copy and mark executable the run.sh script
COPY run.sh /app/run.sh
RUN chmod +x /app/run.sh

# Expose port 8080 (Cloud Run will forward HTTPS → 8080)
EXPOSE 8080

# Entry point: start Nginx (on 8080) and Uvicorn (on 8000)
CMD ["/app/run.sh"]
