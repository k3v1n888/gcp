import joblib
import os
import pandas as pd
from google.cloud import storage

class ThreatForecaster:
    def __init__(self):
        self.bucket_name = "quantum-ai-threat-lake-us"
        self.model_blob_name = "models/forecasting_models.pkl"
        self.local_model_path = "/tmp/forecasting_models.pkl"
        self.models = self._load_models()

    def _load_models(self):
        """Downloads the forecasting models from GCS."""
        try:
            storage_client = storage.Client()
            bucket = storage_client.bucket(self.bucket_name)
            blob = bucket.blob(self.model_blob_name)
            blob.download_to_filename(self.local_model_path)
            models = joblib.load(self.local_model_path)
            print("✅ Forecasting models loaded successfully.")
            return models
        except Exception as e:
            print(f"❌ Failed to load forecasting models: {e}")
            return None

    def predict_next_24_hours(self) -> dict:
        """Generates a forecast for the next 24 hours."""
        if not self.models:
            return {"error": "Forecasting models not available."}

        forecasts = {}
        for threat_type, model_fit in self.models.items():
            # Forecast the next 24 steps (hours)
            forecast = model_fit.forecast(steps=24)
            # We only care about threats that are predicted to occur
            if forecast.sum() > 0.1: # Use a threshold to filter out noise
                forecasts[threat_type] = round(forecast.sum(), 2)
        
        # Sort by most likely threats
        sorted_forecasts = sorted(forecasts.items(), key=lambda item: item[1], reverse=True)
        
        return {
            "forecast_period_hours": 24,
            "predicted_threats": dict(sorted_forecasts)
        }
