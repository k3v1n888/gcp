from fastapi import APIRouter
import httpx
import os
from backend.models import SessionLocal, ThreatLog

router = APIRouter()

OTX_API_KEY = os.getenv("OTX_API_KEY")
ABUSEIPDB_API_KEY = os.getenv("ABUSEIPDB_API_KEY")

@router.get("/api/feeds/otx")
def fetch_otx():
    if not OTX_API_KEY:
        return {"error": "OTX API key not configured."}
    headers = {"X-OTX-API-KEY": OTX_API_KEY}
    url = "https://otx.alienvault.com/api/v1/indicators/IPv4/general"
    resp = httpx.get(url, headers=headers)
    db = SessionLocal()
    results = []
    if resp.status_code == 200:
        data = resp.json()
        for entry in data.get("pulse_info", {}).get("pulses", []):
            ip = entry.get("indicator")
            threat = entry.get("name", "OTX Threat")
            if ip:
                log = ThreatLog(ip=ip, threat=threat, source="OTX")
                db.add(log)
                results.append({"ip": ip, "threat": threat})
        db.commit()
    db.close()
    return {"fetched": len(results), "entries": results}

@router.get("/api/feeds/abuseipdb")
def fetch_abuseipdb():
    if not ABUSEIPDB_API_KEY:
        return {"error": "AbuseIPDB API key not configured."}
    headers = {
        "Key": ABUSEIPDB_API_KEY,
        "Accept": "application/json"
    }
    url = "https://api.abuseipdb.com/api/v2/blacklist?confidenceMinimum=90"
    resp = httpx.get(url, headers=headers)
    db = SessionLocal()
    results = []
    if resp.status_code == 200:
        data = resp.json().get("data", [])
        for entry in data:
            ip = entry.get("ipAddress")
            threat = f"Abuse Score: {entry.get('abuseConfidenceScore')}"
            if ip:
                log = ThreatLog(ip=ip, threat=threat, source="AbuseIPDB")
                db.add(log)
                results.append({"ip": ip, "threat": threat})
        db.commit()
    db.close()
    return {"fetched": len(results), "entries": results}