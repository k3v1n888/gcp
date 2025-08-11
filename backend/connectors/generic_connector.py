"""
Generic Data Connector - Handle any JSON, CSV, or REST API data source
Highly configurable for any cybersecurity tool with flexible mapping
"""

from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
import requests
import json
import csv
import logging
from pathlib import Path
from .base import BaseConnector, StandardizedThreat, SeverityLevel, ThreatType, DataMapper

logger = logging.getLogger(__name__)


class GenericConnector(BaseConnector):
    """
    Universal connector for any data source
    Supports JSON files, CSV files, REST APIs, webhooks
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        # Data source configuration
        self.source_type = config.get('source_type', 'api')  # api, json_file, csv_file, webhook
        self.endpoint_url = config.get('endpoint_url', '')
        self.file_path = config.get('file_path', '')
        self.auth_config = config.get('auth', {})
        self.headers = config.get('headers', {})
        
        # Field mappings - highly configurable
        self.field_mappings = config.get('field_mappings', {
            'id': 'id',
            'timestamp': 'timestamp',
            'title': 'title',
            'description': 'description',
            'severity': 'severity',
            'threat_type': 'type',
            'source_ip': 'source_ip',
            'destination_ip': 'dest_ip'
        })
        
        # Custom severity mapping
        self.severity_mapping = config.get('severity_mapping', {
            'critical': SeverityLevel.CRITICAL,
            '5': SeverityLevel.CRITICAL,
            '4': SeverityLevel.HIGH,
            'high': SeverityLevel.HIGH,
            '3': SeverityLevel.MEDIUM,
            'medium': SeverityLevel.MEDIUM,
            '2': SeverityLevel.LOW,
            'low': SeverityLevel.LOW,
            '1': SeverityLevel.INFO,
            'info': SeverityLevel.INFO
        })
        
        # Custom threat type mapping
        self.threat_mapping = config.get('threat_mapping', {
            'malware': ThreatType.MALWARE,
            'virus': ThreatType.MALWARE,
            'phishing': ThreatType.PHISHING,
            'intrusion': ThreatType.INTRUSION,
            'vulnerability': ThreatType.VULNERABILITY,
            'anomaly': ThreatType.ANOMALY,
            'brute_force': ThreatType.BRUTE_FORCE,
            'sql_injection': ThreatType.SQL_INJECTION,
            'xss': ThreatType.XSS,
            'ddos': ThreatType.DDOS
        })
        
        # Data transformation rules
        self.transformation_rules = config.get('transformation_rules', {})
        
    def connect(self) -> bool:
        """Test connection based on source type"""
        try:
            if self.source_type == 'api':
                return self._test_api_connection()
            elif self.source_type in ['json_file', 'csv_file']:
                return self._test_file_access()
            elif self.source_type == 'webhook':
                return True  # Webhooks don't need connection testing
            
            return False
            
        except Exception as e:
            logger.error(f"Connection test failed for {self.source_name}: {e}")
            return False
    
    def _test_api_connection(self) -> bool:
        """Test API connectivity"""
        try:
            headers = self.headers.copy()
            
            # Handle different authentication methods
            auth_type = self.auth_config.get('type', 'none')
            if auth_type == 'bearer':
                headers['Authorization'] = f"Bearer {self.auth_config['token']}"
            elif auth_type == 'api_key':
                headers[self.auth_config['header_name']] = self.auth_config['api_key']
            elif auth_type == 'basic':
                import base64
                credentials = f"{self.auth_config['username']}:{self.auth_config['password']}"
                encoded = base64.b64encode(credentials.encode()).decode()
                headers['Authorization'] = f"Basic {encoded}"
            
            response = requests.get(self.endpoint_url, headers=headers, timeout=10)
            return response.status_code < 400
            
        except Exception as e:
            logger.error(f"API connection test failed: {e}")
            return False
    
    def _test_file_access(self) -> bool:
        """Test file accessibility"""
        try:
            file_path = Path(self.file_path)
            return file_path.exists() and file_path.is_file()
        except Exception:
            return False
    
    def fetch_data(self, since: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Fetch data based on source type"""
        try:
            if self.source_type == 'api':
                return self._fetch_api_data(since)
            elif self.source_type == 'json_file':
                return self._fetch_json_file()
            elif self.source_type == 'csv_file':
                return self._fetch_csv_file()
            
            return []
            
        except Exception as e:
            logger.error(f"Failed to fetch data from {self.source_name}: {e}")
            return []
    
    def _fetch_api_data(self, since: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Fetch data from REST API"""
        try:
            headers = self.headers.copy()
            params = {}
            
            # Add authentication
            auth_type = self.auth_config.get('type', 'none')
            if auth_type == 'bearer':
                headers['Authorization'] = f"Bearer {self.auth_config['token']}"
            elif auth_type == 'api_key':
                headers[self.auth_config['header_name']] = self.auth_config['api_key']
            
            # Add time filter if supported
            if since and 'time_param' in self.auth_config:
                params[self.auth_config['time_param']] = since.isoformat()
            
            response = requests.get(self.endpoint_url, headers=headers, params=params)
            if response.status_code == 200:
                data = response.json()
                
                # Handle different response structures
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict):
                    # Try common list fields
                    for field in ['data', 'results', 'items', 'events', 'alerts']:
                        if field in data and isinstance(data[field], list):
                            return data[field]
                    return [data]  # Single object
                
            return []
            
        except Exception as e:
            logger.error(f"API data fetch failed: {e}")
            return []
    
    def _fetch_json_file(self) -> List[Dict[str, Any]]:
        """Load data from JSON file"""
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
                
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                # Try to find the array of events
                for field in ['data', 'events', 'alerts', 'results']:
                    if field in data and isinstance(data[field], list):
                        return data[field]
                return [data]
            
            return []
            
        except Exception as e:
            logger.error(f"JSON file read failed: {e}")
            return []
    
    def _fetch_csv_file(self) -> List[Dict[str, Any]]:
        """Load data from CSV file"""
        try:
            data = []
            with open(self.file_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    data.append(dict(row))
            return data
            
        except Exception as e:
            logger.error(f"CSV file read failed: {e}")
            return []
    
    def transform_data(self, raw_data: Dict[str, Any]) -> StandardizedThreat:
        """Transform raw data using flexible field mappings"""
        
        # Apply transformation rules first
        transformed_data = self._apply_transformation_rules(raw_data)
        
        # Extract fields using mappings
        def get_field(field_name: str, default: Any = None) -> Any:
            mapping = self.field_mappings.get(field_name, field_name)
            if '.' in mapping:
                # Handle nested fields
                keys = mapping.split('.')
                value = transformed_data
                for key in keys:
                    if isinstance(value, dict) and key in value:
                        value = value[key]
                    else:
                        return default
                return value
            return transformed_data.get(mapping, default)
        
        # Extract basic information
        source_id = get_field('id', str(hash(str(raw_data))))
        title = get_field('title', 'Generic Alert')
        description = get_field('description', '')
        
        # Map severity
        raw_severity = get_field('severity', 'medium')
        severity = DataMapper.map_severity(raw_severity, self.severity_mapping)
        
        # Map threat type
        raw_threat_type = get_field('threat_type', 'other')
        threat_type = DataMapper.map_threat_type(str(raw_threat_type), self.threat_mapping)
        
        # Extract network information
        source_ip = get_field('source_ip')
        dest_ip = get_field('destination_ip')
        
        # Extract timestamp
        timestamp_value = get_field('timestamp')
        if timestamp_value:
            timestamp = self._parse_timestamp(timestamp_value)
        else:
            timestamp = datetime.utcnow()
        
        # Extract additional fields
        affected_assets = self._extract_list_field(transformed_data, 'affected_assets')
        user_accounts = self._extract_list_field(transformed_data, 'user_accounts')
        iocs = self._extract_list_field(transformed_data, 'indicators')
        attack_techniques = self._extract_list_field(transformed_data, 'attack_techniques')
        
        return StandardizedThreat(
            source=self.source_name,
            source_id=source_id,
            timestamp=timestamp,
            threat_type=threat_type,
            severity=severity,
            title=title,
            description=description,
            source_ip=source_ip,
            destination_ip=dest_ip,
            source_port=get_field('source_port'),
            destination_port=get_field('destination_port'),
            protocol=get_field('protocol'),
            affected_assets=affected_assets,
            user_accounts=user_accounts,
            indicators_of_compromise=iocs,
            attack_techniques=attack_techniques,
            confidence_score=float(get_field('confidence', 0.5)),
            impact_score=self._calculate_impact_score(severity),
            geolocation=get_field('geolocation'),
            raw_data=raw_data
        )
    
    def _apply_transformation_rules(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply custom transformation rules"""
        transformed = data.copy()
        
        for field, rules in self.transformation_rules.items():
            if field in transformed:
                value = transformed[field]
                
                # Apply string transformations
                if 'lowercase' in rules:
                    value = str(value).lower()
                if 'uppercase' in rules:
                    value = str(value).upper()
                if 'replace' in rules:
                    for old, new in rules['replace'].items():
                        value = str(value).replace(old, new)
                
                # Apply value mappings
                if 'mapping' in rules:
                    value = rules['mapping'].get(value, value)
                
                transformed[field] = value
        
        return transformed
    
    def _extract_list_field(self, data: Dict[str, Any], field: str) -> List[str]:
        """Extract list field with flexible formatting"""
        mapping = self.field_mappings.get(field)
        if not mapping:
            return []
        
        value = data.get(mapping)
        if not value:
            return []
        
        if isinstance(value, list):
            return [str(item) for item in value]
        elif isinstance(value, str):
            # Try to parse comma-separated values
            return [item.strip() for item in value.split(',') if item.strip()]
        
        return [str(value)]
    
    def _parse_timestamp(self, timestamp_value: Any) -> datetime:
        """Parse timestamp from various formats"""
        if isinstance(timestamp_value, (int, float)):
            return datetime.fromtimestamp(timestamp_value)
        elif isinstance(timestamp_value, str):
            # Try common formats
            formats = [
                '%Y-%m-%dT%H:%M:%S.%fZ',
                '%Y-%m-%dT%H:%M:%SZ',
                '%Y-%m-%d %H:%M:%S',
                '%Y/%m/%d %H:%M:%S',
                '%d/%m/%Y %H:%M:%S',
                '%m/%d/%Y %H:%M:%S'
            ]
            for fmt in formats:
                try:
                    return datetime.strptime(timestamp_value, fmt)
                except ValueError:
                    continue
        
        return datetime.utcnow()
    
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
