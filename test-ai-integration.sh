#!/bin/bash

echo "🤖 AI System Integration Test"
echo "========================================"

# Test 1: Backend AI API endpoints
echo ""
echo "1️⃣  Testing AI API Endpoints..."
echo "Testing AI system status..."
curl -s "http://192.168.64.13:8000/api/ai/status" | jq '.data.orchestrator_status' || echo "❌ AI status endpoint failed"

echo "Testing AI models..."
curl -s "http://192.168.64.13:8000/api/ai/models" | jq '.total_models' || echo "❌ AI models endpoint failed"

echo "Testing AI health..."
curl -s "http://192.168.64.13:8000/api/ai/health" | jq '.status' || echo "❌ AI health endpoint failed"

# Test 2: AI Data Processing
echo ""
echo "2️⃣  Testing AI Data Processing..."
curl -X POST "http://192.168.64.13:8000/api/ai/process" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "test",
    "data": {
      "title": "Test SQL Injection Attempt",
      "description": "Suspicious SQL injection detected from IP 192.168.1.100",
      "severity": "high",
      "source_ip": "192.168.1.100",
      "timestamp": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'"
    }
  }' | jq '.result.decision_id' || echo "❌ AI processing failed"

# Test 3: Universal Data Connector with AI
echo ""
echo "3️⃣  Testing Universal Data Connector with AI..."
curl -X POST "http://192.168.64.13:8000/api/connectors/collect" \
  -H "Content-Type: application/json" \
  -d '{}' | jq '.threats_analyzed' || echo "❌ Connector AI analysis failed"

# Test 4: Database verification
echo ""
echo "4️⃣  Verifying Database Integration..."
THREAT_COUNT=$(curl -s "http://192.168.64.13:8000/api/threats" | jq 'length' 2>/dev/null || echo "0")
echo "📊 Threats in database: $THREAT_COUNT"

INCIDENT_COUNT=$(curl -s "http://192.168.64.13:8000/api/incidents" | jq 'length' 2>/dev/null || echo "0")
echo "📋 Incidents in database: $INCIDENT_COUNT"

# Test 5: System Health
echo ""
echo "5️⃣  System Health Check..."
echo "Backend health:"
curl -s "http://192.168.64.13:8000/api/health" | jq '.status' || echo "❌ Backend unhealthy"

echo "Frontend accessibility:"
curl -s -o /dev/null -w "%{http_code}" "http://192.168.64.13:3000" || echo "❌ Frontend inaccessible"

# Test 6: AI Orchestrator Status
echo ""
echo "6️⃣  AI Orchestrator Status..."
curl -s "http://192.168.64.13:8000/api/ai/performance" | jq '.metrics.processing_stats.threats_last_24h' || echo "❌ Performance metrics failed"

echo ""
echo "✅ AI Integration Test Complete!"
echo "🔗 Access the AI Dashboard at: http://192.168.64.13:3000/ai-models"
echo "📊 View main dashboard at: http://192.168.64.13:3000/dashboard"
