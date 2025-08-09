# backend/ml/local_prediction.py
import os
import pandas as pd
import numpy as np
import joblib
from datetime import datetime, timezone
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class LocalSeverityPredictor:
    def __init__(self):
        self.model = None
        self.label_encoder = None
        self.scaler = None
        self.is_trained = False
        self.model_path = "models/local_severity_model.pkl"
        self.encoder_path = "models/local_label_encoder.pkl"
        self.scaler_path = "models/local_scaler.pkl"
        
        # Create models directory if it doesn't exist
        os.makedirs("models", exist_ok=True)
        
        # Try to load existing model, otherwise create and train a new one
        if self._load_model():
            print("✅ Local ML model loaded successfully")
        else:
            print("🔄 Training new local ML model...")
            self._train_initial_model()
            print("✅ Local ML model trained and ready")

    def _load_model(self) -> bool:
        """Load existing model from disk"""
        try:
            if os.path.exists(self.model_path) and os.path.exists(self.encoder_path) and os.path.exists(self.scaler_path):
                self.model = joblib.load(self.model_path)
                self.label_encoder = joblib.load(self.encoder_path)
                self.scaler = joblib.load(self.scaler_path)
                self.is_trained = True
                return True
        except Exception as e:
            logger.error(f"Error loading model: {e}")
        return False

    def _save_model(self):
        """Save model to disk"""
        try:
            joblib.dump(self.model, self.model_path)
            joblib.dump(self.label_encoder, self.encoder_path)
            joblib.dump(self.scaler, self.scaler_path)
        except Exception as e:
            logger.error(f"Error saving model: {e}")

    def _train_initial_model(self):
        """Train initial model with synthetic data"""
        # Generate synthetic training data for threat severity prediction
        np.random.seed(42)
        
        # Features: technique_id_encoded, asset_type_encoded, login_hour, is_admin, is_remote_session, 
        #          source_encoded, ip_reputation_score, packet_count, connection_duration
        
        # Generate synthetic data
        n_samples = 1000
        
        # Threat techniques (simplified encoding)
        technique_map = {"T1055": 0, "T1190": 1, "T1059": 2, "T1110": 3, "T1595": 4}
        techniques = np.random.choice(list(technique_map.values()), n_samples)
        
        # Asset types
        asset_types = np.random.choice([0, 1, 2], n_samples)  # server, workstation, network_device
        
        # Login hours
        login_hours = np.random.randint(0, 24, n_samples)
        
        # Binary features
        is_admin = np.random.choice([0, 1], n_samples, p=[0.7, 0.3])
        is_remote = np.random.choice([0, 1], n_samples, p=[0.6, 0.4])
        
        # Sources
        sources = np.random.choice([0, 1, 2, 3], n_samples)  # internal, external, VPN, cloud
        
        # IP reputation scores (0-100, lower is worse)
        ip_scores = np.random.randint(0, 101, n_samples)
        
        # Packet counts
        packet_counts = np.random.exponential(100, n_samples)
        
        # Connection durations (seconds)
        connection_durations = np.random.exponential(300, n_samples)
        
        # Create feature matrix
        X = np.column_stack([
            techniques, asset_types, login_hours, is_admin, is_remote,
            sources, ip_scores, packet_counts, connection_durations
        ])
        
        # Generate labels based on logical rules
        y = []
        for i in range(n_samples):
            score = 0
            
            # High-risk techniques
            if techniques[i] in [1, 2]:  # T1190, T1059
                score += 3
            elif techniques[i] == 3:  # T1110
                score += 2
            
            # Admin access increases risk
            if is_admin[i] == 1:
                score += 1
            
            # Remote access increases risk
            if is_remote[i] == 1:
                score += 1
            
            # Low IP reputation increases risk
            if ip_scores[i] < 30:
                score += 2
            elif ip_scores[i] < 60:
                score += 1
            
            # Off-hours access increases risk
            if login_hours[i] < 6 or login_hours[i] > 22:
                score += 1
            
            # High packet count increases risk
            if packet_counts[i] > 500:
                score += 1
            
            # Long connections can be suspicious
            if connection_durations[i] > 1800:  # 30 minutes
                score += 1
            
            # Map score to severity
            if score >= 6:
                severity = "critical"
            elif score >= 4:
                severity = "high"
            elif score >= 2:
                severity = "medium"
            else:
                severity = "low"
            
            y.append(severity)
        
        # Create and train model
        self.label_encoder = LabelEncoder()
        y_encoded = self.label_encoder.fit_transform(y)
        
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            class_weight='balanced'
        )
        
        self.model.fit(X_scaled, y_encoded)
        self.is_trained = True
        
        # Save the model
        self._save_model()
        
        print(f"Model trained with {n_samples} samples")
        print(f"Classes: {self.label_encoder.classes_}")

    def _prepare_features(self, threat_log: Dict[str, Any]) -> np.ndarray:
        """Prepare features from threat log"""
        # Map threat techniques
        technique_map = {
            "sql injection": 1,  # T1190
            "log4j": 1,          # T1190
            "xss": 2,            # T1059
            "brute force": 3,    # T1110
            "reconnaissance": 4,  # T1595
        }
        
        technique_encoded = 4  # Default to T1595
        threat_text = threat_log.get('threat', '').lower()
        for key, val in technique_map.items():
            if key in threat_text:
                technique_encoded = val
                break
        
        # Asset type mapping
        asset_type_map = {"server": 0, "workstation": 1, "network_device": 2}
        asset_type_encoded = 0  # Default to server
        
        # Extract timestamp info
        timestamp_input = threat_log.get('timestamp')
        if isinstance(timestamp_input, str):
            try:
                dt_object = datetime.fromisoformat(timestamp_input.replace('Z', '+00:00'))
            except:
                dt_object = datetime.now(timezone.utc)
        else:
            dt_object = timestamp_input or datetime.now(timezone.utc)
        
        login_hour = dt_object.hour
        
        # Binary features
        is_admin = 1 if threat_log.get('source') in ['admin', 'root', 'administrator'] else 0
        is_remote = 1 if threat_log.get('source') in ['VPN', 'external', 'remote'] else 0
        
        # Source mapping
        source_map = {"internal": 0, "external": 1, "VPN": 2, "cloud": 3}
        source_encoded = source_map.get(threat_log.get('source', 'internal'), 0)
        
        # IP reputation score (if available, otherwise use default)
        ip_reputation = threat_log.get('ip_reputation_score', 50)
        
        # Additional features with defaults
        packet_count = threat_log.get('packet_count', 100)
        connection_duration = threat_log.get('connection_duration', 300)
        
        features = np.array([[
            technique_encoded, asset_type_encoded, login_hour, is_admin, is_remote,
            source_encoded, ip_reputation, packet_count, connection_duration
        ]])
        
        return features

    def predict_severity(self, threat_log: Dict[str, Any]) -> Dict[str, Any]:
        """Predict threat severity using local model"""
        if not self.is_trained:
            return {
                "severity": "medium",
                "confidence": 0.5,
                "source": "fallback",
                "error": "Model not trained"
            }
        
        try:
            # Prepare features
            features = self._prepare_features(threat_log)
            features_scaled = self.scaler.transform(features)
            
            # Make prediction
            prediction = self.model.predict(features_scaled)[0]
            probabilities = self.model.predict_proba(features_scaled)[0]
            
            # Convert back to label
            severity = self.label_encoder.inverse_transform([prediction])[0]
            confidence = float(np.max(probabilities))
            
            return {
                "severity": severity,
                "confidence": confidence,
                "source": "local_ml_model",
                "model_version": "1.0.0",
                "probabilities": {
                    cls: float(prob) 
                    for cls, prob in zip(self.label_encoder.classes_, probabilities)
                }
            }
            
        except Exception as e:
            logger.error(f"Local prediction error: {e}")
            return {
                "severity": "medium",
                "confidence": 0.5,
                "source": "fallback",
                "error": str(e)
            }

    def retrain_with_feedback(self, threat_logs: list, actual_severities: list):
        """Retrain model with feedback data"""
        if len(threat_logs) < 10:
            print("Not enough feedback data for retraining")
            return
        
        try:
            # Prepare features and labels
            X_new = []
            for log in threat_logs:
                features = self._prepare_features(log)
                X_new.append(features[0])
            
            X_new = np.array(X_new)
            X_new_scaled = self.scaler.transform(X_new)
            y_new_encoded = self.label_encoder.transform(actual_severities)
            
            # Retrain model (you might want to use partial_fit for online learning)
            self.model.fit(X_new_scaled, y_new_encoded)
            
            # Save updated model
            self._save_model()
            
            print(f"Model retrained with {len(threat_logs)} feedback samples")
            
        except Exception as e:
            logger.error(f"Retraining error: {e}")
