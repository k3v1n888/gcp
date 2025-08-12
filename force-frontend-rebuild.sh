#!/bin/bash

echo "🔄 FORCE FRONTEND REBUILD"
echo "========================="

echo "1️⃣ Syncing latest code to VM..."
./sync-dev-to-vm.sh

echo ""
echo "2️⃣ Force rebuilding frontend container..."

# Use heredoc to send commands to VM
cat << 'COMMANDS' | sshpass -p 'V!g1l@nt' ssh -o StrictHostKeyChecking=no -T dev@192.168.64.13
cd /home/dev/gcp

echo "Stopping frontend container..."
docker-compose -f docker-compose.vm.yml stop frontend

echo "Removing old frontend container and image..."
docker-compose -f docker-compose.vm.yml rm -f frontend
docker rmi gcp_frontend 2>/dev/null || echo "Image already removed"

echo "Rebuilding frontend with no cache..."
docker-compose -f docker-compose.vm.yml build --no-cache frontend

echo "Starting frontend container..."
docker-compose -f docker-compose.vm.yml up -d frontend

echo "Waiting for container to start..."
sleep 10

echo "Frontend container status:"
docker-compose -f docker-compose.vm.yml ps frontend

echo "Frontend logs (last 10 lines):"
docker-compose -f docker-compose.vm.yml logs --tail 10 frontend
COMMANDS

echo ""
echo "3️⃣ Testing rebuilt frontend..."
sleep 5

HTTP_CODE=$(curl -s -w "%{http_code}" "http://192.168.64.13:3000/ai-models" -o /tmp/force_rebuild_test.html)
echo "HTTP Status: $HTTP_CODE"

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Frontend is responding"
    
    if grep -qi "zap" /tmp/force_rebuild_test.html; then
        echo "❌ Still contains Zap references - check VM code sync"
        echo "Zap occurrences:"
        grep -i "zap" /tmp/force_rebuild_test.html | head -2
    else
        echo "✅ No Zap references found!"
        echo ""
        echo "🎯 SUCCESS! The container has been rebuilt with the fixed code."
        echo "📱 Dashboard: http://192.168.64.13:3000/ai-models"
        echo "🔄 Do a hard refresh in your browser (Ctrl+F5 / Cmd+Shift+R)"
        echo ""
        echo "If you still see errors, try incognito/private mode to bypass all cache."
    fi
else
    echo "❌ Frontend not responding after rebuild"
fi
