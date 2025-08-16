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


# Development Deployment Script
# Tests changes locally, then prepares for production

set -e

VM_IP="192.168.64.13"
VM_USER="kevin"
VM_PASS="V!g1l@nt"

echo "🧪 Development Deployment Pipeline with ML Model Initialization..."

# Function to initialize ML models in AI service container
initialize_ml_models() {
    echo "🤖 Initializing ML models in AI service..."
    
    # Wait for AI service container to be ready
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if sshpass -p "$VM_PASS" ssh -o StrictHostKeyChecking=no "$VM_USER@$VM_IP" \
            "docker exec ssai_ai_service echo 'ready' 2>/dev/null" | grep -q "ready"; then
            echo "✅ AI service container is ready"
            break
        fi
        
        echo "⏳ Waiting for AI service container... ($attempt/$max_attempts)"
        sleep 2
        ((attempt++))
    done
    
    # Check if models exist
    MODEL_COUNT=$(sshpass -p "$VM_PASS" ssh -o StrictHostKeyChecking=no "$VM_USER@$VM_IP" \
        "docker exec ssai_ai_service ls /app/models/*.joblib 2>/dev/null | wc -l || echo 0")
    
    if [ "$MODEL_COUNT" -lt "5" ]; then
        echo "📊 Creating ML models in container..."
        sshpass -p "$VM_PASS" ssh -o StrictHostKeyChecking=no "$VM_USER@$VM_IP" \
            "docker exec ssai_ai_service python3 -c \"
import joblib
import numpy as np
from sklearn.linear_model import SGDClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
import os

print('🔄 Initializing ML models...')
os.makedirs('/app/models', exist_ok=True)

# Generate sample data
np.random.seed(42)
X = np.random.random((1000, 10))
y = np.random.randint(0, 4, 1000)

# Train models
model = SGDClassifier(random_state=42, loss='log_loss')
model.fit(X, y)

preprocessor = StandardScaler()
preprocessor.fit(X)

isolation_forest = IsolationForest(random_state=42, contamination=0.1)
isolation_forest.fit(X)

column_names = ['technique_id', 'asset_type', 'login_hour', 'is_admin', 'is_remote_session', 'cvss_score', 'criticality_score', 'ioc_risk_score', 'login_duration', 'packet_count']
baseline_shap = np.mean(X, axis=0)

# Save models
joblib.dump(model, '/app/models/model.joblib')
joblib.dump(preprocessor, '/app/models/preprocessor.joblib')
joblib.dump(X, '/app/models/X_train.joblib')
joblib.dump(column_names, '/app/models/column_names.joblib')
joblib.dump(baseline_shap, '/app/models/baseline_shap.joblib')
joblib.dump(isolation_forest, '/app/models/isolation_forest.joblib')

print('✅ ML models initialized successfully!')
\""
        echo "✅ ML models created in container"
    else
        echo "✅ ML models already exist in container ($MODEL_COUNT models found)"
    fi
}

# Step 1: Sync to VM
echo "1️⃣  Syncing to VM..."
./sync-dev-to-vm.sh

# Step 2: Test on VM
echo "2️⃣  Starting containers on VM..."
sshpass -p "$VM_PASS" ssh "$VM_USER@$VM_IP" "cd /mnt/shared/ssai-project && docker compose -f docker-compose.vm.yml up --build -d"

# Step 2.5: Initialize ML models in AI service
echo "2️⃣.5 Initializing ML models..."
initialize_ml_models

# Step 3: Restart backend to ensure connector system loads properly
echo "3️⃣  Restarting backend to load connector system..."
sshpass -p "$VM_PASS" ssh "$VM_USER@$VM_IP" "cd /mnt/shared/ssai-project && docker compose -f docker-compose.vm.yml restart backend"

# Step 4: Restart frontend to clear React cache
echo "4️⃣  Restarting frontend to clear React cache..."
sshpass -p "$VM_PASS" ssh "$VM_USER@$VM_IP" "cd /mnt/shared/ssai-project && docker compose -f docker-compose.vm.yml restart frontend"

# Step 5: Wait for services to be ready
echo "5️⃣  Waiting for services to be ready..."
sleep 30

echo "✅ Development deployment complete!"
echo "🌐 Frontend: http://192.168.64.13:3000"
echo "🔧 Backend: http://192.168.64.13:8000"
echo ""
echo "📋 Next steps:"
echo "   1. Test your changes on VM"
echo "   2. If everything works, run: ./promote-to-prod.sh"
