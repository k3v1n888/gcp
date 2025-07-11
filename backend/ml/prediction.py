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
        storage_client = storage.Client()
        bucket = storage_client.bucket(self.bucket_name)
        blob = bucket.blob(blob_name)
        blob.download_to_filename(destination_path)

    def _load_and_rebuild_model(self):
        try:
            vocab_path = "/tmp/vocabulary.json"
            params_path = "/tmp/model_params.json"
            self._download_from_gcs("models/vocabulary.json", vocab_path)
            self._download_from_gcs("models/model_params.json", params_path)

            with open(vocab_path, 'r') as f:
                vocab = json.load(f)
            vectorizer = TfidfVectorizer(vocabulary=vocab)
            
            with open(params_path, 'r') as f:
                params = json.load(f)
            classifier = LogisticRegression()
            
            classifier.classes_ = np.array(params['classes'])
            classifier.intercept_ = np.array(params['intercept'])
            
            # --- THIS IS THE FINAL FIX ---
            # Reshape the coefficients to match the vocabulary size and classes
            n_features = len(vocab)
            n_classes = len(params['classes'])
            expected_shape = (n_classes, n_features) if n_classes > 2 else (1, n_features)
            classifier.coef_ = np.array(params['coef']).reshape(expected_shape)
            
            # Fit the vectorizer on dummy data to finalize its state
            vectorizer.fit(["dummy text"])

            print("✅ Vectorizer and Classifier rebuilt and synchronized successfully.")
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
            vectorized_text = self.model['vectorizer'].transform([text_feature])
            prediction = self.model['classifier'].predict(vectorized_text)
            return prediction[0]
        except Exception as e:
            # This will catch any remaining prediction errors
            print(f"Prediction failed for text '{text_feature}': {e}")
            return "unknown"
