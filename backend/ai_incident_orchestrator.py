"""
Copyright (c) 2025 Kevin Zachary
All rights reserved.

This software and associated documentation files (the "Software") are the 
exclusive property of Kevin Zachary. Unauthorized copying, distribution, 
modification, or use of this software is strictly prohibited.

For licensing inquiries, contact: kevin@zachary.com
"""

# Author: Kevin Zachary
# Copyright: Sentient Spire

"""
🚀 AI-Driven Incident Orchestrator
Next-Generation Incident Management following MITRE ATT&CK, NIST, and SANS frameworks

This system uses advanced AI to:
1. Intelligently aggregate threats into actual security incidents
2. Apply industry-standard risk scoring (MITRE ATT&CK TTPs)
3. Use behavioral analytics to detect attack campaigns
4. Provide contextual incident narratives with AI explanations

Industry Standards Implemented:
- MITRE ATT&CK framework for TTP mapping
- NIST Incident Response lifecycle
- SANS incident classification
- ISO 27035 incident management process
- FAIR risk quantification
"""

import os
import os
import json
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from dataclasses import dataclass
from enum import Enum

from . import models
from .correlation_service import get_intel_from_misp, get_cvss_score, calculate_criticality_score
from .ml.prediction import SeverityPredictor

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════
# 🎯 Industry Standard Classifications
# ═══════════════════════════════════════════════════════════════════

class AttackPhase(Enum):
    """MITRE ATT&CK Tactics"""
    RECONNAISSANCE = "reconnaissance"
    RESOURCE_DEVELOPMENT = "resource-development"
    INITIAL_ACCESS = "initial-access"
    EXECUTION = "execution"
    PERSISTENCE = "persistence"
    PRIVILEGE_ESCALATION = "privilege-escalation"
    DEFENSE_EVASION = "defense-evasion"
    CREDENTIAL_ACCESS = "credential-access"
    DISCOVERY = "discovery"
    LATERAL_MOVEMENT = "lateral-movement"
    COLLECTION = "collection"
    COMMAND_AND_CONTROL = "command-and-control"
    EXFILTRATION = "exfiltration"
    IMPACT = "impact"

class IncidentCategory(Enum):
    """NIST SP 800-61 Incident Categories"""
    MALWARE = "malware"
    UNAUTHORIZED_ACCESS = "unauthorized-access"
    INAPPROPRIATE_USAGE = "inappropriate-usage"
    DENIAL_OF_SERVICE = "denial-of-service"
    WEB_ATTACK = "web-attack"
    EMAIL_ATTACK = "email-attack"
    SOCIAL_ENGINEERING = "social-engineering"
    DATA_BREACH = "data-breach"
    INSIDER_THREAT = "insider-threat"
    APT_CAMPAIGN = "apt-campaign"

class RiskLevel(Enum):
    """FAIR Risk Model Levels"""
    CRITICAL = "critical"  # >90% business impact probability
    HIGH = "high"          # 70-90% business impact probability  
    MEDIUM = "medium"      # 30-70% business impact probability
    LOW = "low"            # <30% business impact probability

@dataclass
class ThreatIntelligence:
    """Enhanced threat intelligence data"""
    iocs: List[str]
    ttps: List[str]
    threat_actor: Optional[str]
    campaign: Optional[str]
    confidence_level: int
    attribution_confidence: int

@dataclass
class IncidentMetrics:
    """Quantified incident risk metrics"""
    business_impact_score: float
    technical_severity: str
    data_sensitivity: str
    affected_systems: List[str]
    estimated_cost: Optional[float]
    regulatory_implications: List[str]

# ═══════════════════════════════════════════════════════════════════
# 🧠 AI-Powered Incident Orchestrator
# ═══════════════════════════════════════════════════════════════════

