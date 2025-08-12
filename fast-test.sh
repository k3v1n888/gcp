#!/bin/bash

echo "🚀 FAST AI INTEGRATION TEST"
echo "============================"
echo "Testing with timeouts to avoid hanging..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to test with timeout
test_endpoint() {
    local name=$1
    local url=$2
    local timeout=${3:-5}
    local expected_status=${4:-200}
    
    echo -n "   Testing $name... "
    
    # Use curl with timeout
    local response=$(curl -s --max-time $timeout -w "%{http_code}" -o /dev/null "$url" 2>/dev/null)
    
    if [ "$response" = "$expected_status" ]; then
        echo -e "${GREEN}✅ OK${NC}"
        return 0
    else
        echo -e "${RED}❌ FAIL (Status: $response)${NC}"
        return 1
    fi
}

# Function to test API with data
test_api_with_data() {
    local name=$1
    local url=$2
    local timeout=${3:-5}
    
    echo -n "   Testing $name... "
    
    local response=$(curl -s --max-time $timeout "$url" 2>/dev/null)
    local exit_code=$?
    
    if [ $exit_code -eq 0 ] && [ -n "$response" ]; then
        # Try to count items if it's JSON array
        local count=$(echo "$response" | jq 'length' 2>/dev/null || echo "data received")
        echo -e "${GREEN}✅ OK ($count items)${NC}"
        return 0
    else
        echo -e "${RED}❌ TIMEOUT or NO DATA${NC}"
        return 1
    fi
}

echo "1️⃣  Basic Service Health Checks..."
test_endpoint "Backend API" "http://192.168.64.13:8000/api/health" 3
test_endpoint "Frontend" "http://192.168.64.13:3000" 3
test_endpoint "AI Service" "http://192.168.64.13:8001/health" 3

echo ""
echo "2️⃣  AI System Status..."
echo -n "   AI Orchestrator Status... "
AI_STATUS=$(curl -s --max-time 5 "http://192.168.64.13:8000/api/ai/status" 2>/dev/null)
if [ $? -eq 0 ] && [ -n "$AI_STATUS" ]; then
    ORCHESTRATOR_STATUS=$(echo "$AI_STATUS" | jq -r '.data.orchestrator // "unknown"' 2>/dev/null || echo "responding")
    echo -e "${GREEN}✅ $ORCHESTRATOR_STATUS${NC}"
else
    echo -e "${YELLOW}⚠️  TIMEOUT - may be processing${NC}"
fi

echo ""
echo "3️⃣  Quick Data Test..."
test_api_with_data "Threats Database" "http://192.168.64.13:8000/api/threats?limit=5" 5
test_api_with_data "Incidents Database" "http://192.168.64.13:8000/api/incidents?limit=5" 5

echo ""
echo "4️⃣  AI Processing Test..."
echo -n "   Testing AI Pipeline... "

# Simple test data
TEST_DATA='{
  "source": "fast_test",
  "data": {
    "title": "Test Threat",
    "description": "Quick test of AI processing",
    "severity": "medium",
    "source_ip": "192.168.1.100",
    "destination_ip": "10.0.1.50",
    "timestamp": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'"
  }
}'

# Test AI processing with short timeout
AI_RESULT=$(curl -s --max-time 8 -X POST "http://192.168.64.13:8000/api/ai/process" \
    -H "Content-Type: application/json" \
    -d "$TEST_DATA" 2>/dev/null)

if [ $? -eq 0 ] && [ -n "$AI_RESULT" ]; then
    # Check for success indicators
    if echo "$AI_RESULT" | jq -e '.decision_id' > /dev/null 2>&1; then
        DECISION_ID=$(echo "$AI_RESULT" | jq -r '.decision_id')
        echo -e "${GREEN}✅ SUCCESS (Decision: $DECISION_ID)${NC}"
    elif echo "$AI_RESULT" | jq -e '.success' > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PROCESSED${NC}"
    else
        echo -e "${YELLOW}⚠️  PARTIAL RESPONSE${NC}"
    fi
else
    echo -e "${RED}❌ TIMEOUT (>8s)${NC}"
fi

echo ""
echo "5️⃣  Dashboard Access Test..."
DASHBOARDS=(
    "Main Dashboard:http://192.168.64.13:3000/dashboard"
    "AI Models:http://192.168.64.13:3000/ai-models"
    "Connectors:http://192.168.64.13:3000/connectors"
    "Admin Panel:http://192.168.64.13:3000/admin"
)

for dashboard in "${DASHBOARDS[@]}"; do
    name=$(echo "$dashboard" | cut -d: -f1)
    url=$(echo "$dashboard" | cut -d: -f2-)
    test_endpoint "$name" "$url" 3
done

echo ""
echo "=================================="
echo "🎯 FAST TEST COMPLETE!"
echo "=================================="
echo ""

# Quick system summary
echo "📊 Quick System Summary:"
echo -n "   • Backend: "
curl -s --max-time 2 "http://192.168.64.13:8000/api/health" > /dev/null 2>&1 && echo -e "${GREEN}Online${NC}" || echo -e "${RED}Offline${NC}"

echo -n "   • Frontend: "
curl -s --max-time 2 "http://192.168.64.13:3000" > /dev/null 2>&1 && echo -e "${GREEN}Online${NC}" || echo -e "${RED}Offline${NC}"

echo -n "   • AI Service: "
curl -s --max-time 2 "http://192.168.64.13:8001/health" > /dev/null 2>&1 && echo -e "${GREEN}Online${NC}" || echo -e "${RED}Offline${NC}"

echo ""
echo "🔗 Access Points:"
echo "   📊 AI Dashboard:     http://192.168.64.13:3000/ai-models"
echo "   🏠 Main Dashboard:   http://192.168.64.13:3000/dashboard"
echo "   🔌 Data Connectors:  http://192.168.64.13:3000/connectors"
echo "   ⚙️  Admin Panel:     http://192.168.64.13:3000/admin"
echo ""
echo -e "${BLUE}💡 TIP: If tests timeout, services may be under load. Try individual endpoints manually.${NC}"
