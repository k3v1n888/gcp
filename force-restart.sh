#!/bin/bash

echo "🔄 FORCING FRONTEND RESTART"
echo "=========================="

# Try multiple SSH approaches
echo "1️⃣ Attempting SSH connection..."

# Method 1: Direct SSH with password
expect << 'EOF'
set timeout 10
spawn ssh dev@192.168.64.13 "cd /home/dev/gcp && docker-compose -f docker-compose.vm.yml down frontend && docker-compose -f docker-compose.vm.yml up -d frontend"
expect "password:"
send "V!g1l@nt\r"
expect eof
EOF

echo ""
echo "2️⃣ Waiting for container startup..."
sleep 5

echo ""
echo "3️⃣ Testing accessibility..."
curl -s -w "HTTP Status: %{http_code}\n" "http://192.168.64.13:3000/ai-models" -o /dev/null

echo ""
echo "4️⃣ Checking for Zap errors in new bundle..."
curl -s "http://192.168.64.13:3000/ai-models" | grep -i "zap" | head -2 || echo "   ✅ No Zap references found in HTML"
