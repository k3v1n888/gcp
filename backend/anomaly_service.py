"""
Copyright (c) 2025 Kevin Zachary
All rights reserved.

This software and associated documentation files (the "Software") are the 
exclusive property of Kevin Zachary. Unauthorized copying, distribution, 
modification, or use of this software is strictly prohibited.

For licensing inquiries, contact: kevin@zachary.com
"""

# Author: Kevin Zachary
# Copyright: Sentient Spire

import joblib
import os
import pandas as pd
from google.cloud import storage

class AnomalyDetector:
    def __init__(self):
        self.bucket_name = os.getenv("GCS_BUCKET_NAME", "quantum-ai-threat-lake-us")
        self.model = self._load_model("models/anomaly_model.pkl", "/tmp/anomaly_model.pkl")
        self.vectorizer = self._load_model("models/anomaly_vectorizer.pkl", "/tmp/anomaly_vectorizer.pkl")
        
        if self.model and self.vectorizer:
            print("✅ Anomaly Detector initialized successfully.")
        else:
            print("❌ Anomaly Detector initialization failed.")

    def _load_model(self, blob_name, destination_path):
        try:
            storage_client = storage.Client()
            bucket = storage_client.bucket(self.bucket_name)
            blob = bucket.blob(blob_name)
            blob.download_to_filename(destination_path)
            return joblib.load(destination_path)
        except Exception as e:
            print(f"❌ Failed to load model {blob_name}: {e}")
            return None

    def check_for_anomaly(self, threat_log: dict) -> bool:
        if not self.model or not self.vectorizer:
            return False
        
        try:
            text_feature = f"{threat_log.get('threat', '')} {threat_log.get('source', '')}"
            text_vector = self.vectorizer.transform([text_feature]).toarray()
            
            numeric_features = pd.DataFrame([{
                'ip_reputation_score': threat_log.get('ip_reputation_score', 0) or 0,
                'has_cve': 1 if threat_log.get('cve_id') else 0
            }])
            
            features_df = pd.concat([pd.DataFrame(text_vector), numeric_features], axis=1)
            features_df.columns = features_df.columns.astype(str)

            prediction = self.model.predict(features_df)
            return prediction[0] == -1
        except Exception as e:
            print(f"Anomaly check failed: {e}")
            return False
