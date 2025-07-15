import requests
import os
from sqlalchemy.orm import Session
from . import models
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

def fetch_and_save_threat_feed(db: Session):
    """
    Fetches the latest malicious IPs from the Maltiverse feed and saves them.
    """
    api_key = os.getenv("MALTIVERSE_API_KEY")
    if not api_key:
        logger.error("Maltiverse Error: MALTIVERSE_API_KEY environment variable not set.")
        return

    logger.info("Fetching latest threat intelligence feed from Maltiverse...")
    try:
        # --- THIS IS THE CORRECTED MALTIVERSE URL ---
        response = requests.get(
            "https://api.maltiverse.com/collection/popular/iterator?limit=20",
            headers={'Authorization': f'Bearer {api_key}'}
        )
        response.raise_for_status()
        
        threats = response.json()
        new_logs_count = 0

        for threat in threats:
            # The API returns different types of indicators, we only want IPs.
            if threat.get("type") != "ip":
                continue

            ip_address = threat.get("ip_addr")
            if not ip_address:
                continue

            existing = db.query(models.ThreatLog).filter_by(ip=ip_address).first()
            if existing:
                continue

            new_log = models.ThreatLog(
                ip=ip_address,
                threat=f"Malicious IP from feed: {threat.get('blacklist_class', 'N/A')}",
                source="Maltiverse Feed",
                severity="high",
                tenant_id=1,
                ip_reputation_score=100, # Maltiverse results are confirmed malicious
                cve_id=None,
                timestamp=datetime.now(timezone.utc)
            )
            db.add(new_log)
            new_logs_count += 1
        
        db.commit()
        logger.info(f"✅ Successfully ingested {new_logs_count} new threats from Maltiverse.")

    except requests.exceptions.HTTPError as http_err:
        logger.error(f"❌ Maltiverse HTTP Error: {http_err} - Response: {http_err.response.text}")
    except Exception as e:
        logger.error(f"❌ An unexpected error occurred during Maltiverse feed ingestion: {e}")
