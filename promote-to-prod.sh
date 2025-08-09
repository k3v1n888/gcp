#!/bin/bash

# Production Promotion Script
# Merges tested dev changes to main branch for GCP deployment

set -e

echo "🚀 Promoting Development to Production..."

# Check if we're on dev branch
current_branch=$(git branch --show-current)
if [ "$current_branch" != "dev" ]; then
    echo "❌ Must be on dev branch to promote to production"
    exit 1
fi

# Check for uncommitted changes
if ! git diff-index --quiet HEAD --; then
    echo "❌ Please commit all changes before promoting to production"
    exit 1
fi

# Step 1: Update dev branch
echo "1️⃣  Updating dev branch..."
git add .
git commit -m "dev: latest development changes" || echo "No changes to commit"

# Step 2: Switch to main and merge
echo "2️⃣  Switching to main branch..."
git checkout main

echo "3️⃣  Merging dev changes to main..."
git merge dev --no-ff -m "feat: promote tested changes from dev to production"

# Step 3: Clean up production files (remove dev-specific files)
echo "4️⃣  Cleaning up production files..."
rm -f docker-compose.vm.yml vm-*.sh *vm*.sh setup-*.sh dev-*.sh .env.dev .env.vm 2>/dev/null || true

echo "5️⃣  Committing clean production state..."
git add .
git commit -m "chore: clean production files for GCP deployment" || echo "No cleanup needed"

echo "✅ Production promotion complete!"
echo "📤 Ready to push to GCP:"
echo "   git push origin main"
echo ""
echo "🔄 To continue development:"
echo "   git checkout dev"
