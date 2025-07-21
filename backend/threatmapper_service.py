# backend/threatmapper_service.py
import requests
import os
from sqlalchemy.orm import Session
from . import models
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

THREATMAPPER_URL = os.getenv("THREATMAPPER_URL", "https://synapse.quantum-ai.asia")
THREATMAPPER_API_KEY = os.getenv("THREATMAPPER_API_KEY")

def get_threatmapper_token():
    """Authenticates with the ThreatMapper API to get a JWT token."""
    if not THREATMAPPER_URL or not THREATMAPPER_API_KEY:
        return None
    try:
        # --- THIS IS THE FIX: Use the correct URL path and 'api_token' field ---
        response = requests.post(
            f"{THREATMAPPER_URL}/deepfence/auth/token",
            headers={'Content-Type': 'application/json'},
            json={"api_token": THREATMAPPER_API_KEY}, 
            verify=False
        )
        response.raise_for_status()
        return response.json().get("access_token")
    except Exception as e:
        logger.error(f"ThreatMapper Auth Error: {e}")
        return None

def fetch_and_save_threatmapper_vulns(db: Session):
    """Fetches new, critical vulnerabilities from the ThreatMapper API."""
    token = get_threatmapper_token()
    if not token:
        logger.error("Could not get ThreatMapper token, skipping vulnerability fetch.")
        return

    logger.info("Fetching new vulnerabilities from ThreatMapper API...")
    try:
        response = requests.post(
            f"{THREATMAPPER_URL}/deepfence/v2/vulnerabilities",
            headers={'Authorization': f'Bearer {token}'},
            json={"cve_severity": ["critical", "high"], "size": 20}
        )
        response.raise_for_status()
        
        vulnerabilities = response.json().get("data", [])
        new_logs_count = 0

        for vuln in vulnerabilities:
            threat_desc = f"Vulnerability Found: {vuln.get('cve_id')} in {vuln.get('cve_caused_by_package')}"
            
            existing = db.query(models.ThreatLog).filter_by(threat=threat_desc).first()
            if existing:
                continue

            new_log = models.ThreatLog(
                ip=vuln.get("host_name", "N/A"),
                threat=threat_desc,
                source="Quantum Pathfinder",
                severity=vuln.get("cve_severity", "high"),
                tenant_id=1,
                cve_id=vuln.get("cve_id"),
                timestamp=datetime.now(timezone.utc)
            )
            db.add(new_log)
            new_logs_count += 1
        
        db.commit()
        logger.info(f"✅ Successfully ingested {new_logs_count} new vulnerabilities from ThreatMapper.")
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Failed to fetch vulnerabilities from ThreatMapper: {e}")