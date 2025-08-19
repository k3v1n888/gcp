#!/usr/bin/env python3
"""
Threat Simulation Script for Sentient AI SOC
Generates realistic cybersecurity threats to test the full AI pipeline

This script simulates:
- Malicious IP addresses (known attack sources)
- Benign IP addresses (legitimate traffic)  
- Various attack types and severities
- Real-world threat patterns

The data flows through:
1. Ingest Service (Model A) - Data normalization
2. AI Models (B & C) - Threat analysis and prediction
3. Database storage - PostgreSQL persistence
4. Frontend display - Threats dashboard
"""

import requests
import json
import time
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
import argparse
import sys

class ThreatSimulator:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.backend_url = "http://localhost:8001"  # Backend API URL
        self.session = requests.Session()
        
        # Known malicious IP ranges and specific IPs from threat intelligence
        self.malicious_ips = [
            "185.220.101.182",  # Known Tor exit node
            "198.98.51.189",    # Known botnet C&C
            "103.224.182.251",  # APT infrastructure
            "45.142.213.33",    # Malware hosting
            "91.240.118.172",   # Phishing campaigns
            "194.147.140.123",  # Cryptomining malware
            "77.83.247.81",     # DDoS botnet
            "89.248.171.218",   # Data exfiltration
            "178.128.83.165",   # Ransomware C&C
            "167.99.164.201"    # Credential stuffing
        ]
        
        # Legitimate IP addresses (major cloud providers, CDNs, etc.)
        self.benign_ips = [
            "8.8.8.8",          # Google DNS
            "1.1.1.1",          # Cloudflare DNS
            "13.107.42.14",     # Microsoft Office 365
            "52.96.0.0",        # AWS CloudFront
            "104.16.0.0",       # Cloudflare CDN
            "172.217.12.14",    # Google Services
            "157.240.0.0",      # Facebook/Meta
            "199.232.56.250",   # Akamai CDN
            "72.21.91.29",      # Amazon
            "151.101.193.140"   # Reddit/Fastly
        ]
        
        # Attack types with realistic patterns
        self.attack_patterns = {
            "brute_force": {
                "description": "Multiple failed login attempts",
                "severity_range": ["medium", "high"],
                "ports": [22, 3389, 21, 23],
                "user_agents": ["SSH-2.0-OpenSSH_7.4", "RDP Client", "FTP Client"]
            },
            "port_scan": {
                "description": "Network reconnaissance activity",
                "severity_range": ["low", "medium"],
                "ports": [80, 443, 22, 21, 25, 53, 110, 143],
                "user_agents": ["nmap", "masscan", "zmap"]
            },
            "malware_c2": {
                "description": "Command and control communication",
                "severity_range": ["high", "critical"],
                "ports": [443, 80, 8080, 53],
                "user_agents": ["Mozilla/5.0 (compatible; Bot)", "TrickBot", "Emotet"]
            },
            "phishing": {
                "description": "Suspicious email or web activity",
                "severity_range": ["medium", "high"],
                "ports": [80, 443, 25, 587],
                "user_agents": ["Mozilla/5.0 (Windows NT 10.0; Win64; x64)"]
            },
            "data_exfiltration": {
                "description": "Unusual data transfer patterns",
                "severity_range": ["high", "critical"],
                "ports": [443, 80, 21, 22],
                "user_agents": ["curl", "wget", "custom_exfil_tool"]
            },
            "ddos": {
                "description": "Distributed denial of service",
                "severity_range": ["medium", "critical"],
                "ports": [80, 443, 53],
                "user_agents": ["LOIC", "HOIC", "Mirai"]
            }
        }
        
        # Benign traffic patterns
        self.benign_patterns = {
            "web_browsing": {
                "description": "Normal web browsing activity",
                "severity_range": ["low"],
                "ports": [80, 443],
                "user_agents": [
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
                ]
            },
            "api_calls": {
                "description": "Legitimate API interactions",
                "severity_range": ["low"],
                "ports": [80, 443, 8080],
                "user_agents": ["python-requests", "curl", "PostmanRuntime"]
            },
            "email_sync": {
                "description": "Email client synchronization",
                "severity_range": ["low"],
                "ports": [993, 995, 587, 25],
                "user_agents": ["Microsoft Outlook", "Apple Mail", "Thunderbird"]
            }
        }

    def generate_threat_log(self, is_malicious: bool = True) -> Dict[str, Any]:
        """Generate a realistic threat log entry"""
        
        if is_malicious:
            source_ip = random.choice(self.malicious_ips)
            attack_type = random.choice(list(self.attack_patterns.keys()))
            pattern = self.attack_patterns[attack_type]
            severity = random.choice(pattern["severity_range"])
            threat_name = f"{attack_type.replace('_', ' ').title()} from {source_ip}"
        else:
            source_ip = random.choice(self.benign_ips)
            traffic_type = random.choice(list(self.benign_patterns.keys()))
            pattern = self.benign_patterns[traffic_type]
            severity = "low"
            threat_name = f"Benign {traffic_type.replace('_', ' ').title()} from {source_ip}"
        
        # Generate realistic timestamps
        base_time = datetime.now() - timedelta(minutes=random.randint(0, 1440))  # Last 24 hours
        
        return {
            "timestamp": base_time.isoformat(),
            "source_ip": source_ip,
            "destination_ip": f"192.168.1.{random.randint(10, 254)}",
            "destination_port": random.choice(pattern["ports"]),
            "protocol": random.choice(["TCP", "UDP", "HTTP", "HTTPS"]),
            "threat": threat_name,
            "severity": severity,
            "description": pattern["description"],
            "user_agent": random.choice(pattern["user_agents"]),
            "bytes_transferred": random.randint(100, 50000),
            "packets": random.randint(10, 1000),
            "duration": random.randint(1, 300),
            "geolocation": self.get_geolocation(source_ip),
            "threat_family": attack_type if is_malicious else "benign",
            "confidence_score": random.uniform(0.7, 0.99) if is_malicious else random.uniform(0.1, 0.3),
            "is_malicious": is_malicious,
            "source": "threat_simulator",
            "rule_triggered": f"RULE_{random.randint(1000, 9999)}" if is_malicious else None,
            "mitre_attack": self.get_mitre_technique(attack_type) if is_malicious else None
        }

    def get_geolocation(self, ip: str) -> Dict[str, Any]:
        """Get realistic geolocation for IP"""
        locations = {
            "185.220.101.182": {"country": "Germany", "city": "Frankfurt", "lat": 50.1109, "lon": 8.6821},
            "198.98.51.189": {"country": "United States", "city": "Chicago", "lat": 41.8781, "lon": -87.6298},
            "8.8.8.8": {"country": "United States", "city": "Mountain View", "lat": 37.4056, "lon": -122.0775},
            "1.1.1.1": {"country": "Australia", "city": "Sydney", "lat": -33.8688, "lon": 151.2093}
        }
        
        return locations.get(ip, {
            "country": random.choice(["China", "Russia", "North Korea", "Iran", "Romania"]),
            "city": "Unknown",
            "lat": random.uniform(-90, 90),
            "lon": random.uniform(-180, 180)
        })

    def get_mitre_technique(self, attack_type: str) -> str:
        """Get MITRE ATT&CK technique for attack type"""
        mitre_map = {
            "brute_force": "T1110 - Brute Force",
            "port_scan": "T1046 - Network Service Scanning", 
            "malware_c2": "T1071 - Application Layer Protocol",
            "phishing": "T1566 - Phishing",
            "data_exfiltration": "T1041 - Exfiltration Over C2 Channel",
            "ddos": "T1498 - Network Denial of Service"
        }
        return mitre_map.get(attack_type, "T1000 - Unknown Technique")

    def send_to_backend_api(self, threat_data: Dict[str, Any]) -> bool:
        """Send threat data directly to backend threats/create endpoint"""
        try:
            # Prepare simplified data structure that matches backend expectations
            backend_payload = {
                "ip": threat_data.get("source_ip"),
                "threat": threat_data.get("threat"),
                "source": threat_data.get("source", "threat_simulator"),
                "severity": threat_data.get("severity"),
                "cvss_score": random.uniform(4.0, 9.5) if threat_data.get("is_malicious") else random.uniform(1.0, 3.0)
            }
            
            # Send to the backend threats/create endpoint that actually stores in DB
            response = self.session.post(
                f"{self.backend_url}/api/threats/create",
                json=backend_payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                print(f"✅ Sent {threat_data['threat']} (severity: {threat_data['severity']})")
                return True
            else:
                print(f"❌ Failed to send threat: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error sending threat data: {e}")
            return False

    def verify_database_storage(self) -> Dict[str, int]:
        """Check how many threats are stored in the database"""
        try:
            response = self.session.get(f"{self.backend_url}/api/admin/health/database")
            if response.status_code == 200:
                data = response.json()
                return {
                    "total_threats": data.get("metrics", {}).get("total_threats", 0),
                    "total_incidents": data.get("metrics", {}).get("total_incidents", 0),
                    "recent_threats_24h": data.get("metrics", {}).get("recent_threats_24h", 0)
                }
        except Exception as e:
            print(f"❌ Error checking database: {e}")
        
        return {"total_threats": 0, "total_incidents": 0, "recent_threats_24h": 0}

    def check_ai_pipeline_status(self) -> Dict[str, Any]:
        """Check if all AI models are healthy"""
        try:
            response = self.session.get(f"{self.base_url}/api/admin/health/ai-models")
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"❌ Error checking AI pipeline: {e}")
        
        return {"status": "unknown", "models": []}

    def simulate_attack_campaign(self, num_threats: int = 20, malicious_ratio: float = 0.7, delay: float = 2.0):
        """Simulate a realistic attack campaign"""
        
        print("🚀 Starting Threat Simulation Campaign")
        print("="*60)
        
        # Check initial state
        print("📊 Initial Database State:")
        initial_db = self.verify_database_storage()
        print(f"   Total Threats: {initial_db['total_threats']}")
        print(f"   Total Incidents: {initial_db['total_incidents']}")
        print(f"   Recent (24h): {initial_db['recent_threats_24h']}")
        
        print("\n🤖 AI Pipeline Status:")
        ai_status = self.check_ai_pipeline_status()
        print(f"   Status: {ai_status.get('status', 'unknown')}")
        print(f"   Models: {ai_status.get('healthy_count', 0)}/{ai_status.get('total_count', 0)} healthy")
        
        print(f"\n🎯 Simulation Plan:")
        malicious_count = int(num_threats * malicious_ratio)
        benign_count = num_threats - malicious_count
        print(f"   Total Threats: {num_threats}")
        print(f"   Malicious: {malicious_count} ({malicious_ratio*100:.1f}%)")
        print(f"   Benign: {benign_count} ({(1-malicious_ratio)*100:.1f}%)")
        print(f"   Delay between threats: {delay}s")
        
        print("\n" + "="*60)
        print("🔥 STARTING THREAT INJECTION")
        print("="*60)
        
        # Generate threat sequence
        threat_sequence = (
            [True] * malicious_count + 
            [False] * benign_count
        )
        random.shuffle(threat_sequence)
        
        successful_sends = 0
        failed_sends = 0
        
        for i, is_malicious in enumerate(threat_sequence, 1):
            print(f"\n[{i:2d}/{num_threats}] ", end="")
            
            # Generate and send threat
            threat_data = self.generate_threat_log(is_malicious)
            
            if self.send_to_backend_api(threat_data):
                successful_sends += 1
            else:
                failed_sends += 1
            
            # Wait between requests
            if i < num_threats:  # Don't wait after the last one
                time.sleep(delay)
        
        print("\n" + "="*60)
        print("📊 SIMULATION COMPLETE - FINAL RESULTS")
        print("="*60)
        
        # Check final state
        time.sleep(5)  # Wait for processing
        final_db = self.verify_database_storage()
        
        print(f"✅ Threats Sent Successfully: {successful_sends}")
        print(f"❌ Failed Sends: {failed_sends}")
        print(f"📈 Database Changes:")
        print(f"   Total Threats: {initial_db['total_threats']} → {final_db['total_threats']} (+{final_db['total_threats'] - initial_db['total_threats']})")
        print(f"   Total Incidents: {initial_db['total_incidents']} → {final_db['total_incidents']} (+{final_db['total_incidents'] - initial_db['total_incidents']})")
        print(f"   Recent (24h): {initial_db['recent_threats_24h']} → {final_db['recent_threats_24h']} (+{final_db['recent_threats_24h'] - initial_db['recent_threats_24h']})")
        
        print(f"\n🎯 Next Steps:")
        print(f"   1. View threats in dashboard: {self.base_url.replace(':8000', ':3000')}")
        print(f"   2. Check AI model predictions in admin panel")
        print(f"   3. Monitor incidents correlation")
        print(f"   4. Review threat intelligence feeds")
        
        return {
            "successful_sends": successful_sends,
            "failed_sends": failed_sends,
            "database_changes": {
                "threats_added": final_db['total_threats'] - initial_db['total_threats'],
                "incidents_added": final_db['total_incidents'] - initial_db['total_incidents']
            }
        }

