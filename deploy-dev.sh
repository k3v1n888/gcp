#!/bin/bash

# Development Deployment Script
# Tests changes locally, then prepares for production

set -e

echo "🧪 Development Deployment Pipeline..."

# Step 1: Sync to VM
echo "1️⃣  Syncing to VM..."
./sync-dev-to-vm.sh

# Step 2: Test on VM (optional automated tests)
echo "2️⃣  Testing on VM..."
ssh kevin@192.168.64.13 "cd /mnt/shared/ssai-project && docker compose -f docker-compose.vm.yml up --build -d"

echo "✅ Development deployment complete!"
echo "🌐 Frontend: http://192.168.64.13:3000"
echo "🔧 Backend: http://192.168.64.13:8000"
echo ""
echo "📋 Next steps:"
echo "   1. Test your changes on VM"
echo "   2. If everything works, run: ./promote-to-prod.sh"
