#!/bin/bash

# CXyber AI SOC System Startup Script
# This script launches the complete multi-model AI SOC architecture

echo "🚀 Starting CXyber AI SOC Multi-Model Architecture..."
echo ""

# Export environment variables for orchestration connectors (optional)
export SLACK_WEBHOOK_URL=${SLACK_WEBHOOK_URL:-""}
export TEAMS_WEBHOOK_URL=${TEAMS_WEBHOOK_URL:-""}
export JIRA_BASE_URL=${JIRA_BASE_URL:-""}
export JIRA_EMAIL=${JIRA_EMAIL:-""}
export JIRA_API_TOKEN=${JIRA_API_TOKEN:-""}
export JIRA_PROJECT_KEY=${JIRA_PROJECT_KEY:-"SEC"}

echo "📋 Architecture Overview:"
echo "  Model A: Data Intake & Normalization AI (Port 8000)"
echo "  Model B: Post-Processing & Enrichment AI (Port 8001)"  
echo "  Model C: Quantum AI Predictive Security Engine (Port 9000)"
echo "  Threat Service: Model C Wrapper (Port 8002)"
echo "  Orchestrator: Action Execution (Port 8003)"
echo "  Console: Web Approval Interface (Port 8005)"
echo "  Frontend: React Dashboard (Port 3000)"
echo ""

echo "🔧 Building services..."
docker-compose -f docker-compose.cxyber.yml build

echo "🟢 Starting all services..."
docker-compose -f docker-compose.cxyber.yml up -d

echo "⏳ Waiting for services to initialize..."
sleep 30

echo "📊 Service Status Check:"
docker-compose -f docker-compose.cxyber.yml ps

echo ""
echo "🎯 Your CXyber AI SOC System is now running!"
echo ""
echo "📱 Access URLs:"
echo "  🌐 Main Dashboard: http://localhost:3000"
echo "  📥 Data Ingest API: http://localhost:8000/docs"
echo "  🧠 Post-Process API: http://localhost:8001/docs" 
echo "  🔮 Threat Model API: http://localhost:9000/docs"
echo "  🎯 Threat Service API: http://localhost:8002/docs"
echo "  🎭 Orchestrator API: http://localhost:8003/docs"
echo "  ⚙️  Approval Console: http://localhost:8005"
echo ""
echo "🧪 Test your AI models:"
echo "  curl -X POST http://localhost:9000/predict \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"features\":{\"cvss_score\":8.5,\"criticality_score\":0.9,\"ioc_risk_score\":85}}'"
echo ""
echo "📚 Data Flow:"
echo "  [Security Tool] → Model A (Normalize) → Model B (Enrich) → Model C (Predict) → [Action]"
echo ""

# Optional: Run a quick health check
echo "🏥 Health Check (after 1 minute):"
sleep 30
echo "  Model A (Ingest): $(curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/health)"
echo "  Model B (Backend): $(curl -s -o /dev/null -w '%{http_code}' http://localhost:8001/health 2>/dev/null || echo 'Starting...')"
echo "  Model C (AI): $(curl -s -o /dev/null -w '%{http_code}' http://localhost:9000/health 2>/dev/null || echo 'Starting...')"
echo "  Threat Service: $(curl -s -o /dev/null -w '%{http_code}' http://localhost:8002/health 2>/dev/null || echo 'Starting...')"
echo "  Frontend: $(curl -s -o /dev/null -w '%{http_code}' http://localhost:3000 2>/dev/null || echo 'Starting...')"

echo ""
echo "✅ CXyber AI SOC System successfully deployed!"
echo "   Monitor logs: docker-compose -f docker-compose.cxyber.yml logs -f"
echo "   Stop system: docker-compose -f docker-compose.cxyber.yml down"
