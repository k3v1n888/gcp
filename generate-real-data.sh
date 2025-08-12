#!/bin/bash

echo "🌊 REAL-TIME CYBERSECURITY DATA STREAM GENERATOR"
echo "================================================="
echo "Continuously generating realistic threat data for AI processing"
echo ""

# Configuration
BACKEND_URL="http://192.168.64.13:8000"
DELAY_BETWEEN_THREATS=5  # seconds
TOTAL_THREATS=${1:-50}   # default 50 threats, or first argument

# Threat templates with realistic cybersecurity scenarios
declare -a THREAT_TEMPLATES=(
    # Network-based threats
    '{"source": "suricata", "severity": "critical", "category": "network", "title": "SQL Injection Attack", "base_description": "SQL injection attempt detected against web application", "ips": ["203.0.113.45", "198.51.100.22", "192.0.2.100"]}'
    
    '{"source": "zeek", "severity": "high", "category": "network", "title": "Port Scan Activity", "base_description": "Systematic port scanning detected from external IP", "ips": ["185.220.101.50", "167.99.247.33", "104.248.111.22"]}'
    
    '{"source": "pfsense", "severity": "medium", "category": "network", "title": "Brute Force SSH", "base_description": "Multiple failed SSH authentication attempts", "ips": ["91.189.88.152", "209.97.176.100", "45.32.105.18"]}'
    
    # Endpoint threats  
    '{"source": "wazuh", "severity": "critical", "category": "endpoint", "title": "Malware Detected", "base_description": "Malicious file detected and quarantined", "ips": ["10.0.1.45", "10.0.1.88", "10.0.1.92"]}'
    
    '{"source": "ossec", "severity": "high", "category": "endpoint", "title": "Privilege Escalation", "base_description": "Local privilege escalation attempt detected", "ips": ["10.0.1.15", "10.0.1.67", "10.0.1.23"]}'
    
    '{"source": "crowdstrike", "severity": "critical", "category": "endpoint", "title": "Ransomware Activity", "base_description": "File encryption activity detected - potential ransomware", "ips": ["10.0.1.78", "10.0.1.34", "10.0.1.56"]}'
    
    # Cloud & identity threats
    '{"source": "azure_ad", "severity": "medium", "category": "identity", "title": "Suspicious Login", "base_description": "Login from unusual geographic location", "ips": ["203.0.113.77", "198.51.100.88", "192.0.2.99"]}'
    
    '{"source": "aws_cloudtrail", "severity": "high", "category": "cloud", "title": "Unusual API Activity", "base_description": "High volume of API calls from single user", "ips": ["52.86.85.143", "54.208.100.253", "34.207.173.82"]}'
    
    # Application threats
    '{"source": "mod_security", "severity": "high", "category": "application", "title": "Web Application Attack", "base_description": "Cross-site scripting attempt detected", "ips": ["203.0.113.66", "198.51.100.77", "192.0.2.44"]}'
    
    '{"source": "elastic_siem", "severity": "critical", "category": "application", "title": "Data Exfiltration", "base_description": "Large data transfer to external destination", "ips": ["10.0.1.99", "10.0.1.12", "10.0.1.87"]}'
)

