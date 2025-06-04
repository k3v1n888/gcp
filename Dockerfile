################################################################################
# Stage 1: Build React front-end
################################################################################
FROM node:18-alpine AS frontend-build

WORKDIR /app

# Copy package.json + yarn.lock (or package-lock.json) to leverage layer caching.
COPY frontend/package.json frontend/package-lock.json* ./

# Install JS dependencies
RUN npm install

# Copy the rest of the front-end source and run the production build
COPY frontend/ ./
RUN npm run build

################################################################################
# Stage 2: Build FastAPI back-end (Uvicorn + dependencies)
################################################################################
FROM python:3.11-slim AS backend-build

WORKDIR /app

# (1) Install system dependencies for building Python packages and any libs (e.g. Postgres client)
RUN apt-get update \
 && apt-get install -y \
        build-essential \
        libpq-dev \
        curl \
 && rm -rf /var/lib/apt/lists/*

# (2) Copy only requirements.txt, then pip install
COPY backend/requirements.txt ./
RUN pip install --upgrade pip setuptools wheel \
 && pip install --no-cache-dir -r requirements.txt

# (3) Copy the entire backend folder so that Uvicorn can import it in this stage
COPY backend/ ./backend/

################################################################################
# Stage 3: Final image
#   – Installs Nginx
#   – Copies built React files → /usr/share/nginx/html
#   – Copies Uvicorn binary + site-packages from the backend-build stage
#   – Copies run.sh (to start Nginx + Uvicorn)
################################################################################
FROM python:3.11-slim AS final

WORKDIR /app

# 1) Install Nginx
RUN apt-get update \
 && apt-get install -y nginx \
 && rm -rf /var/lib/apt/lists/*

# 2) Copy your custom Nginx config into /etc/nginx/conf.d/default.conf
COPY nginx/default.conf /etc/nginx/conf.d/default.conf

# 3) Copy the React build from stage 1 → Nginx’s default webroot
COPY --from=frontend-build /app/build/ /usr/share/nginx/html/

# 4) Copy Uvicorn + site-packages from the Python/backend build stage
COPY --from=backend-build /usr/local/bin/uvicorn /usr/local/bin/uvicorn
COPY --from=backend-build /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/

# Sanity check: ensure uvicorn is present
RUN ls -l /usr/local/bin/uvicorn

# 5) Copy the FastAPI backend itself (so Uvicorn can find “backend/”)
COPY --from=backend-build /app/backend/ /app/backend/

# 6) Copy run.sh and make it executable
COPY run.sh /app/run.sh
RUN chmod +x /app/run.sh

# 7) Expose port 8080 (Cloud Run expects this)
EXPOSE 8080

# 8) Entry point: start Nginx, then exec Uvicorn
CMD ["/app/run.sh"]