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


# Start only the local AI service
# Useful for testing the AI service independently

cd /mnt/shared/ssai-project/ai-service

echo "🤖 Starting local AI service..."
echo "🔧 Available at: http://192.168.64.13:8001"
echo "📚 API docs: http://192.168.64.13:8001/debug"

# Activate AI service virtual environment
source venv/bin/activate
:
# Start the Flask AI service
python main.py
