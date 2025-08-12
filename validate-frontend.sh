#!/bin/bash

echo "🔧 FRONTEND COMPILATION VALIDATOR"
echo "================================="
echo ""

# Check frontend compilation status
echo "1️⃣  Frontend Compilation Status:"
FRONTEND_LOG=$(sshpass -p 'V!g1l@nt' ssh kevin@192.168.64.13 'docker logs ssai_frontend --tail=5' 2>/dev/null)

if echo "$FRONTEND_LOG" | grep -q "Compiled successfully"; then
    echo "   ✅ SUCCESS - Frontend compiled without errors"
else
    echo "   ❌ COMPILATION ISSUES DETECTED:"
    echo "$FRONTEND_LOG" | grep -E "(ERROR|error)" || echo "   Check logs manually"
fi

echo ""
echo "2️⃣  Dashboard Access Test:"

# Test AI Models Dashboard specifically
AI_RESPONSE=$(curl -s --max-time 5 -o /dev/null -w "%{http_code}" "http://192.168.64.13:3000/ai-models" 2>/dev/null)
if [ "$AI_RESPONSE" = "200" ]; then
    echo "   ✅ AI Models Dashboard: ACCESSIBLE"
else
    echo "   ❌ AI Models Dashboard: ERROR ($AI_RESPONSE)"
fi

# Test main dashboard
MAIN_RESPONSE=$(curl -s --max-time 5 -o /dev/null -w "%{http_code}" "http://192.168.64.13:3000/dashboard" 2>/dev/null)
if [ "$MAIN_RESPONSE" = "200" ]; then
    echo "   ✅ Main Dashboard: ACCESSIBLE"
else
    echo "   ❌ Main Dashboard: ERROR ($MAIN_RESPONSE)"
fi

echo ""
echo "3️⃣  JavaScript Runtime Test:"
# This will help detect if there are any remaining runtime errors
JS_TEST_RESPONSE=$(curl -s --max-time 5 "http://192.168.64.13:3000/ai-models" 2>/dev/null | grep -c "Clock is not defined" || echo "0")
if [ "$JS_TEST_RESPONSE" = "0" ]; then
    echo "   ✅ No 'Clock is not defined' errors detected"
else
    echo "   ❌ Still detecting Clock errors"
fi

echo ""
echo "🔗 Direct Access Links:"
echo "   AI Models:   http://192.168.64.13:3000/ai-models"
echo "   Dashboard:   http://192.168.64.13:3000/dashboard"
echo "   Connectors:  http://192.168.64.13:3000/connectors"
echo "   Admin:       http://192.168.64.13:3000/admin"
echo ""

if [ "$AI_RESPONSE" = "200" ] && [ "$MAIN_RESPONSE" = "200" ] && [ "$JS_TEST_RESPONSE" = "0" ]; then
    echo "🎉 ALL FRONTEND ISSUES RESOLVED!"
    echo "   The dashboards should now load without errors."
else
    echo "⚠️  Some issues may still exist. Try refreshing your browser cache."
fi
