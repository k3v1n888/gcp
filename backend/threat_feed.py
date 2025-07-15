import requests
import os
from sqlalchemy.orm import Session
from . import models
from datetime import datetime, timezone
from fastapi import APIRouter # <-- 1. Import APIRouter

# --- 2. Create the router instance ---
router = APIRouter()

def fetch_and_save_threat_feed(db: Session):
    """
    Fetches the latest malicious IPs from the Maltiverse feed and saves them.
    """
    api_key = os.getenv("MALTIVERSE_API_KEY")
    if not api_key:
        print("Maltiverse API key not configured. Skipping feed.")
        return

    print("Fetching latest threat intelligence feed from Maltiverse...")
    try:
        response = requests.get(
            f"https://api.maltiverse.com/ip?sort=-modification_time&limit=20",
            headers={'Authorization': f'Bearer {api_key}'}
        )
        response.raise_for_status()
        
        threats = response.json()
        new_logs_count = 0

        for threat in threats:
            existing = db.query(models.ThreatLog).filter_by(ip=threat.get("ip_addr")).first()
            if existing:
                continue

            new_log = models.ThreatLog(
                ip=threat.get("ip_addr"),
                threat=f"Malicious IP detected: {threat.get('classification')}",
                source="Maltiverse Feed",
                severity="high",
                tenant_id=1,
                ip_reputation_score=threat.get("score", 80),
                cve_id=None,
                timestamp=datetime.now(timezone.utc)
            )
            db.add(new_log)
            new_logs_count += 1
        
        db.commit()
        print(f"✅ Successfully ingested {new_logs_count} new threats from Maltiverse.")

    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to fetch data from Maltiverse: {e}")

# --- 3. Add a simple test endpoint ---
@router.get("/api/threat_feed/status")
def get_feed_status():
    return {"status": "Threat feed service is running"}
