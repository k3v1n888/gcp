# backend/ml/prediction.py

import os
import requests
import pandas as pd
import google.auth
import google.auth.transport.requests
from datetime import datetime, timezone

AI_SERVICE_URL = os.getenv("AI_SERVICE_URL", "https://quantum-predictor-api-1020401092050.asia-southeast1.run.app")

class SeverityPredictor:
    def __init__(self):
        self.auth_req = google.auth.transport.requests.Request()
        self.target_audience = AI_SERVICE_URL
        print("✅ Predictor initialized to call remote AI service.")

    def _get_auth_token(self):
        try:
            creds, project = google.auth.default()
            creds.refresh(self.auth_req)
            return creds.token
        except Exception as e:
            print(f"❌ Could not generate auth token for AI service: {e}")
            return None

    def _prepare_payload(self, threat_log: dict) -> dict:
        technique_map = {
            "sql injection": "T1055", "log4j": "T1190",
            "xss": "T1059", "brute force": "T1110",
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
            dt_object = timestamp_input

        login_hour = dt_object.hour if dt_object else datetime.now(timezone.utc).hour

        return {
            "technique_id": technique_id,
            "asset_type": "server",
            "login_hour": login_hour,
            "is_admin": 1,
            "is_remote_session": 1 if threat_log.get('source') == "VPN" else 0,
            "num_failed_logins": 1 if "failed" in threat_log.get('threat', '').lower() else 0,
            "bytes_sent": 10000,
            "bytes_received": 50000,
            "location_mismatch": 1 if "new country" in threat_log.get('threat', '').lower() else 0,
            "previous_alerts": 0,
            "criticality_score": threat_log.get("criticality_score", 0),
            "cvss_score": threat_log.get("cvss_score", 0),
            "ioc_risk_score": (threat_log.get('ip_reputation_score', 0) or 0) / 100.0
        }

    def predict(self, threat: str, source: str, ip_reputation_score: int, cve_id: str | None,
                cvss_score: float = 0.0, criticality_score: float = 0.0) -> str:
        token = self._get_auth_token()
        if not token:
            return "unknown"

        headers = {'Authorization': f'Bearer {token}'}
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
        print(f"📦 Sending to AI model: {payload}")

        try:
            response = requests.post(f"{AI_SERVICE_URL}/predict", json=payload, headers=headers)
            response.raise_for_status()
            prediction_map = {0: "low", 1: "medium", 2: "high", 3: "critical"}
            prediction_int = response.json().get('prediction', 0)
            return prediction_map.get(prediction_int, "unknown")
        except Exception as e:
            print(f"Prediction API call failed: {e}")
            return "unknown"

    def explain_prediction(self, threat_log: dict) -> dict | None:
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