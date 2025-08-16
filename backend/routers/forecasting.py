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

from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/api/forecasting/24_hour")
def get_24_hour_forecast(
    request: Request, 
    db: Session = Depends(get_db)
):
    """
    Get 24-hour threat forecast with multiple fallback layers
    """
    try:
        # Get the safe forecaster from app state
        forecaster = getattr(request.app.state, 'safe_forecaster', None)
        
        if not forecaster:
            # Fallback: create a temporary forecaster
            from ..forecasting_service_safe import SafeThreatForecaster
            forecaster = SafeThreatForecaster()
            logger.warning("Created temporary forecaster - consider fixing app initialization")
        
        # Get prediction with database session for statistical fallback
        prediction = forecaster.predict_next_24_hours(db_session=db)
        return prediction
        
    except Exception as e:
        logger.error(f"Forecasting endpoint failed: {e}")
        # Final failsafe - return mock data
        return {
            "forecast_period_hours": 24,
            "predicted_threats": {
                "System Alert": 0.10,
                "Network Anomaly": 0.05
            },
            "method": "emergency_fallback",
            "error": "Forecasting service temporarily unavailable"
        }

@router.get("/api/forecasting/health")
def get_forecasting_health(request: Request):
    """
    Check the health of the forecasting service
    """
    try:
        forecaster = getattr(request.app.state, 'safe_forecaster', None)
        if forecaster:
            return forecaster.health_check()
        else:
            return {
                "status": "degraded",
                "message": "Safe forecaster not initialized"
            }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
