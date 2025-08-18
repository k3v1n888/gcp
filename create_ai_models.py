#!/usr/bin/env python3
"""
Quick model generation script for AI service initialization
Creates basic model artifacts to resolve startup errors
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import IsolationForest
import joblib
import os
import shap

def create_basic_models():
    """Create basic model artifacts for AI service"""
    
    # Create models directory
    os.makedirs("ai-service/models", exist_ok=True)
    
    print("🚀 Creating basic model artifacts...")
    
    # Generate synthetic training data
    np.random.seed(42)
    n_samples = 1000
    n_features = 10
    
    # Feature names for cyber security context
    feature_names = [
        'network_anomaly_score', 'port_scan_count', 'malware_indicators',
        'authentication_failures', 'data_exfiltration_risk', 'vulnerability_score',
        'traffic_volume_anomaly', 'privilege_escalation_attempts', 'lateral_movement_risk',
        'threat_intelligence_score'
    ]
    
    # Generate synthetic features
    X = np.random.randn(n_samples, n_features)
    
    # Generate synthetic labels (binary classification for threat detection)
    y = np.random.binomial(1, 0.3, n_samples)  # 30% threats
    
    # Create DataFrame
    X_df = pd.DataFrame(X, columns=feature_names)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X_df, y, test_size=0.2, random_state=42)
    
    print("📊 Training RandomForest classifier...")
    
    # Create and train the main model
    model = RandomForestClassifier(n_estimators=50, random_state=42)
    model.fit(X_train, y_train)
    
    print("🔧 Creating preprocessor...")
    
    # Create preprocessor
    preprocessor = StandardScaler()
    preprocessor.fit(X_train)
    
    print("🔍 Creating anomaly detector...")
    
    # Create isolation forest for anomaly detection
    isolation_forest = IsolationForest(contamination=0.1, random_state=42)
    isolation_forest.fit(X_train)
    
    print("🧠 Creating SHAP explainer...")
    
    # Create SHAP baseline (use mean of training data)
    baseline_shap = X_train.mean().values
    
    # Create SHAP explainer
    explainer = shap.TreeExplainer(model)
    
    print("💾 Saving model artifacts...")
    
    # Save all artifacts with the expected names
    model_files = {
        "new-model-ssai01_models_model.joblib": model,
        "new-model-ssai01_models_preprocessor.joblib": preprocessor,
        "new-model-ssai01_models_X_train.joblib": X_train.values,
        "new-model-ssai01_models_column_names.joblib": feature_names,
        "new-model-ssai01_models_baseline_shap.joblib": baseline_shap,
        "new-model-ssai01_models_isolation_forest.joblib": isolation_forest
    }
    
    for filename, artifact in model_files.items():
        filepath = f"ai-service/models/{filename}"
        joblib.dump(artifact, filepath)
        print(f"✅ Saved {filename}")
    
    print("🎉 Model artifacts created successfully!")
    print(f"📈 Model accuracy on test set: {model.score(X_test, y_test):.3f}")
    print(f"📂 Files saved in ai-service/models/")
    
    return True

if __name__ == "__main__":
    try:
        create_basic_models()
        print("✨ AI service models are now ready!")
    except Exception as e:
        print(f"❌ Error creating models: {e}")
        import traceback
        traceback.print_exc()
