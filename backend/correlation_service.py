import os
import requests
import openai
import json
import logging
from functools import lru_cache
from sqlalchemy.orm import Session
from sqlalchemy import func
from . import models
from .ml.prediction import SeverityPredictor

logger = logging.getLogger(__name__)

MISP_URL = os.getenv("MISP_URL", "https://intel.quantum-ai.asia")
MISP_API_KEY = os.getenv("MISP_API_KEY")

predictor = SeverityPredictor()

# --- MISP Intel Fetcher ---
def get_intel_from_misp(indicator: str) -> dict:
    if not MISP_URL or not MISP_API_KEY:
        logger.warning("MISP_URL or MISP_API_KEY not configured. Skipping MISP enrichment.")
        return {"ip_reputation_score": 0}
    try:
        response = requests.post(
            f"{MISP_URL}/attributes/restSearch",
            headers={
                'Authorization': MISP_API_KEY,
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            json={"value": indicator},
            verify=False
        )
        response.raise_for_status()
        data = response.json().get("response", {}).get("Attribute", [])
        if data:
            logger.info(f"MISP Intel Found for indicator: {indicator}")
            return {"ip_reputation_score": 95}
        return {"ip_reputation_score": 0}
    except Exception as e:
        logger.error(f"MISP Error for indicator {indicator}: {e}")
        return {"ip_reputation_score": 0}

# --- CVE Identifier ---
@lru_cache(maxsize=500)
def find_cve_for_threat(threat_text: str) -> str | None:
    threat_text_lower = threat_text.lower()
    if "log4j" in threat_text_lower or "jndi" in threat_text_lower:
        return "CVE-2021-44228"
    if "sql injection" in threat_text_lower:
        return "CWE-89"
    if "xss" in threat_text_lower or "cross-site scripting" in threat_text_lower:
        return "CWE-79"

    try:
        response = requests.get(f"https://cve.circl.lu/api/search/{threat_text}", timeout=5)
        response.raise_for_status()
        data = response.json()
        for item in data.get("data", []):
            cve_id = item.get("id")
            if cve_id and cve_id.startswith("CVE-"):
                return cve_id
    except Exception as e:
        logger.warning(f"⚠️ Failed to retrieve CVE from CIRCL for '{threat_text}': {e}")

    return None

# --- CVSS Score Fetcher ---
def get_cvss_score(cve_id: str) -> float:
    if not cve_id:
        return 0.0

    NVD_API_KEY = os.getenv("NVD_API_KEY")
    try:
        # Updated to NVD API v2.0 endpoint
        url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
        headers = {
            "User-Agent": "QuantumAI-CVE-Fetcher/2.0"
        }
        
        # Parameters for the new API
        params = {
            "cveId": cve_id
        }
        
        # Add API key to headers (not URL) for v2.0
        if NVD_API_KEY:
            headers["apiKey"] = NVD_API_KEY
        else:
            logger.warning(f"⚠️ No NVD API key - rate limited to 5 requests per 30 seconds")

        response = requests.get(url, headers=headers, params=params, timeout=10)

        if response.status_code == 403:
            logger.error(f"❌ NVD API access denied for {cve_id}. Check API key validity.")
            return 0.0
        elif response.status_code == 429:
            logger.warning(f"⚠️ Rate limited by NVD API for {cve_id}")
            return 0.0
        elif response.status_code != 200:
            logger.warning(f"⚠️ Failed to fetch CVE {cve_id}: HTTP {response.status_code}")
            return 0.0

        data = response.json()
        
        # Parse the new v2.0 response format
        vulnerabilities = data.get("vulnerabilities", [])
        if not vulnerabilities:
            logger.info(f"No vulnerability data found for {cve_id}")
            return 0.0

        # Get the CVE data from the first vulnerability
        cve_data = vulnerabilities[0].get("cve", {})
        metrics = cve_data.get("metrics", {})
        
        # Try CVSS versions in order of preference: v3.1 > v3.0 > v2.0
        if "cvssMetricV31" in metrics and metrics["cvssMetricV31"]:
            cvss_data = metrics["cvssMetricV31"][0]["cvssData"]
            score = float(cvss_data["baseScore"])
            logger.info(f"Found CVSS v3.1 score {score} for {cve_id}")
            return score
        elif "cvssMetricV30" in metrics and metrics["cvssMetricV30"]:
            cvss_data = metrics["cvssMetricV30"][0]["cvssData"]
            score = float(cvss_data["baseScore"])
            logger.info(f"Found CVSS v3.0 score {score} for {cve_id}")
            return score
        elif "cvssMetricV2" in metrics and metrics["cvssMetricV2"]:
            cvss_data = metrics["cvssMetricV2"][0]["cvssData"]
            score = float(cvss_data["baseScore"])
            logger.info(f"Found CVSS v2.0 score {score} for {cve_id}")
            return score
        else:
            logger.info(f"No CVSS score available for {cve_id}")
            return 0.0

    except requests.exceptions.RequestException as e:
        logger.error(f"⚠️ Network error fetching CVSS score for {cve_id}: {e}")
        return 0.0
    except (KeyError, ValueError, TypeError) as e:
        logger.error(f"⚠️ Error parsing CVSS data for {cve_id}: {e}")
        return 0.0
    except Exception as e:
        logger.error(f"⚠️ Unexpected error fetching CVSS score for {cve_id}: {e}")
        return 0.0

# --- Criticality Score Calculator ---
def calculate_criticality_score(ip_score: int, cvss_score: float) -> float:
    ip_weight = 0.5
    cvss_weight = 0.5
    ip_norm = ip_score / 100.0
    cvss_norm = cvss_score / 10.0
    return round(ip_weight * ip_norm + cvss_weight * cvss_norm, 2)

# --- Correlation Engine ---
def correlate_and_enrich_threats(db: Session, tenant_id: int):
    common_threats = (
        db.query(models.ThreatLog.threat)
        .filter(models.ThreatLog.tenant_id == tenant_id)
        .group_by(models.ThreatLog.threat)
        .having(func.count(models.ThreatLog.threat) > 1)
        .limit(10).all()
    )
    for threat_tuple in common_threats:
        threat_desc = threat_tuple[0]
        existing = db.query(models.CorrelatedThreat).filter_by(title=f"Attack Pattern: {threat_desc}").first()
        if existing:
            continue

        cve_id = find_cve_for_threat(threat_desc)
        cvss_score = get_cvss_score(cve_id)

        associated_ips = (
            db.query(models.ThreatLog.ip)
            .filter(models.ThreatLog.threat == threat_desc, models.ThreatLog.tenant_id == tenant_id)
            .distinct().all()
        )

        highest_risk_score = 0
        chosen_ip = None
        for ip_tuple in associated_ips:
            ip = ip_tuple[0]
            intel = get_intel_from_misp(ip)
            score = intel.get("ip_reputation_score", 0)
            if score > highest_risk_score:
                highest_risk_score = score
                chosen_ip = ip

        criticality_score = calculate_criticality_score(highest_risk_score, cvss_score)
        logger.info(f"[AI INPUT] threat='{threat_desc}', ip_score={highest_risk_score}, cvss_score={cvss_score}, criticality_score={criticality_score}, cve_id={cve_id}")

        predicted_severity = predictor.predict(
            threat=threat_desc,
            source="correlation",
            ip_reputation_score=highest_risk_score,
            cve_id=cve_id,
            cvss_score=cvss_score,
            criticality_score=criticality_score
        )

        logger.info(f"[AI SEVERITY] Predicted severity for '{threat_desc}' = {predicted_severity}")

        new_correlated_threat = models.CorrelatedThreat(
            title=f"Attack Pattern: {threat_desc}",
            cve_id=cve_id,
            risk_score=highest_risk_score,
            summary=f"{len(associated_ips)} sources detected this activity.",
            tenant_id=tenant_id
        )
        db.add(new_correlated_threat)
    db.commit()

# --- Executive Summary ---
def generate_holistic_summary(db: Session, tenant_id: int) -> str:
    correlate_and_enrich_threats(db, tenant_id)
    critical_logs = db.query(models.ThreatLog).filter_by(severity='critical', tenant_id=tenant_id).limit(5).all()
    correlated_threats = db.query(models.CorrelatedThreat).filter_by(tenant_id=tenant_id).order_by(models.CorrelatedThreat.risk_score.desc()).limit(3).all()
    prompt = "You are a cybersecurity analyst. Based on the following data, provide a high-level executive summary for a non-technical manager.\n\n"
    prompt += "== Top Correlated Attack Patterns ==\n"
    for threat in correlated_threats:
        prompt += f"- {threat.title} (Risk Score: {threat.risk_score}, CVE: {threat.cve_id or 'N/A'})\n"
    prompt += "\n== Recent Critical Events ==\n"
    for log in critical_logs:
        prompt += f"- {log.threat} from {log.source} (IP: {log.ip})\n"
    openai.api_key = os.getenv("OPENAI_API_KEY")
    if not openai.api_key:
        return "OpenAI API key not configured. Cannot generate summary."
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Failed to generate AI summary: {e}"

# --- AI Remediation Plan ---
def generate_threat_remediation_plan(threat_log: models.ThreatLog) -> dict | None:
    openai.api_key = os.getenv("OPENAI_API_KEY")
    if not openai.api_key:
        logger.error("OpenAI API key not configured for remediation plan.")
        return None

    prompt = f"""
    You are a cybersecurity analyst providing a report on a threat.
    Details:
    - Threat: "{threat_log.threat}"
    - Source: "{threat_log.source}"
    - Severity: "{threat_log.severity}"
    - IP: "{threat_log.ip}"
    - IP Reputation Score: "{threat_log.ip_reputation_score}"
    - CVE: "{threat_log.cve_id or 'N/A'}"

    Return JSON with: "explanation", "impact", "mitigation".
    """

    try:
        response = openai.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.3,
        )
        recommendations = json.loads(response.choices[0].message.content)

        if isinstance(recommendations.get("mitigation"), str):
            recommendations["mitigation"] = [recommendations["mitigation"]]

        return recommendations
    except Exception as e:
        logger.error(f"Error generating remediation plan: {e}")
        return None

# --- AI MISP Summarizer ---
def get_and_summarize_misp_intel(indicator: str) -> str | None:
    if not MISP_URL or not MISP_API_KEY:
        logger.warning("MISP credentials not configured for summary.")
        return "Quantum Intel hub not configured."
    openai.api_key = os.getenv("OPENAI_API_KEY")
    if not openai.api_key:
        logger.warning("OpenAI key not configured for MISP summary.")
        return "AI summarizer not configured."
    try:
        response = requests.post(
            f"{MISP_URL}/attributes/restSearch",
            headers={'Authorization': MISP_API_KEY, 'Accept': 'application/json'},
            json={"value": indicator, "includeEventData": True},
            verify=False
        )
        response.raise_for_status()
        attributes = response.json().get("response", {}).get("Attribute", [])
        if not attributes:
            return "No intelligence found for this indicator."
        prompt = f"""
        You are a threat intel analyst. Summarize the following MISP data for '{indicator}'.
        Focus on what it's associated with (e.g., malware, actors), and its reputation.

        --- Raw MISP Data ---
        {json.dumps(attributes, indent=2)}
        """
        summary_response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=200
        )
        return summary_response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Failed to summarize MISP intel for {indicator}: {e}")
        return f"Error: {e}"