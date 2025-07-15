# backend/ml/prediction.py

import joblib
import os
import pandas as pd # <-- Import pandas
from google.cloud import storage

class SeverityPredictor:
    def __init__(self):
        self.bucket_name = "quantum-ai-threat-lake-us"
        # --- CHANGE: Point to the new, enhanced model file ---
        self.model_blob_name = "models/severity_model_v2.pkl"
        self.local_model_path = "/tmp/severity_model_v2.pkl"
        self.model = self._load_model()
        
        if self.model:
            print(f"✅ Predictor initialized. Enhanced model loaded: {self.model_blob_name}")
        else:
            print("❌ Predictor initialized, but model is not available.")

    def _download_from_gcs(self, blob_name, destination_path):
        """Helper function to download a file from GCS."""
        storage_client = storage.Client()
        bucket = storage_client.bucket(self.bucket_name)
        blob = bucket.blob(blob_name)
        blob.download_to_filename(destination_path)

    def _load_model(self):
        """Downloads the .pkl model from GCS and loads it into memory."""
        try:
            self._download_from_gcs(self.model_blob_name, self.local_model_path)
            model = joblib.load(self.local_model_path)
            print("✅ Model file loaded successfully from GCS.")
            return model
        except Exception as e:
            print(f"❌ CRITICAL ERROR: An exception occurred during model loading. Error: {e}")
            return None
    
    def _clean_text(self, text: str) -> str:
        """Converts text to lowercase and removes leading/trailing whitespace."""
        return str(text).strip().lower()

    def predict(self, threat: str, source: str, ip_reputation_score: int, cve_id: str | None) -> str:
        """
        Predicts the severity using a DataFrame with all features.
        """
        if not self.model:
            return "unknown"
        
        try:
            # --- CHANGE: Create a DataFrame that matches the model's training data ---
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
