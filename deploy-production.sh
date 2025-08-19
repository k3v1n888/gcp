#!/bin/bash

# Production Deployment Script
# This script prepares and deploys the cybersecurity dashboard

set -e  # Exit on any error

echo "🚀 Starting Production Deployment..."
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Load production environment
if [ -f .env.production ]; then
    print_status "Loading production environment variables..."
    export $(cat .env.production | xargs)
else
    print_warning ".env.production not found. Using default values."
fi

# Build frontend for production
print_status "Building React frontend for production..."
cd frontend
if [ -f package.json ]; then
    npm install --production
    npm run build
    print_success "Frontend build completed"
else
    print_warning "Frontend package.json not found, skipping frontend build"
fi
cd ..

# Build and start services with Docker Compose
print_status "Building Docker images..."
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

print_status "Starting production services..."
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Wait for services to be healthy
print_status "Waiting for services to be ready..."
sleep 10

# Health checks
print_status "Performing health checks..."

# Check backend API
if curl -f http://localhost:8000/api/forecasting/health > /dev/null 2>&1; then
    print_success "Backend API is healthy"
else
    print_error "Backend API health check failed"
    exit 1
fi

# Check if database is accessible (if using PostgreSQL)
if [ -n "$DATABASE_URL" ]; then
    print_status "Checking database connection..."
    # Add database health check here if needed
fi

# Final deployment status
print_success "🎉 Production deployment completed successfully!"
echo ""
echo "Services are running at:"
echo "  🌐 Frontend: http://localhost (behind nginx)"
echo "  🔧 Backend API: http://localhost:8000"
echo "  📊 Dashboard: http://localhost:8000/"
echo "  💾 Database: PostgreSQL (if configured)"
echo ""
echo "To view logs: docker-compose logs -f"
echo "To stop services: docker-compose down"
echo ""
print_success "Dashboard is ready for production use! 🚀"
