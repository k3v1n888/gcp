"""
Copyright (c) 2025 Kevin Zachary
All rights reserved.

This software and associated documentation files (the "Software") are the 
exclusive property of Kevin Zachary. Unauthorized copying, distribution, 
modification, or use of this software is strictly prohibited.

For licensing inquiries, contact: kevin@zachary.com
"""

# backend/ai_providers.py
"""
AI Provider Architecture for Incident Orchestration
Supports multiple AI providers with a unified interface
"""
import os
import json
import logging
import requests
import google.auth
import google.auth.transport.requests
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from enum import Enum

logger = logging.getLogger(__name__)

class AIProvider(Enum):
    SENTIENT_AI = "sentient_ai"  # Your existing AI service
    OPENAI = "openai"          # Fallback to OpenAI if needed
    LOCAL = "local"            # For local models
    
class BaseAIProvider(ABC):
    """Base class for all AI providers"""
    
    @abstractmethod
    def analyze_threats_for_incidents(self, threats: List[Dict], context: Dict) -> Dict:
        """
        Analyze threats and determine incident groupings
        
        Args:
            threats: List of threat dictionaries
            context: Additional context for analysis
            
        Returns:
            Dict with incident analysis results
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the AI provider is available"""
        pass

class SentientAIProvider(BaseAIProvider):
    """Your custom Sentient AI service provider"""
    
    def __init__(self):
        self.ai_service_url = os.getenv("AI_SERVICE_URL", "https://sentient-predictor-api-1020401092050.asia-southeast1.run.app")
        self.auth_req = google.auth.transport.requests.Request()
        logger.info(f"✅ Sentient AI Provider initialized: {self.ai_service_url}")
    
    def _get_auth_token(self) -> Optional[str]:
        """Get authentication token for Sentient AI service"""
        try:
            creds, _ = google.auth.default()
            creds.refresh(self.auth_req)
            return creds.token
        except Exception as e:
            logger.error(f"❌ Could not generate auth token for Sentient AI service: {e}")
            return None
    
    def _prepare_threat_analysis_payload(self, threats: List[Dict], context: Dict) -> Dict:
        """Prepare payload for threat analysis"""
        threat_summaries = []
        
        for threat in threats:
            # Extract key threat information
            threat_summary = {
                "id": threat.get('id'),
                "threat_text": threat.get('threat', ''),
                "source": threat.get('source', ''),
                "ip": threat.get('ip', ''),
                "severity": threat.get('severity', 'unknown'),
                "timestamp": threat.get('timestamp', datetime.now(timezone.utc).isoformat()),
                "mitre_technique": self._extract_mitre_technique(threat.get('threat', '')),
                "threat_indicators": self._extract_indicators(threat),
                "risk_score": threat.get('risk_score', 0.0),
                "criticality": threat.get('criticality_score', 0.0)
            }
            threat_summaries.append(threat_summary)
        
        return {
            "threats": threat_summaries,
            "analysis_type": "incident_correlation",
            "context": {
                "time_window_hours": context.get('time_window_hours', 24),
                "correlation_threshold": context.get('correlation_threshold', 0.7),
                "require_incident_worthy": True,
                "include_mitre_mapping": True,
                "include_risk_assessment": True,
                "industry_standards": ["MITRE_ATTACK", "NIST_800_61", "SANS"]
            },
            "output_format": {
                "groups_required": True,
                "confidence_scores": True,
                "recommendations": True,
                "business_impact": True
            }
        }
    
    def _extract_mitre_technique(self, threat_text: str) -> str:
        """Extract MITRE ATT&CK technique from threat text"""
        technique_map = {
            "sql injection": "T1055",
            "log4j": "T1190", 
            "xss": "T1059",
            "brute force": "T1110",
            "phishing": "T1566",
            "ransomware": "T1486",
            "lateral movement": "T1021",
            "privilege escalation": "T1548",
            "data exfiltration": "T1041",
            "persistence": "T1053",
            "command execution": "T1059",
            "network scan": "T1046"
        }
        
        threat_lower = threat_text.lower()
        for key, technique in technique_map.items():
            if key in threat_lower:
                return technique
        return "T1595"  # Default: Active Scanning
    
    def _extract_indicators(self, threat: Dict) -> List[str]:
        """Extract key indicators from threat data"""
        indicators = []
        
        if threat.get('ip'):
            indicators.append(f"Source IP: {threat['ip']}")
        if threat.get('source'):
            indicators.append(f"Detection Source: {threat['source']}")
        if 'failed' in threat.get('threat', '').lower():
            indicators.append("Failed authentication detected")
        if 'scan' in threat.get('threat', '').lower():
            indicators.append("Network scanning behavior")
        if threat.get('severity') in ['high', 'critical']:
            indicators.append(f"High severity: {threat.get('severity')}")
            
        return indicators
    
    def analyze_threats_for_incidents(self, threats: List[Dict], context: Dict = None) -> Dict:
        """
        Use Sentient AI service to analyze threats for incident correlation
        """
        if not threats:
            return {"groups": [], "analysis_summary": "No threats to analyze"}
        
        context = context or {}
        token = self._get_auth_token()
        
        if not token:
            logger.error("❌ No authentication token available for Sentient AI")
            return self._fallback_analysis(threats, context)
        
        headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
        payload = self._prepare_threat_analysis_payload(threats, context)
        
        try:
            # Try incident correlation endpoint first
            response = requests.post(
                f"{self.ai_service_url}/correlate_incidents", 
                json=payload, 
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info("✅ Sentient AI incident correlation successful")
                return self._format_sentient_response(result, threats)
            
            elif response.status_code == 404:
                # Endpoint doesn't exist, try individual predictions
                logger.info("🔄 Using individual threat predictions for correlation")
                return self._correlate_via_predictions(threats, headers, context)
            
            else:
                logger.warning(f"⚠️ Sentient AI returned status {response.status_code}: {response.text}")
                return self._fallback_analysis(threats, context)
                
        except requests.exceptions.Timeout:
            logger.error("⏰ Sentient AI service timeout")
            return self._fallback_analysis(threats, context)
        except Exception as e:
            logger.error(f"❌ Error calling Sentient AI service: {e}")
            return self._fallback_analysis(threats, context)
    
    def _correlate_via_predictions(self, threats: List[Dict], headers: Dict, context: Dict) -> Dict:
        """Use existing prediction endpoints to correlate threats"""
        threat_analyses = []
        
        for threat in threats:
            try:
                # Use existing prediction endpoint
                payload = self._prepare_prediction_payload(threat)
                response = requests.post(
                    f"{self.ai_service_url}/predict", 
                    json=payload, 
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    prediction = response.json()
                    
                    # Get explanation if available
                    explanation = None
                    try:
                        explain_response = requests.post(
                            f"{self.ai_service_url}/explain", 
                            json=payload, 
                            headers=headers,
                            timeout=10
                        )
                        if explain_response.status_code == 200:
                            explanation = explain_response.json()
                    except:
                        pass
                    
                    threat_analyses.append({
                        'threat': threat,
                        'prediction': prediction,
                        'explanation': explanation
                    })
                    
            except Exception as e:
                logger.warning(f"⚠️ Failed to analyze threat {threat.get('id', 'unknown')}: {e}")
                continue
        
        # Correlate based on predictions
        return self._correlate_predictions(threat_analyses, context)
    
    def _prepare_prediction_payload(self, threat: Dict) -> Dict:
        """Prepare payload for individual threat prediction"""
        timestamp_input = threat.get('timestamp')
        if isinstance(timestamp_input, str):
            dt_object = datetime.fromisoformat(timestamp_input.replace('Z', '+00:00'))
        else:
            dt_object = timestamp_input or datetime.now(timezone.utc)
        
        return {
            "technique_id": self._extract_mitre_technique(threat.get('threat', '')),
            "asset_type": "server",
            "login_hour": dt_object.hour,
            "is_admin": 1,
            "is_remote_session": 1 if threat.get('source') == "VPN" else 0,
            "num_failed_logins": 1 if "failed" in threat.get('threat', '').lower() else 0,
            "bytes_sent": threat.get("bytes_sent", 10000),
            "bytes_received": threat.get("bytes_received", 50000),
            "location_mismatch": 1 if "new country" in threat.get('threat', '').lower() else 0,
            "previous_alerts": threat.get("previous_alerts", 0),
            "criticality_score": round(threat.get('criticality_score', 0), 2),
            "cvss_score": round(threat.get('cvss_score', 0), 2),
            "ioc_risk_score": round((threat.get('ip_reputation_score', 0) or 0) / 100.0, 2)
        }
    
    def _correlate_predictions(self, analyses: List[Dict], context: Dict) -> Dict:
        """Correlate threats based on individual predictions"""
        groups = []
        group_id = 1
        
        # Group by severity and similar characteristics
        high_severity_threats = []
        medium_severity_threats = []
        low_severity_threats = []
        
        for analysis in analyses:
            threat = analysis['threat']
            prediction = analysis.get('prediction', {})
            severity_level = prediction.get('prediction', 0)
            
            if severity_level >= 3:  # Critical
                high_severity_threats.append(analysis)
            elif severity_level >= 2:  # High
                high_severity_threats.append(analysis)
            elif severity_level >= 1:  # Medium
                medium_severity_threats.append(analysis)
            else:
                low_severity_threats.append(analysis)
        
        # Create incident groups
        if high_severity_threats:
            groups.append(self._create_incident_group(
                high_severity_threats, group_id, "critical", "Critical Security Incident"
            ))
            group_id += 1
        
        if medium_severity_threats and len(medium_severity_threats) >= 3:
            groups.append(self._create_incident_group(
                medium_severity_threats, group_id, "medium", "Medium Priority Incident"
            ))
            group_id += 1
        
        return {
            "groups": groups,
            "analysis_summary": f"Sentient AI analyzed {len(analyses)} threats and created {len(groups)} incident groups",
            "provider": "sentient_ai",
            "correlation_method": "prediction_based"
        }
    
    def _create_incident_group(self, analyses: List[Dict], group_id: int, severity: str, title: str) -> Dict:
        """Create an incident group from threat analyses"""
        threat_ids = [analysis['threat']['id'] for analysis in analyses]
        key_indicators = []
        mitre_techniques = set()
        
        for analysis in analyses:
            threat = analysis['threat']
            key_indicators.extend(self._extract_indicators(threat))
            mitre_techniques.add(self._extract_mitre_technique(threat.get('threat', '')))
        
        return {
            "group_id": f"SAI-INC-{group_id:04d}",
            "incident_worthy": True,
            "confidence_level": 0.85,
            "incident_category": "Security Incident",
            "attack_phase": "Multiple Phases",
            "severity": severity,
            "title": title,
            "description": f"Sentient AI identified {len(analyses)} correlated threats requiring incident response",
            "threat_ids": threat_ids,
            "key_indicators": list(set(key_indicators))[:10],  # Top 10 unique indicators
            "recommended_actions": [
                "Immediate threat containment",
                "Forensic analysis of affected systems",
                "Review and update security controls",
                "Monitor for lateral movement"
            ],
            "business_impact": "medium" if severity == "medium" else "high",
            "mitre_techniques": list(mitre_techniques),
            "estimated_risk_score": min(9.0, len(analyses) * 1.5),
            "ai_provider": "sentient_ai"
        }
    
    def _format_sentient_response(self, result: Dict, threats: List[Dict]) -> Dict:
        """Format response from Sentient AI service"""
        # If Sentient AI returns structured incident data, use it
        if 'incidents' in result or 'groups' in result:
            return result
        
        # Otherwise format the response
        return {
            "groups": result.get('groups', []),
            "analysis_summary": result.get('summary', 'Sentient AI analysis completed'),
            "provider": "sentient_ai",
            "correlation_method": "sentient_ai_direct"
        }
    
    def _fallback_analysis(self, threats: List[Dict], context: Dict) -> Dict:
        """Fallback analysis when Sentient AI is unavailable"""
        logger.info("🔄 Using fallback correlation analysis")
        
        # Simple rule-based correlation
        groups = []
        
        # Group threats by similarity
        ip_groups = {}
        source_groups = {}
        
        for threat in threats:
            ip = threat.get('ip', 'unknown')
            source = threat.get('source', 'unknown')
            
            if ip not in ip_groups:
                ip_groups[ip] = []
            ip_groups[ip].append(threat)
            
            if source not in source_groups:
                source_groups[source] = []
            source_groups[source].append(threat)
        
        group_id = 1
        
        # Create groups for IPs with multiple threats
        for ip, ip_threats in ip_groups.items():
            if len(ip_threats) >= 3 and ip != 'unknown':
                groups.append({
                    "group_id": f"FALLBACK-IP-{group_id:04d}",
                    "incident_worthy": True,
                    "confidence_level": 0.7,
                    "incident_category": "Network-based Attack",
                    "attack_phase": "Initial Access",
                    "severity": "medium",
                    "title": f"Multiple threats from IP {ip}",
                    "description": f"Detected {len(ip_threats)} threats from same IP address",
                    "threat_ids": [t['id'] for t in ip_threats],
                    "key_indicators": [f"Source IP: {ip}", f"Threat count: {len(ip_threats)}"],
                    "recommended_actions": ["Block suspicious IP", "Investigate source", "Review firewall rules"],
                    "business_impact": "medium",
                    "mitre_techniques": ["T1595"],
                    "estimated_risk_score": min(8.0, len(ip_threats) * 1.2),
                    "ai_provider": "fallback"
                })
                group_id += 1
        
        return {
            "groups": groups,
            "analysis_summary": f"Fallback analysis created {len(groups)} incident groups from {len(threats)} threats",
            "provider": "fallback",
            "correlation_method": "rule_based"
        }
    
    def is_available(self) -> bool:
        """Check if Sentient AI service is available"""
        try:
            token = self._get_auth_token()
            if not token:
                return False
            
            headers = {'Authorization': f'Bearer {token}'}
            response = requests.get(f"{self.ai_service_url}/health", headers=headers, timeout=10)
            return response.status_code == 200
        except:
            return False

class OpenAIProvider(BaseAIProvider):
    """OpenAI provider as fallback (existing implementation)"""
    
    def __init__(self):
        import openai
        self.client = openai.OpenAI()
        logger.info("✅ OpenAI Provider initialized")
    
    def analyze_threats_for_incidents(self, threats: List[Dict], context: Dict = None) -> Dict:
        """Use OpenAI for threat analysis (existing GPT-4 implementation)"""
        # This would contain the existing GPT-4 logic
        # Implementation omitted for brevity - use existing GPT code
        pass
    
    def is_available(self) -> bool:
        """Check if OpenAI is available"""
        try:
            import openai
            return True
        except:
            return False

class AIProviderManager:
    """Manages multiple AI providers with fallback logic"""
    
    def __init__(self):
        self.providers = {}
        self._initialize_providers()
        logger.info(f"✅ AI Provider Manager initialized with {len(self.providers)} providers")
    
    def _initialize_providers(self):
        """Initialize all available AI providers"""
        
        # Always try Sentient AI first (your preferred provider)
        try:
            self.providers[AIProvider.SENTIENT_AI] = SentientAIProvider()
        except Exception as e:
            logger.warning(f"⚠️ Could not initialize Sentient AI provider: {e}")
        
        # OpenAI as fallback
        try:
            self.providers[AIProvider.OPENAI] = OpenAIProvider()
        except Exception as e:
            logger.warning(f"⚠️ Could not initialize OpenAI provider: {e}")
    
    def get_preferred_provider(self) -> Optional[BaseAIProvider]:
        """Get the preferred AI provider"""
        # Check environment variable for preference
        preferred = os.getenv("AI_PROVIDER", "sentient_ai").lower()
        
        if preferred == "sentient_ai" and AIProvider.SENTIENT_AI in self.providers:
            if self.providers[AIProvider.SENTIENT_AI].is_available():
                logger.info("🎯 Using Sentient AI as preferred provider")
                return self.providers[AIProvider.SENTIENT_AI]
        
        if preferred == "openai" and AIProvider.OPENAI in self.providers:
            if self.providers[AIProvider.OPENAI].is_available():
                logger.info("🎯 Using OpenAI as preferred provider")
                return self.providers[AIProvider.OPENAI]
        
        # Fallback logic
        for provider_type, provider in self.providers.items():
            if provider.is_available():
                logger.info(f"🔄 Falling back to {provider_type.value} provider")
                return provider
        
        logger.error("❌ No AI providers available")
        return None
    
    def analyze_threats_for_incidents(self, threats: List[Dict], context: Dict = None) -> Dict:
        """Analyze threats using the best available provider"""
        provider = self.get_preferred_provider()
        
        if not provider:
            return {
                "groups": [],
                "analysis_summary": "No AI providers available for analysis",
                "provider": "none",
                "error": "All AI providers unavailable"
            }
        
        try:
            result = provider.analyze_threats_for_incidents(threats, context)
            logger.info(f"✅ Successfully analyzed {len(threats)} threats")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error during threat analysis: {e}")
            return {
                "groups": [],
                "analysis_summary": f"Analysis failed: {str(e)}",
                "provider": "error",
                "error": str(e)
            }

# Global instance
ai_provider_manager = AIProviderManager()

def get_ai_provider_manager() -> AIProviderManager:
    """Get the global AI provider manager instance"""
    return ai_provider_manager
