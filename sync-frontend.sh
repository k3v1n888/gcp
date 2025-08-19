#!/bin/bash

# Quick Frontend Update Script
# Syncs frontend changes and restarts React dev server

set -e

echo "🔄 Quick Frontend Update..."

# Sync with frontend restart
RESTART_FRONTEND=1 ./sync-dev-to-vm.sh

echo "✅ Frontend updated and restarted!"
echo "🌐 Access your app: http://192.168.64.13:3000"
