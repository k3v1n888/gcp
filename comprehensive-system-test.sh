#!/bin/bash

# Comprehensive Sentient AI SOC System Test
# This script tests all the key functionalities of the system

echo "🧪 Sentient AI SOC System - Comprehensive Live Test"
echo "=================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper function for testing API endpoints
test_api() {
    local endpoint=$1
    local description=$2
    local expected_field=$3
    
    echo -n "Testing $description... "
    
    response=$(curl -s -w "%{http_code}" -o /tmp/api_response.json "http://localhost:8001$endpoint")
    http_code="${response: -3}"
    
    if [ "$http_code" = "200" ]; then
        if [ -n "$expected_field" ]; then
            if jq -e ".$expected_field" /tmp/api_response.json > /dev/null 2>&1; then
                count=$(jq -r ".$expected_field | length" /tmp/api_response.json 2>/dev/null || jq -r ".$expected_field" /tmp/api_response.json 2>/dev/null)
                echo -e "${GREEN}✅ PASS${NC} (${count} items)"
            else
                echo -e "${RED}❌ FAIL${NC} (missing $expected_field)"
                return 1
            fi
        else
            echo -e "${GREEN}✅ PASS${NC}"
        fi
    else
        echo -e "${RED}❌ FAIL${NC} (HTTP $http_code)"
        return 1
    fi
    return 0
}

# Test frontend accessibility
test_frontend() {
    echo -n "Testing Frontend Accessibility... "
    response=$(curl -s -w "%{http_code}" -o /dev/null "http://localhost:3000")
    if [ "$response" = "200" ]; then
        echo -e "${GREEN}✅ PASS${NC}"
        return 0
    else
        echo -e "${RED}❌ FAIL${NC} (HTTP $response)"
        return 1
    fi
}

# Test Docker containers
test_containers() {
    echo "🐳 Docker Container Health Check:"
    echo "=================================="
    
    containers=("ssai_postprocess" "ssai_frontend" "ssai_db" "ssai_redis" "ssai_orchestrator")
    
    for container in "${containers[@]}"; do
        echo -n "  $container: "
        if docker ps --format "table {{.Names}}" | grep -q "^$container$"; then
            status=$(docker ps --format "table {{.Names}}\t{{.Status}}" | grep "^$container" | awk '{print $2}')
            if [[ $status == "Up" ]]; then
                echo -e "${GREEN}✅ Running${NC}"
            else
                echo -e "${YELLOW}⚠️  $status${NC}"
            fi
        else
            echo -e "${RED}❌ Not Running${NC}"
        fi
    done
    echo ""
}

# Test all API endpoints
test_apis() {
    echo "🔗 API Endpoints Test:"
    echo "======================"
    
    failed_tests=0
    
    # Core APIs
    test_api "/api/health" "Health Check" "" || ((failed_tests++))
    test_api "/api/incidents" "Incidents API" "incidents" || ((failed_tests++))
    test_api "/api/threats" "Threats API" "threats" || ((failed_tests++))
    test_api "/api/ai/status" "AI Status API" "models" || ((failed_tests++))
    
    # Analytics APIs
    test_api "/api/analytics/summary" "Analytics Summary" "by_type" || ((failed_tests++))
    test_api "/api/analytics/incidents-summary" "Incidents Analytics" "total" || ((failed_tests++))
    test_api "/api/forecasting/24_hour" "Threat Forecast" "forecast" || ((failed_tests++))
    test_api "/api/correlation/summary" "Correlation Analysis" "correlations" || ((failed_tests++))
    
    # Admin APIs
    test_api "/api/admin/health/system" "System Health" "" || ((failed_tests++))
    test_api "/api/admin/health/apis" "APIs Health" "" || ((failed_tests++))
    test_api "/api/admin/health/docker" "Docker Health" "" || ((failed_tests++))
    test_api "/api/admin/health/ai-models" "AI Models Health" "" || ((failed_tests++))
    
    echo ""
    if [ $failed_tests -eq 0 ]; then
        echo -e "${GREEN}🎉 All API tests passed!${NC}"
    else
        echo -e "${RED}❌ $failed_tests API tests failed${NC}"
    fi
    echo ""
    
    return $failed_tests
}

