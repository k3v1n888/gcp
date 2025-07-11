# backend/ml/prediction.py

import json
import os
import numpy as np
from google.cloud import storage
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

class SeverityPredictor:
    def __init__(self):
        self.bucket_name = "quantum-ai-threat-lake-us"
        self.model = self._load_and_rebuild_model()
        
        if self.model:
            print("✅ Predictor initialized. Model rebuilt successfully.")
        else:
            print("❌ Predictor initialized, but model is not available.")

    def _download_from_gcs(self, blob_name, destination_path):
        """Helper function to download a file from GCS."""
        storage_client = storage.Client()
        bucket = storage_client.bucket(self.bucket_name)
        blob = bucket.blob(blob_name)
        blob.download_to_filename(destination_path)

    def _load_and_rebuild_model(self):
        """Downloads JSON files and rebuilds the model objects."""
        try:
            # Download model files
            vocab_path = "/tmp/vocabulary.json"
            params_path = "/tmp/model_params.json"
            self._download_from_gcs("models/vocabulary.json", vocab_path)
            self._download_from_gcs("models/model_params.json", params_path)

            # Load vocabulary and create vectorizer
            with open(vocab_path, 'r') as f:
                vocab = json.load(f)
            vectorizer = TfidfVectorizer(vocabulary=vocab)
            
            # Load params and create classifier
            with open(params_path, 'r') as f:
                params = json.load(f)
            classifier = LogisticRegression()
            
            # Manually set the learned parameters
            classifier.classes_ = np.array(params['classes'])
            classifier.intercept_ = np.array(params['intercept'])
            classifier.coef_ = np.array(params['coef'])

            # Return a dictionary containing the two rebuilt components
            return {'vectorizer': vectorizer, 'classifier': classifier}

        except Exception as e:
            print(f"❌ CRITICAL ERROR: An exception occurred during model rebuilding. Error: {e}")
            return None
    
    def _clean_text(self, text: str) -> str:
        return str(text).strip().lower()

    def predict(self, threat: str, source: str) -> str:
        if not self.model:
            return "unknown"
        
        text_feature = self._clean_text(f"{threat} {source}")
        
        try:
            # Use the rebuilt components to predict
            vectorized_text = self.model['vectorizer'].transform([text_feature])
            prediction = self.model['classifier'].predict(vectorized_text)
            return prediction[0]
        except Exception as e:
            print(f"Prediction failed: {e}")
            return "unknown"
