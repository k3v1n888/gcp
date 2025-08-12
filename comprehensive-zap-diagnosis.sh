#!/bin/bash

echo "🔍 COMPREHENSIVE ZAP ERROR DIAGNOSIS"
echo "===================================="

echo "1️⃣ Checking LOCAL AIModelDashboard.jsx for Zap references..."
echo "Local file status:"
if grep -n "Zap" frontend/src/components/AIModelDashboard.jsx; then
    echo "   ❌ Found Zap references in LOCAL file:"
    grep -n "Zap" frontend/src/components/AIModelDashboard.jsx
else
    echo "   ✅ No Zap references in LOCAL file"
fi

echo ""
echo "2️⃣ Checking LOCAL imports..."
echo "BoltIcon import status:"
if grep -n "BoltIcon" frontend/src/components/AIModelDashboard.jsx; then
    echo "   ✅ BoltIcon properly imported"
else
    echo "   ❌ BoltIcon not found in imports"
fi

echo ""
echo "3️⃣ Checking for ALL icon usage patterns..."
echo "Icon usage summary:"
grep -n "Icon className" frontend/src/components/AIModelDashboard.jsx | head -10

echo ""
echo "4️⃣ VM accessibility test..."
curl -s -w "VM Status: %{http_code}\n" "http://192.168.64.13:3000" -o /dev/null

echo ""
echo "5️⃣ Direct browser cache bypass test..."
echo "Testing with cache-busting timestamp..."
TIMESTAMP=$(date +%s)
curl -s -H "Cache-Control: no-cache" -H "Pragma: no-cache" "http://192.168.64.13:3000/ai-models?t=$TIMESTAMP" -o /tmp/cache_bypass_test.html
if grep -qi "zap" /tmp/cache_bypass_test.html; then
    echo "   ❌ Still finding Zap in VM response (cache or deployment issue)"
    echo "   First few Zap occurrences:"
    grep -i "zap" /tmp/cache_bypass_test.html | head -2
else
    echo "   ✅ No Zap found in VM response"
fi

echo ""
echo "🎯 RECOMMENDATION:"
if ! grep -q "Zap" frontend/src/components/AIModelDashboard.jsx; then
    echo "✅ Local code is fixed - this is a deployment/cache issue"
    echo "🔄 Solution: Force browser hard refresh (Ctrl+F5 / Cmd+Shift+R)"
    echo "🕵️  Alternative: Try incognito/private browsing mode"
    echo "📱 VM rebuild may be needed if issue persists"
else
    echo "❌ Local code still has Zap references - needs fixing"
fi
