#!/bin/bash

echo "🔍 CHECKING FOR ICON ERRORS"
echo "=========================="

echo "1️⃣ Checking for undefined icon patterns in AIModelDashboard.jsx..."
echo "❌ Components that might be missing Icon suffix:"
grep -n "<[A-Z][a-z]\+ " frontend/src/components/AIModelDashboard.jsx | grep -v "Icon\|Card\|Badge\|Button\|Progress\|div\|span\|h1\|h2\|p\|main" || echo "   ✅ No obvious icon issues found"

echo ""
echo "2️⃣ Testing dashboard accessibility..."
curl -s -w "HTTP Status: %{http_code}\n" "http://192.168.64.13:3000/ai-models" -o /dev/null

echo ""
echo "3️⃣ Checking frontend container status..."
sshpass -p 'V!g1l@nt' ssh -o StrictHostKeyChecking=no dev@192.168.64.13 "cd /home/dev/gcp && docker-compose -f docker-compose.vm.yml ps frontend"
