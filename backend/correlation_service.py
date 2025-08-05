# backend/correlation_service.py
import os
import requests
import openai
from sqlalchemy.orm import Session
from sqlalchemy import func
import json
from . import models
import logging

logger = logging.getLogger(__name__)

MISP_URL = os.getenv("MISP_URL", "https://intel.quantum-ai.asia")
MISP_API_KEY = os.getenv("MISP_API_KEY")

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

@lru_cache(maxsize=500)
def find_cve_for_threat(threat_text: str) -> str | None:
    """
    Attempts to find the most relevant CVE ID for a given threat description.
    First tries a live CIRCL search, then falls back to hardcoded rules.
    """
    if not threat_text:
        return None

    try:
        search_url = f"https://cve.circl.lu/api/search/{threat_text}"
        response = requests.get(search_url, timeout=5)
        response.raise_for_status()
        results = response.json()

        if isinstance(results, list) and results:
            for entry in results:
                cve_id = entry.get("id")
                if cve_id and cve_id.startswith("CVE"):
                    return cve_id
    except Exception as e:
        logger.warning(f"⚠️ Failed to retrieve CVE from CIRCL for '{threat_text}': {e}")

    # Fallback keyword mappings
    threat_text_lower = threat_text.lower()
    if "log4j" in threat_text_lower or "jndi" in threat_text_lower:
        return "CVE-2021-44228"
    if "sql injection" in threat_text_lower:
        return "CWE-89"
    if "xss" in threat_text_lower or "cross-site scripting" in threat_text_lower:
        return "CWE-79"
    if "cobalt strike" in threat_text_lower:
        return "CVE-2019-0708"
    if "powershell" in threat_text_lower:
        return "CVE-2021-31166"
    if "brute force" in threat_text_lower:
        return "CWE-307"
    if "ransomware" in threat_text_lower:
        return "CWE-501"

    return None

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
        associated_ips = (
            db.query(models.ThreatLog.ip)
            .filter(models.ThreatLog.threat == threat_desc, models.ThreatLog.tenant_id == tenant_id)
            .distinct().all()
        )
        highest_risk_score = 0
        for ip_tuple in associated_ips:
            intel = get_intel_from_misp(ip_tuple[0])
            score = intel.get("ip_reputation_score", 0)
            if score > highest_risk_score:
                highest_risk_score = score
        new_correlated_threat = models.CorrelatedThreat(
            title=f"Attack Pattern: {threat_desc}",
            cve_id=cve_id,
            risk_score=highest_risk_score,
            summary=f"{len(associated_ips)} sources detected this activity.",
            tenant_id=tenant_id
        )
        db.add(new_correlated_threat)
    db.commit()

def generate_holistic_summary(db: Session, tenant_id: int) -> str:
    correlate_and_enrich_threats(db, tenant_id)
    critical_logs = db.query(models.ThreatLog).filter_by(severity='critical', tenant_id=tenant_id).limit(5).all()
    correlated_threats = db.query(models.CorrelatedThreat).filter_by(tenant_id=tenant_id).order_by(models.CorrelatedThreat.risk_score.desc()).limit(3).all()
    prompt = "You are a cybersecurity analyst. Based on the following data, provide a brief, high-level executive summary of the current security landscape for a non-technical manager. Highlight the most pressing issue.\n\n"
    prompt += "== Top Correlated Attack Patterns ==\n"
    for threat in correlated_threats:
        prompt += f"- {threat.title} (Risk Score: {threat.risk_score}, CVE: {threat.cve_id or 'N/A'})\n"
    prompt += "\n== Recent Critical Severity Events ==\n"
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

def generate_threat_remediation_plan(threat_log: models.ThreatLog) -> dict | None:
    openai.api_key = os.getenv("OPENAI_API_KEY")
    if not openai.api_key:
        logger.error("OpenAI API key not configured for remediation plan.")
        return None
    prompt = f"""
    You are a cybersecurity analyst providing a detailed report on a specific threat event.
    The event details are:
    - Threat Description: "{threat_log.threat}"
    - Source: "{threat_log.source}"
    - Severity: "{threat_log.severity}"
    - Attacker IP: "{threat_log.ip}"
    - IP Reputation Score (from private MISP): "{threat_log.ip_reputation_score}"
    - Associated CVE: "{threat_log.cve_id or 'N/A'}"

    Based on these details, provide a structured JSON response with three keys: "explanation", "impact", and "mitigation".
    - "explanation": Briefly explain what this threat is in simple terms.
    - "impact": Describe the potential business or security impact if this threat is successful.
    - "mitigation": Provide a list of concrete, actionable steps to mitigate or remediate this threat.
    """
    try:
        response = openai.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.3,
        )
        recommendations = json.loads(response.choices[0].message.content)
        return recommendations
    except Exception as e:
        logger.error(f"Error generating remediation plan: {e}")
        return None

# --- NEW: Function to get a detailed AI summary from MISP ---
def get_and_summarize_misp_intel(indicator: str) -> str | None:
    """
    Fetches all related attributes for an indicator from MISP and uses an LLM
    to generate a concise summary.
    """
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
            return "No intelligence found for this indicator in the Quantum Intel hub."

        prompt = f"""
        You are a threat intelligence analyst. Summarize the following raw threat intelligence data from a MISP instance for the indicator '{indicator}'.
        Focus on what the indicator is, what it's associated with (e.g., malware families, threat actors), and its overall reputation.
        Provide a brief, human-readable paragraph.

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
        logger.error(f"Failed to get or summarize MISP intel for {indicator}: {e}")
        return f"An error occurred while fetching intelligence: {e}"