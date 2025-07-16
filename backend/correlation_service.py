import os
import requests
import openai
from sqlalchemy.orm import Session
from sqlalchemy import func
import json
from . import models
import logging

logger = logging.getLogger(__name__)

def get_ip_reputation(ip: str) -> int:
    """Gets the abuse confidence score for an IP from AbuseIPDB."""
    api_key = os.getenv("ABUSEIPDB_API_KEY")
    if not api_key:
        return 0
    response = requests.get(
        "https://api.abuseipdb.com/api/v2/check",
        params={'ipAddress': ip, 'maxAgeInDays': '90'},
        headers={'Key': api_key, 'Accept': 'application/json'}
    )
    if response.status_code == 200:
        return response.json()['data'].get('abuseConfidenceScore', 0)
    return 0

def find_cve_for_threat(threat_text: str) -> str | None:
    """A simple keyword-to-CVE mapping."""
    threat_text_lower = threat_text.lower()
    if "log4j" in threat_text_lower or "jndi" in threat_text_lower:
        return "CVE-2021-44228"
    if "sql injection" in threat_text_lower:
        return "CWE-89"
    if "xss" in threat_text_lower or "cross-site scripting" in threat_text_lower:
        return "CWE-79"
    return None

def correlate_and_enrich_threats(db: Session, tenant_id: int):
    """Groups threats by description, enriches them, and saves them."""
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
            score = get_ip_reputation(ip_tuple[0])
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
    """Gathers data and uses an LLM to generate an executive summary."""
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

# --- NEW: Function to generate a detailed threat analysis ---
def generate_threat_remediation_plan(threat_log: models.ThreatLog) -> dict | None:
    """Generates an analysis and mitigation plan for a specific threat."""
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
    - IP Reputation Score (AbuseIPDB): "{threat_log.ip_reputation_score}"
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
