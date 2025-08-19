#!/usr/bin/env python3
"""
SOC Data Collector Agent
Universal agent that can be deployed on any environment (cloud/on-prem)
to collect security data and send to the main SOC platform.

Copyright (c) 2025 Kevin Zachary
"""
import os
import sys
import json
import time
import logging
import hashlib
import platform
import subprocess
import configparser
from datetime import datetime, timezone
from typing import Dict, List, Optional
import requests
from pathlib import Path

class SOCAgent:
    def __init__(self, config_path: str = "soc_agent.conf"):
        self.config_path = config_path
        self.config = self.load_config()
        self.setup_logging()
        self.agent_id = self.generate_agent_id()
        self.last_heartbeat = None
        
    def load_config(self) -> configparser.ConfigParser:
        """Load agent configuration"""
        config = configparser.ConfigParser()
        
        # Default configuration
        config['server'] = {
            'endpoint': 'https://localhost:8001',
            'api_key': '',
            'tenant_id': 'default',
            'verify_ssl': 'false'
        }
        
        config['agent'] = {
            'name': f'soc-agent-{platform.node()}',
            'environment': 'production',
            'collection_interval': '60',
            'heartbeat_interval': '300'
        }
        
        config['collectors'] = {
            'system_logs': 'true',
            'security_logs': 'true',
            'network_events': 'true',
            'process_events': 'true',
            'file_events': 'false'
        }
        
        config['logs'] = {
            'level': 'INFO',
            'file': 'soc_agent.log',
            'max_size': '10MB'
        }
        
        # Load from file if exists
        if os.path.exists(self.config_path):
            config.read(self.config_path)
        else:
            # Create default config file
            with open(self.config_path, 'w') as f:
                config.write(f)
                
        return config
    
    def setup_logging(self):
        """Setup logging configuration"""
        log_level = getattr(logging, self.config['logs']['level'].upper())
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.config['logs']['file']),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('SOCAgent')
    
    def generate_agent_id(self) -> str:
        """Generate unique agent ID based on system characteristics"""
        system_info = f"{platform.node()}-{platform.system()}-{platform.machine()}"
        return hashlib.sha256(system_info.encode()).hexdigest()[:16]
    
    def collect_system_logs(self) -> List[Dict]:
        """Collect system logs based on platform"""
        logs = []
        
        try:
            if platform.system() == "Linux":
                # Collect from journalctl or syslog
                result = subprocess.run(
                    ['journalctl', '--since', '1 minute ago', '--output', 'json'],
                    capture_output=True, text=True, timeout=30
                )
                if result.returncode == 0:
                    for line in result.stdout.strip().split('\n'):
                        if line:
                            try:
                                log_entry = json.loads(line)
                                logs.append({
                                    'timestamp': log_entry.get('__REALTIME_TIMESTAMP'),
                                    'message': log_entry.get('MESSAGE', ''),
                                    'priority': log_entry.get('PRIORITY', '6'),
                                    'source': 'system',
                                    'host': platform.node()
                                })
                            except json.JSONDecodeError:
                                continue
                                
            elif platform.system() == "Windows":
                # Windows Event Log collection would go here
                # Using PowerShell or Windows API
                pass
                
            elif platform.system() == "Darwin":
                # macOS log collection
                result = subprocess.run(
                    ['log', 'show', '--predicate', 'eventType == logEvent', '--last', '1m', '--style', 'json'],
                    capture_output=True, text=True, timeout=30
                )
                if result.returncode == 0:
                    try:
                        log_data = json.loads(result.stdout)
                        for entry in log_data:
                            logs.append({
                                'timestamp': entry.get('timestamp'),
                                'message': entry.get('eventMessage', ''),
                                'category': entry.get('category', ''),
                                'source': 'system',
                                'host': platform.node()
                            })
                    except json.JSONDecodeError:
                        pass
                        
        except Exception as e:
            self.logger.error(f"Error collecting system logs: {e}")
            
        return logs
    
    def collect_security_events(self) -> List[Dict]:
        """Collect security-specific events"""
        events = []
        
        try:
            # Check for failed authentication attempts
            if platform.system() == "Linux":
                result = subprocess.run(
                    ['grep', '-E', 'Failed password|authentication failure', '/var/log/auth.log'],
                    capture_output=True, text=True, timeout=30
                )
                if result.returncode == 0:
                    for line in result.stdout.strip().split('\n'):
                        if line:
                            events.append({
                                'timestamp': datetime.now(timezone.utc).isoformat(),
                                'event_type': 'authentication_failure',
                                'message': line,
                                'severity': 'medium',
                                'source': 'auth',
                                'host': platform.node()
                            })
                            
            # Add more security event collection logic here
            
        except Exception as e:
            self.logger.error(f"Error collecting security events: {e}")
            
        return events
    
    def collect_network_events(self) -> List[Dict]:
        """Collect network-related events"""
        events = []
        
        try:
            # Check for suspicious network activity
            if platform.system() == "Linux":
                # Get network connections
                result = subprocess.run(
                    ['netstat', '-tuln'],
                    capture_output=True, text=True, timeout=30
                )
                if result.returncode == 0:
                    listening_ports = []
                    for line in result.stdout.split('\n'):
                        if 'LISTEN' in line:
                            parts = line.split()
                            if len(parts) >= 4:
                                listening_ports.append(parts[3])
                    
                    events.append({
                        'timestamp': datetime.now(timezone.utc).isoformat(),
                        'event_type': 'network_status',
                        'listening_ports': listening_ports,
                        'source': 'network',
                        'host': platform.node()
                    })
                    
        except Exception as e:
            self.logger.error(f"Error collecting network events: {e}")
            
        return events
    
    def collect_process_events(self) -> List[Dict]:
        """Collect process-related events"""
        events = []
        
        try:
            if platform.system() in ["Linux", "Darwin"]:
                # Get running processes
                result = subprocess.run(
                    ['ps', 'aux'],
                    capture_output=True, text=True, timeout=30
                )
                if result.returncode == 0:
                    processes = []
                    lines = result.stdout.split('\n')[1:]  # Skip header
                    for line in lines[:20]:  # Limit to top 20 processes
                        if line.strip():
                            parts = line.split()
                            if len(parts) >= 11:
                                processes.append({
                                    'user': parts[0],
                                    'pid': parts[1],
                                    'cpu': parts[2],
                                    'mem': parts[3],
                                    'command': ' '.join(parts[10:])
                                })
                    
                    events.append({
                        'timestamp': datetime.now(timezone.utc).isoformat(),
                        'event_type': 'process_snapshot',
                        'processes': processes,
                        'source': 'process',
                        'host': platform.node()
                    })
                    
        except Exception as e:
            self.logger.error(f"Error collecting process events: {e}")
            
        return events
    
    def send_data_to_server(self, data: Dict) -> bool:
        """Send collected data to SOC server"""
        try:
            endpoint = self.config['server']['endpoint']
            api_key = self.config['server']['api_key']
            tenant_id = self.config['server']['tenant_id']
            verify_ssl = self.config['server'].getboolean('verify_ssl')
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}',
                'X-Tenant-ID': tenant_id,
                'X-Agent-ID': self.agent_id
            }
            
            payload = {
                'agent_id': self.agent_id,
                'agent_name': self.config['agent']['name'],
                'environment': self.config['agent']['environment'],
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'data': data
            }
            
            response = requests.post(
                f"{endpoint}/api/data/ingest",
                headers=headers,
                json=payload,
                verify=verify_ssl,
                timeout=30
            )
            
            if response.status_code == 200:
                self.logger.info("Data sent successfully to SOC server")
                return True
            else:
                self.logger.error(f"Failed to send data: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error sending data to server: {e}")
            return False
    
    def send_heartbeat(self) -> bool:
        """Send heartbeat to SOC server"""
        try:
            endpoint = self.config['server']['endpoint']
            api_key = self.config['server']['api_key']
            tenant_id = self.config['server']['tenant_id']
            verify_ssl = self.config['server'].getboolean('verify_ssl')
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}',
                'X-Tenant-ID': tenant_id,
                'X-Agent-ID': self.agent_id
            }
            
            payload = {
                'agent_id': self.agent_id,
                'agent_name': self.config['agent']['name'],
                'status': 'active',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'system_info': {
                    'platform': platform.system(),
                    'hostname': platform.node(),
                    'python_version': platform.python_version()
                }
            }
            
            response = requests.post(
                f"{endpoint}/api/agents/heartbeat",
                headers=headers,
                json=payload,
                verify=verify_ssl,
                timeout=10
            )
            
            if response.status_code == 200:
                self.last_heartbeat = datetime.now(timezone.utc)
                self.logger.debug("Heartbeat sent successfully")
                return True
            else:
                self.logger.error(f"Failed to send heartbeat: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error sending heartbeat: {e}")
            return False
    
    def collect_all_data(self) -> Dict:
        """Collect all enabled data types"""
        data = {}
        
        if self.config['collectors'].getboolean('system_logs'):
            data['system_logs'] = self.collect_system_logs()
            
        if self.config['collectors'].getboolean('security_logs'):
            data['security_events'] = self.collect_security_events()
            
        if self.config['collectors'].getboolean('network_events'):
            data['network_events'] = self.collect_network_events()
            
        if self.config['collectors'].getboolean('process_events'):
            data['process_events'] = self.collect_process_events()
            
        return data
    
    def run_once(self):
        """Run data collection once"""
        self.logger.info("Starting data collection cycle")
        
        # Collect data
        data = self.collect_all_data()
        
        # Send to server
        if data:
            success = self.send_data_to_server(data)
            if success:
                self.logger.info(f"Successfully sent {len(data)} data types to server")
            else:
                self.logger.error("Failed to send data to server")
        else:
            self.logger.warning("No data collected")
    
    def run_daemon(self):
        """Run as daemon process"""
        self.logger.info(f"Starting SOC Agent daemon (ID: {self.agent_id})")
        
        collection_interval = int(self.config['agent']['collection_interval'])
        heartbeat_interval = int(self.config['agent']['heartbeat_interval'])
        
        last_collection = 0
        last_heartbeat = 0
        
        while True:
            try:
                current_time = time.time()
                
                # Send heartbeat
                if current_time - last_heartbeat >= heartbeat_interval:
                    self.send_heartbeat()
                    last_heartbeat = current_time
                
                # Collect and send data
                if current_time - last_collection >= collection_interval:
                    self.run_once()
                    last_collection = current_time
                
                time.sleep(10)  # Sleep for 10 seconds before checking again
                
            except KeyboardInterrupt:
                self.logger.info("Received interrupt signal, shutting down...")
                break
            except Exception as e:
                self.logger.error(f"Error in daemon loop: {e}")
                time.sleep(30)  # Wait 30 seconds before retrying

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='SOC Data Collector Agent')
    parser.add_argument('--config', default='soc_agent.conf', help='Configuration file path')
    parser.add_argument('--daemon', action='store_true', help='Run as daemon')
    parser.add_argument('--once', action='store_true', help='Run once and exit')
    parser.add_argument('--test-connection', action='store_true', help='Test connection to SOC server')
    
    args = parser.parse_args()
    
    agent = SOCAgent(config_path=args.config)
    
    if args.test_connection:
        print(f"Agent ID: {agent.agent_id}")
        print("Testing connection to SOC server...")
        success = agent.send_heartbeat()
        if success:
            print("✅ Connection successful!")
        else:
            print("❌ Connection failed!")
        sys.exit(0 if success else 1)
    
    elif args.once:
        agent.run_once()
    
    elif args.daemon:
        agent.run_daemon()
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
