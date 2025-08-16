#!/bin/bash
# Copyright (c) 2025 Kevin Zachary
# All rights reserved.
#
# This software and associated documentation files (the "Software") are the 
# exclusive property of Kevin Zachary. Unauthorized copying, distribution, 
# modification, or use of this software is strictly prohibited.
#
# For licensing inquiries, contact: kevin@zachary.com


# Copyright: Sentient Spire
# Author: Kevin Zachary
# Comprehensive cleanup and rebranding script

echo "🔄 Starting comprehensive cleanup and rebranding..."

# Step 1: Replace "Sentient" with "Sentient" in all files
echo "📝 Replacing 'Sentient' with 'Sentient' throughout codebase..."

# Find and replace in all text files
find . -type f \( -name "*.py" -o -name "*.js" -o -name "*.jsx" -o -name "*.ts" -o -name "*.tsx" -o -name "*.md" -o -name "*.yml" -o -name "*.yaml" -o -name "*.json" -o -name "*.sh" -o -name "*.env*" \) -not -path "./.git/*" -not -path "./node_modules/*" -not -path "./.venv/*" -exec sed -i '' 's/Sentient/Sentient/g' {} \;

echo "✅ Sentient -> Sentient replacement completed"

# Step 2: Clean up Docker containers and images
echo "🧹 Cleaning up Docker containers and images..."
docker container prune -f
docker image prune -f
docker volume prune -f
docker network prune -f

echo "✅ Docker cleanup completed"
