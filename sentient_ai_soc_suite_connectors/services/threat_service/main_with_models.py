"""
Copyright (c) 2025 Kevin Zachary
All rights reserved.

This software and associated documentation files (the "Software") are the 
exclusive property of Kevin Zachary. Unauthorized copying, distribution, 
modification, or use of this software is strictly prohibited.

For licensing inquiries, contact: kevin@zachary.com
"""

# Author: Kevin Zachary
# Copyright: Sentient Spire

# ai-service/main.py - Local AI Prediction Service for Development

from flask import Flask, request, jsonify
import os
import pandas as pd
import numpy as np
from datetime import datetime
import joblib
import shap
from sklearn.linear_model import SGDClassifier
from sklearn.ensemble import IsolationForest
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables for model artifacts
model = None
preprocessor = None
X_train = None
column_names = None
baseline_shap = None
iso = None
explainer = None

def calculate_severity(cvss, criticality, ioc_risk):
    """Calculate threat severity based on scores"""
    score = (cvss / 10.0 + criticality + ioc_risk) / 3
    if score > 0.85:
        return "critical"
    elif score > 0.6:
        return "high"
    elif score > 0.3:
        return "medium"
    else:
        return "low"

def load_artifacts_local():
    """Load model artifacts from local files with version compatibility"""
    global model, preprocessor, X_train, column_names, baseline_shap, iso, explainer
    
    model_dir = "models"
    files = {
        "model": "new-model-ssai01_models_model.joblib",
        "preprocessor": "new-model-ssai01_models_preprocessor.joblib", 
        "X_train": "new-model-ssai01_models_X_train.joblib",
        "column_names": "new-model-ssai01_models_column_names.joblib",
        "baseline_shap": "new-model-ssai01_models_baseline_shap.joblib",
        "isolation_forest": "new-model-ssai01_models_isolation_forest.joblib"
    }
    
    logger.info("🚀 Loading model artifacts...")
    
    artifacts = {}
    loaded_count = 0
    
    for key, filename in files.items():
        filepath = os.path.join(model_dir, filename)
        if os.path.exists(filepath):
            try:
                # Try loading with joblib
                artifacts[key] = joblib.load(filepath)
                logger.info(f"✅ Loaded {key} from {filename}")
                loaded_count += 1
            except Exception as e:
                logger.error(f"❌ Error loading {key}: {e}")
                # Create fallback for critical components
                if key == "model":
                    logger.info(f"🔄 Creating fallback model for {key}")
                    from sklearn.ensemble import RandomForestClassifier
                    artifacts[key] = RandomForestClassifier(n_estimators=10, random_state=42)
                elif key == "preprocessor":
                    logger.info(f"🔄 Creating fallback preprocessor for {key}")
                    from sklearn.preprocessing import StandardScaler
                    artifacts[key] = StandardScaler()
                elif key == "column_names":
                    artifacts[key] = [
                        'technique_id', 'asset_type', 'login_hour', 'is_admin', 
                        'is_remote_session', 'cvss_score', 'criticality_score', 
                        'ioc_risk_score', 'login_duration', 'packet_count'
                    ]
                else:
                    artifacts[key] = None
        else:
            logger.warning(f"⚠️ Missing {filepath}")
            # Create fallbacks for missing files
            if key == "model":
                logger.info(f"🔄 Creating fallback model for missing {key}")
                from sklearn.ensemble import RandomForestClassifier
                artifacts[key] = RandomForestClassifier(n_estimators=10, random_state=42)
            elif key == "preprocessor":
                from sklearn.preprocessing import StandardScaler
                artifacts[key] = StandardScaler()
            elif key == "column_names":
                artifacts[key] = [
                    'technique_id', 'asset_type', 'login_hour', 'is_admin', 
                    'is_remote_session', 'cvss_score', 'criticality_score', 
                    'ioc_risk_score', 'login_duration', 'packet_count'
                ]
            else:
                artifacts[key] = None
    
    # Train fallback models if needed
    if loaded_count == 0:
        logger.info("🔄 No models loaded successfully, creating and training fallback models...")
        
        # Create synthetic training data
        import numpy as np
        X_dummy = np.random.random((1000, 10))
        y_dummy = np.random.randint(0, 4, 1000)  # 4 severity levels
        
        # Train fallback preprocessor
        if artifacts.get("preprocessor"):
            artifacts["preprocessor"].fit(X_dummy)
        
        # Train fallback model
        if artifacts.get("model"):
            X_scaled = artifacts["preprocessor"].transform(X_dummy)
            artifacts["model"].fit(X_scaled, y_dummy)
            logger.info("✅ Fallback model fitted successfully")
        
        # Create dummy X_train for SHAP if missing
        if not artifacts.get("X_train"):
            artifacts["X_train"] = X_scaled[:100]  # Use first 100 samples for SHAP
            logger.info("✅ Created X_train for SHAP explainer")
        
        logger.info("✅ Fallback models trained and ready")
    elif loaded_count < len(files):
        logger.info(f"⚠️ Partial load: {loaded_count}/{len(files)} models loaded, using fallbacks for missing")
    else:
        logger.info(f"🎉 All {loaded_count} models loaded successfully!")
    
    return artifacts
    
    artifacts = {}
    for key, filename in files.items():
        filepath = os.path.join(model_dir, filename)
        if os.path.exists(filepath):
            artifacts[key] = joblib.load(filepath)
            logger.info(f"✅ Loaded {key} from {filepath}")
        else:
            logger.warning(f"⚠️ Missing {filepath}, using fallback")
            # Create fallback artifacts if files don't exist
            if key == "model":
                artifacts[key] = SGDClassifier()
            elif key == "column_names":
                artifacts[key] = ["technique_id", "asset_type", "login_hour", "is_admin", "is_remote_session"]
            else:
                artifacts[key] = None
    
    # Assign to global variables
    model = artifacts["model"]
    preprocessor = artifacts["preprocessor"]
    X_train = artifacts["X_train"]
    column_names = artifacts["column_names"]
    baseline_shap = artifacts["baseline_shap"]
    iso = artifacts["isolation_forest"]
    
    # Create explainer if we have the necessary components
    if X_train is not None and model is not None:
        try:
            # Check if model is fitted by testing if it has the required attributes
            if hasattr(model, 'estimators_') or hasattr(model, 'coef_') or hasattr(model, 'classes_'):
                X_train_sample = shap.sample(X_train, min(100, X_train.shape[0]))
                explainer = shap.KernelExplainer(model.predict_proba, X_train_sample)
                logger.info("✅ SHAP explainer created")
            else:
                logger.warning("⚠️ Model not fitted, cannot create SHAP explainer")
                explainer = None
        except Exception as e:
            logger.warning(f"⚠️ Could not create SHAP explainer: {e}")
            explainer = None
    
    return model, preprocessor, X_train, column_names, baseline_shap, iso, explainer

