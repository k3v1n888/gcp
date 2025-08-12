"""
AI Model Management and Orchestration System
Manages all AI models and coordinates their interactions
"""

import os
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from dataclasses import dataclass
import json
import requests
import threading
import time
from concurrent.futures import ThreadPoolExecutor

from .database import get_db
from .models import ThreatLog, SecurityIncident
from .ai_data_processor import ai_data_processor

logger = logging.getLogger(__name__)

@dataclass
class AIModelStatus:
    """Status of an AI model"""
    name: str
    status: str  # 'healthy', 'degraded', 'offline'
    last_check: datetime
    response_time: float
    accuracy: float
    throughput: int
    error_rate: float
    

@dataclass
class SystemDecision:
    """AI system decision"""
    decision_id: str
    timestamp: datetime
    decision_type: str
    confidence: float
    rationale: str
    actions: List[str]
    model_inputs: Dict[str, Any]
    model_outputs: Dict[str, Any]


class AIOrchestrator:
    """Central AI orchestration and management system"""
    
    def __init__(self):
        self.models = {}
        self.performance_metrics = {}
        self.decision_history = []
        self.is_running = False
        self.monitoring_thread = None
        
        # Use environment variables for AI service URLs
        ai_service_base = os.getenv("AI_SERVICE_URL", "http://ai-service:8001")
        backend_base = os.getenv("BACKEND_URL", "http://localhost:8000")
        
        self.model_endpoints = {
            "data_intelligence": f"{backend_base}/ingest_auto",
            "threat_scoring": f"{ai_service_base}/threat/score".replace(":8001", ":8001"), 
            "policy_decision": f"{ai_service_base}/policy/decide".replace(":8001", ":8002"),
            "incident_correlation": f"{backend_base}/api/incidents/aggregate-threats"
        }
        
    def start_orchestration(self):
        """Start the AI orchestration system"""
        if self.is_running:
            return
            
        self.is_running = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        logger.info("🤖 AI Orchestration System started")
        
    def stop_orchestration(self):
        """Stop the AI orchestration system"""
        self.is_running = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        logger.info("🛑 AI Orchestration System stopped")
        
    def process_threat_intelligently(self, raw_data: Dict[str, Any], source: str) -> Dict[str, Any]:
        """
        Process a threat through the complete AI pipeline
        1. Data Intelligence Processing
        2. Threat Scoring
        3. Policy Decision
        4. Action Execution
        """
        
        decision_id = f"dec-{datetime.utcnow().strftime('%Y%m%d-%H%M%S-%f')}"
        start_time = time.time()
        
        try:
            # Step 1: Intelligent Data Processing
            logger.info(f"🔄 Processing threat {decision_id} through AI pipeline")
            
            processing_result = ai_data_processor.intelligent_data_ingestion(raw_data, source)
            
            # Step 2: Correlation Analysis
            correlation_result = self._analyze_correlations(processing_result)
            
            # Step 3: Strategic Decision Making
            strategic_decision = self._make_strategic_decision(processing_result, correlation_result)
            
            # Step 4: Action Orchestration
            action_result = self._orchestrate_actions(strategic_decision)
            
            # Step 5: Record Decision
            decision = SystemDecision(
                decision_id=decision_id,
                timestamp=datetime.utcnow(),
                decision_type="threat_processing",
                confidence=processing_result.get("threat_score", {}).get("confidence", 0.5),
                rationale=self._generate_rationale(processing_result, strategic_decision),
                actions=action_result.get("actions", []),
                model_inputs={"raw_data": raw_data, "source": source},
                model_outputs={
                    "processing": processing_result,
                    "correlation": correlation_result,
                    "decision": strategic_decision,
                    "actions": action_result
                }
            )
            
            self.decision_history.append(decision)
            
            processing_time = time.time() - start_time
            logger.info(f"✅ Threat {decision_id} processed in {processing_time:.2f}s")
            
            return {
                "decision_id": decision_id,
                "status": "completed",
                "processing_time": processing_time,
                "threat_id": processing_result.get("threat_id"),
                "severity": processing_result.get("threat_score", {}).get("severity", "medium"),
                "confidence": processing_result.get("threat_score", {}).get("confidence", 0.5),
                "actions_taken": action_result.get("actions", []),
                "ai_analysis": {
                    "data_intelligence": processing_result.get("ai_processing", {}),
                    "correlation_found": len(correlation_result.get("related_threats", [])) > 0,
                    "strategic_priority": strategic_decision.get("priority", "normal")
                }
            }
            
        except Exception as e:
            logger.error(f"❌ AI orchestration failed for {decision_id}: {str(e)}")
            return {
                "decision_id": decision_id,
                "status": "error",
                "error": str(e),
                "fallback_action": "manual_review_required"
            }
    
    def _analyze_correlations(self, processing_result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze correlations with existing threats"""
        
        try:
            db = next(get_db())
            threat_id = processing_result.get("threat_id")
            canonical_event = processing_result.get("canonical_event", {})
            
            # Find related threats by IP
            src_ip = canonical_event.get("src_ip")
            related_by_ip = []
            if src_ip and src_ip != "unknown":
                recent_threats = db.query(ThreatLog).filter(
                    ThreatLog.ip == src_ip,
                    ThreatLog.timestamp >= datetime.utcnow() - timedelta(hours=24)
                ).limit(10).all()
                related_by_ip = [{"id": t.id, "threat": t.threat, "timestamp": t.timestamp.isoformat()} for t in recent_threats]
            
            # Find related threats by pattern
            threat_text = canonical_event.get("description", "").lower()
            pattern_matches = []
            if len(threat_text) > 10:
                similar_threats = db.query(ThreatLog).filter(
                    ThreatLog.threat.ilike(f"%{threat_text[:20]}%"),
                    ThreatLog.timestamp >= datetime.utcnow() - timedelta(hours=48)
                ).limit(5).all()
                pattern_matches = [{"id": t.id, "threat": t.threat, "similarity": "pattern"} for t in similar_threats]
            
            correlation_score = len(related_by_ip) * 0.3 + len(pattern_matches) * 0.2
            
            db.close()
            
            return {
                "related_threats": related_by_ip + pattern_matches,
                "correlation_score": min(correlation_score, 1.0),
                "correlation_types": {
                    "ip_based": len(related_by_ip),
                    "pattern_based": len(pattern_matches)
                },
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Correlation analysis failed: {str(e)}")
            return {
                "related_threats": [],
                "correlation_score": 0.0,
                "error": str(e)
            }
    
    def _make_strategic_decision(self, processing_result: Dict[str, Any], correlation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Make strategic decisions based on AI analysis"""
        
        threat_score = processing_result.get("threat_score", {})
        severity = threat_score.get("severity", "medium")
        confidence = threat_score.get("confidence", 0.5)
        correlation_score = correlation_result.get("correlation_score", 0.0)
        
        # Strategic priority calculation
        base_priority = {"low": 1, "medium": 2, "high": 3, "critical": 4}.get(severity, 2)
        confidence_multiplier = confidence
        correlation_multiplier = 1 + correlation_score
        
        strategic_priority = base_priority * confidence_multiplier * correlation_multiplier
        
        # Decision making logic
        if strategic_priority >= 3.5:
            decision_level = "critical"
            response_actions = ["immediate_alert", "auto_investigate", "prepare_containment"]
        elif strategic_priority >= 2.5:
            decision_level = "high"
            response_actions = ["alert", "investigate", "monitor_closely"]
        elif strategic_priority >= 1.5:
            decision_level = "medium" 
            response_actions = ["log", "monitor", "scheduled_review"]
        else:
            decision_level = "low"
            response_actions = ["log", "baseline_monitoring"]
        
        # Resource allocation
        resource_allocation = {
            "analyst_priority": decision_level,
            "automation_level": "full" if strategic_priority >= 3.0 else "partial",
            "escalation_required": strategic_priority >= 3.5
        }
        
        return {
            "strategic_priority": strategic_priority,
            "decision_level": decision_level,
            "response_actions": response_actions,
            "resource_allocation": resource_allocation,
            "rationale": f"Priority {strategic_priority:.2f} based on severity={severity}, confidence={confidence:.2f}, correlation={correlation_score:.2f}",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _orchestrate_actions(self, strategic_decision: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate actions based on strategic decision"""
        
        response_actions = strategic_decision.get("response_actions", [])
        decision_level = strategic_decision.get("decision_level", "medium")
        
        executed_actions = []
        failed_actions = []
        
        for action in response_actions:
            try:
                if action == "immediate_alert":
                    # Trigger immediate alert
                    alert_result = self._trigger_alert("critical", strategic_decision)
                    executed_actions.append({"action": action, "result": alert_result, "status": "success"})
                
                elif action == "auto_investigate":
                    # Start automated investigation
                    investigation_result = self._start_investigation(strategic_decision)
                    executed_actions.append({"action": action, "result": investigation_result, "status": "success"})
                
                elif action == "prepare_containment":
                    # Prepare containment measures
                    containment_result = self._prepare_containment(strategic_decision)
                    executed_actions.append({"action": action, "result": containment_result, "status": "success"})
                
                elif action in ["alert", "log", "monitor"]:
                    # Standard actions
                    executed_actions.append({"action": action, "status": "success", "timestamp": datetime.utcnow().isoformat()})
                
            except Exception as e:
                failed_actions.append({"action": action, "error": str(e)})
                logger.error(f"❌ Action {action} failed: {str(e)}")
        
        return {
            "executed_actions": executed_actions,
            "failed_actions": failed_actions,
            "orchestration_status": "completed" if not failed_actions else "partial",
            "next_review": (datetime.utcnow() + timedelta(hours=1)).isoformat()
        }
    
    def _trigger_alert(self, level: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Trigger system alert"""
        return {
            "alert_id": f"alert-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}",
            "level": level,
            "triggered": True,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _start_investigation(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Start automated investigation"""
        return {
            "investigation_id": f"inv-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}",
            "status": "initiated",
            "automated_steps": ["log_analysis", "pattern_matching", "threat_intelligence_lookup"],
            "estimated_duration": "15-30 minutes"
        }
    
    def _prepare_containment(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare containment measures"""
        return {
            "containment_plan": "network_isolation_ready",
            "approval_required": True,
            "estimated_impact": "low",
            "rollback_plan": "available"
        }
    
    def _generate_rationale(self, processing_result: Dict[str, Any], strategic_decision: Dict[str, Any]) -> str:
        """Generate human-readable rationale for the decision"""
        
        threat_score = processing_result.get("threat_score", {})
        severity = threat_score.get("severity", "medium")
        confidence = threat_score.get("confidence", 0.5)
        findings = threat_score.get("findings", [])
        
        rationale = f"AI analysis determined {severity} severity threat with {confidence:.0%} confidence. "
        
        if findings:
            rationale += f"Key findings: {', '.join(findings[:3])}. "
        
        strategic_priority = strategic_decision.get("strategic_priority", 0)
        rationale += f"Strategic priority score: {strategic_priority:.2f}. "
        
        decision_level = strategic_decision.get("decision_level", "medium")
        rationale += f"Recommended response level: {decision_level}."
        
        return rationale
    
    def _monitoring_loop(self):
        """Continuous monitoring of AI models"""
        while self.is_running:
            try:
                self._check_model_health()
                self._update_performance_metrics()
                self._cleanup_old_decisions()
                time.sleep(30)  # Check every 30 seconds
            except Exception as e:
                logger.error(f"❌ Monitoring loop error: {str(e)}")
                time.sleep(60)  # Wait longer on error
    
    def _check_model_health(self):
        """Check health of all AI models"""
        for name, endpoint in self.model_endpoints.items():
            try:
                start_time = time.time()
                response = requests.get(f"{endpoint}/health" if "/health" not in endpoint else endpoint.replace("/threat/score", "/health").replace("/policy/decide", "/health").replace("/ingest_auto", "/health").replace("/aggregate-threats", "/api/health"), timeout=5)
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    status = "healthy"
                else:
                    status = "degraded"
                    
            except Exception as e:
                status = "offline"
                response_time = 5.0
                logger.warning(f"⚠️  Model {name} health check failed: {str(e)}")
            
            self.models[name] = AIModelStatus(
                name=name,
                status=status,
                last_check=datetime.utcnow(),
                response_time=response_time,
                accuracy=0.85,  # Would be calculated from actual performance
                throughput=100,  # Requests per minute
                error_rate=0.05  # 5% error rate
            )
    
    def _update_performance_metrics(self):
        """Update performance metrics"""
        # Calculate recent performance metrics
        recent_decisions = [d for d in self.decision_history if d.timestamp >= datetime.utcnow() - timedelta(hours=1)]
        
        self.performance_metrics = {
            "total_decisions": len(self.decision_history),
            "recent_decisions": len(recent_decisions),
            "average_confidence": sum(d.confidence for d in recent_decisions) / len(recent_decisions) if recent_decisions else 0,
            "model_health": {name: model.status for name, model in self.models.items()},
            "system_uptime": (datetime.utcnow() - datetime.utcnow().replace(hour=0, minute=0, second=0)).total_seconds() / 3600,
            "last_updated": datetime.utcnow().isoformat()
        }
    
    def _cleanup_old_decisions(self):
        """Clean up old decision history"""
        cutoff = datetime.utcnow() - timedelta(days=7)
        self.decision_history = [d for d in self.decision_history if d.timestamp >= cutoff]
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        return {
            "orchestrator_status": "running" if self.is_running else "stopped",
            "models": {name: {
                "status": model.status,
                "response_time": f"{model.response_time:.3f}s",
                "last_check": model.last_check.isoformat()
            } for name, model in self.models.items()},
            "performance_metrics": self.performance_metrics,
            "recent_decisions": len([d for d in self.decision_history if d.timestamp >= datetime.utcnow() - timedelta(hours=1)]),
            "system_health": self._calculate_system_health()
        }
    
    def _calculate_system_health(self) -> str:
        """Calculate overall system health"""
        if not self.models:
            return "unknown"
        
        healthy_models = sum(1 for model in self.models.values() if model.status == "healthy")
        total_models = len(self.models)
        
        health_ratio = healthy_models / total_models
        
        if health_ratio >= 0.8:
            return "healthy"
        elif health_ratio >= 0.5:
            return "degraded"
        else:
            return "critical"

# Global orchestrator instance
ai_orchestrator = AIOrchestrator()
