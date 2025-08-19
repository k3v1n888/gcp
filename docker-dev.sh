#!/bin/bash

# Docker Development Environment Manager
# Complete containerized development setup

echo "🐳 SSAI Docker Development Environment"
echo "======================================"

case "$1" in
    "start"|"up")
        echo "🚀 Starting all services..."
        docker-compose -f docker-compose.full.yml up -d
        echo ""
        echo "✅ Services started! Available at:"
        echo "   🌐 Frontend:  http://localhost:3000"
        echo "   🔧 Backend:   http://localhost:8000" 
        echo "   🤖 AI Service: http://localhost:8001"
        echo "   📚 API Docs:  http://localhost:8000/docs"
        echo ""
        echo "🔍 Check status: ./docker-dev.sh status"
        ;;
    
    "stop"|"down")
        echo "🛑 Stopping all services..."
        docker-compose -f docker-compose.full.yml down
        echo "✅ All services stopped"
        ;;
    
    "restart")
        echo "🔄 Restarting all services..."
        docker-compose -f docker-compose.full.yml down
        docker-compose -f docker-compose.full.yml up -d
        echo "✅ Services restarted"
        ;;
    
    "build")
        echo "🔨 Rebuilding all containers..."
        docker-compose -f docker-compose.full.yml build --no-cache
        docker-compose -f docker-compose.full.yml up -d
        echo "✅ All containers rebuilt and started"
        ;;
    
    "logs")
        SERVICE=${2:-""}
        if [ -z "$SERVICE" ]; then
            echo "📋 Showing logs for all services..."
            docker-compose -f docker-compose.full.yml logs -f
        else
            echo "📋 Showing logs for $SERVICE..."
            docker-compose -f docker-compose.full.yml logs -f $SERVICE
        fi
        ;;
    
    "status")
        echo "📊 Service Status:"
        docker-compose -f docker-compose.full.yml ps
        echo ""
        echo "🔍 Health Checks:"
        curl -s http://localhost:3000 >/dev/null && echo "✅ Frontend: Running" || echo "❌ Frontend: Down"
        curl -s http://localhost:8000 >/dev/null && echo "✅ Backend: Running" || echo "❌ Backend: Down"
        curl -s http://localhost:8001 >/dev/null && echo "✅ AI Service: Running" || echo "❌ AI Service: Down"
        ;;
    
    "clean")
        echo "🧹 Cleaning up Docker resources..."
        docker-compose -f docker-compose.full.yml down -v
        docker system prune -f
        echo "✅ Cleanup complete"
        ;;
    
    "shell")
        SERVICE=${2:-"backend"}
        echo "🐚 Opening shell in $SERVICE container..."
        docker-compose -f docker-compose.full.yml exec $SERVICE /bin/bash
        ;;
    
    *)
        echo "Usage: $0 {start|stop|restart|build|logs|status|clean|shell}"
        echo ""
        echo "Commands:"
        echo "  start/up    - Start all services"
        echo "  stop/down   - Stop all services"  
        echo "  restart     - Restart all services"
        echo "  build       - Rebuild and start all containers"
        echo "  logs [svc]  - Show logs (optionally for specific service)"
        echo "  status      - Show service status and health"
        echo "  clean       - Stop services and clean up volumes"
        echo "  shell [svc] - Open shell in container (default: backend)"
        echo ""
        echo "Services: frontend, backend, ai-service, db, redis"
        echo ""
        echo "🌐 Your URLs:"
        echo "   Frontend:  http://localhost:3000"
        echo "   Backend:   http://localhost:8000"
        echo "   AI Service: http://localhost:8001"
        exit 1
        ;;
esac
