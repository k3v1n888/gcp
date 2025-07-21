# backend/wazuh_service.py
import requests
import os
from sqlalchemy.orm import Session
from . import models
from datetime import datetime, timezone, timedelta
import logging
import time

logger = logging.getLogger(__name__)

WAZUH_URL = os.getenv("WAZUH_API_URL", "https://xdr.quantum-ai.asia")
# --- THIS IS THE FIX: Hardcode the correct username to override any defaults ---
WAZUH_USER = "wazuh-wui" 
WAZUH_PASSWORD = os.getenv("WAZUH_API_PASSWORD")

def get_wazuh_jwt():
    """Authenticates with the Wazuh API, with retries."""
    print("--- WAZUH AUTH ATTEMPT ---")
    print(f"URL: {WAZUH_URL}")
    print(f"USER: {WAZUH_USER}")
    print(f"PASSWORD IS SET: {bool(WAZUH_PASSWORD)}")

    if not WAZUH_PASSWORD or not WAZUH_USER or not WAZUH_URL:
        print("--- WAZUH AUTH FAILED: Missing credentials or URL ---")
        return None
    
    auth_attempts = 3
    for attempt in range(auth_attempts):
        try:
            response = requests.post(
                f"{WAZUH_URL}/security/user/authenticate",
                auth=(WAZUH_USER, WAZUH_PASSWORD),
                verify=False
            )
            response.raise_for_status()
            logger.info("✅ Successfully authenticated with Wazuh API.")
            return response.json()['data']['token']
        except Exception as e:
            logger.error(f"Wazuh Auth Attempt {attempt + 1}/{auth_attempts} failed: {e}")
            if attempt < auth_attempts - 1:
                time.sleep(10)
    
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
                ip=agent_ip, threat=rule_desc, source="Quantum XDR",
                severity="critical", tenant_id=1, timestamp=datetime.now(timezone.utc)
            )
            db.add(new_log)
            new_logs_count += 1
        
        db.commit()
        logger.info(f"✅ Successfully ingested {new_logs_count} new alerts from Wazuh.")
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Failed to fetch alerts from Wazuh: {e}")