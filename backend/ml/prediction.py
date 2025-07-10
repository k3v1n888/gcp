# backend/ml/prediction.py

import joblib
import os
from google.cloud import storage
from sklearn.exceptions import NotFittedError
from sklearn.utils.validation import check_is_fitted

class SeverityPredictor:
    def __init__(self):
        self.bucket_name = "quantum-ai-threat-lake-us"
        self.model_blob_name = "models/severity_model.pkl"
        self.local_model_path = "/tmp/severity_model.pkl"
        self.model = self._load_model()

    def _load_model(self):
        """Downloads the model from GCS and verifies it's fitted."""
        try:
            storage_client = storage.Client()
            bucket = storage_client.bucket(self.bucket_name)
            blob = bucket.blob(self.model_blob_name)

            print(f"Downloading model from gs://{self.bucket_name}/{self.model_blob_name}...")
            blob.download_to_filename(self.local_model_path)
            
            model = joblib.load(self.local_model_path)
            print("Model file loaded from GCS.")
            
            # --- NEW: Verify the loaded model ---
            try:
                check_is_fitted(model.named_steps['tfidfvectorizer'])
                print("✅ Model integrity check PASSED: Loaded model is fitted.")
                return model
            except NotFittedError as e:
                print(f"❌ CRITICAL ERROR: The loaded model file is NOT FITTED. Error: {e}")
                return None
            
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
