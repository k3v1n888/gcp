#!/bin/bash

# Development Environment Validation Script
echo "🔧 Validating Development Environment Setup..."

# Check if we're on dev branch
current_branch=$(git branch --show-current)
echo "Branch: $current_branch"

if [ "$current_branch" != "dev" ]; then
    echo "❌ Not on dev branch"
    exit 1
fi

# Check if services are running
echo "Checking Docker services..."
if command -v ssh >/dev/null 2>&1; then
    ssh kevin@192.168.64.13 "docker ps --format 'table {{.Names}}\t{{.Status}}' | grep ssai"
else
    echo "SSH not available, skipping service check"
fi

# Test dev endpoints
echo "Testing development endpoints..."
curl -s http://192.168.64.13:8000/api/auth/dev-login || echo "Backend not accessible"

echo "✅ Development validation complete"
