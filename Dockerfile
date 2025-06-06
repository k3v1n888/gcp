# ───────────────────────────────────────────────────────────────────────────────
# Stage 1: Build React Frontend
# ───────────────────────────────────────────────────────────────────────────────
FROM node:18-alpine AS frontend-build

WORKDIR /app

# 1) Copy only package.json so we can leverage Docker cache
COPY frontend/package.json

# 2) Install JS dependencies
RUN npm install

# 3) Copy the rest of the frontend code & build
COPY frontend/ ./
RUN npm run build


# ───────────────────────────────────────────────────────────────────────────────
# Stage 2: Build Python/FastAPI Backend (and install all Python dependencies)
# ───────────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim AS backend-build

WORKDIR /app

# 1) Install system dependencies (for psycopg2, etc.)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 2) Copy requirements.txt and install Python packages
COPY backend/requirements.txt ./
RUN pip install --upgrade pip setuptools wheel \
 && pip install --no-cache-dir -r requirements.txt

# 3) Copy your backend source code so Uvicorn can import it
COPY backend/ ./backend/


# ───────────────────────────────────────────────────────────────────────────────
# Stage 3 (Final): Combine Nginx + React Build + Uvicorn
# ───────────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim AS final

# 1) Install Nginx (the web server)
RUN apt-get update && apt-get install -y nginx \
    && rm -rf /var/lib/apt/lists/*

# 2) Copy our Nginx config into place
COPY nginx/default.conf /etc/nginx/conf.d/default.conf

# 3) Copy React’s production build from stage 1 → Nginx’s root
COPY --from=frontend-build /app/build/ /usr/share/nginx/html/

# 4) Copy Uvicorn binary & Python site-packages from stage 2
COPY --from=backend-build /usr/local/bin/uvicorn /usr/local/bin/uvicorn
COPY --from=backend-build /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/

# 5) Copy your entire backend source so FastAPI imports work
COPY --from=backend-build /app/backend/ /app/backend/

# 6) Copy & mark run.sh as executable
COPY run.sh /app/run.sh
RUN chmod +x /app/run.sh

# 7) Make /app the working directory
WORKDIR /app

# 8) Expose port 8080 (Cloud Run expects the container to listen here)
EXPOSE 8080

# 9) Default command: run our run.sh (which launches nginx + uvicorn)
CMD ["/app/run.sh"]
