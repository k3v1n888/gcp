#!/bin/bash

echo "💉 QUICK DATA INJECTION"
echo "======================="
echo "Injecting 5 test threats quickly..."

BACKEND_URL="http://192.168.64.13:8000"

# Simple threat templates
THREATS=(
    '{"source": "quick_test", "data": {"title": "SQL Injection Test", "description": "Quick test threat", "severity": "high", "source_ip": "203.0.113.45", "destination_ip": "10.0.1.50", "timestamp": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'"}}' 
    
    '{"source": "quick_test", "data": {"title": "Port Scan Test", "description": "Network scanning detected", "severity": "medium", "source_ip": "185.220.101.50", "destination_ip": "10.0.1.0/24", "timestamp": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'"}}' 
    
    '{"source": "quick_test", "data": {"title": "Malware Test", "description": "Suspicious file behavior", "severity": "critical", "source_ip": "10.0.1.45", "destination_ip": "10.0.1.45", "timestamp": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'"}}' 
    
    '{"source": "quick_test", "data": {"title": "Brute Force Test", "description": "Multiple login failures", "severity": "medium", "source_ip": "91.189.88.152", "destination_ip": "10.0.1.10", "timestamp": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'"}}' 
    
    '{"source": "quick_test", "data": {"title": "Suspicious Activity", "description": "Unusual network behavior", "severity": "high", "source_ip": "167.99.247.33", "destination_ip": "10.0.1.99", "timestamp": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'"}}'
)

for i in "${!THREATS[@]}"; do
    threat_num=$((i + 1))
    echo -n "[$threat_num/5] Injecting threat... "
    
    response=$(curl -s --max-time 5 -X POST "$BACKEND_URL/api/ai/process" \
        -H "Content-Type: application/json" \
        -d "${THREATS[$i]}" 2>/dev/null)
    
    if [ $? -eq 0 ] && [ -n "$response" ]; then
        echo "✅ Success"
    else
        echo "⚠️ Timeout/Error"
    fi
    
    sleep 1
done

echo ""
echo "🎉 Quick injection complete!"
echo ""
echo "📊 Check results:"
echo "   Database: curl -s 'http://192.168.64.13:8000/api/threats?limit=5' | jq ."
echo "   Dashboard: http://192.168.64.13:3000/dashboard"
