#!/bin/bash
# Copyright (c) 2025 Kevin Zachary
# All rights reserved.
#
# This software and associated documentation files (the "Software") are the 
# exclusive property of Kevin Zachary. Unauthorized copying, distribution, 
# modification, or use of this software is strictly prohibited.
#
# For licensing inquiries, contact: kevin@zachary.com

#!/bin/bash
# Author: Kevin Zachary
# Copyright: Sentient Spire

# 🚀 UNIFIED PROJECT CLEANUP & OPTIMIZATION SCRIPT
# This script consolidates all project files and creates an optimized development environment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
CURRENT_DIR="/Users/kevinzachary/Downloads/VS-GCP-QAI/gcp"
OLD_SSAI_DIR="/Users/kevinzachary/Downloads/ssai-vm-dev"
CLEAN_PROJECT_DIR="/Users/kevinzachary/Downloads/SSAI-CLEAN"
VM_USER="kevin"
VM_HOST="192.168.64.13"
VM_PASSWORD="V!g1l@nt"
VM_PROJECT_DIR="/home/kevin/ssai-project"

echo -e "${BLUE}🧹 SSAI PROJECT CLEANUP & OPTIMIZATION${NC}"
echo "=================================================="

# Step 1: Create clean project directory
echo -e "${YELLOW}📁 Step 1: Creating clean project structure...${NC}"
if [ -d "$CLEAN_PROJECT_DIR" ]; then
    echo "Removing existing clean directory..."
    rm -rf "$CLEAN_PROJECT_DIR"
fi

mkdir -p "$CLEAN_PROJECT_DIR"
cd "$CLEAN_PROJECT_DIR"

# Step 2: Copy current working files (with all fixes)
echo -e "${YELLOW}📋 Step 2: Copying current working files...${NC}"
cp -r "$CURRENT_DIR/"* . 2>/dev/null || true
cp -r "$CURRENT_DIR/".git . 2>/dev/null || true
cp -r "$CURRENT_DIR/".gitignore . 2>/dev/null || true

# Step 3: Create unified docker-compose configuration
echo -e "${YELLOW}🐳 Step 3: Creating unified Docker configuration...${NC}"

cat > docker-compose.unified.yml << 'EOF'
version: "3.8"

services:
  # PostgreSQL Database
  db:
    image: postgres:15-alpine
    container_name: ssai_db
    restart: always
    environment:
      POSTGRES_USER: cyber_user
      POSTGRES_PASSWORD: secure_pass
      POSTGRES_DB: cyberdb
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U cyber_user -d cyberdb"]
      interval: 30s
      timeout: 10s
      retries: 5

  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: ssai_redis
    restart: always
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 5

  # AI Service (Local ML Models)
  ai-service:
    build:
      context: ./ai-service
      dockerfile: Dockerfile.dev
    container_name: ssai_ai_service
    restart: always
    ports:
      - "8001:8001"
      - "8002:8002" 
      - "8003:8003"
      - "8004:8004"
    volumes:
      - ./ai-service:/app
      - ai_models:/app/models
    environment:
      - PYTHONPATH=/app
      - MODEL_PATH=/app/models
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 60s

  # Backend API
  backend:
    build:
      context: .
      dockerfile: Dockerfile.dev
    container_name: ssai_backend
    restart: always
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app/backend
      - ./shared:/app/shared
    environment:
      - DATABASE_URL=postgresql://cyber_user:secure_pass@db:5432/cyberdb
      - REDIS_URL=redis://redis:6379
      - AI_SERVICE_URL=http://ai-service:8001
      - BACKEND_BASE_URL=http://backend:8000
      - DEV_MODE=true
      - PYTHONPATH=/app
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
      ai-service:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 30s

  # Frontend React App
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    container_name: ssai_frontend
    restart: always
    ports:
      - "3000:3000"
    volumes:
      - ./frontend/src:/app/src
      - ./frontend/public:/app/public
      - /app/node_modules
    environment:
      - REACT_APP_API_URL=http://192.168.64.13:8000
      - REACT_APP_WS_URL=ws://192.168.64.13:8000
      - CHOKIDAR_USEPOLLING=true
    depends_on:
      backend:
        condition: service_healthy
    stdin_open: true
    tty: true

