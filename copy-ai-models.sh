#!/bin/bash

# Copy AI models from Mac to VM
# Run this on your Mac to sync the AI models to the VM

echo "📁 Copying AI models to VM..."

# Create the directory structure on VM
ssh kevin@192.168.64.13 "mkdir -p /mnt/shared/ssai-project/ai-service/models"

# Copy the AI model files
scp -r ~/Downloads/"ai model 2"/* kevin@192.168.64.13:/mnt/shared/ssai-project/ai-service/models/

echo "✅ AI models copied to VM"
echo "🔄 Next steps:"
echo "1. SSH to VM: ssh kevin@192.168.64.13"
echo "2. Run the local AI service setup: cd /mnt/shared/ssai-project && ./setup-local-ai.sh"
