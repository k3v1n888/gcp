"""
Enhanced AI Data Ingestion Service
Integrates advanced AI models for intelligent data processing
"""

import os
import sys
import json
import yaml
import requests
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException

# Add the AI services to the path
sys.path.append("/app/cxyber_ai_soc_suite/services/ingest")
sys.path.append("/app/cxyber_ai_soc_suite/shared")

try:
    from automapper import propose_json_mapping, build_yaml
    from normalizer import load_mapping, normalize
    from enrichers import enrich_and_featureize
    from schemas import FeatureVector, CanonicalEvent
except ImportError:
    print("⚠️  Advanced AI ingestion modules not found, using fallback")
    
from .models import ThreatLog
from .database import get_db

class AIDataProcessor:
    """Advanced AI-powered data processor that intelligently handles incoming data"""
    
    def __init__(self):
        ai_service_base = os.getenv("AI_SERVICE_URL", "http://ai-service:8001")
        self.threat_service_url = ai_service_base
        self.policy_service_url = ai_service_base.replace(":8001", ":8002")
        self.auto_mapping_enabled = True
        self.ai_enrichment_enabled = True
        
    def intelligent_data_ingestion(self, 
                                 raw_data: Union[Dict[str, Any], str], 
                                 source: str,
                                 tenant_id: int = 1) -> Dict[str, Any]:
        """
        Intelligently process incoming data using AI models
        
        1. Auto-detect data structure and propose mapping
        2. Normalize data to canonical format
        3. Enrich with AI features
        4. Score threat severity
        5. Apply policy decisions
        """
        
        try:
            # Step 1: Intelligent Data Mapping
            if isinstance(raw_data, str):
                try:
                    parsed_data = json.loads(raw_data)
                except json.JSONDecodeError:
                    # Handle syslog or other text formats
                    parsed_data = {"raw_message": raw_data, "timestamp": datetime.utcnow().isoformat()}
            else:
                parsed_data = raw_data
            
            # Auto-propose mapping if no mapping exists for this source
            mapping = self._get_or_create_mapping(source, parsed_data)
            
            # Step 2: Normalize to canonical format
            canonical_event = self._normalize_data(parsed_data, mapping)
            
            # Step 3: AI Feature Enrichment
            feature_vector = self._enrich_with_ai(canonical_event, source)
            
            # Step 4: AI Threat Scoring
            threat_score = self._score_threat(feature_vector, canonical_event)
            
            # Step 5: Policy Decision
            policy_decision = self._apply_policy(threat_score)
            
            # Step 6: Store in database
            threat_log = self._store_threat(canonical_event, feature_vector, threat_score, tenant_id)
            
            return {
                "status": "processed",
                "threat_id": threat_log.id,
                "canonical_event": canonical_event,
                "feature_vector": feature_vector,
                "threat_score": threat_score,
                "policy_decision": policy_decision,
                "ai_processing": {
                    "data_mapping": "auto" if self.auto_mapping_enabled else "manual",
                    "enrichment": "ai_enhanced" if self.ai_enrichment_enabled else "basic",
                    "confidence": threat_score.get("confidence", 0.0)
                }
            }
            
        except Exception as e:
            print(f"❌ AI Data Processing Error: {str(e)}")
            # Fallback to basic processing
            return self._fallback_processing(raw_data, source, tenant_id)
    
    def _get_or_create_mapping(self, source: str, sample_data: Dict[str, Any]) -> Dict[str, str]:
        """Get existing mapping or create new one using AI"""
        
        mapping_file = f"/app/cxyber_ai_soc_suite/services/ingest/mappings/{source}.yaml"
        
        if os.path.exists(mapping_file):
            # Load existing mapping
            with open(mapping_file, 'r') as f:
                mapping_config = yaml.safe_load(f)
            return mapping_config.get('fields', {})
        
        elif self.auto_mapping_enabled:
            # Use AI to propose mapping
            try:
                proposed_mapping = propose_json_mapping(sample_data)
                
                # Save the proposed mapping for future use
                yaml_content = build_yaml(source, proposed_mapping, vendor="Auto-Detected", product=source)
                os.makedirs(os.path.dirname(mapping_file), exist_ok=True)
                with open(mapping_file, 'w') as f:
                    f.write(yaml_content)
                
                print(f"🤖 AI auto-created mapping for {source}")
                return proposed_mapping
            except Exception as e:
                print(f"⚠️  AI mapping failed for {source}: {e}")
                return self._default_mapping()
        else:
            return self._default_mapping()
    
    def _normalize_data(self, data: Dict[str, Any], mapping: Dict[str, str]) -> Dict[str, Any]:
        """Normalize data using the mapping"""
        try:
            return normalize(data, mapping)
        except:
            # Fallback normalization
            return {
                "timestamp": data.get("timestamp", datetime.utcnow().isoformat()),
                "severity": data.get("severity", "medium"),
                "src_ip": data.get("src_ip", data.get("ip", "unknown")),
                "description": data.get("description", data.get("message", "Unknown threat")),
                "raw_data": json.dumps(data)
            }
    
    def _enrich_with_ai(self, canonical_event: Dict[str, Any], source: str) -> Dict[str, Any]:
        """Enrich data with AI-generated features"""
        
        if not self.ai_enrichment_enabled:
            return self._basic_feature_extraction(canonical_event)
        
        try:
            # Use the AI enrichment service
            enriched = enrich_and_featureize(
                canonical_event, 
                ip_rep_score=None,
                cvss_score=None, 
                asset_criticality=None,
                anomaly_hint=None
            )
            return enriched.model_dump() if hasattr(enriched, 'model_dump') else enriched
        except Exception as e:
            print(f"⚠️  AI enrichment failed: {e}")
            return self._basic_feature_extraction(canonical_event)
    
    def _score_threat(self, feature_vector: Dict[str, Any], canonical_event: Dict[str, Any]) -> Dict[str, Any]:
        """Score threat using AI model"""
        
        try:
            # Call the threat scoring service
            response = requests.post(
                f"{self.threat_service_url}/threat/score",
                json={
                    "feature_vector": feature_vector,
                    "canonical_event": canonical_event,
                    "context": {}
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"⚠️  Threat service error: {response.status_code}")
                return self._fallback_threat_scoring(feature_vector, canonical_event)
                
        except Exception as e:
            print(f"⚠️  Threat scoring failed: {e}")
            return self._fallback_threat_scoring(feature_vector, canonical_event)
    
    def _apply_policy(self, threat_score: Dict[str, Any]) -> Dict[str, Any]:
        """Apply policy decisions using AI"""
        
        try:
            response = requests.post(
                f"{self.policy_service_url}/policy/decide",
                json={
                    "case_id": threat_score.get("case_id", "unknown"),
                    "severity": threat_score.get("severity", "medium"),
                    "confidence": threat_score.get("confidence", 0.5),
                    "business_context": {
                        "owner": "default",
                        "sla": "gold", 
                        "change_freeze": False
                    },
                    "controls": {
                        "can_isolate": True,
                        "require_approval": ["contain", "block"]
                    }
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return self._default_policy_decision(threat_score)
                
        except Exception as e:
            print(f"⚠️  Policy service failed: {e}")
            return self._default_policy_decision(threat_score)
    
    def _store_threat(self, canonical_event: Dict[str, Any], feature_vector: Dict[str, Any], 
                     threat_score: Dict[str, Any], tenant_id: int) -> ThreatLog:
        """Store processed threat in database"""
        
        db = next(get_db())
        try:
            threat_log = ThreatLog(
                threat=canonical_event.get("description", "Unknown threat"),
                ip=canonical_event.get("src_ip", "unknown"),
                source=canonical_event.get("source", "ai_processor"),
                timestamp=datetime.fromisoformat(canonical_event.get("timestamp", datetime.utcnow().isoformat()).replace('Z', '+00:00')),
                severity=threat_score.get("severity", "medium"),
                details=json.dumps({
                    "canonical_event": canonical_event,
                    "feature_vector": feature_vector,
                    "ai_analysis": threat_score,
                    "confidence": threat_score.get("confidence", 0.0),
                    "findings": threat_score.get("findings", [])
                }),
                tenant_id=tenant_id
            )
            
            db.add(threat_log)
            db.commit()
            db.refresh(threat_log)
            return threat_log
            
        finally:
            db.close()
    
    def _fallback_processing(self, raw_data: Any, source: str, tenant_id: int) -> Dict[str, Any]:
        """Fallback processing when AI services are unavailable"""
        
        if isinstance(raw_data, dict):
            description = raw_data.get("description", raw_data.get("message", "Unknown threat"))
            ip = raw_data.get("ip", raw_data.get("src_ip", "unknown"))
            severity = raw_data.get("severity", "medium")
        else:
            description = str(raw_data)[:200]
            ip = "unknown"
            severity = "medium"
        
        db = next(get_db())
        try:
            threat_log = ThreatLog(
                threat=description,
                ip=ip,
                source=source,
                timestamp=datetime.utcnow(),
                severity=severity,
                details=json.dumps({"raw_data": raw_data, "processing": "fallback"}),
                tenant_id=tenant_id
            )
            
            db.add(threat_log)
            db.commit()
            db.refresh(threat_log)
            
            return {
                "status": "processed_fallback",
                "threat_id": threat_log.id,
                "processing_mode": "basic"
            }
            
        finally:
            db.close()
    
    def _default_mapping(self) -> Dict[str, str]:
        """Default field mapping"""
        return {
            "timestamp": "$.timestamp",
            "severity": "$.severity", 
            "src_ip": "$.ip",
            "description": "$.message"
        }
    
    def _basic_feature_extraction(self, canonical_event: Dict[str, Any]) -> Dict[str, Any]:
        """Basic feature extraction when AI is unavailable"""
        return {
            "has_ip": bool(canonical_event.get("src_ip")),
            "severity_score": {"low": 1, "medium": 2, "high": 3, "critical": 4}.get(canonical_event.get("severity", "medium"), 2),
            "timestamp_feature": datetime.utcnow().hour,  # Hour of day
            "source_risk": 0.5  # Default risk score
        }
    
    def _fallback_threat_scoring(self, feature_vector: Dict[str, Any], canonical_event: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback threat scoring"""
        severity = canonical_event.get("severity", "medium")
        confidence = 0.6 if severity in ["high", "critical"] else 0.4
        
        return {
            "case_id": f"fallback-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}",
            "severity": severity,
            "confidence": confidence,
            "findings": ["Basic threat detection"],
            "explanations": {"method": "fallback_scoring"},
            "recommendations": ["Monitor activity", "Review logs"]
        }
    
    def _default_policy_decision(self, threat_score: Dict[str, Any]) -> Dict[str, Any]:
        """Default policy decision"""
        severity = threat_score.get("severity", "medium")
        
        if severity in ["critical", "high"]:
            action_plan = ["alert", "investigate", "contain"]
        else:
            action_plan = ["monitor", "log"]
        
        return {
            "decision": "auto_process",
            "action_plan": action_plan,
            "requires_approval": severity == "critical",
            "priority": severity
        }

# Global instance
ai_data_processor = AIDataProcessor()
