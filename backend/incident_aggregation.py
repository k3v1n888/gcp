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
AI-Powered Incident Aggregation Service
Analyzes threats and creates comprehensive incident reports
"""

from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging
import json
from dataclasses import asdict

from .models import ThreatLog, SecurityIncident
from .correlation_service import generate_holistic_summary, correlate_and_enrich_threats
from .ml.prediction import SeverityPredictor

logger = logging.getLogger(__name__)

class AIIncidentAggregator:
    """AI-powered service to aggregate threats into comprehensive incidents"""
    
    def __init__(self):
        self.severity_predictor = SeverityPredictor()
        
    def analyze_threat_patterns(self, threats: List[ThreatLog]) -> Dict[str, Any]:
        """Analyze patterns in threats to identify potential incidents"""
        
        patterns = {
            'ip_clusters': {},
            'attack_chains': [],
            'time_clusters': [],
            'severity_distribution': {},
            'source_analysis': {}
        }
        
        # Group threats by source IP
        for threat in threats:
            ip = threat.ip or 'unknown'
            if ip not in patterns['ip_clusters']:
                patterns['ip_clusters'][ip] = []
            patterns['ip_clusters'][ip].append(threat)
        
        # Analyze severity distribution
        for threat in threats:
            severity = threat.severity
            patterns['severity_distribution'][severity] = patterns['severity_distribution'].get(severity, 0) + 1
        
        # Analyze source distribution
        for threat in threats:
            source = threat.source or 'unknown'
            patterns['source_analysis'][source] = patterns['source_analysis'].get(source, 0) + 1
        
        # Identify potential attack chains (threats from same IP within time window)
        for ip, ip_threats in patterns['ip_clusters'].items():
            if len(ip_threats) > 1:
                # Sort by timestamp
                sorted_threats = sorted(ip_threats, key=lambda x: x.timestamp)
                
                # Check if threats are within reasonable time window (e.g., 1 hour)
                time_window = timedelta(hours=1)
                for i in range(len(sorted_threats) - 1):
                    if sorted_threats[i+1].timestamp - sorted_threats[i].timestamp <= time_window:
                        patterns['attack_chains'].append({
                            'ip': ip,
                            'threats': sorted_threats[i:i+2],
                            'time_span': (sorted_threats[i+1].timestamp - sorted_threats[i].timestamp).total_seconds()
                        })
        
        return patterns
    
    def generate_incident_summary(self, threats: List[ThreatLog], patterns: Dict[str, Any]) -> str:
        """Generate AI-powered incident summary"""
        
        # Prepare data for AI analysis
        threat_data = []
        for threat in threats:
            threat_data.append({
                'title': threat.threat,
                'severity': threat.severity,
                'ip': threat.ip,
                'source': threat.source,
                'timestamp': threat.timestamp.isoformat() if threat.timestamp else None
            })
        
        # Create comprehensive prompt for local AI
        prompt = f"""
        Analyze the following cybersecurity threats and provide a comprehensive incident summary:
        
        Threats ({len(threats)} total):
        {json.dumps(threat_data, indent=2)}
        
        Pattern Analysis:
        - IP Clusters: {len(patterns['ip_clusters'])} unique IPs
        - Attack Chains: {len(patterns['attack_chains'])} potential chains
        - Severity Distribution: {patterns['severity_distribution']}
        - Source Distribution: {patterns['source_analysis']}
        
        Please provide:
        1. Incident Title
        2. Executive Summary
        3. Attack Timeline
        4. Affected Assets
        5. Indicators of Compromise (IOCs)
        6. Recommended Actions
        7. Risk Assessment
        """
        
        try:
            # Use local AI service for analysis
            import requests
            response = requests.post(
                "http://localhost:8001/analyze",
                json={"prompt": prompt},
                timeout=30
            )
            
            if response.status_code == 200:
                ai_analysis = response.json().get('analysis', 'Analysis not available')
            else:
                ai_analysis = self._generate_fallback_summary(threats, patterns)
                
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            ai_analysis = self._generate_fallback_summary(threats, patterns)
        
        return ai_analysis
    
    def _generate_fallback_summary(self, threats: List[ThreatLog], patterns: Dict[str, Any]) -> str:
        """Generate fallback summary when AI service is unavailable"""
        
        highest_severity = max(threats, key=lambda t: self._severity_score(t.severity)).severity
        unique_ips = len(patterns['ip_clusters'])
        attack_chains = len(patterns['attack_chains'])
        
        summary = f"""
        INCIDENT SUMMARY (Generated by Fallback Analysis)
        
        Title: Security Incident - {len(threats)} Threats Detected
        
        Executive Summary:
        A security incident involving {len(threats)} threats has been detected across {unique_ips} unique IP addresses.
        The highest severity threat is classified as {highest_severity}.
        {attack_chains} potential attack chains have been identified.
        
        Key Statistics:
        - Total Threats: {len(threats)}
        - Unique IPs: {unique_ips}
        - Severity Distribution: {patterns['severity_distribution']}
        - Attack Chains: {attack_chains}
        
        Recommended Actions:
        1. Investigate all IP addresses involved
        2. Block malicious IPs immediately
        3. Review logs for additional indicators
        4. Implement additional monitoring for affected systems
        5. Consider incident response activation for {highest_severity} severity
        
        Time Range: {min(t.timestamp for t in threats if t.timestamp)} to {max(t.timestamp for t in threats if t.timestamp)}
        """
        
        return summary
    
    def _severity_score(self, severity: str) -> int:
        """Convert severity to numeric score for comparison"""
        scores = {
            'critical': 4,
            'high': 3,
            'medium': 2,
            'low': 1,
            'unknown': 0
        }
        return scores.get(severity.lower(), 0)
    
    def create_incident_from_threats(
        self, 
        threats: List[ThreatLog], 
        db: Session,
        tenant_id: int = 1
    ) -> SecurityIncident:
        """Create a comprehensive incident from related threats"""
        
        if not threats:
            raise ValueError("No threats provided for incident creation")
        
        # Analyze patterns
        patterns = self.analyze_threat_patterns(threats)
        
        # Generate AI summary
        ai_summary = self.generate_incident_summary(threats, patterns)
        
        # Determine incident severity (highest threat severity)
        incident_severity = max(threats, key=lambda t: self._severity_score(t.severity)).severity
        
        # Create incident title
        unique_ips = len(patterns['ip_clusters'])
        incident_title = f"Security Incident - {len(threats)} Threats Across {unique_ips} IPs"
        
        # Extract IOCs
        iocs = list(set([t.ip for t in threats if t.ip]))
        
        # Create incident
        incident = SecurityIncident(
            title=incident_title,
            description=ai_summary,
            severity=incident_severity,
            status="open",
            tenant_id=tenant_id,
            created_at=datetime.utcnow(),
            
            # AI-generated fields
            ai_summary=ai_summary,
            confidence_score=0.8,  # Could be calculated based on pattern strength
            
            # Pattern analysis results
            affected_assets=json.dumps(list(patterns['ip_clusters'].keys())),
            indicators_of_compromise=json.dumps(iocs),
            
            # Statistics
            related_threats_count=len(threats)
        )
        
        # Add to database
        db.add(incident)
        db.flush()  # Get the ID
        
        # Associate threats with incident
        for threat in threats:
            if incident not in threat.incidents:
                threat.incidents.append(incident)
        
        db.commit()
        
        logger.info(f"Created incident {incident.id} from {len(threats)} threats")
        return incident
    
    def auto_aggregate_recent_threats(
        self, 
        db: Session, 
        hours_back: int = 24,
        min_threats: int = 3,
        tenant_id: int = 1
    ) -> List[SecurityIncident]:
        """Automatically aggregate recent threats into incidents"""
        
        # Get recent threats not already in incidents
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
        
        recent_threats = db.query(ThreatLog).filter(
            ThreatLog.timestamp >= cutoff_time,
            ThreatLog.tenant_id == tenant_id,
            ~ThreatLog.incidents.any()  # Not already in an incident
        ).all()
        
        if len(recent_threats) < min_threats:
            logger.info(f"Only {len(recent_threats)} unassigned threats found, minimum is {min_threats}")
            return []
        
        logger.info(f"Found {len(recent_threats)} recent threats for aggregation")
        
        created_incidents = []
        
        # Group threats by IP for incident creation
        ip_groups = {}
        for threat in recent_threats:
            ip = threat.ip or 'unknown'
            if ip not in ip_groups:
                ip_groups[ip] = []
            ip_groups[ip].append(threat)
        
        # Create incidents for IP groups with multiple threats
        for ip, threats in ip_groups.items():
            if len(threats) >= min_threats:
                try:
                    incident = self.create_incident_from_threats(threats, db, tenant_id)
                    created_incidents.append(incident)
                    logger.info(f"Created incident for IP {ip} with {len(threats)} threats")
                except Exception as e:
                    logger.error(f"Failed to create incident for IP {ip}: {e}")
        
        # If remaining threats are diverse but numerous, create a general incident
        unassigned_threats = [t for t in recent_threats if not t.incidents]
        if len(unassigned_threats) >= min_threats:
            try:
                incident = self.create_incident_from_threats(unassigned_threats, db, tenant_id)
                created_incidents.append(incident)
                logger.info(f"Created general incident with {len(unassigned_threats)} diverse threats")
            except Exception as e:
                logger.error(f"Failed to create general incident: {e}")
        
        return created_incidents


# Global instance
incident_aggregator = AIIncidentAggregator()
