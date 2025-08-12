#!/bin/bash

echo "💪 MANUAL CONTAINER REBUILD"
echo "=========================="

echo "1️⃣ Syncing latest changes..."
./sync-dev-to-vm.sh

echo ""
echo "2️⃣ Manual container rebuild..."
cat << 'EOL' | sshpass -p 'V!g1l@nt' ssh -o StrictHostKeyChecking=no -T dev@192.168.64.13
cd /home/dev/gcp
echo "Stopping frontend container..."
docker-compose -f docker-compose.vm.yml stop frontend
echo "Removing frontend container..."
docker-compose -f docker-compose.vm.yml rm -f frontend
echo "Rebuilding frontend container..."
docker-compose -f docker-compose.vm.yml build frontend
echo "Starting frontend container..."
docker-compose -f docker-compose.vm.yml up -d frontend
echo "Waiting for startup..."
sleep 10
echo "Container status:"
docker-compose -f docker-compose.vm.yml ps frontend
EOL

echo ""
echo "3️⃣ Testing after rebuild..."
sleep 5
curl -s -w "HTTP Status: %{http_code}\n" "http://192.168.64.13:3000/ai-models" -o /tmp/test_after_rebuild.html

echo ""
echo "4️⃣ Checking for errors in rebuilt version..."
if grep -qi "zap" /tmp/test_after_rebuild.html; then
    echo "   ❌ Still finding Zap references"
    grep -i "zap" /tmp/test_after_rebuild.html | head -2
else
    echo "   ✅ No Zap references found - rebuild successful!"
fi
