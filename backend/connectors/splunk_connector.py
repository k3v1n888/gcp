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
Splunk Connector - Ingest data from Splunk SIEM
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import requests
import json
import time
import logging
from .base import BaseConnector, StandardizedThreat, SeverityLevel, ThreatType, DataMapper

logger = logging.getLogger(__name__)


class SplunkConnector(BaseConnector):
    """Connector for Splunk SIEM"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = config.get('base_url', '')
        self.username = config.get('username', '')
        self.password = config.get('password', '')
        self.search_query = config.get('search_query', 'search index=* earliest=-1h')
        self.session = None
        
        # Splunk-specific mappings
        self.severity_mapping = {
            'critical': SeverityLevel.CRITICAL,
            'high': SeverityLevel.HIGH,
            'medium': SeverityLevel.MEDIUM,
            'low': SeverityLevel.LOW,
            'info': SeverityLevel.INFO,
            'informational': SeverityLevel.INFO
        }
        
        self.threat_mapping = {
            'malware': ThreatType.MALWARE,
            'virus': ThreatType.MALWARE,
            'trojan': ThreatType.MALWARE,
            'phishing': ThreatType.PHISHING,
            'intrusion': ThreatType.INTRUSION,
            'brute_force': ThreatType.BRUTE_FORCE,
            'sql_injection': ThreatType.SQL_INJECTION,
            'xss': ThreatType.XSS,
            'ddos': ThreatType.DDOS,
            'anomaly': ThreatType.ANOMALY
        }
    
    def connect(self) -> bool:
        """Authenticate with Splunk"""
        try:
            self.session = requests.Session()
            auth_url = f"{self.base_url}/services/auth/login"
            
            auth_data = {
                'username': self.username,
                'password': self.password
            }
            
            response = self.session.post(auth_url, data=auth_data, verify=False)
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Splunk authentication failed: {e}")
            return False
    
    def fetch_data(self, since: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Fetch data from Splunk using search API"""
        try:
            if since:
                time_filter = f"earliest={since.isoformat()}"
                search_query = f"{self.search_query} {time_filter}"
            else:
                search_query = self.search_query
            
            # Create search job
            search_url = f"{self.base_url}/services/search/jobs"
            search_data = {'search': search_query}
            
            response = self.session.post(search_url, data=search_data)
            if response.status_code != 201:
                return []
            
            # Extract job ID
            job_id = response.text.split('<sid>')[1].split('</sid>')[0]
            
            # Wait for job completion
            status_url = f"{self.base_url}/services/search/jobs/{job_id}"
            while True:
                status_response = self.session.get(status_url)
                if 'isDone">1' in status_response.text:
                    break
                time.sleep(1)
            
            # Get results
            results_url = f"{self.base_url}/services/search/jobs/{job_id}/results"
            results_response = self.session.get(results_url, params={'output_mode': 'json'})
            
            if results_response.status_code == 200:
                data = results_response.json()
                return data.get('results', [])
            
            return []
            
        except Exception as e:
            logger.error(f"Failed to fetch Splunk data: {e}")
            return []
    
    def transform_data(self, raw_data: Dict[str, Any]) -> StandardizedThreat:
        """Transform Splunk event to standardized threat"""
        
        # Extract basic information
        title = raw_data.get('signature', raw_data.get('rule_name', 'Splunk Alert'))
        description = raw_data.get('description', raw_data.get('message', ''))
        
        # Map severity
        raw_severity = raw_data.get('severity', raw_data.get('priority', 'medium'))
        severity = DataMapper.map_severity(raw_severity, self.severity_mapping)
        
        # Map threat type
        raw_threat_type = raw_data.get('category', raw_data.get('alert_type', 'other'))
        threat_type = DataMapper.map_threat_type(raw_threat_type, self.threat_mapping)
        
        # Extract network information
        source_ip, dest_ip = DataMapper.extract_ips(raw_data, [
            'src_ip', 'source_ip', 'srcip', 
            'dest_ip', 'destination_ip', 'destip'
        ])
        
        # Extract timestamp
        timestamp = DataMapper.extract_timestamp(raw_data, [
            '_time', 'timestamp', 'event_time', 'time'
        ])
        
        return StandardizedThreat(
            source=self.source_name,
            source_id=raw_data.get('_raw', str(hash(str(raw_data)))),
            timestamp=timestamp,
            threat_type=threat_type,
            severity=severity,
            title=title,
            description=description,
            source_ip=source_ip,
            destination_ip=dest_ip,
            source_port=raw_data.get('src_port'),
            destination_port=raw_data.get('dest_port'),
            protocol=raw_data.get('protocol'),
            affected_assets=[raw_data.get('dest_host', raw_data.get('host', ''))],
            user_accounts=[raw_data.get('user', raw_data.get('username', ''))],
            indicators_of_compromise=self._extract_iocs(raw_data),
            confidence_score=float(raw_data.get('confidence', 0.5)),
            impact_score=self._calculate_impact_score(severity),
            raw_data=raw_data
        )
    
    def _extract_iocs(self, data: Dict[str, Any]) -> List[str]:
        """Extract indicators of compromise from Splunk data"""
        iocs = []
        
        # Common IoC fields in Splunk
        ioc_fields = ['hash', 'md5', 'sha1', 'sha256', 'url', 'domain', 'file_name']
        
        for field in ioc_fields:
            if field in data and data[field]:
                iocs.append(f"{field}: {data[field]}")
        
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
