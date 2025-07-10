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
        
        # --- NEW: Log the final status of the model after loading ---
        if self.model:
            print(f"✅ Predictor initialized. Model type: {type(self.model)}")
        else:
            print("❌ Predictor initialized, but model is not available.")

    def _load_model(self):
        """Downloads the model from GCS and verifies it's fitted."""
        try:
            # ... (download code is the same) ...
            storage_client = storage.Client()
            bucket = storage_client.bucket(self.bucket_name)
            blob = bucket.blob(self.model_blob_name)
            blob.download_to_filename(self.local_model_path)
            
            model = joblib.load(self.local_model_path)
            print(f"--- Model file loaded. Object type: {type(model)} ---")
            
            # --- NEW: More detailed verification ---
            try:
                vectorizer = model.named_steps['tfidfvectorizer']
                print(f"--- Vectorizer step found. Type: {type(vectorizer)} ---")
                check_is_fitted(vectorizer)
                print("✅ Model integrity check PASSED: Loaded model is fitted.")
                return model
            except NotFittedError as e:
                print(f"❌ CRITICAL ERROR: The loaded model file is NOT FITTED. Error: {e}")
                return None
            
        except Exception as e:
            print(f"❌ CRITICAL ERROR: An exception occurred during model loading. Error: {e}")
            return None

    def predict(self, threat: str, source: str) -> str:
        if not self.model:
            return "unknown"
        
        text_feature = f"{threat} {source}"
        prediction = self.model.predict([text_feature])
        return prediction[0]

severity_predictor = SeverityPredictor()