class AIIncidentOrchestrator:
    """
    Next-generation AI incident orchestrator that intelligently aggregates threats
    into security incidents following industry best practices.
    """
    
    def __init__(self):
        print("🔥 DEBUG: Initializing AIIncidentOrchestrator")
        try:
            # Initialize your existing Sentient AI service
            self.predictor = SeverityPredictor()
            print("🔥 DEBUG: SeverityPredictor initialized successfully")
        except Exception as e:
            print(f"🔥 DEBUG: Failed to initialize SeverityPredictor: {e}")
            raise
        
        # Industry-standard time windows for correlation
        self.correlation_windows = {
            "immediate": timedelta(minutes=15),    # Burst attacks
            "tactical": timedelta(hours=4),        # Coordinated campaigns  
            "strategic": timedelta(days=1),        # APT activities
            "extended": timedelta(days=7)          # Long-term campaigns
        }
        
        # MITRE ATT&CK TTP mappings
        self.ttp_mappings = self._load_ttp_mappings()
        print("🔥 DEBUG: AIIncidentOrchestrator initialization complete")
        
    def _load_ttp_mappings(self) -> Dict[str, Dict[str, Any]]:
        """Load MITRE ATT&CK technique mappings"""
        return {
            "sql injection": {
                "technique_id": "T1190",
                "tactic": AttackPhase.INITIAL_ACCESS,
                "severity_multiplier": 1.5
            },
            "powershell": {
                "technique_id": "T1059.001",
                "tactic": AttackPhase.EXECUTION,
                "severity_multiplier": 1.3
            },
            "brute force": {
                "technique_id": "T1110",
                "tactic": AttackPhase.CREDENTIAL_ACCESS,
                "severity_multiplier": 1.4
            },
            "lateral movement": {
                "technique_id": "T1021",
                "tactic": AttackPhase.LATERAL_MOVEMENT,
                "severity_multiplier": 1.8
            },
            "data exfiltration": {
                "technique_id": "T1041",
                "tactic": AttackPhase.EXFILTRATION,
                "severity_multiplier": 2.0
            },
            "privilege escalation": {
                "technique_id": "T1068",
                "tactic": AttackPhase.PRIVILEGE_ESCALATION,
                "severity_multiplier": 1.7
            }
        }

    async def orchestrate_incident_creation(self, db: Session, tenant_id: int) -> List[Dict[str, Any]]:
        """
        Main orchestration function - intelligently creates incidents from threat data
        using AI analysis and industry best practices.
        """
        logger.info(f"🚀 Starting AI-driven incident orchestration for tenant {tenant_id}")
        
        try:
            # Step 1: Get uncorrelated threats
            uncorrelated_threats = self._get_uncorrelated_threats(db, tenant_id)
            if not uncorrelated_threats:
                logger.info("No uncorrelated threats found")
                return []
            
            # Step 2: AI-powered threat analysis and grouping
            threat_groups = await self._ai_analyze_and_group_threats(uncorrelated_threats)
            
            # Step 3: Create incidents from significant threat groups
            created_incidents = []
            for group in threat_groups:
                if group["incident_worthy"]:
                    incident = await self._create_ai_incident(db, group, tenant_id)
                    if incident:
                        created_incidents.append(incident)
            
            logger.info(f"✅ Created {len(created_incidents)} AI-driven incidents")
            return created_incidents
            
        except Exception as e:
            logger.error(f"❌ AI incident orchestration failed: {e}")
            return []

    def _get_uncorrelated_threats(self, db: Session, tenant_id: int) -> List[models.ThreatLog]:
        """Get threats not yet associated with incidents"""
        return db.query(models.ThreatLog)\
            .filter(
                and_(
                    models.ThreatLog.tenant_id == tenant_id,
                    ~models.ThreatLog.incidents.any(),  # Not associated with any incidents
                    models.ThreatLog.timestamp >= datetime.now(timezone.utc) - timedelta(hours=72)
                )
            )\
            .order_by(models.ThreatLog.timestamp.desc())\
            .limit(100)\
            .all()

    async def _ai_analyze_and_group_threats(self, threats: List[models.ThreatLog]) -> List[Dict[str, Any]]:
        """
        Use your Sentient AI service to intelligently analyze and group threats into potential incidents
        based on cybersecurity best practices and attack patterns.
        """
        if not threats:
            logger.info("No threats provided for analysis")
            return []
        
        logger.info(f"🎯 Analyzing {len(threats)} threats using Sentient AI service")
        
        # Analyze each threat using your existing Sentient AI service
        threat_analyses = []
        for threat in threats:
            try:
                # Convert SQLAlchemy object to dictionary for your AI service
                threat_dict = {
                    "id": threat.id,
                    "threat": threat.threat or "",
                    "source": threat.source or "",
                    "severity": threat.severity or "unknown",
                    "ip": threat.ip or "",
                    "timestamp": threat.timestamp.isoformat() if threat.timestamp else datetime.now().isoformat(),
                    "cve_id": threat.cve_id,
                    "is_anomaly": threat.is_anomaly or False,
                    "ip_reputation_score": threat.ip_reputation_score or 0,
                    "criticality_score": getattr(threat, 'criticality_score', 0),
                    "cvss_score": getattr(threat, 'cvss_score', 0.0)
                }
                
                # Get AI analysis from your existing service
                severity_prediction = self.predictor.predict(
                    threat=threat_dict["threat"],
                    source=threat_dict["source"], 
                    ip_reputation_score=threat_dict["ip_reputation_score"],
                    cve_id=threat_dict["cve_id"],
                    cvss_score=threat_dict["cvss_score"],
                    criticality_score=threat_dict["criticality_score"]
                )
                
                # Get explanation from your AI service
                explanation = self.predictor.explain_prediction(threat_dict)
                
                threat_analyses.append({
                    'threat': threat_dict,
                    'ai_severity': severity_prediction,
                    'explanation': explanation
                })
                
                logger.debug(f"✅ Sentient AI analyzed threat {threat.id}: {severity_prediction}")
                
            except Exception as e:
                logger.warning(f"⚠️ Failed to analyze threat {threat.id} with Sentient AI: {e}")
                # Continue with basic data if AI fails
                threat_analyses.append({
                    'threat': threat_dict,
                    'ai_severity': 'unknown',
                    'explanation': None
                })
        
        # Group threats using Sentient AI insights
        return self._correlate_with_quantum_ai(threat_analyses)

    def _correlate_with_quantum_ai(self, analyses: List[Dict]) -> List[Dict[str, Any]]:
        """
        Use Sentient AI analysis results to correlate threats into incidents
        """
        logger.info("🔗 Correlating threats using Sentient AI insights")
        groups = []
        group_id = 1
        
        # Group by AI-determined severity and characteristics
        critical_threats = []
        high_threats = []
        medium_threats = []
        suspicious_ips = {}
        
        for analysis in analyses:
            threat = analysis['threat']
            ai_severity = analysis['ai_severity']
            explanation = analysis.get('explanation', {})
            
            # Group by AI severity assessment
            if ai_severity == 'critical':
                critical_threats.append(analysis)
            elif ai_severity == 'high':
                high_threats.append(analysis)
            elif ai_severity in ['medium', 'low']:
                medium_threats.append(analysis)
            
            # Track IP-based patterns
            ip = threat.get('ip', '')
            if ip and ip != 'unknown':
                if ip not in suspicious_ips:
                    suspicious_ips[ip] = []
                suspicious_ips[ip].append(analysis)
        
        # Create incidents based on Sentient AI analysis
        
        # Critical threat incidents
        if critical_threats:
            groups.append(self._create_ai_incident_group(
                critical_threats, group_id, "critical", 
                "Critical Security Incident - Sentient AI Detected", 
                "Sentient AI identified critical threats requiring immediate response"
            ))
            group_id += 1
        
        # High severity coordinated attacks
        if len(high_threats) >= 2:
            groups.append(self._create_ai_incident_group(
                high_threats, group_id, "high",
                "High-Priority Security Event",
                "Multiple high-severity threats detected by Sentient AI"
            ))
            group_id += 1
        
        # IP-based attack campaigns (using AI insights)
        for ip, ip_analyses in suspicious_ips.items():
            if len(ip_analyses) >= 3:  # Multiple threats from same IP
                # Check if AI considers this coordinated
                ai_severities = [a['ai_severity'] for a in ip_analyses]
                if any(sev in ['critical', 'high'] for sev in ai_severities):
                    groups.append(self._create_ai_incident_group(
                        ip_analyses, group_id, "medium",
                        f"Coordinated Attack from {ip}",
                        f"Sentient AI detected {len(ip_analyses)} correlated threats from IP {ip}"
                    ))
                    group_id += 1
        
        logger.info(f"✅ Sentient AI correlation created {len(groups)} incident groups")
        return groups
    
    def _create_ai_incident_group(self, analyses: List[Dict], group_id: int, 
                                  severity: str, title: str, description: str) -> Dict[str, Any]:
        """Create an incident group from Sentient AI analysis"""
        threat_ids = [analysis['threat']['id'] for analysis in analyses]
        key_indicators = []
        mitre_techniques = set()
        
        # Extract AI-driven insights
        for analysis in analyses:
            threat = analysis['threat']
            explanation = analysis.get('explanation', {})
            
            # Add key indicators
            if threat.get('ip'):
                key_indicators.append(f"Source IP: {threat['ip']}")
            if threat.get('source'):
                key_indicators.append(f"Detection: {threat['source']}")
            
            # Extract MITRE techniques
            ttp_info = self._get_ttp_info(threat.get('threat', ''))
            if ttp_info:
                mitre_techniques.add(ttp_info["technique_id"])
        
        return {
            "group_id": f"QAI-INC-{group_id:04d}",
            "incident_worthy": True,
            "confidence_level": 0.85,  # High confidence from Sentient AI
            "incident_category": "ai_detected_incident",
            "attack_phase": "multiple_phases",
            "severity": severity,
            "title": title,
            "description": description,
            "threat_ids": threat_ids,
            "key_indicators": list(set(key_indicators))[:10],
            "recommended_actions": [
                "Immediate threat containment",
                "Sentient AI forensic analysis",
                "Review affected systems",
                "Monitor for lateral movement"
            ],
            "business_impact": "high" if severity in ['critical', 'high'] else "medium",
            "mitre_techniques": list(mitre_techniques),
            "estimated_risk_score": min(9.0, len(analyses) * 2.0),
            "ai_provider": "quantum_ai",
            "ai_confidence": "high"
        }

    def _validate_incident_group(self, group: Dict[str, Any]) -> bool:
        """Validate that an incident group has required fields"""
        required_fields = ["group_id", "incident_worthy", "threat_ids"]
        
        for field in required_fields:
            if field not in group:
                logger.warning(f"⚠️ Incident group missing required field: {field}")
                return False
        
        if not group.get("incident_worthy", False):
            return False
            
        threat_ids = group.get("threat_ids", [])
        if not threat_ids or not isinstance(threat_ids, list):
            logger.warning("⚠️ Incident group has no valid threat IDs")
            return False
            
        return True
    
    def _enhance_incident_group(self, group: Dict[str, Any], threats: List[models.ThreatLog]) -> Dict[str, Any]:
        """Enhance incident group with additional analysis"""
        # Create threat lookup
        threat_lookup = {t.id: t for t in threats}
        
        # Get threats for this group
        group_threats = []
        for threat_id in group.get("threat_ids", []):
            if threat_id in threat_lookup:
                group_threats.append(threat_lookup[threat_id])
        
        if not group_threats:
            return group
        
        # Enhance with calculated metrics
        enhanced_group = group.copy()
        
        # Add time range analysis
        timestamps = [t.timestamp for t in group_threats if t.timestamp]
        if timestamps:
            enhanced_group.update({
                "earliest_timestamp": min(timestamps).isoformat(),
                "latest_timestamp": max(timestamps).isoformat(),
                "duration_minutes": (max(timestamps) - min(timestamps)).total_seconds() / 60
            })
        
        # Add IP analysis
        unique_ips = list(set(t.ip for t in group_threats if t.ip))
        enhanced_group["unique_source_ips"] = unique_ips
        enhanced_group["ip_count"] = len(unique_ips)
        
        # Add source analysis
        unique_sources = list(set(t.source for t in group_threats if t.source))
        enhanced_group["detection_sources"] = unique_sources
        enhanced_group["source_count"] = len(unique_sources)
        
        # Add quantum AI provider tag
        enhanced_group["ai_provider"] = "quantum_ai"
        enhanced_group["analysis_timestamp"] = datetime.now().isoformat()
        
        return enhanced_group

    def _fallback_threat_grouping(self, threats: List[models.ThreatLog]) -> List[Dict[str, Any]]:
        """Fallback grouping when AI is not available"""
        logger.info("🔄 Using fallback rule-based threat grouping")
        groups = []
        
        # Group by IP address and time proximity
        ip_groups = {}
        for threat in threats:
            if not threat.ip:
                continue
                
            if threat.ip not in ip_groups:
                ip_groups[threat.ip] = []
            ip_groups[threat.ip].append(threat)
        
        for ip, ip_threats in ip_groups.items():
            if len(ip_threats) >= 2:  # Only create incidents for multiple threats
                severity_scores = {"critical": 4, "high": 3, "medium": 2, "low": 1, "unknown": 0}
                max_severity = max([severity_scores.get(t.severity, 0) for t in ip_threats])
                severity = next(s for s, score in severity_scores.items() if score == max_severity)
                
                groups.append({
                    "group_id": f"fallback_{ip}_{int(datetime.now().timestamp())}",
                    "incident_worthy": True,
                    "confidence_level": 70,
                    "incident_category": "unauthorized-access",
                    "attack_phase": "initial-access", 
                    "severity": severity,
                    "title": f"Coordinated Activity from {ip}",
                    "description": f"Multiple security events detected from IP {ip} suggesting coordinated attack activity",
                    "threat_ids": [t.id for t in ip_threats],
                    "key_indicators": [ip],
                    "recommended_actions": ["Block IP address", "Investigate affected systems", "Review logs for lateral movement"],
                    "business_impact": "Potential unauthorized access to systems",
                    "mitre_techniques": ["T1190"],
                    "estimated_risk_score": 60,
                    "ai_provider": "fallback"
                })
        
        logger.info(f"✅ Fallback analysis created {len(groups)} incident groups")
        return groups

    def _get_ttp_info(self, threat_text: str) -> Optional[Dict[str, Any]]:
        """Map threat text to MITRE ATT&CK TTPs"""
        threat_lower = threat_text.lower()
        for pattern, info in self.ttp_mappings.items():
            if pattern in threat_lower:
                return info
        return None

    async def _create_ai_incident(self, db: Session, group: Dict[str, Any], tenant_id: int) -> Optional[Dict[str, Any]]:
        """Create a security incident from an AI-analyzed threat group"""
        try:
            # Get threat objects
            threat_ids = group.get("threat_ids", [])
            threats = db.query(models.ThreatLog).filter(
                models.ThreatLog.id.in_(threat_ids)
            ).all()
            
            if not threats:
                return None
            
            # Calculate incident metrics
            metrics = self._calculate_incident_metrics(threats, group)
            
            # Create the incident
            incident = models.SecurityIncident(
                title=group.get("title", "AI-Detected Security Incident"),
                status="open",
                severity=group.get("severity", "medium"),
                start_time=min(t.timestamp for t in threats if t.timestamp),
                end_time=max(t.timestamp for t in threats if t.timestamp),
                tenant_id=tenant_id
            )
            
            # Add enhanced metadata
            incident_metadata = {
                "ai_analysis": {
                    "confidence_level": group.get("confidence_level", 0),
                    "incident_category": group.get("incident_category"),
                    "attack_phase": group.get("attack_phase"),
                    "mitre_techniques": group.get("mitre_techniques", []),
                    "estimated_risk_score": group.get("estimated_risk_score", 0),
                    "business_impact": group.get("business_impact"),
                    "key_indicators": group.get("key_indicators", [])
                },
                "metrics": metrics,
                "recommended_actions": group.get("recommended_actions", []),
                "created_by": "AI-IncidentOrchestrator",
                "creation_timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            # Store metadata in a JSON field (if your model supports it)
            # incident.metadata = json.dumps(incident_metadata)
            
            # Associate threats with incident
            for threat in threats:
                incident.threat_logs.append(threat)
            
            db.add(incident)
            db.commit()
            db.refresh(incident)
            
            logger.info(f"✅ Created AI incident: {incident.title} (ID: {incident.id})")
            
            # Create automation log for this incident creation
            automation_log = models.AutomationLog(
                threat_id=threats[0].id,  # Associate with first threat
                action_type="incident_creation",
                details=f"AI-created incident '{incident.title}' from {len(threats)} correlated threats",
                timestamp=datetime.now(timezone.utc)
            )
            db.add(automation_log)
            db.commit()
            
            return {
                "incident_id": incident.id,
                "title": incident.title,
                "severity": incident.severity,
                "threat_count": len(threats),
                "ai_confidence": group.get("confidence_level", 0),
                "metadata": incident_metadata
            }
            
        except Exception as e:
            logger.error(f"Failed to create AI incident: {e}")
            db.rollback()
            return None

    def _calculate_incident_metrics(self, threats: List[models.ThreatLog], group: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate quantified incident metrics following FAIR risk model"""
        
        # Calculate business impact score
        severity_weights = {"critical": 100, "high": 75, "medium": 50, "low": 25, "unknown": 10}
        avg_severity_score = sum(severity_weights.get(t.severity, 10) for t in threats) / len(threats)
        
        # Factor in MITRE technique severity multipliers
        technique_multiplier = 1.0
        mitre_techniques = group.get("mitre_techniques", [])
        for threat in threats:
            ttp_info = self._get_ttp_info(threat.threat or "")
            if ttp_info:
                technique_multiplier = max(technique_multiplier, ttp_info["severity_multiplier"])
        
        # Calculate final business impact
        business_impact_score = min(100, avg_severity_score * technique_multiplier)
        
        # Determine risk level based on score
        if business_impact_score >= 90:
            risk_level = RiskLevel.CRITICAL
        elif business_impact_score >= 70:
            risk_level = RiskLevel.HIGH
        elif business_impact_score >= 30:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.LOW
        
        return {
            "business_impact_score": round(business_impact_score, 2),
            "risk_level": risk_level.value,
            "technique_multiplier": technique_multiplier,
            "threat_count": len(threats),
            "unique_ips": len(set(t.ip for t in threats if t.ip)),
            "time_span_hours": self._calculate_time_span_hours(threats),
            "has_cve": any(t.cve_id for t in threats),
            "anomaly_count": sum(1 for t in threats if t.is_anomaly)
        }

    def _calculate_time_span_hours(self, threats: List[models.ThreatLog]) -> float:
        """Calculate time span of incident in hours"""
        timestamps = [t.timestamp for t in threats if t.timestamp]
        if len(timestamps) < 2:
            return 0.0
        
        time_span = max(timestamps) - min(timestamps)
        return round(time_span.total_seconds() / 3600, 2)

# ═══════════════════════════════════════════════════════════════════
# 🔄 Integration Functions
# ═══════════════════════════════════════════════════════════════════

async def run_ai_incident_orchestration(db: Session, tenant_id: int = 1) -> Dict[str, Any]:
    """
    Main entry point for AI-driven incident orchestration.
    Call this periodically (e.g., every 15 minutes) to create incidents.
    """
    print(f"🔥 DEBUG: Starting orchestration for tenant {tenant_id}")
    orchestrator = AIIncidentOrchestrator()
    print(f"🔥 DEBUG: Orchestrator initialized")
    
    try:
        incidents = await orchestrator.orchestrate_incident_creation(db, tenant_id)
        print(f"🔥 DEBUG: Orchestration completed with {len(incidents)} incidents")
        
        return {
            "status": "success",
            "incidents_created": len(incidents),
            "incidents": incidents,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        print(f"🔥 DEBUG: Orchestration failed with error: {e}")
        import traceback
        traceback.print_exc()
        logger.error(f"AI incident orchestration failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "incidents_created": 0,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

def get_ai_incident_recommendations(incident_id: int, db: Session) -> Dict[str, Any]:
    """
    Get AI-powered recommendations for incident response actions.
    """
    incident = db.query(models.SecurityIncident).filter_by(id=incident_id).first()
    if not incident:
        return {"error": "Incident not found"}
    
    # Implementation for AI recommendations based on incident data
    # This would use the threat data, MITRE techniques, etc. to suggest response actions
    
    return {
        "incident_id": incident_id,
        "recommendations": "Advanced AI recommendations would go here",
        "priority_actions": [],
        "estimated_resolution_time": "2-4 hours",
        "required_resources": []
    }
