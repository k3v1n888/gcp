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
CrowdStrike Falcon Connector - Ingest data from CrowdStrike EDR
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import requests
import json
import logging
from .base import BaseConnector, StandardizedThreat, SeverityLevel, ThreatType, DataMapper

logger = logging.getLogger(__name__)


class CrowdStrikeConnector(BaseConnector):
    """Connector for CrowdStrike Falcon EDR"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = config.get('base_url', 'https://api.crowdstrike.com')
        self.client_id = config.get('client_id', '')
        self.client_secret = config.get('client_secret', '')
        self.access_token = None
        
        # CrowdStrike-specific mappings
        self.severity_mapping = {
            'critical': SeverityLevel.CRITICAL,
            'high': SeverityLevel.HIGH,
            'medium': SeverityLevel.MEDIUM,
            'low': SeverityLevel.LOW,
            'informational': SeverityLevel.INFO
        }
        
        self.threat_mapping = {
            'malware': ThreatType.MALWARE,
            'exploit': ThreatType.VULNERABILITY,
            'suspicious_activity': ThreatType.ANOMALY,
            'policy_violation': ThreatType.OTHER,
            'network_discovery': ThreatType.INTRUSION,
            'lateral_movement': ThreatType.APT,
            'data_theft': ThreatType.DATA_EXFILTRATION
        }
    
    def connect(self) -> bool:
        """Authenticate with CrowdStrike API"""
        try:
            auth_url = f"{self.base_url}/oauth2/token"
            auth_data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret
            }
            
            response = requests.post(auth_url, data=auth_data)
            if response.status_code == 200:
                self.access_token = response.json().get('access_token')
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"CrowdStrike authentication failed: {e}")
            return False
    
    def fetch_data(self, since: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Fetch detections from CrowdStrike API"""
        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            # Build time filter
            if since:
                time_filter = since.strftime('%Y-%m-%dT%H:%M:%SZ')
            else:
                time_filter = (datetime.utcnow() - timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M:%SZ')
            
            # Get detection IDs
            detections_url = f"{self.base_url}/detects/queries/detects/v1"
            params = {
                'filter': f"first_behavior:>'{time_filter}'",
                'limit': 100
            }
            
            response = requests.get(detections_url, headers=headers, params=params)
            if response.status_code != 200:
                return []
            
            detection_ids = response.json().get('resources', [])
            if not detection_ids:
                return []
            
            # Get detailed detection data
            details_url = f"{self.base_url}/detects/entities/summaries/GET/v1"
            details_data = {'ids': detection_ids}
            
            details_response = requests.post(details_url, headers=headers, json=details_data)
            if details_response.status_code == 200:
                return details_response.json().get('resources', [])
            
            return []
            
        except Exception as e:
            logger.error(f"Failed to fetch CrowdStrike data: {e}")
            return []
    
    def transform_data(self, raw_data: Dict[str, Any]) -> StandardizedThreat:
        """Transform CrowdStrike detection to standardized threat"""
        
        # Extract basic information
        title = raw_data.get('detection_description', 'CrowdStrike Detection')
        description = raw_data.get('tactic', '') + ' - ' + raw_data.get('technique', '')
        
        # Map severity
        raw_severity = raw_data.get('max_severity_displayname', 'Medium')
        severity = DataMapper.map_severity(raw_severity, self.severity_mapping)
        
        # Map threat type based on behavior
        behaviors = raw_data.get('behaviors', [])
        threat_type = ThreatType.OTHER
        if behaviors:
            behavior_name = behaviors[0].get('display_name', '').lower()
            for key, value in self.threat_mapping.items():
                if key in behavior_name:
                    threat_type = value
                    break
        
        # Extract network and system information
        device = raw_data.get('device', {})
        source_ip = device.get('local_ip', device.get('external_ip'))
        
        # Extract timestamp
        timestamp_str = raw_data.get('first_behavior')
        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00')) if timestamp_str else datetime.utcnow()
        
        # Extract MITRE ATT&CK techniques
        attack_techniques = []
        for behavior in behaviors:
            technique = behavior.get('technique')
            if technique:
                attack_techniques.append(technique)
        
        return StandardizedThreat(
            source=self.source_name,
            source_id=raw_data.get('detection_id', ''),
            timestamp=timestamp,
            threat_type=threat_type,
            severity=severity,
            title=title,
            description=description,
            source_ip=source_ip,
            affected_assets=[device.get('hostname', device.get('device_id', ''))],
            user_accounts=[raw_data.get('assigned_to_name', '')],
            indicators_of_compromise=self._extract_iocs(raw_data),
            attack_techniques=attack_techniques,
            confidence_score=float(raw_data.get('max_confidence', 50)) / 100.0,
            impact_score=self._calculate_impact_score(severity),
            raw_data=raw_data
        )
    
    def _extract_iocs(self, data: Dict[str, Any]) -> List[str]:
        """Extract indicators of compromise from CrowdStrike data"""
        iocs = []
        
        behaviors = data.get('behaviors', [])
        for behavior in behaviors:
            # Extract file hashes
            if 'sha256' in behavior:
                iocs.append(f"SHA256: {behavior['sha256']}")
            if 'md5' in behavior:
                iocs.append(f"MD5: {behavior['md5']}")
            
            # Extract file names
            if 'filename' in behavior:
                iocs.append(f"File: {behavior['filename']}")
            
            # Extract command lines
            if 'cmdline' in behavior:
                iocs.append(f"Command: {behavior['cmdline']}")
        
        return iocs
    
    def _calculate_impact_score(self, severity: SeverityLevel) -> float:
        """Calculate impact score based on severity"""
        impact_mapping = {
            SeverityLevel.CRITICAL: 1.0,
            SeverityLevel.HIGH: 0.8,
            SeverityLevel.MEDIUM: 0.6,
            SeverityLevel.LOW: 0.4,
            SeverityLevel.INFO: 0.2
        }
        return impact_mapping.get(severity, 0.5)
