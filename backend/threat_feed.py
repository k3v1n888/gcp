import requests
import os
from sqlalchemy.orm import Session
from . import models
from datetime import datetime, timezone
from fastapi import APIRouter
import logging

router = APIRouter()
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

    # --- 1. Define the parameters for the search query ---
    # We will search for malicious IPs and get the most recent 20.
    params = {
        "query": "classification:malicious AND type:ip",
        "limit": 20,
        "sort": "modification_time_desc" # Sort by most recently modified
    }

    try:
        # --- 2. Use the correct '/search' endpoint with the defined params ---
        response = requests.get(
            "https://api.maltiverse.com/search",
            headers={'Authorization': f'Bearer {api_key}'},
            params=params # Pass the query parameters
        )
        response.raise_for_status()

        threats = response.json()
        new_logs_count = 0

        # The rest of your logic remains the same as it correctly processes the results
        for threat in threats:
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
                threat=f"Malicious IP from feed: {threat.get('classification', 'N/A')}",
                source="Maltiverse Feed",
                severity="high",
                tenant_id=1,
                ip_reputation_score=100,
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

@router.get("/api/threat_feed/status")
def get_feed_status():
    return {"status": "Threat feed service is running"}