def predict_fn(df, model, preprocessor, column_names, anomaly_filter=None):
    """Make predictions on the input dataframe"""
    logger.info(f"🔧 predict_fn called with columns: {column_names}")
    logger.info(f"🔧 DataFrame columns: {list(df.columns)}")
    
    # The preprocessor was trained with timestamp, so we need to add it as a dummy column
    if 'timestamp' not in df.columns:
        df = df.copy()
        df['timestamp'] = '2025-01-01T00:00:00Z'
        logger.info("🔧 Added dummy timestamp column")
    
    # Now include timestamp in the columns for preprocessing
    all_expected_columns = column_names + ['timestamp'] if 'timestamp' not in column_names else column_names
    logger.info(f"🔧 All expected columns (including timestamp): {all_expected_columns}")
    
    # Ensure all expected columns exist in DataFrame
    for col in all_expected_columns:
        if col not in df.columns:
            if col == 'timestamp':
                df[col] = '2025-01-01T00:00:00Z'
            else:
                df[col] = 0
            logger.info(f"🔧 Added missing column '{col}'")
    
    logger.info(f"🔧 Final DataFrame columns: {list(df.columns)}")
    logger.info(f"🔧 DataFrame shape before transform: {df[all_expected_columns].shape}")
    
    # Create a clean DataFrame with proper data types
    df_clean = pd.DataFrame()
    
    for col in all_expected_columns:
        if col == 'timestamp':
            df_clean[col] = df[col].astype(str).fillna('2025-01-01T00:00:00Z')
        elif col in ['technique_id', 'asset_type']:
            df_clean[col] = df[col].astype(str).fillna('unknown')
        elif col in ['is_admin', 'is_remote_session', 'location_mismatch']:
            df_clean[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        else:
            df_clean[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(float)
        
        logger.info(f"🔧 Column '{col}': dtype={df_clean[col].dtype}, sample={df_clean[col].iloc[0]}")
    
    try:
        if preprocessor is not None:
            X = preprocessor.transform(df_clean)
            logger.info(f"🔧 Transform successful! Shape: {X.shape}")
        else:
            # Fallback: use the dataframe as-is for numeric columns
            numeric_cols = [col for col in df_clean.columns if col != 'timestamp']
            X = df_clean[numeric_cols].values
            logger.info(f"🔧 Using fallback transform! Shape: {X.shape}")
    except Exception as e:
        logger.error(f"❌ Transform failed: {e}")
        # Use a simple fallback
        X = np.array([[0] * 10])  # Default feature vector
    
    anomaly_score = anomaly_filter.decision_function(X)[0] if anomaly_filter else 0
    
    if model is not None:
        prediction = model.predict(X)[0]
        proba = model.predict_proba(X)[0].tolist()
    else:
        # Fallback prediction
        prediction = 1  # Default to "medium" threat
        proba = [0.2, 0.4, 0.3, 0.1]  # Default probabilities
    
    # Safely get these values with defaults
    cvss = float(df["cvss_score"].values[0]) if "cvss_score" in df.columns else 5.0
    crit = float(df["criticality_score"].values[0]) if "criticality_score" in df.columns else 0.5
    ioc = float(df["ioc_risk_score"].values[0]) if "ioc_risk_score" in df.columns else 0.5
    severity = calculate_severity(cvss, crit, ioc)
    
    return {
        "prediction": int(prediction),
        "confidence": proba,
        "anomaly_score": float(anomaly_score),
        "severity": severity
    }

# Initialize the model when the app starts
try:
    logger.info("🚀 Initializing AI service...")
    artifacts = load_artifacts_local()
    
    # Assign to global variables
    model = artifacts.get("model")
    preprocessor = artifacts.get("preprocessor") 
    X_train = artifacts.get("X_train")
    column_names = artifacts.get("column_names")
    baseline_shap = artifacts.get("baseline_shap")
    iso = artifacts.get("isolation_forest")
    
    logger.info("✅ AI service initialized and ready!")
    
except Exception as e:
    logger.error(f"❌ Critical error during initialization: {e}")
    logger.info("🔄 Service will continue with fallback predictions only")

@app.route("/")
def root():
    return jsonify({"status": "Local Sentient AI Predictive Security Engine is running"}), 200

@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "service": "Local AI Prediction Service", 
        "model_loaded": model is not None,
        "preprocessor_loaded": preprocessor is not None,
        "explainer_available": explainer is not None,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }), 200

