# Dockerfile

# ───────────────────────────────────────────────────────────────────────────────
# Stage 1: Build React Frontend
# ───────────────────────────────────────────────────────────────────────────────
# (No changes in this stage)
FROM node:18-alpine AS frontend-build
WORKDIR /app
COPY frontend/package.json ./frontend/package-lock.json* ./
RUN npm install
COPY frontend/ ./
RUN npm run build


# ───────────────────────────────────────────────────────────────────────────────
# Stage 2: Build Python/FastAPI Backend
# ───────────────────────────────────────────────────────────────────────────────
# (No changes in this stage)
FROM python:3.11-slim AS backend-build
WORKDIR /app
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*
COPY backend/requirements.txt ./
# --- MODIFIED: Added cython before installing requirements ---
RUN pip install --upgrade pip setuptools wheel cython \
 && pip install --no-cache-dir -r requirements.txt
COPY backend/ ./backend/


# ───────────────────────────────────────────────────────────────────────────────
# Stage 3 (Final): Combine Nginx + React Build + Uvicorn
# ───────────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim AS final

# --- MODIFIED: Install Nginx and gosu ---
RUN apt-get update && apt-get install -y nginx gosu \
    && rm -rf /var/lib/apt/lists/*

# --- NEW: Create a non-privileged user to run the application ---
RUN groupadd -r appgroup && useradd -r -g appgroup -s /sbin/nologin appuser

# Copy our Nginx config into place
COPY nginx/default.conf /etc/nginx/conf.d/default.conf

# Copy React’s production build from stage 1
COPY --from=frontend-build /app/build/ /usr/share/nginx/html/

# Copy Uvicorn binary & Python site-packages from stage 2
COPY --from=backend-build /usr/local/bin/uvicorn /usr/local/bin/uvicorn
COPY --from=backend-build /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/

# Copy your entire backend source
COPY --from=backend-build /app/backend/ /app/backend/

# Copy & mark run.sh as executable
COPY run.sh /app/run.sh
RUN chmod +x /app/run.sh

# Make /app the working directory
WORKDIR /app

# --- NEW: Change ownership of the app directory ---
RUN chown -R appuser:appgroup /app

# Expose port 8080
EXPOSE 8080

# Default command: run our run.sh (which launches nginx + uvicorn)
# The script will be run as root, but it will start the app process as 'appuser'
CMD ["/app/run.sh"]
