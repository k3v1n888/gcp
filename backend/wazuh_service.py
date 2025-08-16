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
import os
from sqlalchemy.orm import Session
from . import models
from datetime import datetime, timezone, timedelta
import logging
import time
import base64 # <-- 1. Import the base64 library

logger = logging.getLogger(__name__)

WAZUH_URL = os.getenv("WAZUH_API_URL", "https://xdr.quantum-ai.asia")
WAZUH_USER = "wazuh-wui" 
WAZUH_PASSWORD = os.getenv("WAZUH_API_PASSWORD")

def get_wazuh_jwt():
    """Authenticates with the Wazuh API using Basic Auth and retrieves a JWT token."""
    if not WAZUH_PASSWORD or not WAZUH_USER or not WAZUH_URL:
        logger.error("Wazuh credentials or URL not configured.")
        return None

    auth_string = f"{WAZUH_USER}:{WAZUH_PASSWORD}"
    encoded_auth = base64.b64encode(auth_string.encode('utf-8')).decode('utf-8')
    auth_header = f"Basic {encoded_auth}"

    headers = {
        'Content-Type': 'application/json',  # required
        'Authorization': auth_header
    }

    login_url = f"{WAZUH_URL}/security/user/authenticate"

    for attempt in range(3):
        try:
            response = requests.post(login_url, headers=headers, verify=False)
            logger.debug(f"Wazuh auth response: {response.status_code} - {response.text}")
            response.raise_for_status()
            token = response.json().get('data', {}).get('token')
            logger.info("✅ Successfully authenticated with Wazuh API.")
            return token
        except requests.exceptions.RequestException as e:
            logger.error(f"Wazuh Auth Attempt {attempt + 1}/3 failed: {e}")
            if attempt < 2:
                time.sleep(5)

    return None

def fetch_and_save_wazuh_alerts(db: Session):
    """Fetches new, high-severity alerts from the Wazuh API."""
    jwt_token = get_wazuh_jwt()
    if not jwt_token:
        logger.error("Could not get Wazuh JWT, skipping alert fetch.")
        return

    time_filter = (datetime.utcnow() - timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    
    logger.info("Fetching new alerts from Wazuh API...")
    try:
        response = requests.get(
            f"{WAZUH_URL}/alerts",
            params={'q': f'rule.level>=10;timestamp>={time_filter}', 'limit': 50},
            headers={'Authorization': f'Bearer {jwt_token}'},
            verify=False
        )
        response.raise_for_status()
        alerts = response.json()['data']['affected_items']
        new_logs_count = 0

        for alert in alerts:
            rule_desc = alert.get('rule', {}).get('description', 'Wazuh Alert')
            agent_ip = alert.get('agent', {}).get('ip', 'N/A')
            
            existing = db.query(models.ThreatLog).filter_by(threat=rule_desc, ip=agent_ip).first()
            if existing:
                continue

            new_log = models.ThreatLog(
                ip=agent_ip, threat=rule_desc, source="Sentient XDR",
                severity="critical", tenant_id=1, timestamp=datetime.now(timezone.utc)
            )
            db.add(new_log)
            new_logs_count += 1
        
        db.commit()
        logger.info(f"✅ Successfully ingested {new_logs_count} new alerts from Wazuh.")
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Failed to fetch alerts from Wazuh: {e}")