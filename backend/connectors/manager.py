"""
Universal Data Connector Manager
Orchestrates all connectors and feeds standardized data to AI model for analysis
"""

from typing import Dict, List, Any, Optional, Type
from datetime import datetime, timedelta
import logging
import asyncio
from sqlalchemy.orm import Session
from concurrent.futures import ThreadPoolExecutor, as_completed

from .base import BaseConnector, StandardizedThreat
from .splunk_connector import SplunkConnector
from .crowdstrike_connector import CrowdStrikeConnector
from .generic_connector import GenericConnector

# Import your existing models and AI components
from .. import models, database
from ..ml.prediction import SeverityPredictor
from ..ai_incident_orchestrator import AIIncidentOrchestrator

logger = logging.getLogger(__name__)


class ConnectorManager:
    """
    Manages all data connectors and orchestrates the threat analysis pipeline
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.connectors: Dict[str, BaseConnector] = {}
        self.ai_predictor = SeverityPredictor()
        self.incident_orchestrator = None
        
        # Connector type mapping
        self.connector_types: Dict[str, Type[BaseConnector]] = {
            'splunk': SplunkConnector,
            'crowdstrike': CrowdStrikeConnector,
            'generic': GenericConnector,
            'api': GenericConnector,
            'json_file': GenericConnector,
            'csv_file': GenericConnector
        }
        
        self._initialize_connectors()
    
    def _initialize_connectors(self):
        """Initialize all configured connectors"""
        connectors_config = self.config.get('connectors', {})
        
        for connector_name, connector_config in connectors_config.items():
            try:
                connector_type = connector_config.get('type', 'generic')
                
                if connector_type in self.connector_types:
                    # Add source name to config
                    connector_config['source_name'] = connector_name
                    
                    # Create connector instance
                    connector_class = self.connector_types[connector_type]
                    connector = connector_class(connector_config)
                    
                    self.connectors[connector_name] = connector
                    logger.info(f"Initialized {connector_type} connector: {connector_name}")
                else:
                    logger.error(f"Unknown connector type: {connector_type}")
                    
            except Exception as e:
                logger.error(f"Failed to initialize connector {connector_name}: {e}")
    
    def get_active_connectors(self) -> List[str]:
        """Get list of active connector names"""
        return [name for name, connector in self.connectors.items() if connector.enabled]
    
    def test_connections(self) -> Dict[str, bool]:
        """Test all connector connections"""
        results = {}
        
        for name, connector in self.connectors.items():
            try:
                results[name] = connector.connect()
                logger.info(f"Connector {name}: {'Connected' if results[name] else 'Failed'}")
            except Exception as e:
                logger.error(f"Connection test failed for {name}: {e}")
                results[name] = False
        
        return results
    
    def collect_threats(self, 
                       since: Optional[datetime] = None,
                       connector_names: Optional[List[str]] = None) -> List[StandardizedThreat]:
        """
        Collect threats from specified connectors (or all if none specified)
        """
        if since is None:
            since = datetime.utcnow() - timedelta(hours=1)  # Default to last hour
        
        if connector_names is None:
            connector_names = self.get_active_connectors()
        
        all_threats = []
        
        # Use thread pool for parallel data collection
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {}
            
            for name in connector_names:
                if name in self.connectors:
                    connector = self.connectors[name]
                    future = executor.submit(connector.process_batch, since)
                    futures[future] = name
            
            # Collect results as they complete
            for future in as_completed(futures):
                connector_name = futures[future]
                try:
                    threats = future.result()
                    all_threats.extend(threats)
                    logger.info(f"Collected {len(threats)} threats from {connector_name}")
                except Exception as e:
                    logger.error(f"Failed to collect threats from {connector_name}: {e}")
        
        logger.info(f"Total threats collected: {len(all_threats)}")
        return all_threats
    
    def analyze_threats_with_ai(self, threats: List[StandardizedThreat]) -> List[Dict[str, Any]]:
        """
        Analyze threats using your existing AI model (simplified)
        """
        analyzed_threats = []
        
        logger.info(f"Analyzing {len(threats)} threats with AI...")
        
        for threat in threats:
            try:
                # Use your existing AI predictor with correct method name
                ai_severity = self.ai_predictor.predict_severity(
                    threat=threat.title,
                    source=threat.source,
                    ip_reputation_score=getattr(threat, 'ip_reputation_score', 0),
                    cve_id=threat.cve_ids[0] if threat.cve_ids else None,
                    cvss_score=getattr(threat, 'cvss_score', 0.0),
                    criticality_score=threat.impact_score
                )
                
                analyzed_threat = {
                    'threat': threat,
                    'ai_severity': ai_severity,
                    'explanation': None,  # Skip explanation for now
                    'analysis_timestamp': datetime.utcnow()
                }
                
                analyzed_threats.append(analyzed_threat)
                logger.info(f"Analyzed threat: {threat.title} -> {ai_severity}")
                
            except Exception as e:
                logger.error(f"Failed to analyze threat with AI: {e}")
                # Add threat without AI analysis
                analyzed_threats.append({
                    'threat': threat,
                    'ai_severity': 'medium',
                    'explanation': None,
                    'analysis_timestamp': datetime.utcnow()
                })
        
        logger.info(f"Completed analysis of {len(analyzed_threats)} threats")
        return analyzed_threats
    
    def store_threats(self, analyzed_threats: List[Dict[str, Any]], db: Session, tenant_id: int = 1):
        """
        Store analyzed threats in your existing database
        """
        stored_count = 0
        
        logger.info(f"Attempting to store {len(analyzed_threats)} analyzed threats...")
        
        for analyzed_threat in analyzed_threats:
            try:
                threat = analyzed_threat['threat']
                
                logger.info(f"Storing threat: {threat.title} from {threat.source}")
                
                # Create ThreatLog entry using your existing model fields
                threat_log = models.ThreatLog(
                    ip=threat.source_ip or '',
                    threat=threat.title,
                    source=threat.source,
                    severity=threat.severity.value,
                    tenant_id=tenant_id,
                    timestamp=threat.timestamp,
                    
                    # Additional fields that exist in your model
                    ip_reputation_score=getattr(threat, 'ip_reputation_score', 0),
                    cve_id=threat.cve_ids[0] if threat.cve_ids else None,
                    cvss_score=getattr(threat, 'cvss_score', 0.0),
                    criticality_score=threat.impact_score,
                    ioc_risk_score=getattr(threat, 'ioc_risk_score', 0.0),
                    is_anomaly=threat.confidence_score < 0.5  # Simple anomaly detection
                )
                
                db.add(threat_log)
                stored_count += 1
                logger.info(f"Added threat to session: {threat.title}")
                
            except Exception as e:
                logger.error(f"Failed to store threat: {e}")
                continue
        
        try:
            db.commit()
            logger.info(f"✅ Successfully stored {stored_count} threats in database")
        except Exception as e:
            logger.error(f"❌ Failed to commit threats to database: {e}")
            db.rollback()
    
    def trigger_incident_correlation(self, db: Session, tenant_id: int = 1):
        """
        Trigger your existing incident correlation system (simplified)
        """
        try:
            # Skip incident correlation for now to focus on threat storage
            logger.info("Skipping incident correlation for now")
            return []
            
        except Exception as e:
            logger.error(f"Failed to trigger incident correlation: {e}")
            return []
    
    def run_full_pipeline(self, 
                         since: Optional[datetime] = None,
                         connector_names: Optional[List[str]] = None,
                         tenant_id: int = 1) -> Dict[str, Any]:
        """
        Run the complete data ingestion and analysis pipeline
        """
        pipeline_start = datetime.utcnow()
        
        try:
            # Step 1: Collect threats from all connectors
            logger.info("🔄 Starting threat collection...")
            threats = self.collect_threats(since, connector_names)
            
            if not threats:
                logger.info("No new threats found")
                return {
                    'status': 'success',
                    'threats_collected': 0,
                    'threats_analyzed': 0,
                    'incidents_created': 0,
                    'duration': (datetime.utcnow() - pipeline_start).total_seconds()
                }
            
            # Step 2: Analyze threats with AI
            logger.info("🤖 Analyzing threats with AI...")
            analyzed_threats = self.analyze_threats_with_ai(threats)
            
            # Step 3: Store threats in database
            logger.info("💾 Storing threats in database...")
            db = database.SessionLocal()
            try:
                self.store_threats(analyzed_threats, db, tenant_id)
                
                # Step 4: Trigger incident correlation
                logger.info("🔗 Triggering incident correlation...")
                incidents = self.trigger_incident_correlation(db, tenant_id)
                
                db.close()
                
                pipeline_duration = (datetime.utcnow() - pipeline_start).total_seconds()
                
                result = {
                    'status': 'success',
                    'threats_collected': len(threats),
                    'threats_analyzed': len(analyzed_threats),
                    'incidents_created': len(incidents),
                    'duration': pipeline_duration,
                    'pipeline_start': pipeline_start.isoformat(),
                    'sources': list(set([threat.source for threat in threats]))
                }
                
                logger.info(f"✅ Pipeline completed successfully in {pipeline_duration:.2f}s")
                return result
                
            finally:
                if db:
                    db.close()
            
        except Exception as e:
            logger.error(f"❌ Pipeline failed: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'duration': (datetime.utcnow() - pipeline_start).total_seconds()
            }
    
    def get_connector_status(self) -> Dict[str, Any]:
        """Get status of all connectors"""
        status = {
            'total_connectors': len(self.connectors),
            'active_connectors': len(self.get_active_connectors()),
            'connectors': {}
        }
        
        for name, connector in self.connectors.items():
            status['connectors'][name] = {
                'type': connector.__class__.__name__,
                'enabled': connector.enabled,
                'source_name': connector.source_name
            }
        
        return status
