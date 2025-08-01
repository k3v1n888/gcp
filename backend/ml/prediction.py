import os
import requests
import pandas as pd
import google.auth
import google.auth.transport.requests

# The URL of your new, deployed AI model service
AI_SERVICE_URL = os.getenv("AI_SERVICE_URL", "https://quantum-predictor-api-1020401092050.asia-southeast1.run.app")

class SeverityPredictor:
    def __init__(self):
        self.auth_req = google.auth.transport.requests.Request()
        self.target_audience = AI_SERVICE_URL
        print("✅ Predictor initialized to call remote AI service.")

    def _get_auth_token(self):
        """Generates a Google-signed ID token for service-to-service auth."""
        try:
            creds, project = google.auth.default()
            creds.refresh(self.auth_req)
            return creds.token
        except Exception as e:
            print(f"❌ Could not generate auth token for AI service: {e}")
            return None

    def predict(self, threat: str, source: str, ip_reputation_score: int, cve_id: str | None) -> str:
        """Calls the remote AI service to get a severity prediction."""
        token = self._get_auth_token()
        if not token:
            return "unknown"

        headers = {'Authorization': f'Bearer {token}'}
        payload = {
            "threat": threat,
            "source": source,
            "ip_reputation_score": ip_reputation_score,
            "cve_id": cve_id
        }

        try:
            # Assuming your AI service has a '/predict' endpoint
            response = requests.post(f"{AI_SERVICE_URL}/predict", json=payload, headers=headers)
            response.raise_for_status()
            # The "correctness" of the severity comes from your custom model's logic
            return response.json().get('severity', 'unknown')
        except Exception as e:
            print(f"Prediction API call to remote AI service failed: {e}")
            return "unknown"
            
    def explain_prediction(self, threat_log: dict) -> dict | None:
        """Calls the remote AI service to get a SHAP-based explanation."""
        token = self._get_auth_token()
        if not token:
            return None

        headers = {'Authorization': f'Bearer {token}'}
        
        try:
            # Assuming your AI service has an '/explain' endpoint
            response = requests.post(f"{AI_SERVICE_URL}/explain", json=threat_log, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Explanation API call to remote AI service failed: {e}")
            return None