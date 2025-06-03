# Use official Python slim image as base
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Install system dependencies required for building Python packages and PostgreSQL client libs
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip, setuptools, and wheel for better compatibility
RUN pip install --upgrade pip setuptools wheel

# Copy requirements file and install Python dependencies with verbose logging
COPY backend/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt --verbose

# Copy backend source code
COPY backend/ ./backend/

# Set environment variables inside container (can be overridden by Docker Compose or runtime)
ENV DOMAIN=quantum-ai.asia
ENV FRONTEND_URL=https://quantum-ai.asia

# Expose the port Cloud Run expects
EXPOSE 8080

# Command to run FastAPI app on the port Cloud Run sets (default 8080)
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
