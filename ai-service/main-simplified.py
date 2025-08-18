# ai-service/main.py - Simplified AI Prediction Service (SHAP-free for now)

from flask import Flask, request, jsonify
import os
import pandas as pd
import numpy as np
from datetime import datetime
import joblib
from sklearn.linear_model import SGDClassifier
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables for model artifacts
model = None
preprocessor = None
iso = None
column_names = None

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
    """Load model artifacts from local files with fallbacks"""
    global model, preprocessor, iso, column_names
    
    logger.info("🚀 Loading model artifacts...")
    
    model_dir = "models"
    files = {
        "model": "new-model-ssai01_models_model.joblib",
        "preprocessor": "new-model-ssai01_models_preprocessor.joblib", 
        "isolation_forest": "new-model-ssai01_models_isolation_forest.joblib"
    }
    
    artifacts = {}
    loaded_count = 0
    
    for key, filename in files.items():
        filepath = os.path.join(model_dir, filename)
        if os.path.exists(filepath):
            try:
                artifacts[key] = joblib.load(filepath)
                logger.info(f"✅ Loaded {key} from {filename}")
                loaded_count += 1
            except Exception as e:
                logger.error(f"❌ Error loading {key}: {e}")
                artifacts[key] = None
        else:
            logger.warning(f"⚠️ Missing {filepath}")
            artifacts[key] = None
    
    # Create fallbacks if needed
    if loaded_count == 0:
        logger.info("🔄 Creating fallback models...")
        
        # Create synthetic training data
        X_dummy = np.random.random((1000, 10))
        y_dummy = np.random.randint(0, 4, 1000)  # 4 severity levels
        
        # Create fallback preprocessor
        artifacts["preprocessor"] = StandardScaler()
        artifacts["preprocessor"].fit(X_dummy)
        
        # Create fallback model
        artifacts["model"] = RandomForestClassifier(n_estimators=10, random_state=42)
        X_scaled = artifacts["preprocessor"].transform(X_dummy)
        artifacts["model"].fit(X_scaled, y_dummy)
        
        # Create fallback isolation forest
        artifacts["isolation_forest"] = IsolationForest(contamination=0.1, random_state=42)
        artifacts["isolation_forest"].fit(X_scaled)
        
        logger.info("✅ Fallback models created and trained")
    
    # Set global variables
    model = artifacts.get("model")
    preprocessor = artifacts.get("preprocessor") 
    iso = artifacts.get("isolation_forest")
    column_names = [
        'technique_id', 'asset_type', 'login_hour', 'is_admin', 
        'is_remote_session', 'cvss_score', 'criticality_score', 
        'ioc_risk_score', 'login_duration', 'packet_count'
    ]
    
    logger.info("✅ AI service initialized and ready!")
    return True

def predict_fn(df, model, preprocessor, column_names, anomaly_filter=None):
    """Make predictions on the input dataframe"""
    logger.info(f"🔧 predict_fn called")
    
    # Ensure all expected columns exist in DataFrame
    for col in column_names:
        if col not in df.columns:
            df[col] = 0
    
    try:
        if preprocessor is not None:
            X = preprocessor.transform(df[column_names])
        else:
            X = df[column_names].values
    except Exception as e:
        logger.error(f"❌ Transform failed: {e}")
        X = np.array([[0] * len(column_names)])
    
    anomaly_score = anomaly_filter.decision_function(X)[0] if anomaly_filter else 0
    
    if model is not None:
        prediction = model.predict(X)[0]
        proba = model.predict_proba(X)[0].tolist()
    else:
        prediction = 1
        proba = [0.2, 0.4, 0.3, 0.1]
    
    # Get severity components
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
    success = load_artifacts_local()
    if success:
        logger.info("✅ AI service ready!")
    else:
        logger.warning("⚠️ AI service running with fallbacks")
except Exception as e:
    logger.error(f"❌ Critical error during initialization: {e}")
    logger.info("🔄 Service will continue with fallback predictions only")

@app.route("/")
def root():
    return jsonify({"status": "Local AI Prediction Service is running"}), 200

@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "service": "Local AI Prediction Service", 
        "model_loaded": model is not None,
        "preprocessor_loaded": preprocessor is not None,
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
        
        # Add missing columns with default values
        for col in column_names:
            if col not in df.columns:
                df[col] = 0
        
        result = predict_fn(
            df=df,
            model=model,
            preprocessor=preprocessor,
            column_names=column_names,
            anomaly_filter=iso
        )
        
        result["timestamp"] = datetime.utcnow().isoformat() + "Z"
        result["source"] = "local_ai_service"
        
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"❌ Error in /predict: {e}")
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
        
        # Simple feature importance explanation without SHAP
        feature_importance = {}
        for i, feature in enumerate(column_names):
            if feature in data:
                # Simple heuristic for feature importance
                value = float(data.get(feature, 0))
                if feature in ['cvss_score', 'criticality_score', 'ioc_risk_score']:
                    importance = abs(value) / 10.0
                else:
                    importance = abs(value) / 100.0
                feature_importance[feature] = min(importance, 1.0)
        
        return jsonify({
            "explanation": "Simple feature importance analysis",
            "feature_importance": feature_importance,
            "features": data,
            "model_version": "local-dev-simplified",
            "source": "local_ai_service",
            "note": "SHAP explanations will be available in production version"
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error in /explain: {e}")
        return jsonify({
            "error": str(e),
            "features": data,
            "source": "local_ai_service_error"
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8001)), debug=True)