# Function to generate random threat data
generate_threat() {
    local template_index=$((RANDOM % ${#THREAT_TEMPLATES[@]}))
    local template=${THREAT_TEMPLATES[$template_index]}
    
    # Extract template data
    local source=$(echo "$template" | jq -r '.source')
    local severity=$(echo "$template" | jq -r '.severity') 
    local category=$(echo "$template" | jq -r '.category')
    local title=$(echo "$template" | jq -r '.title')
    local base_description=$(echo "$template" | jq -r '.base_description')
    local ips_array=$(echo "$template" | jq -r '.ips[]')
    
    # Select random IP from template
    local ip_array=($ips_array)
    local random_ip=${ip_array[$RANDOM % ${#ip_array[@]}]}
    
    # Generate random destination IP based on category
    local dest_ip
    case $category in
        "network"|"application")
            dest_ip="10.0.1.$((RANDOM % 254 + 1))"
            ;;
        "endpoint")
            dest_ip="127.0.0.1"
            ;;
        "cloud"|"identity")
            dest_ip="external"
            ;;
        *)
            dest_ip="10.0.1.$((RANDOM % 254 + 1))"
            ;;
    esac
    
    # Add variety to descriptions
    local descriptions=(
        "$base_description from suspicious source"
        "$base_description - investigation required"
        "$base_description detected by security monitoring"
        "$base_description - automated response initiated"
        "$base_description - correlating with threat intelligence"
    )
    local description=${descriptions[$RANDOM % ${#descriptions[@]}]}
    
    # Generate additional context based on category
    local additional_data
    case $category in
        "network")
            additional_data='{"protocol": "tcp", "port": '$((RANDOM % 65535))', "packets": '$((RANDOM % 1000))'}' 
            ;;
        "endpoint")
            local processes=("powershell.exe" "cmd.exe" "rundll32.exe" "regsvr32.exe" "svchost.exe")
            local process=${processes[$RANDOM % ${#processes[@]}]}
            additional_data='{"process": "'$process'", "pid": '$((RANDOM % 10000))', "parent_process": "explorer.exe"}'
            ;;
        "cloud")
            local services=("EC2" "S3" "IAM" "CloudTrail" "Lambda")
            local service=${services[$RANDOM % ${#services[@]}]}
            additional_data='{"service": "'$service'", "region": "us-east-1", "api_calls": '$((RANDOM % 500))'}'
            ;;
        "identity") 
            local locations=("Brazil" "China" "Russia" "Unknown" "Romania")
            local location=${locations[$RANDOM % ${#locations[@]}]}
            additional_data='{"location": "'$location'", "user_agent": "Mozilla/5.0", "failed_attempts": '$((RANDOM % 10))'}'
            ;;
        "application")
            additional_data='{"url": "/admin/login", "method": "POST", "payload_size": '$((RANDOM % 1000))'}'
            ;;
        *)
            additional_data='{"detection_confidence": 0.'$((RANDOM % 100))', "severity_score": '$((RANDOM % 10))'}'
            ;;
    esac
    
    # Create the threat JSON
    cat <<EOF
{
  "source": "$source",
  "data": {
    "title": "$title - $(date '+%H:%M:%S')",
    "description": "$description",
    "severity": "$severity",
    "source_ip": "$random_ip",
    "destination_ip": "$dest_ip", 
    "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
    "category": "$category",
    "additional_data": $additional_data
  }
}
EOF
}

# Function to send threat to AI pipeline
send_threat() {
    local threat_data="$1"
    local threat_id=$2
    
    echo "🔄 [$threat_id/$TOTAL_THREATS] Processing: $(echo "$threat_data" | jq -r '.data.title')"
    
    # Send to AI processing pipeline
    local result=$(curl -s -X POST "$BACKEND_URL/api/ai/process" \
        -H "Content-Type: application/json" \
        -d "$threat_data" \
        --max-time 10)
    
    if echo "$result" | jq -e '.success' > /dev/null 2>&1; then
        local decision_id=$(echo "$result" | jq -r '.decision_id // "unknown"')
        echo "   ✅ AI processed successfully (Decision ID: $decision_id)"
    elif echo "$result" | jq -e '.decision_id' > /dev/null 2>&1; then
        local decision_id=$(echo "$result" | jq -r '.decision_id')
        echo "   ✅ AI processed (Decision ID: $decision_id)"
    else
        echo "   ⚠️  Processing completed (AI may be using fallback mode)"
    fi
}

# Function to display real-time statistics
show_statistics() {
    echo ""
    echo "📊 Real-time System Statistics:"
    
    # Database counts
    local total_threats=$(curl -s "$BACKEND_URL/api/threats" | jq 'length' 2>/dev/null || echo "N/A")
    local total_incidents=$(curl -s "$BACKEND_URL/api/incidents" | jq 'length' 2>/dev/null || echo "N/A")
    
    echo "   📈 Database: $total_threats threats, $total_incidents incidents"
    
    # AI system status
    local ai_status=$(curl -s "$BACKEND_URL/api/ai/status" 2>/dev/null)
    if [ $? -eq 0 ]; then
        local orchestrator_status=$(echo "$ai_status" | jq -r '.data.orchestrator // "unknown"')
        echo "   🤖 AI Orchestrator: $orchestrator_status"
    fi
    
    echo ""
}

# Main execution function
main() {
    echo "🚀 Starting Real-time Data Stream..."
    echo "   📊 Total threats to generate: $TOTAL_THREATS"
    echo "   ⏱️  Delay between threats: ${DELAY_BETWEEN_THREATS}s"
    echo ""
    
    for i in $(seq 1 $TOTAL_THREATS); do
        # Generate and send threat
        local threat_data=$(generate_threat)
        send_threat "$threat_data" "$i"
        
        # Show statistics every 10 threats
        if [ $((i % 10)) -eq 0 ]; then
            show_statistics
        fi
        
        # Wait before next threat (except for last one)
        if [ $i -lt $TOTAL_THREATS ]; then
            sleep $DELAY_BETWEEN_THREATS
        fi
    done
    
    echo ""
    echo "🎉 Data stream generation complete!"
    show_statistics
    echo ""
    echo "🔗 View the results in your dashboards:"
    echo "   📊 AI Dashboard:     http://192.168.64.13:3000/ai-models"
    echo "   🏠 Main Dashboard:   http://192.168.64.13:3000/dashboard"
}

# Handle Ctrl+C gracefully
trap 'echo ""; echo "⏹️  Data stream stopped by user"; exit 0' INT

# Run the data generator
main
