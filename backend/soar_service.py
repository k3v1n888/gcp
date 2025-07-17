# backend/soar_service.py
import os
import google.cloud.compute_v1 as compute_v1
import logging
from sqlalchemy.orm import Session
from . import models

logger = logging.getLogger(__name__)

def block_ip_with_cloud_armor(db: Session, threat: models.ThreatLog):
    """Adds a DENY rule for a specific IP to a Cloud Armor security policy."""
    PROJECT_ID = os.getenv("GCP_PROJECT_ID")
    POLICY_NAME = os.getenv("CLOUD_ARMOR_POLICY_NAME")
    
    if not PROJECT_ID or not POLICY_NAME:
        logger.error("GCP_PROJECT_ID or CLOUD_ARMOR_POLICY_NAME not set for SOAR.")
        return

    try:
        client = compute_v1.SecurityPoliciesClient()
        policy = client.get(project=PROJECT_ID, security_policy=POLICY_NAME)
        
        highest_priority = max((rule.priority for rule in policy.rules), default=999)
        new_priority = highest_priority + 1
        
        new_rule = compute_v1.SecurityPolicyRule(
            action="deny(403)",
            priority=new_priority,
            description=f"Automated block of malicious IP: {threat.ip}",
            match=compute_v1.SecurityPolicyRuleMatcher(
                versioned_expr=compute_v1.SecurityPolicyRuleMatcher.VersionedExpr.SRC_IPS_V1,
                config=compute_v1.SecurityPolicyRuleMatcherConfig(src_ip_ranges=[f"{threat.ip}/32"])
            )
        )
        
        client.add_rule(
            project=PROJECT_ID,
            security_policy=POLICY_NAME,
            security_policy_rule_resource=new_rule
        )
        log_entry = models.AutomationLog(
            threat_id=threat.id,
            action_type="IP_BLOCK_SUCCESS",
            details=f"Successfully added IP {threat.ip} to Cloud Armor policy {POLICY_NAME}."
        )
        db.add(log_entry)
        db.commit()
        logger.info(f"✅ SOAR: Successfully logged blocking of IP {threat.ip}.")
    except Exception as e:
        log_entry = models.AutomationLog(
            threat_id=threat.id,
            action_type="IP_BLOCK_FAILURE",
            details=f"Failed to block IP {threat.ip}. Reason: {e}"
        )
        db.add(log_entry)
        db.commit()
        logger.error(f"❌ SOAR Error: Failed to block IP {threat.ip}. Reason: {e}")
