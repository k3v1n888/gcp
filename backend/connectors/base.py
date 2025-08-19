"""
Universal Data Connector - Base Classes
Flexible data ingestion and transformation for any cybersecurity tool
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from datetime import datetime
import json
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class SeverityLevel(Enum):
    """Standardized severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ThreatType(Enum):
    """Standardized threat categories"""
    MALWARE = "malware"
    PHISHING = "phishing"
    INTRUSION = "intrusion"
    DATA_EXFILTRATION = "data_exfiltration"
    VULNERABILITY = "vulnerability"
    ANOMALY = "anomaly"
    BRUTE_FORCE = "brute_force"
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    DDOS = "ddos"
    INSIDER_THREAT = "insider_threat"
    APT = "apt"
    OTHER = "other"


@dataclass
class StandardizedThreat:
    """Standardized threat format for AI processing"""
    # Core identification
    source: str  # Tool that detected the threat (e.g., "CrowdStrike", "Splunk")
    source_id: str  # Original ID from source system
    timestamp: datetime
    
    # Threat details
    threat_type: ThreatType
    severity: SeverityLevel
    title: str
    description: str
    
    # Network context
    source_ip: Optional[str] = None
    destination_ip: Optional[str] = None
    source_port: Optional[int] = None
    destination_port: Optional[int] = None
    protocol: Optional[str] = None
    
    # Asset context
    affected_assets: List[str] = None
    user_accounts: List[str] = None
    
    # Technical details
    indicators_of_compromise: List[str] = None
    attack_techniques: List[str] = None  # MITRE ATT&CK techniques
    cve_ids: List[str] = None
    
    # Risk assessment
    confidence_score: float = 0.0  # 0.0 to 1.0
    impact_score: float = 0.0  # 0.0 to 1.0
    
    # Contextual data
    geolocation: Optional[Dict] = None
    raw_data: Dict[str, Any] = None  # Original data for reference
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage"""
        return {
            'source': self.source,
            'source_id': self.source_id,
            'timestamp': self.timestamp.isoformat(),
            'threat_type': self.threat_type.value,
            'severity': self.severity.value,
            'title': self.title,
            'description': self.description,
            'source_ip': self.source_ip,
            'destination_ip': self.destination_ip,
            'source_port': self.source_port,
            'destination_port': self.destination_port,
            'protocol': self.protocol,
            'affected_assets': self.affected_assets or [],
            'user_accounts': self.user_accounts or [],
            'indicators_of_compromise': self.indicators_of_compromise or [],
            'attack_techniques': self.attack_techniques or [],
            'cve_ids': self.cve_ids or [],
            'confidence_score': self.confidence_score,
            'impact_score': self.impact_score,
            'geolocation': self.geolocation,
            'raw_data': self.raw_data or {}
        }


class BaseConnector(ABC):
    """Base class for all cybersecurity tool connectors"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.source_name = config.get('source_name', 'Unknown')
        self.enabled = config.get('enabled', True)
        
    @abstractmethod
    def connect(self) -> bool:
        """Establish connection to the security tool"""
        pass
    
    @abstractmethod
    def fetch_data(self, since: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Fetch raw data from the security tool"""
        pass
    
    @abstractmethod
    def transform_data(self, raw_data: Dict[str, Any]) -> StandardizedThreat:
        """Transform raw data to standardized format"""
        pass
    
    def process_batch(self, since: Optional[datetime] = None) -> List[StandardizedThreat]:
        """Complete pipeline: fetch -> transform -> return standardized threats"""
        try:
            if not self.enabled:
                logger.info(f"Connector {self.source_name} is disabled")
                return []
                
            if not self.connect():
                logger.error(f"Failed to connect to {self.source_name}")
                return []
            
            raw_data_list = self.fetch_data(since)
            standardized_threats = []
            
            for raw_data in raw_data_list:
                try:
                    standardized_threat = self.transform_data(raw_data)
                    standardized_threats.append(standardized_threat)
                except Exception as e:
                    logger.error(f"Failed to transform data from {self.source_name}: {e}")
                    continue
            
            logger.info(f"Processed {len(standardized_threats)} threats from {self.source_name}")
            return standardized_threats
            
        except Exception as e:
            logger.error(f"Error processing batch from {self.source_name}: {e}")
            return []


class DataMapper:
    """Flexible data mapping utility for transforming any data format"""
    
    @staticmethod
    def map_severity(raw_severity: Union[str, int, float], mapping: Dict[Any, SeverityLevel]) -> SeverityLevel:
        """Map various severity formats to standardized levels"""
        if raw_severity in mapping:
            return mapping[raw_severity]
        
        # Try string matching (case insensitive)
        if isinstance(raw_severity, str):
            severity_lower = raw_severity.lower()
            for key, value in mapping.items():
                if isinstance(key, str) and key.lower() == severity_lower:
                    return value
        
        # Default fallback
        return SeverityLevel.MEDIUM
    
    @staticmethod
    def map_threat_type(raw_type: str, mapping: Dict[str, ThreatType]) -> ThreatType:
        """Map various threat type formats to standardized types"""
        if raw_type in mapping:
            return mapping[raw_type]
            
        # Try fuzzy matching
        raw_lower = raw_type.lower()
        for key, value in mapping.items():
            if key.lower() in raw_lower or raw_lower in key.lower():
                return value
        
        return ThreatType.OTHER
    
    @staticmethod
    def extract_ips(data: Dict[str, Any], ip_fields: List[str]) -> tuple:
        """Extract source and destination IPs from various field names"""
        source_ip = None
        dest_ip = None
        
        for field in ip_fields:
            if 'source' in field.lower() or 'src' in field.lower():
                source_ip = data.get(field)
            elif 'dest' in field.lower() or 'dst' in field.lower():
                dest_ip = data.get(field)
                
        return source_ip, dest_ip
    
    @staticmethod
    def extract_timestamp(data: Dict[str, Any], timestamp_fields: List[str]) -> datetime:
        """Extract timestamp from various formats and field names"""
        for field in timestamp_fields:
            if field in data:
                timestamp_value = data[field]
                
                # Handle various timestamp formats
                if isinstance(timestamp_value, (int, float)):
                    # Unix timestamp
                    return datetime.fromtimestamp(timestamp_value)
                elif isinstance(timestamp_value, str):
                    # Try common date formats
                    formats = [
                        '%Y-%m-%dT%H:%M:%S.%fZ',
                        '%Y-%m-%d %H:%M:%S',
                        '%Y/%m/%d %H:%M:%S',
                        '%d/%m/%Y %H:%M:%S'
                    ]
                    for fmt in formats:
                        try:
                            return datetime.strptime(timestamp_value, fmt)
                        except ValueError:
                            continue
        
        # Default to current time
        return datetime.utcnow()