volumes:
  postgres_data:
  redis_data:
  ai_models:

networks:
  default:
    driver: bridge
EOF

# Step 4: Create optimized Dockerfile for backend
echo -e "${YELLOW}🏗️ Step 4: Creating optimized Dockerfiles...${NC}"

cat > Dockerfile.optimized << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY backend/requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt

# Copy application code
COPY backend/ ./backend/
COPY shared/ ./shared/
COPY ai-service/ ./ai-service/

# Create startup script
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
# Wait for database\n\
echo "Waiting for database..."\n\
while ! nc -z db 5432; do\n\
  sleep 1\n\
done\n\
echo "Database is ready!"\n\
\n\
# Wait for AI service\n\
echo "Waiting for AI service..."\n\
while ! nc -z ai-service 8001; do\n\
  sleep 1\n\
done\n\
echo "AI service is ready!"\n\
\n\
# Start the application\n\
exec uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload\n\
' > /app/start.sh && chmod +x /app/start.sh

EXPOSE 8000

CMD ["/app/start.sh"]
EOF

# Step 5: Create AI service optimized Dockerfile
cat > ai-service/Dockerfile.optimized << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create models directory
RUN mkdir -p models

EXPOSE 8001 8002 8003 8004

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:8001/health || exit 1

CMD ["python", "main.py"]
EOF

# Step 6: Create optimized management scripts
echo -e "${YELLOW}⚙️ Step 5: Creating management scripts...${NC}"

cat > dev-manager.sh << 'EOF'
#!/bin/bash
# 🚀 SSAI Development Manager Script

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
COMPOSE_FILE="docker-compose.unified.yml"
VM_USER="kevin"
VM_HOST="192.168.64.13"
VM_PASSWORD="V!g1l@nt"
VM_PROJECT_DIR="/home/kevin/ssai-project"

show_usage() {
    echo -e "${BLUE}🚀 SSAI Development Manager${NC}"
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start       - Start all services"
    echo "  stop        - Stop all services"
    echo "  restart     - Restart all services"
    echo "  status      - Show service status"
    echo "  logs [svc]  - Show logs (optional service name)"
    echo "  deploy      - Deploy to VM"
    echo "  clean       - Clean up containers and volumes"
    echo "  test        - Run tests"
    echo "  ai-test     - Test AI models"
    echo "  rebuild     - Rebuild and restart all services"
    echo ""
}

start_services() {
    echo -e "${GREEN}🚀 Starting SSAI services...${NC}"
    docker-compose -f $COMPOSE_FILE up -d
    echo -e "${GREEN}✅ Services started!${NC}"
    show_status
}

stop_services() {
    echo -e "${YELLOW}🛑 Stopping SSAI services...${NC}"
    docker-compose -f $COMPOSE_FILE down
    echo -e "${YELLOW}✅ Services stopped!${NC}"
}

restart_services() {
    echo -e "${BLUE}🔄 Restarting SSAI services...${NC}"
    docker-compose -f $COMPOSE_FILE restart
    echo -e "${GREEN}✅ Services restarted!${NC}"
    show_status
}

show_status() {
    echo -e "${BLUE}📊 Service Status:${NC}"
    docker-compose -f $COMPOSE_FILE ps
    echo ""
    echo -e "${BLUE}🏥 Health Checks:${NC}"
    echo "Frontend: http://localhost:3000"
    echo "Backend API: http://localhost:8000/api/health"
    echo "AI Service: http://localhost:8001/health"
}

