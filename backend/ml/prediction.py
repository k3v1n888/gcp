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
        
        if self.model:
            print(f"✅ Predictor initialized. Model type: {type(self.model)}")
        else:
            print("❌ Predictor initialized, but model is not available.")

    def _load_model(self):
        """Downloads the model from GCS and verifies it's fitted."""
        try:
            storage_client = storage.Client()
            bucket = storage_client.bucket(self.bucket_name)
            blob = bucket.blob(self.model_blob_name)
            print(f"Downloading model from gs://{self.bucket_name}/{self.model_blob_name}...")
            blob.download_to_filename(self.local_model_path)
            
            model = joblib.load(self.local_model_path)
            print(f"--- Model file loaded. Object type: {type(model)} ---")
            
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
    
    # --- NEW: A consistent cleaning function ---
    def _clean_text(self, text: str) -> str:
        """Converts text to lowercase and removes leading/trailing whitespace."""
        return str(text).strip().lower()

    def predict(self, threat: str, source: str) -> str:
        """Predicts the severity of a threat log."""
        if not self.model:
            return "unknown"
        
        # Apply the same cleaning function before prediction
        text_feature = self._clean_text(f"{threat} {source}")
        
        prediction = self.model.predict([text_feature])
        return prediction[0]
