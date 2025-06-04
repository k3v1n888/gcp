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

# Copy the cached Python dependencies from backend-build
COPY --from=backend-build /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
# Copy the pip‐installed console scripts (uvicorn entrypoint, etc.)
COPY --from=backend-build /usr/local/bin/uvicorn /usr/local/bin/uvicorn
COPY --from=backend-build /usr/local/bin/gunicorn /usr/local/bin/gunicorn  || true
COPY --from=backend-build /usr/local/bin/python* /usr/local/bin/  || true

# Copy the backend source code itself
COPY --from=backend-build /app/backend /app/backend

# Copy React’s build output into Nginx’s webroot
COPY --from=frontend-build /app/build /usr/share/nginx/html

# Copy our Nginx configuration (listening on port 8080)
COPY nginx/default.conf /etc/nginx/conf.d/default.conf

# Copy the entry‐point script that starts Nginx + Uvicorn
COPY run.sh /app/run.sh
RUN chmod +x /app/run.sh

# Expose port 8080 (Cloud Run will route HTTPS → 8080)
EXPOSE 8080

# Start the combined server
CMD ["/app/run.sh"]