@app.route("/debug", methods=["GET"])
def debug():
    return jsonify({
        "column_names": column_names if column_names else [],
        "model_loaded": model is not None,
        "preprocessor_loaded": preprocessor is not None,
        "mode": "local_development"
    }), 200

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()
        logger.info("📥 /predict payload received")
        
        df = pd.DataFrame([data])
        
        # Filter column_names to exclude timestamp first
        model_columns = [col for col in (column_names or []) if col != 'timestamp']
        
        # Add missing columns with default values
        for col in model_columns:
            if col not in df.columns:
                df[col] = 0
        
        result = predict_fn(
            df=df,
            model=model,
            preprocessor=preprocessor,
            column_names=model_columns or [],
            anomaly_filter=iso
        )
        
        # Add timestamp for API compatibility
        result["timestamp"] = datetime.utcnow().isoformat() + "Z"
        result["source"] = "local_ai_service"
        
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"❌ Error in /predict: {e}")
        # Return a fallback prediction
        return jsonify({
            "prediction": 1,
            "confidence": [0.2, 0.4, 0.3, 0.1],
            "anomaly_score": 0.0,
            "severity": "medium",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": "local_ai_service_fallback",
            "error": str(e)
        }), 200

@app.route("/explain", methods=["POST"])
def explain():
    try:
        data = request.get_json()
        logger.info("📥 /explain payload received")
        
        if explainer is None:
            logger.warning("⚠️ SHAP explainer not available")
            return jsonify({
                "explanation": "SHAP explainer not available - using fallback explanation",
                "features": data,
                "model_version": "local-dev-1.0",
                "source": "local_ai_service_fallback",
                "shap_available": False
            }), 200
        
        # Create DataFrame from input data
        df = pd.DataFrame([data])
        model_columns = [col for col in (column_names or []) if col != 'timestamp']
        
        # Add missing columns with default values
        for col in model_columns:
            if col not in df.columns:
                df[col] = 0
        
        # Transform the data
        if preprocessor is not None:
            # Add timestamp for preprocessing if needed
            if 'timestamp' not in df.columns:
                df['timestamp'] = '2025-01-01T00:00:00Z'
            
            X = preprocessor.transform(df)
        else:
            # Fallback transformation
            X = df[model_columns].values
        
        # Get SHAP explanation
        shap_values = explainer.shap_values(X)
        
        # Get feature importance (absolute mean of SHAP values)
        feature_importance = {}
        if isinstance(shap_values, list):  # Multi-class
            # Use the SHAP values for the predicted class
            prediction = model.predict(X)[0]
            shap_vals = shap_values[prediction][0]
        else:  # Binary or single output
            shap_vals = shap_values[0]
        
        # Map SHAP values to feature names
        for i, feature in enumerate(model_columns[:len(shap_vals)]):
            feature_importance[feature] = float(shap_vals[i])
        
        return jsonify({
            "explanation": "SHAP-based feature explanation",
            "feature_importance": feature_importance,
            "features": data,
            "model_version": "local-dev-1.0",
            "source": "local_ai_service",
            "shap_available": True,
            "prediction": int(model.predict(X)[0]) if model else None
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error in /explain: {e}")
        return jsonify({
            "explanation": f"Error generating explanation: {str(e)}",
            "features": data,
            "model_version": "local-dev-1.0",
            "source": "local_ai_service_error",
            "shap_available": False,
            "error": str(e)
        }), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8001)), debug=True)
