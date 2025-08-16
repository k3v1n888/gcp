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