def main():
    parser = argparse.ArgumentParser(description="Threat Simulator for Sentient AI SOC")
    parser.add_argument("--count", "-c", type=int, default=20, help="Number of threats to generate (default: 20)")
    parser.add_argument("--malicious-ratio", "-m", type=float, default=0.7, help="Ratio of malicious to benign threats (default: 0.7)")
    parser.add_argument("--delay", "-d", type=float, default=2.0, help="Delay between threats in seconds (default: 2.0)")
    parser.add_argument("--base-url", "-u", type=str, default="http://localhost:8000", help="Base URL for the API (default: http://localhost:8000)")
    parser.add_argument("--quick-test", "-q", action="store_true", help="Run a quick test with 5 threats")
    
    args = parser.parse_args()
    
    if args.quick_test:
        args.count = 5
        args.delay = 1.0
        print("🚀 Quick Test Mode Enabled")
    
    # Validate arguments
    if args.malicious_ratio < 0 or args.malicious_ratio > 1:
        print("❌ Error: malicious-ratio must be between 0 and 1")
        sys.exit(1)
    
    if args.count <= 0:
        print("❌ Error: count must be positive")
        sys.exit(1)
    
    # Create simulator and run
    simulator = ThreatSimulator(args.base_url)
    
    try:
        results = simulator.simulate_attack_campaign(
            num_threats=args.count,
            malicious_ratio=args.malicious_ratio,
            delay=args.delay
        )
        
        print(f"\n🎉 Simulation completed successfully!")
        print(f"📊 Results: {results['successful_sends']}/{args.count} threats processed")
        
    except KeyboardInterrupt:
        print(f"\n⚠️ Simulation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Simulation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
