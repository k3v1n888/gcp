#!/bin/bash
# Copyright (c) 2025 Kevin Zachary
# All rights reserved.
#
# This software and associated documentation files (the "Software") are the 
# exclusive property of Kevin Zachary. Unauthorized copying, distribution, 
# modification, or use of this software is strictly prohibited.
#
# For licensing inquiries, contact: kevin@zachary.com

#!/bin/bash
# Author: Kevin Zachary
# Copyright: Sentient Spire


# Quick Frontend Update Script
# Syncs frontend changes and restarts React dev server

set -e

echo "🔄 Quick Frontend Update..."

# Sync with frontend restart
RESTART_FRONTEND=1 ./sync-dev-to-vm.sh

echo "✅ Frontend updated and restarted!"
echo "🌐 Access your app: http://192.168.64.13:3000"
