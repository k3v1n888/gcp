#!/bin/bash

# Development Deployment Script
# Tests changes locally, then prepares for production

set -e

VM_IP="192.168.64.13"
VM_USER="kevin"
VM_PASS="V!g1l@nt"

echo "🧪 Development Deployment Pipeline..."

# Step 1: Sync to VM
echo "1️⃣  Syncing to VM..."
./sync-dev-to-vm.sh

# Step 2: Test on VM (optional automated tests)
echo "2️⃣  Testing on VM..."
sshpass -p "$VM_PASS" ssh "$VM_USER@$VM_IP" "cd /mnt/shared/ssai-project && docker compose -f docker-compose.vm.yml up --build -d"

# Step 3: Restart frontend to clear React cache and ensure hot reload
echo "3️⃣  Restarting frontend to clear React cache..."
sshpass -p "$VM_PASS" ssh "$VM_USER@$VM_IP" "cd /mnt/shared/ssai-project && docker compose -f docker-compose.vm.yml restart frontend"

# Step 4: Wait for frontend to recompile
echo "4️⃣  Waiting for frontend to recompile..."
sleep 25

echo "✅ Development deployment complete!"
echo "🌐 Frontend: http://192.168.64.13:3000"
echo "🔧 Backend: http://192.168.64.13:8000"
echo ""
echo "📋 Next steps:"
echo "   1. Test your changes on VM"
echo "   2. If everything works, run: ./promote-to-prod.sh"
