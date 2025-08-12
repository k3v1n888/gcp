#!/bin/bash

echo "🤖 Starting Advanced AI Services Locally"
echo "========================================="

# Password for VM authentication
export SSHPASS='V!g1l@nt'

# Function to run command on VM with password
vm_exec() {
    sshpass -e ssh -o StrictHostKeyChecking=no kevin@192.168.64.13 "$1"
}

echo ""
echo "0️⃣  Setting up AI Models in AI Service Container..."
echo "Copying AI models from backend to AI service container..."
vm_exec "docker exec ssai_backend tar -czf /tmp/ai_models.tar.gz -C /app cxyber_ai_soc_suite"
vm_exec "docker cp ssai_backend:/tmp/ai_models.tar.gz /tmp/ai_models.tar.gz"
vm_exec "docker cp /tmp/ai_models.tar.gz ssai_ai_service:/app/ai_models.tar.gz"
vm_exec "docker exec ssai_ai_service tar -xzf /app/ai_models.tar.gz -C /app"
vm_exec "docker exec ssai_ai_service pip install fastapi uvicorn pydantic scikit-learn pandas numpy"

echo ""
echo "1️⃣  Starting AI Data Ingestion Service (Port 8001)..."
vm_exec "docker exec -d ssai_ai_service bash -c 'cd /app/cxyber_ai_soc_suite/services/ingest && uvicorn app:app --host 0.0.0.0 --port 8001 > /tmp/ingest.log 2>&1'" &

sleep 3

echo ""
echo "2️⃣  Starting AI Threat Scoring Service (Port 8002)..."
vm_exec "docker exec -d ssai_ai_service bash -c 'cd /app/cxyber_ai_soc_suite/services/threat_service && uvicorn app:app --host 0.0.0.0 --port 8002 > /tmp/threat.log 2>&1'" &

sleep 3

echo ""
echo "3️⃣  Starting AI Policy Decision Service (Port 8003)..."
vm_exec "docker exec -d ssai_ai_service bash -c 'cd /app/cxyber_ai_soc_suite/services/policy_service && uvicorn app:app --host 0.0.0.0 --port 8003 > /tmp/policy.log 2>&1'" &

sleep 3

echo ""
echo "4️⃣  Starting AI Orchestrator Service (Port 8004)..."
vm_exec "docker exec -d ssai_ai_service bash -c 'cd /app/cxyber_ai_soc_suite/services/orchestrator && uvicorn app:app --host 0.0.0.0 --port 8004 > /tmp/orchestrator.log 2>&1'" &

sleep 5

echo ""
echo "5️⃣  Checking AI Services Status..."
echo ""

# Check if services are running
echo "🔍 AI Service Status:"
vm_exec "ps aux | grep python3 | grep -E '(ingest|threat_service|policy_service|orchestrator)' | grep -v grep" || echo "⚠️  Some AI services may still be starting..."

echo ""
echo "6️⃣  Testing AI Service Endpoints..."

# Test each service
echo "Testing AI Ingestion Service..."
curl -s -m 5 http://192.168.64.13:8001/health && echo "✅ Ingestion Service: OK" || echo "❌ Ingestion Service: Not Ready"

echo "Testing AI Threat Scoring Service..."
curl -s -m 5 http://192.168.64.13:8002/health && echo "✅ Threat Scoring Service: OK" || echo "❌ Threat Scoring Service: Not Ready"

echo "Testing AI Policy Decision Service..."
curl -s -m 5 http://192.168.64.13:8003/health && echo "✅ Policy Decision Service: OK" || echo "❌ Policy Decision Service: Not Ready"

echo "Testing AI Orchestrator Service..."
curl -s -m 5 http://192.168.64.13:8004/health && echo "✅ Orchestrator Service: OK" || echo "❌ Orchestrator Service: Not Ready"

echo ""
echo "7️⃣  Starting AI Orchestrator in Backend..."
curl -s -X POST http://192.168.64.13:8000/api/ai/orchestrator/start && echo "✅ Backend AI Orchestrator: Started" || echo "⚠️  Backend AI Orchestrator: May already be running"

echo ""
echo "✅ AI Services Startup Complete!"
echo ""
echo "🔗 Available AI Services:"
echo "   📥 Data Ingestion:    http://192.168.64.13:8001"
echo "   🎯 Threat Scoring:    http://192.168.64.13:8002" 
echo "   🛡️  Policy Decisions:  http://192.168.64.13:8003"
echo "   🤖 AI Orchestrator:   http://192.168.64.13:8004"
echo "   📊 AI Dashboard:      http://192.168.64.13:3000/ai-models"
echo ""
echo "📋 To test the full AI pipeline:"
echo "   ./test-ai-integration.sh"
