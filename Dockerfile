# ────────────────────────────────────────────────────────────────────────────────
#  Stage 1: Build React frontend
# ────────────────────────────────────────────────────────────────────────────────
FROM node:18-alpine AS frontend-build

# 1) Set working dir & copy package.json + lockfile to leverage cache
WORKDIR /app

# Copy only package.json (no lockfile present)

COPY frontend/package.json ./

# Install JS dependencies
RUN npm install

# 3) Copy rest of frontend code & build
COPY frontend/ ./
RUN npm run build


# ────────────────────────────────────────────────────────────────────────────────
#  Stage 2: Build Python/FastAPI backend
# ────────────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim AS backend-build

WORKDIR /app

# 1) Install system deps for building Python packages + Postgres client libs
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 2) Copy only requirements.txt & install Python dependencies
COPY backend/requirements.txt ./
RUN pip install --upgrade pip setuptools wheel \
 && pip install --no-cache-dir -r requirements.txt

# 3) Copy entire backend source so Uvicorn can import it
COPY backend/ ./backend/


# ────────────────────────────────────────────────────────────────────────────────
#  Stage 3: Final image (Nginx + React build + Uvicorn backend)
# ────────────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim AS final

# 1) Install Nginx
RUN apt-get update && apt-get install -y nginx \
    && rm -rf /var/lib/apt/lists/*

# 2) Copy your custom Nginx config into /etc/nginx/conf.d/
COPY nginx/default.conf /etc/nginx/conf.d/default.conf

# 3) Copy React’s production build from stage 1
COPY --from=frontend-build /app/build/ /usr/share/nginx/html/

# 4) Copy Uvicorn binary and site-packages from stage 2
COPY --from=backend-build /usr/local/bin/uvicorn /usr/local/bin/uvicorn
COPY --from=backend-build /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/

# 5) Copy backend source itself (if your FastAPI code needs to import from files)
COPY --from=backend-build /app/backend/ /app/backend/

# 6) Copy and make run.sh executable
COPY run.sh /app/run.sh
RUN chmod +x /app/run.sh

WORKDIR /app

# 7) Expose port 8080 (Cloud Run expects this)
EXPOSE 8080

# 8) Start Nginx + Uvicorn
CMD ["/app/run.sh"]
