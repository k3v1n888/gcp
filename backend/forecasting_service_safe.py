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

"""
Safe Threat Forecasting Service with Multiple Fallback Layers
This service ensures the application never breaks due to forecasting failures.
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

logger = logging.getLogger(__name__)

class SafeThreatForecaster:
    """
    A safe threat forecasting service with multiple fallback layers:
    1. ML-based forecasting (when available)
    2. Statistical forecasting (based on historical data)
    3. Mock forecasting (when no data is available)
    """
    
    def __init__(self):
        self.ml_forecaster = None
        self._initialize_ml_forecaster()
    
    def _initialize_ml_forecaster(self):
        """Try to initialize ML forecaster, but don't fail if it's not available"""
        try:
            from .forecasting_service import ThreatForecaster
            self.ml_forecaster = ThreatForecaster()
            if self.ml_forecaster.models:
                logger.info("✅ ML-based forecasting available")
            else:
                logger.warning("⚠️ ML models not available, will use fallback")
                self.ml_forecaster = None
        except Exception as e:
            logger.warning(f"⚠️ ML forecasting unavailable: {e}")
            self.ml_forecaster = None
    
    def predict_next_24_hours(self, db_session: Optional[Session] = None) -> Dict[str, Any]:
        """
        Generate 24-hour threat forecast with fallback layers
        """
        # Layer 1: Try ML-based forecasting
        if self.ml_forecaster:
            try:
                result = self.ml_forecaster.predict_next_24_hours()
                if not result.get("error"):
                    logger.info("✅ Using ML-based forecast")
                    result["method"] = "ml_based"
                    return result
            except Exception as e:
                logger.warning(f"ML forecasting failed: {e}")
        
        # Layer 2: Statistical forecasting based on historical data
        if db_session:
            try:
                result = self._statistical_forecast(db_session)
                logger.info("✅ Using statistical forecast")
                return result
            except Exception as e:
                logger.warning(f"Statistical forecasting failed: {e}")
        
        # Layer 3: Mock forecast (always works)
        logger.info("⚠️ Using mock forecast")
        return self._mock_forecast()
    
    def _statistical_forecast(self, db: Session) -> Dict[str, Any]:
        """
        Statistical forecasting based on recent threat patterns
        """
        from .models import ThreatLog
        
        # Get threats from last 7 days
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        
        recent_threats = (
            db.query(ThreatLog.threat, func.count(ThreatLog.id).label('count'))
            .filter(ThreatLog.timestamp >= seven_days_ago)
            .filter(ThreatLog.threat.isnot(None))
            .group_by(ThreatLog.threat)
            .order_by(func.count(ThreatLog.id).desc())
            .limit(10)
            .all()
        )
        
        if not recent_threats:
            return self._mock_forecast("No recent threat data available")
        
        # Create forecast based on recent frequency
        predicted_threats = {}
        total_threats = sum([count for _, count in recent_threats])
        
        for threat, count in recent_threats:
            # Calculate probability based on frequency
            frequency_score = count / 7.0  # Average per day
            probability = min(frequency_score / max(total_threats / 7.0, 1.0), 1.0)
            
            # Only include significant predictions
            if probability > 0.05:
                predicted_threats[threat] = round(probability, 3)
        
        return {
            "forecast_period_hours": 24,
            "predicted_threats": predicted_threats,
            "method": "statistical",
            "data_period": "7_days",
            "total_historical_threats": total_threats
        }
    
    def _mock_forecast(self, note: str = "Using simulated data") -> Dict[str, Any]:
        """
        Mock forecast for when no real data is available
        """
        # Simulate realistic threat predictions with varied probabilities
        mock_threats = {
            "Suspicious PowerShell activity detected": 0.12,
            "Multiple failed login attempts observed": 0.08,
            "Network scanning behavior identified": 0.06,
            "Unusual outbound connections detected": 0.05,
            "Potential malware communication patterns": 0.04
        }
        
        return {
            "forecast_period_hours": 24,
            "predicted_threats": mock_threats,
            "method": "mock",
            "note": note,
            "warning": "This is simulated data for demonstration purposes",
            "threat_categories": {
                "endpoint": ["Suspicious PowerShell activity detected", "Potential malware communication patterns"],
                "identity": ["Multiple failed login attempts observed"],
                "network": ["Network scanning behavior identified", "Unusual outbound connections detected"]
            },
            "risk_assessment": {
                "overall_risk": "medium",
                "confidence": 0.7,
                "trend": "stable"
            }
        }
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check the health of the forecasting service
        """
        return {
            "ml_forecaster_available": self.ml_forecaster is not None,
            "can_use_ml": self.ml_forecaster and self.ml_forecaster.models is not None,
            "fallback_methods": ["statistical", "mock"],
            "status": "healthy"
        }
