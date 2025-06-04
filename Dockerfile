# ────────────────────────────────────────────────────────────────────────────────
#  Stage 1: Build React frontend
# ────────────────────────────────────────────────────────────────────────────────
FROM node:18‐alpine AS frontend‐build

# Set working dir, copy only package.json & lockfile to leverage Docker cache
WORKDIR /app

COPY frontend/package.json frontend/package‐lock.json ./

# Install dependencies
RUN npm ci 

# Copy rest of frontend code
COPY frontend/ ./

# Build the React app; output goes to /app/build
RUN npm run build

# ────────────────────────────────────────────────────────────────────────────────
#  Stage 2: Build Python/FastAPI backend
# ────────────────────────────────────────────────────────────────────────────────
FROM python:3.11‐slim AS backend‐build

WORKDIR /app

# Install system deps needed to compile Python packages
RUN apt‐get update && apt‐get install ‐y \
    build‐essential \
    libpq‐dev \
    && rm ‐rf /var/lib/apt/lists/*

# Copy only requirements, install them
COPY backend/requirements.txt ./
RUN pip install --upgrade pip setuptools wheel \
 && pip install --no‐cache‐dir -r requirements.txt

# Copy the rest of the backend source
COPY backend/ ./backend/

# ────────────────────────────────────────────────────────────────────────────────
#  Stage 3: Final image (Nginx + React build + Uvicorn backend)
# ────────────────────────────────────────────────────────────────────────────────
FROM python:3.11‐slim AS final

# Install Nginx
RUN apt‐get update && apt‐get install ‐y nginx \
    && rm ‐rf /var/lib/apt/lists/*

# 1) Copy Nginx config (make sure nginx/default.conf exists in your repo)
COPY nginx/default.conf /etc/nginx/conf.d/default.conf

# 2) Copy the React build artifacts from stage `frontend‐build`
COPY --from=frontend‐build /app/build/ /usr/share/nginx/html/

# 3) Copy Uvicorn binary and backend site-packages from stage `backend‐build`
COPY --from=backend‐build /usr/local/bin/uvicorn /usr/local/bin/uvicorn
COPY --from=backend‐build /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/

# 4) Copy the backend source itself (if your FastAPI code references files at runtime)
COPY --from=backend‐build /app/backend/ /app/backend/

# 5) Copy run.sh and ensure it’s executable
COPY run.sh /app/run.sh
RUN chmod +x /app/run.sh

WORKDIR /app

# Expose port 8080 (Cloud Run routes on 8080 by default)
EXPOSE 8080

# Start Nginx + Uvicorn
CMD ["/app/run.sh"]
