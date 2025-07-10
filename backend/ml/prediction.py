# backend/ml/prediction.py

import joblib
import os
from google.cloud import storage

class SeverityPredictor:
    def __init__(self):
        self.bucket_name = "quantum-ai-threat-lake-raw"
        self.model_blob_name = "models/severity_model.pkl" # Path in GCS
        self.local_model_path = "/tmp/severity_model.pkl" # Temp path inside the container
        self.model = self._load_model()

    def _load_model(self):
        """Downloads the model from GCS and loads it into memory."""
        try:
            storage_client = storage.Client()
            bucket = storage_client.bucket(self.bucket_name)
            blob = bucket.blob(self.model_blob_name)

            print(f"Downloading model from gs://{self.bucket_name}/{self.model_blob_name}...")
            blob.download_to_filename(self.local_model_path)

            model = joblib.load(self.local_model_path)
            print("✅ Severity prediction model loaded successfully from GCS.")
            return model
        except Exception as e:
            print(f"❌ Warning: Failed to load model from GCS. Prediction will be disabled. Error: {e}")
            return None

    def predict(self, threat: str, source: str) -> str:
        """Predicts the severity of a threat log."""
        if not self.model:
            return "unknown"

        text_feature = f"{threat} {source}"
        prediction = self.model.predict([text_feature])
        return prediction[0]

# Create a single instance for the app to use
severity_predictor = SeverityPredictor()
