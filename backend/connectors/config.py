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

# Configuration for Universal Data Connector System
import os


def get_connector_config():
    """Get configuration based on environment"""
    env = os.getenv('ENV', 'development')
    
    if env == 'production':
        return PROD_CONFIG
    elif env == 'development':
        return DEV_CONFIG
    else:
        return DEFAULT_CONFIG


# Default connector configurations
DEFAULT_CONFIG = {
    "connectors": {
        # Example Splunk connector configuration
        "splunk_prod": {
            "type": "splunk",
            "enabled": True,
            "host": "splunk.company.com",
            "port": 8089,
            "username": "admin",
            "password": "changeme",  # Use environment variable in production
            "ssl_verify": True,
            "search_queries": [
                "index=security sourcetype=firewall | head 100",
                "index=windows EventCode=4625 | head 50",
                "index=linux sourcetype=syslog suspicious | head 50"
            ],
            "poll_interval": 300  # 5 minutes
        },
        
        # Example CrowdStrike connector configuration
        "crowdstrike_prod": {
            "type": "crowdstrike",
            "enabled": True,
            "client_id": "your_client_id",
            "client_secret": "your_client_secret",
            "base_url": "https://api.crowdstrike.com",
            "severity_filter": ["high", "critical"],
            "poll_interval": 180  # 3 minutes
        },
        
        # Example generic API connector
        "security_api": {
            "type": "generic",
            "enabled": True,
            "source_type": "api",
            "endpoint": "https://api.security-tool.com/alerts",
            "method": "GET",
            "auth_type": "bearer",
            "auth_token": "your_api_token",
            "field_mappings": {
                "title": "alert_name",
                "description": "alert_description", 
                "severity": "severity_level",
                "timestamp": "created_time",
                "source_ip": "source_address",
                "source_host": "hostname"
            },
            "severity_mappings": {
                "1": "low",
                "2": "medium", 
                "3": "high",
                "4": "critical"
            },
            "poll_interval": 300
        },
        
        # Example JSON file connector
        "json_feed": {
            "type": "generic",
            "enabled": False,
            "source_type": "json_file",
            "file_path": "/data/threat_feed.json",
            "field_mappings": {
                "title": "threat_name",
                "description": "details",
                "severity": "risk_level",
                "timestamp": "detected_at"
            },
            "poll_interval": 600  # 10 minutes
        },
        
        # Example CSV file connector 
        "csv_feed": {
            "type": "generic",
            "enabled": False,
            "source_type": "csv_file",
            "file_path": "/data/alerts.csv",
            "field_mappings": {
                "title": "Alert Name",
                "description": "Description",
                "severity": "Severity",
                "timestamp": "Timestamp",
                "source_ip": "Source IP"
            },
            "poll_interval": 900  # 15 minutes
        }
    },
    
    # AI analysis configuration
    "ai_analysis": {
        "enabled": True,
        "severity_threshold": 0.7,
        "batch_size": 100,
        "parallel_processing": True
    },
    
    # Database configuration
    "database": {
        "batch_size": 50,
        "auto_commit": True
    },
    
    # Incident correlation settings
    "incident_correlation": {
        "enabled": True,
        "correlation_window": 3600,  # 1 hour
        "minimum_threats": 3
    },
    
    # Logging configuration
    "logging": {
        "level": "INFO",
        "file": "/var/log/connector_manager.log"
    }
}


# Environment-specific configurations
DEV_CONFIG = {
    "connectors": {
        # Development test connectors with mock data
        "mock_firewall": {
            "type": "generic",
            "enabled": True,
            "source_type": "json_file",
            "file_path": "/app/mock-data/mock_firewall.json",
            "field_mappings": {
                "title": "rule_name",
                "description": "description",
                "severity": "severity",
                "timestamp": "timestamp",
                "source_ip": "src_ip",
                "dest_ip": "dst_ip"
            },
            "poll_interval": 60
        },
        
        "mock_ids": {
            "type": "generic",
            "enabled": True,
            "source_type": "json_file", 
            "file_path": "/app/mock-data/mock_ids.json",
            "field_mappings": {
                "title": "signature_name",
                "description": "details",
                "severity": "priority",
                "timestamp": "detected_at",
                "source_ip": "attacker_ip"
            },
            "poll_interval": 60
        }
    }
}


PROD_CONFIG = {
    "connectors": {
        # Production connectors - values should come from environment variables
        "splunk_production": {
            "type": "splunk",
            "enabled": True,
            "host": "${SPLUNK_HOST}",
            "port": 8089,
            "username": "${SPLUNK_USERNAME}",
            "password": "${SPLUNK_PASSWORD}",
            "ssl_verify": True,
            "search_queries": [
                "index=security earliest=-15m | head 500",
                "index=windows EventCode=4625 earliest=-15m | head 100",
                "index=linux suspicious earliest=-15m | head 100"
            ],
            "poll_interval": 300
        }
    }
}
