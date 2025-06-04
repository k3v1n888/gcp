# ───────────────────────────────────────────────────────────────────────────────
# Stage 1: Build React frontend
# ───────────────────────────────────────────────────────────────────────────────
FROM node:20-alpine AS frontend-build
WORKDIR /app

# Copy package.json & package-lock.json so we only re-run npm ci when they change
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci

# Copy the rest of the frontend sources and build
COPY frontend/ ./
RUN npm run build

# ───────────────────────────────────────────────────────────────────────────────
# Stage 2: Build FastAPI backend
# ───────────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim AS backend-build
WORKDIR /app

# Install system dependencies needed for Python packages (e.g. psycopg2, etc.)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements.txt first (for caching)
COPY backend/requirements.txt .
RUN pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY backend/ ./backend/

# ───────────────────────────────────────────────────────────────────────────────
# Stage 3: Final image: Nginx + Uvicorn
# ───────────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim
WORKDIR /app

# Install Nginx
RUN apt-get update && apt-get install -y nginx \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages + backend code from backend-build
COPY --from=backend-build /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend-build /app/backend /app/backend

# Copy React static build from frontend-build into Nginx’s html folder
COPY --from=frontend-build /app/build /usr/share/nginx/html

# Copy custom Nginx configuration
COPY nginx/default.conf /etc/nginx/conf.d/default.conf

# Copy the run.sh script (to launch Nginx + Uvicorn)
COPY run.sh /app/run.sh
RUN chmod +x /app/run.sh

# Expose port 80 (Nginx) and port 8000 (Uvicorn)
EXPOSE 80 8000

# Start Nginx and Uvicorn together
CMD ["/app/run.sh"]
