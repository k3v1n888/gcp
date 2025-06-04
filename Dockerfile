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
# … earlier stages …

FROM python:3.11-slim AS final

# Install Nginx
RUN apt-get update && apt-get install -y nginx \
    && rm -rf /var/lib/apt/lists/*

# Copy Nginx config
COPY nginx/default.conf /etc/nginx/conf.d/default.conf

# Copy the Uvicorn binary & site-packages from the backend build
COPY --from=backend-build /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=backend-build /usr/local/bin/uvicorn /usr/local/bin/uvicorn

# Copy run.sh and force it to be executable
COPY run.sh /app/run.sh
RUN chmod +x /app/run.sh

# Copy React’s production build
COPY frontend/build/ /usr/share/nginx/html/

WORKDIR /app
EXPOSE 8080

CMD ["/app/run.sh"]
