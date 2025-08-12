# backend/ml/prediction.py
import os
import requests
import pandas as pd
import google.auth
import google.auth.transport.requests
from datetime import datetime, timezone

# Import local model for development
DEV_MODE = os.getenv("DEV_MODE", "false").lower() == "true"

if DEV_MODE:
    from .local_prediction import LocalSeverityPredictor

AI_SERVICE_URL = os.getenv("AI_SERVICE_URL", "https://quantum-predictor-api-1020401092050.asia-southeast1.run.app")
LOCAL_AI_SERVICE_URL = os.getenv("AI_SERVICE_URL", "http://ai-service:8001")  # Use container name in dev

class SeverityPredictor:
    def __init__(self):
        if DEV_MODE:
            print("🔄 Initializing local ML predictor for development...")
            self.local_predictor = LocalSeverityPredictor()
            print("✅ Local ML predictor initialized")
        else:
            self.auth_req = google.auth.transport.requests.Request()
            self.target_audience = AI_SERVICE_URL
            print("✅ Predictor initialized to call remote AI service.")

    def _get_auth_token(self):
        try:
            creds, _ = google.auth.default()
            creds.refresh(self.auth_req)
            return creds.token
        except Exception as e:
            print(f"❌ Could not generate auth token for AI service: {e}")
            return None

    def _prepare_payload(self, threat_log: dict) -> dict:
        technique_map = {
            "sql injection": "T1055",
            "log4j": "T1190",
            "xss": "T1059",
            "brute force": "T1110",
        }
        technique_id = "T1595"
        for key, val in technique_map.items():
            if key in threat_log.get('threat', '').lower():
                technique_id = val
                break

        timestamp_input = threat_log.get('timestamp')
        if isinstance(timestamp_input, str):
            dt_object = datetime.fromisoformat(timestamp_input.replace('Z', '+00:00'))
        else:
            dt_object = timestamp_input or datetime.now(timezone.utc)

        return {
            "technique_id": technique_id,
            "asset_type": "server",
            "login_hour": dt_object.hour,
            "is_admin": 1,
            "is_remote_session": 1 if threat_log.get('source') == "VPN" else 0,
            "num_failed_logins": 1 if "failed" in threat_log.get('threat', '').lower() else 0,
            "bytes_sent": threat_log.get("bytes_sent", 10000),
            "bytes_received": threat_log.get("bytes_received", 50000),
            "location_mismatch": 1 if "new country" in threat_log.get('threat', '').lower() else 0,
            "previous_alerts": threat_log.get("previous_alerts", 0),
            "criticality_score": round(threat_log.get('criticality_score', 0), 2),
            "cvss_score": round(threat_log.get('cvss_score', 0), 2),
            "ioc_risk_score": round((threat_log.get('ip_reputation_score', 0) or 0) / 100.0, 2)
        }

    def predict_severity(self, threat, source, ip_reputation_score=None, cve_id=None, cvss_score=None, criticality_score=None):
        if DEV_MODE:
            # Use local AI service in development
            temp_log = {
                "threat": threat,
                "source": source,
                "ip_reputation_score": ip_reputation_score or 50,
                "cve_id": cve_id,
                "cvss_score": cvss_score or 5.0,
                "criticality_score": criticality_score or 0.5,
                "ioc_risk_score": 0.5,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            # First try local ML model
            try:
                result = self.local_predictor.predict_severity(temp_log)
                return result.get("severity", "medium")
            except Exception as e:
                print(f"Local ML model failed, trying local AI service: {e}")
                
                # Fallback to local AI service
                try:
                    payload = self._prepare_payload(temp_log)
                    response = requests.post(f"{LOCAL_AI_SERVICE_URL}/predict", json=payload, timeout=10)
                    response.raise_for_status()
                    result = response.json()
                    prediction_map = {0: "low", 1: "medium", 2: "high", 3: "critical"}
                    return result.get("severity", prediction_map.get(result.get('prediction', 1), "medium"))
                except Exception as ai_error:
                    print(f"Local AI service also failed: {ai_error}")
                    return "medium"  # Final fallback
        
        # Use remote AI service in production
        token = self._get_auth_token()
        if not token:
            return "unknown"

        headers = {"Authorization": f"Bearer {token}"}
        temp_log = {
            "threat": threat,
            "source": source,
            "ip_reputation_score": ip_reputation_score,
            "cve_id": cve_id,
            "cvss_score": cvss_score,
            "criticality_score": criticality_score,
            "timestamp": datetime.now(timezone.utc)
        }
        payload = self._prepare_payload(temp_log)

        try:
            response = requests.post(f"{AI_SERVICE_URL}/predict", json=payload, headers=headers)
            response.raise_for_status()
            prediction_map = {0: "low", 1: "medium", 2: "high", 3: "critical"}
            return prediction_map.get(response.json().get('prediction', 0), "unknown")
        except Exception as e:
            print(f"Prediction API call failed: {e}")
            return "unknown"

    def explain_prediction(self, threat_log: dict) -> dict | None:
        if DEV_MODE:
            # Use local model explanation in development
            result = self.local_predictor.predict_severity(threat_log)
            return {
                "explanation": "Local ML model prediction based on threat patterns",
                "confidence": result.get("confidence", 0.5),
                "features_importance": {
                    "threat_type": 0.3,
                    "source": 0.2,
                    "time_of_day": 0.15,
                    "ip_reputation": 0.25,
                    "admin_access": 0.1
                },
                "model_version": "local-1.0.0",
                "probabilities": result.get("probabilities", {})
            }
        
        # Use remote AI service in production
        token = self._get_auth_token()
        if not token:
            return None
        headers = {'Authorization': f'Bearer {token}'}
        payload = self._prepare_payload(threat_log)
        try:
            response = requests.post(f"{AI_SERVICE_URL}/explain", json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Explanation API call failed: {e}")
            return None