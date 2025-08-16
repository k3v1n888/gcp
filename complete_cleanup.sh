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


echo "🧹 Starting comprehensive cleanup..."

# 1. Replace "AI" with "Sentient AI" (but avoid double replacements)
echo "📝 Replacing AI with Sentient AI..."
find . -type f \( -name "*.py" -o -name "*.js" -o -name "*.jsx" -o -name "*.ts" -o -name "*.tsx" -o -name "*.json" -o -name "*.md" -o -name "*.txt" -o -name "*.yml" -o -name "*.yaml" -o -name "*.sh" \) \
  -not -path "./node_modules/*" \
  -not -path "./.git/*" \
  -not -path "./venv/*" \
  -not -path "./.venv/*" \
  -not -path "./__pycache__/*" \
  -exec sed -i '' 's/\bAI\b/Sentient AI/g' {} \;

# Fix any double replacements that might have occurred
find . -type f \( -name "*.py" -o -name "*.js" -o -name "*.jsx" -o -name "*.ts" -o -name "*.tsx" -o -name "*.json" -o -name "*.md" -o -name "*.txt" -o -name "*.yml" -o -name "*.yaml" -o -name "*.sh" \) \
  -not -path "./node_modules/*" \
  -not -path "./.git/*" \
  -not -path "./venv/*" \
  -not -path "./.venv/*" \
  -not -path "./__pycache__/*" \
  -exec sed -i '' 's/Sentient AI/Sentient AI/g' {} \;

# 2. Replace any remaining "Sentient" with "Sentient"
echo "🔄 Replacing remaining Sentient with Sentient..."
find . -type f \( -name "*.py" -o -name "*.js" -o -name "*.jsx" -o -name "*.ts" -o -name "*.tsx" -o -name "*.json" -o -name "*.md" -o -name "*.txt" -o -name "*.yml" -o -name "*.yaml" -o -name "*.sh" \) \
  -not -path "./node_modules/*" \
  -not -path "./.git/*" \
  -not -path "./venv/*" \
  -not -path "./.venv/*" \
  -not -path "./__pycache__/*" \
  -exec sed -i '' 's/Sentient/Sentient/g' {} \;

echo "✅ Text replacements complete!"
