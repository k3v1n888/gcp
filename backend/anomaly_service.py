import joblib
import os
import pandas as pd
from google.cloud import storage

class AnomalyDetector:
    def __init__(self):
        # ... (code to download anomaly_model.pkl and anomaly_vectorizer.pkl from GCS) ...
        self.model = joblib.load("/tmp/anomaly_model.pkl")
        self.vectorizer = joblib.load("/tmp/anomaly_vectorizer.pkl")

    def check_for_anomaly(self, threat_log: dict) -> bool:
        """Checks if a single threat log is an anomaly."""
        if not self.model or not self.vectorizer:
            return False
        
        # Create a DataFrame with the same structure as the training data
        text_feature = self.vectorizer.transform([f"{threat_log['threat']} {threat_log['source']}"]).toarray()
        numeric_features = pd.DataFrame([{
            'ip_reputation_score': threat_log.get('ip_reputation_score', 0),
            'has_cve': 1 if threat_log.get('cve_id') else 0
        }])
        
        features_df = pd.concat([pd.DataFrame(text_feature), numeric_features], axis=1)
        features_df.columns = features_df.columns.astype(str)

        # predict() returns -1 for outliers (anomalies) and 1 for inliers.
        prediction = self.model.predict(features_df)
        return prediction[0] == -1
