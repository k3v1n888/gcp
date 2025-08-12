#!/bin/bash

echo "⚡ INSTANT SYSTEM STATUS CHECK"
echo "=============================="

# Quick ping tests (1 second timeout each)
echo -n "Backend (8000): "
nc -z -w1 192.168.64.13 8000 && echo "✅ UP" || echo "❌ DOWN"

echo -n "Frontend (3000): "
nc -z -w1 192.168.64.13 3000 && echo "✅ UP" || echo "❌ DOWN"

echo -n "AI Service (8001): "
nc -z -w1 192.168.64.13 8001 && echo "✅ UP" || echo "❌ DOWN"

echo ""
echo "📊 Quick Data Check:"

# Ultra-fast database check
echo -n "Database accessible: "
curl -s --max-time 2 "http://192.168.64.13:8000/api/health" > /dev/null && echo "✅ YES" || echo "❌ NO"

echo ""
echo "🚀 Ready to test! Try:"
echo "   ./fast-test.sh           # Quick comprehensive test"  
echo "   ./generate-real-data.sh  # Generate test data"
echo "   ./comprehensive-test.sh  # Full system test"