show_logs() {
    service=${1:-""}
    if [ -z "$service" ]; then
        docker-compose -f $COMPOSE_FILE logs -f
    else
        docker-compose -f $COMPOSE_FILE logs -f $service
    fi
}

deploy_to_vm() {
    echo -e "${BLUE}🚀 Deploying to VM...${NC}"
    
    # Copy files to VM
    echo "📦 Copying files..."
    sshpass -p "$VM_PASSWORD" rsync -avz --progress --exclude='.git' --exclude='node_modules' --exclude='__pycache__' ./ $VM_USER@$VM_HOST:$VM_PROJECT_DIR/
    
    # Restart services on VM
    echo "🔄 Restarting services on VM..."
    sshpass -p "$VM_PASSWORD" ssh $VM_USER@$VM_HOST "cd $VM_PROJECT_DIR && docker-compose -f docker-compose.unified.yml down && docker-compose -f docker-compose.unified.yml up -d"
    
    echo -e "${GREEN}✅ Deployment complete!${NC}"
    echo "🌐 Frontend: http://192.168.64.13:3000"
    echo "🔗 Backend: http://192.168.64.13:8000"
}

clean_all() {
    echo -e "${RED}🧹 Cleaning up...${NC}"
    docker-compose -f $COMPOSE_FILE down -v --remove-orphans
    docker system prune -f
    echo -e "${GREEN}✅ Cleanup complete!${NC}"
}

run_tests() {
    echo -e "${BLUE}🧪 Running tests...${NC}"
    if [ -f "generate_test_data.py" ]; then
        python generate_test_data.py
    else
        echo "Test script not found"
    fi
}

test_ai_models() {
    echo -e "${BLUE}🤖 Testing AI models...${NC}"
    curl -X GET http://localhost:8001/health || echo "AI service not responding"
    curl -X POST http://localhost:8000/api/admin/test-ai-models || echo "Backend AI tests not responding"
}

rebuild_all() {
    echo -e "${BLUE}🏗️ Rebuilding all services...${NC}"
    docker-compose -f $COMPOSE_FILE down
    docker-compose -f $COMPOSE_FILE build --no-cache
    docker-compose -f $COMPOSE_FILE up -d
    echo -e "${GREEN}✅ Rebuild complete!${NC}"
    show_status
}

# Main command handler
case "$1" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs $2
        ;;
    deploy)
        deploy_to_vm
        ;;
    clean)
        clean_all
        ;;
    test)
        run_tests
        ;;
    ai-test)
        test_ai_models
        ;;
    rebuild)
        rebuild_all
        ;;
    *)
        show_usage
        ;;
esac
EOF

chmod +x dev-manager.sh

# Step 7: Create cleanup script
cat > cleanup-duplicates.sh << 'EOF'
#!/bin/bash
# 🧹 Remove duplicate project directories

set -e

echo "🧹 Cleaning up duplicate directories..."

# Remove old ssai-vm-dev directory
if [ -d "/Users/kevinzachary/Downloads/ssai-vm-dev" ]; then
    echo "Removing /Users/kevinzachary/Downloads/ssai-vm-dev..."
    rm -rf "/Users/kevinzachary/Downloads/ssai-vm-dev"
    echo "✅ Removed old ssai-vm-dev directory"
fi

echo "✅ Cleanup complete!"
echo "📁 Clean project location: $(pwd)"
EOF

chmod +x cleanup-duplicates.sh

echo -e "${GREEN}✅ Step 6: Cleanup and optimization complete!${NC}"
echo ""
echo -e "${BLUE}📋 NEXT STEPS:${NC}"
echo "1. Run: ./cleanup-duplicates.sh"
echo "2. Use: ./dev-manager.sh start"
echo "3. Deploy: ./dev-manager.sh deploy"
echo ""
echo -e "${BLUE}📁 New project location: ${CLEAN_PROJECT_DIR}${NC}"
echo -e "${BLUE}🚀 Management script: ./dev-manager.sh${NC}"
