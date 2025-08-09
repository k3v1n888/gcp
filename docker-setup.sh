#!/bin/bash

# Quick Docker Development Setup
echo "🚀 Setting up Docker Development Environment..."

# Make scripts executable
chmod +x docker-dev.sh

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
fi

# Copy AI models if they exist
if [ -d ~/Downloads/"ai model 2" ]; then
    echo "📁 Copying AI models..."
    mkdir -p ai-service/models
    cp ~/Downloads/"ai model 2"/* ai-service/models/ 2>/dev/null || true
    echo "✅ AI models copied"
else
    echo "⚠️  AI models not found in ~/Downloads/ai model 2"
    echo "   You can copy them later to ai-service/models/"
fi

# Build and start services
echo "🔨 Building containers..."
docker-compose -f docker-compose.full.yml build

echo "🚀 Starting services..."
docker-compose -f docker-compose.full.yml up -d

echo ""
echo "🎉 Docker Development Environment Ready!"
echo "======================================"
echo ""
echo "🌐 Your Services:"
echo "   Frontend:    http://localhost:3000"
echo "   Backend:     http://localhost:8000"
echo "   AI Service:  http://localhost:8001"
echo "   API Docs:    http://localhost:8000/docs"
echo ""
echo "🛠️  Management Commands:"
echo "   ./docker-dev.sh status   # Check service health"
echo "   ./docker-dev.sh logs     # View all logs"
echo "   ./docker-dev.sh restart  # Restart all services"
echo "   ./docker-dev.sh stop     # Stop everything"
echo ""
echo "✏️  Development Workflow:"
echo "   1. Edit files in VS Code (auto-reload enabled)"
echo "   2. Changes appear instantly in containers"
echo "   3. No need to restart unless changing dependencies"
echo ""
echo "🧪 Test your setup:"
echo "   curl http://localhost:8000/     # Backend health"
echo "   curl http://localhost:8001/     # AI service health"
echo "   Visit http://localhost:3000     # Frontend"

# Show status
echo ""
echo "📊 Current Status:"
./docker-dev.sh status
