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

import requests
from sqlalchemy.orm import Session
from . import models
from .wazuh_service import get_wazuh_jwt, WAZUH_URL
from .ml.prediction import AI_SERVICE_URL # Import the AI service URL
from datetime import datetime, timezone

def run_ai_threat_hunt(db: Session, tenant_id: int):
    """
    Calls the AI model service to get top indicators and then hunts for them in Wazuh.
    """
    print("Starting AI-Driven Threat Hunt...")

    try:
        # --- 1. Get Top Indicators from the AI Model Service ---
        print(f"Querying AI service for top indicators at: {AI_SERVICE_URL}/get_top_indicators")
        response = requests.get(f"{AI_SERVICE_URL}/get_top_indicators")
        response.raise_for_status()
        top_indicators = response.json().get("top_indicators", [])
        
        if not top_indicators:
            print("No indicators returned from AI service.")
            return {"message": "Threat Hunt complete. No new indicators from AI."}
        
        print(f"Top indicators for 'critical' threats: {top_indicators}")

        # --- 2. Generate and Run Hunting Queries in Wazuh ---
        jwt_token = get_wazuh_jwt()
        if not jwt_token:
            return {"error": "Could not authenticate with Wazuh for threat hunt."}

        all_results = []
        for indicator in top_indicators:
            # Create a simple query to search for this indicator in Wazuh logs
            wazuh_query = f'"{indicator}"' # Search for the exact keyword
            print(f"Hunting in Wazuh for: {wazuh_query}")
            
            alert_response = requests.get(
                f"{WAZUH_URL}/alerts",
                params={'q': wazuh_query, 'limit': 10},
                headers={'Authorization': f'Bearer {jwt_token}'},
                verify=False
            )
            if alert_response.ok:
                results = alert_response.json().get('data', {}).get('affected_items', [])
                all_results.extend(results)
        
        # Save hunt results to the database
        new_hunt = models.ThreatHunt(
            status="completed",
            query=str(top_indicators),
            results={"found_alerts": all_results},
            tenant_id=tenant_id,
            completed_at=datetime.now(timezone.utc)
        )
        db.add(new_hunt)
        db.commit()
        
        print(f"✅ Threat Hunt complete. Found {len(all_results)} potential stealthy threats.")
        return new_hunt

    except Exception as e:
        print(f"❌ Threat Hunt failed: {e}")
        return {"error": str(e)}