# Test database connectivity
test_database() {
    echo "💾 Database Connectivity Test:"
    echo "==============================="
    
    echo -n "Testing Database Connection... "
    if docker exec ssai_db pg_isready -U user -d cyberdb > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PASS${NC}"
        
        echo -n "Testing Table Creation... "
        table_count=$(docker exec ssai_db psql -U user -d cyberdb -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null | xargs)
        if [ "$table_count" -gt 0 ]; then
            echo -e "${GREEN}✅ PASS${NC} ($table_count tables)"
        else
            echo -e "${RED}❌ FAIL${NC} (No tables found)"
        fi
    else
        echo -e "${RED}❌ FAIL${NC}"
    fi
    echo ""
}

# Test individual features
test_features() {
    echo "🎯 Feature-Specific Tests:"
    echo "=========================="
    
    # Test Incidents
    echo -n "Incidents Page Data: "
    incident_count=$(curl -s "http://localhost:8001/api/incidents" | jq -r '.incidents | length' 2>/dev/null)
    if [ "$incident_count" -gt 0 ]; then
        echo -e "${GREEN}✅ $incident_count incidents loaded${NC}"
    else
        echo -e "${RED}❌ No incidents found${NC}"
    fi
    
    # Test Threats
    echo -n "Threats Page Data: "
    threat_count=$(curl -s "http://localhost:8001/api/threats" | jq -r '.threats | length' 2>/dev/null)
    if [ "$threat_count" -gt 0 ]; then
        echo -e "${GREEN}✅ $threat_count threats loaded${NC}"
    else
        echo -e "${RED}❌ No threats found${NC}"
    fi
    
    # Test AI Models
    echo -n "AI Models Data: "
    model_count=$(curl -s "http://localhost:8001/api/ai/status" | jq -r '.models | keys | length' 2>/dev/null)
    if [ "$model_count" -gt 0 ]; then
        echo -e "${GREEN}✅ $model_count AI models loaded${NC}"
    else
        echo -e "${RED}❌ No AI models found${NC}"
    fi
    
    # Test Health Dashboard
    echo -n "Health Dashboard: "
    health_status=$(curl -s "http://localhost:8001/api/admin/health/system" | jq -r '.status' 2>/dev/null)
    if [ "$health_status" = "healthy" ]; then
        echo -e "${GREEN}✅ System healthy${NC}"
    else
        echo -e "${YELLOW}⚠️  Status: $health_status${NC}"
    fi
    
    echo ""
}

# Main test execution
main() {
    echo "Starting comprehensive system test..."
    echo ""
    
    # Test containers
    test_containers
    
    # Test frontend
    echo "🌐 Frontend Test:"
    echo "=================="
    test_frontend
    echo ""
    
    # Test database
    test_database
    
    # Test APIs
    test_apis
    api_result=$?
    
    # Test features
    test_features
    
    # Summary
    echo "📊 Test Summary:"
    echo "================"
    
    if [ $api_result -eq 0 ]; then
        echo -e "${GREEN}✅ System Status: OPERATIONAL${NC}"
        echo ""
        echo "🎯 Manual Testing Instructions:"
        echo "1. Open http://localhost:3000 in your browser"
        echo "2. Navigate to different tabs (Dashboard, Incidents, Threats, AI Models)"
        echo "3. Check that data is loading and displaying correctly"
        echo "4. Verify that all charts and statistics show real data (not zeros)"
        echo "5. Test the admin panel health checks"
        echo ""
        echo -e "${BLUE}🔧 If you see any zeros in the UI, check browser console for errors${NC}"
    else
        echo -e "${RED}❌ System Status: ISSUES DETECTED${NC}"
        echo ""
        echo "🔧 Troubleshooting Steps:"
        echo "1. Check Docker container logs: docker logs ssai_postprocess"
        echo "2. Verify database connection: docker exec ssai_db pg_isready -U user -d cyberdb"
        echo "3. Restart containers if needed: docker restart ssai_postprocess ssai_frontend"
        echo "4. Check browser console for frontend errors"
    fi
}

# Run the tests
main

# Clean up temporary file
rm -f /tmp/api_response.json
