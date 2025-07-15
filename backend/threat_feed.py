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

    params = {
        "query": "classification:malicious AND type:ip",
        "limit": 20,
        "sort": "modification_time_desc"
    }

    try:
        response = requests.get(
            "https://api.maltiverse.com/search",
            headers={'Authorization': f'Bearer {api_key}'},
            params=params
        )
        response.raise_for_status()

        threats = response.json()

        # --- FIX: Validate the API response before processing ---
        # If the response is not a list, it's probably an error object from the API.
        if not isinstance(threats, list):
            error_message = threats.get("message", "API did not return a list of threats.")
            logger.error(f"❌ Maltiverse Error: {error_message}")
            return # Stop the function execution

        new_logs_count = 0

        # Now we can safely assume 'threats' is a list of dictionaries
        for threat in threats:
            if not isinstance(threat, dict) or threat.get("type") != "ip":
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

        if new_logs_count > 0:
            logger.info(f"✅ Successfully ingested {new_logs_count} new threats from Maltiverse.")
        else:
            logger.info("ℹ️ No new threats to ingest from Maltiverse.")


    except requests.exceptions.HTTPError as http_err:
        logger.error(f"❌ Maltiverse HTTP Error: {http_err} - Response: {http_err.response.text}")
    except Exception as e:
        logger.error(f"❌ An unexpected error occurred during Maltiverse feed ingestion: {e}")

@router.get("/api/threat_feed/status")
def get_feed_status():
    return {"status": "Threat feed service is running"}

