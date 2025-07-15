# backend/ml/prediction.py

import joblib
import os
import pandas as pd
from google.cloud import storage
from sklearn.utils.validation import check_is_fitted

class SeverityPredictor:
    def __init__(self):
        self.bucket_name = "quantum-ai-threat-lake-us"
        self.model_blob_name = "models/severity_model_v2.pkl"
        self.local_model_path = "/tmp/severity_model_v2.pkl"
        self.model = self._load_model()

    def _load_model(self):
        try:
            storage_client = storage.Client()
            bucket = storage_client.bucket(self.bucket_name)
            blob = bucket.blob(self.model_blob_name)
            blob.download_to_filename(self.local_model_path)
            
            model = joblib.load(self.local_model_path)
            check_is_fitted(model) # Check the entire pipeline
            print("✅ Model loaded and verified successfully.")
            return model
        except Exception as e:
            print(f"❌ CRITICAL ERROR: Failed to load or verify model. Error: {e}")
            return None
    
    def _clean_text(self, text: str) -> str:
        return str(text).strip().lower()

    def predict(self, threat: str, source: str, ip_reputation_score: int, cve_id: str | None) -> str:
        if not self.model:
            return "unknown"
        
        try:
            text_feature = self._clean_text(f"{threat} {source}")
            has_cve = 1 if cve_id else 0
            
            input_data = pd.DataFrame([{
                'text_feature': text_feature,
                'ip_reputation_score': ip_reputation_score,
                'has_cve': has_cve
            }])
            
            prediction = self.model.predict(input_data)
            return prediction[0]
        except Exception as e:
            print(f"Prediction failed: {e}")
            return "unknown"
