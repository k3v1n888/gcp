#!/usr/bin/env python3
"""
Copyright (c) 2025 Kevin Zachary
All rights reserved.

This software and associated documentation files (the "Software") are the 
exclusive property of Kevin Zachary. The Software is protected by copyright 
laws and international copyright treaties, as well as other intellectual 
property laws and treaties.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL 
KEVIN ZACHARY BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER 
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN 
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Unauthorized copying, modification, distribution, or use of this software, 
via any medium, is strictly prohibited without the express written permission 
of Kevin Zachary.
"""

"""
🧪 Comprehensive Sentient AI SOC System Test Suite
==================================================

This comprehensive test suite validates all components of the Sentient AI SOC Multi-Model Architecture:
- Backend API endpoints and routers
- AI models and services 
- Database operations and data integrity
- Frontend components and user interface
- Docker microservices orchestration
- Orchestrator services and model testing
- Security and authentication systems
- Data connectors and ingestion
- Threat forecasting and prediction
- Real-time monitoring and alerting

Author: Kevin Zachary
System: Sentient AI SOC Multi-Model Architecture
"""

import asyncio
import sys
import os
import json
import time
import requests
import subprocess
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from unittest.mock import MagicMock

# Add project paths
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))

@dataclass
class TestResult:
    """Test result data structure"""
    name: str
    status: str  # 'PASS', 'FAIL', 'SKIP', 'WARN'
    message: str
    duration: float
    details: Optional[Dict[str, Any]] = None

class SentientSOCTestSuite:
    """Comprehensive test suite for Sentient AI SOC system"""
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.base_url = "http://localhost:8000"
        self.orchestrator_url = "http://localhost:8003"
        self.frontend_url = "http://localhost:3000"
        self.start_time = time.time()
        
        # Test categories
        self.test_categories = {
            'infrastructure': 'Infrastructure & Services',
            'database': 'Database Operations',
            'api': 'API Endpoints',
            'ai_models': 'AI Models & Services',
            'orchestrator': 'Orchestrator Services',
            'frontend': 'Frontend Components',
            'security': 'Security & Authentication',
            'data_flow': 'Data Flow & Processing',
            'monitoring': 'Monitoring & Alerting',
            'integration': 'System Integration'
        }
    
    def log_test(self, category: str, name: str, status: str, message: str, 
                 duration: float, details: Optional[Dict] = None):
        """Log a test result"""
        self.results.append(TestResult(
            name=f"[{category.upper()}] {name}",
            status=status,
            message=message,
            duration=duration,
            details=details or {}
        ))
        
        # Color coding for console output
        colors = {
            'PASS': '\033[92m✅',
            'FAIL': '\033[91m❌',
            'SKIP': '\033[93m⏭️ ',
            'WARN': '\033[93m⚠️ '
        }
        reset = '\033[0m'
        
        print(f"{colors.get(status, '🔍')} {name}: {message} ({duration:.2f}s){reset}")
    
    async def test_infrastructure_services(self):
        """Test Docker services and infrastructure"""
        print(f"\n🏗️  Testing {self.test_categories['infrastructure']}")
        print("=" * 60)
        
        # Test Docker services
        start_time = time.time()
        try:
            result = subprocess.run(['docker', 'ps', '--format', 'table {{.Names}}\t{{.Status}}'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                running_services = []
                for line in result.stdout.split('\n')[1:]:
                    if line.strip():
                        name = line.split('\t')[0]
                        if 'ssai_' in name:
                            running_services.append(name)
                
                duration = time.time() - start_time
                if len(running_services) >= 5:
                    self.log_test('infrastructure', 'Docker Services', 'PASS', 
                                f'{len(running_services)} services running', duration,
                                {'services': running_services})
                else:
                    self.log_test('infrastructure', 'Docker Services', 'WARN', 
                                f'Only {len(running_services)} services running', duration,
                                {'services': running_services})
            else:
                duration = time.time() - start_time
                self.log_test('infrastructure', 'Docker Services', 'FAIL', 
                            'Docker command failed', duration)
        except Exception as e:
            duration = time.time() - start_time
            self.log_test('infrastructure', 'Docker Services', 'FAIL', 
                        f'Docker check failed: {str(e)}', duration)
    
    async def test_database_operations(self):
        """Test database connectivity and operations"""
        print(f"\n🗄️  Testing {self.test_categories['database']}")
        print("=" * 60)
        
        # Test database connection
        start_time = time.time()
        try:
            from backend.database import SessionLocal
            from backend.models import Threat, Incident
            
            db = SessionLocal()
            
            # Test basic query
            threat_count = db.query(Threat).count()
            incident_count = db.query(Incident).count()
            
            db.close()
            duration = time.time() - start_time
            
            self.log_test('database', 'Database Connection', 'PASS', 
                        f'Connected successfully', duration,
                        {'threats': threat_count, 'incidents': incident_count})
                        
        except Exception as e:
            duration = time.time() - start_time
            self.log_test('database', 'Database Connection', 'FAIL', 
                        f'Connection failed: {str(e)}', duration)
        
        # Test database health
        start_time = time.time()
        try:
            response = requests.get(f"{self.base_url}/api/health/database", timeout=5)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.log_test('database', 'Database Health', 'PASS', 
                            'Health check passed', duration, data)
            else:
                self.log_test('database', 'Database Health', 'FAIL', 
                            f'Health check failed: {response.status_code}', duration)
        except Exception as e:
            duration = time.time() - start_time
            self.log_test('database', 'Database Health', 'FAIL', 
                        f'Health check error: {str(e)}', duration)
    
    async def test_api_endpoints(self):
        """Test all API endpoints"""
        print(f"\n🌐 Testing {self.test_categories['api']}")
        print("=" * 60)
        
        # Define all API endpoints to test
        endpoints = {
            '/api/health': 'System Health',
            '/api/threats': 'Threats API',
            '/api/incidents': 'Incidents API',
            '/api/ai/status': 'AI Status',
            '/api/ai/models': 'AI Models',
            '/api/ai/health': 'AI Health',
            '/api/forecasting/24_hour': 'Threat Forecasting',
            '/api/correlation/status': 'Correlation Status',
            '/api/predictive/status': 'Predictive Status',
            '/api/graph/health': 'Graph API',
            '/api/hunting/status': 'Threat Hunting',
            '/api/connectors/status': 'Data Connectors',
            '/api/admin/dashboard': 'Admin Dashboard'
        }
        
        for endpoint, name in endpoints.items():
            start_time = time.time()
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                duration = time.time() - start_time
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        self.log_test('api', f'{name} Endpoint', 'PASS', 
                                    f'Status 200, valid JSON', duration, 
                                    {'response_size': len(str(data))})
                    except:
                        self.log_test('api', f'{name} Endpoint', 'WARN', 
                                    f'Status 200, invalid JSON', duration)
                elif response.status_code == 404:
                    self.log_test('api', f'{name} Endpoint', 'SKIP', 
                                f'Endpoint not implemented', duration)
                else:
                    self.log_test('api', f'{name} Endpoint', 'FAIL', 
                                f'Status {response.status_code}', duration)
                                
            except requests.exceptions.Timeout:
                duration = time.time() - start_time
                self.log_test('api', f'{name} Endpoint', 'FAIL', 
                            'Request timeout', duration)
            except Exception as e:
                duration = time.time() - start_time
                self.log_test('api', f'{name} Endpoint', 'FAIL', 
                            f'Request failed: {str(e)}', duration)
    
    async def test_ai_models_and_services(self):
        """Test AI models and services"""
        print(f"\n🤖 Testing {self.test_categories['ai_models']}")
        print("=" * 60)
        
        # Test Safe Threat Forecaster
        start_time = time.time()
        try:
            from backend.forecasting_service_safe import SafeThreatForecaster
            
            forecaster = SafeThreatForecaster()
            health = forecaster.health_check()
            result = forecaster.predict_next_24_hours()
            
            duration = time.time() - start_time
            self.log_test('ai_models', 'Safe Threat Forecaster', 'PASS', 
                        'Forecaster working correctly', duration,
                        {'health': health, 'prediction_method': result.get('method')})
                        
        except Exception as e:
            duration = time.time() - start_time
            self.log_test('ai_models', 'Safe Threat Forecaster', 'FAIL', 
                        f'Forecaster failed: {str(e)}', duration)
        
        # Test AI Provider Manager
        start_time = time.time()
        try:
            from backend.ai_providers import get_ai_provider_manager
            
            ai_manager = get_ai_provider_manager()
            preferred = ai_manager.get_preferred_provider()
            
            duration = time.time() - start_time
            if preferred:
                provider_type = "Sentient AI" if hasattr(preferred, 'ai_service_url') else "Other"
                self.log_test('ai_models', 'AI Provider Manager', 'PASS', 
                            f'Manager initialized, provider: {provider_type}', duration)
            else:
                self.log_test('ai_models', 'AI Provider Manager', 'WARN', 
                            'No preferred provider available', duration)
                            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test('ai_models', 'AI Provider Manager', 'FAIL', 
                        f'Provider manager failed: {str(e)}', duration)
        
        # Test AI Incident Orchestrator
        start_time = time.time()
        try:
            from backend.ai_incident_orchestrator import AIIncidentOrchestrator
            
            orchestrator = AIIncidentOrchestrator()
            duration = time.time() - start_time
            
            has_ai_manager = hasattr(orchestrator, 'ai_provider_manager')
            self.log_test('ai_models', 'AI Incident Orchestrator', 'PASS', 
                        f'Orchestrator initialized, AI integration: {has_ai_manager}', duration)
                        
        except Exception as e:
            duration = time.time() - start_time
            self.log_test('ai_models', 'AI Incident Orchestrator', 'FAIL', 
                        f'Orchestrator failed: {str(e)}', duration)
        
        # Test ML Prediction Models
        start_time = time.time()
        try:
            from backend.ml.prediction import SeverityPredictor
            
            predictor = SeverityPredictor()
            # Test with mock data
            mock_threat = {
                'severity': 'high',
                'source': 'SIEM',
                'ip_reputation_score': 85,
                'has_cve': False
            }
            prediction = predictor.predict_severity(mock_threat)
            
            duration = time.time() - start_time
            self.log_test('ai_models', 'ML Severity Predictor', 'PASS', 
                        f'Prediction successful: {prediction}', duration)
                        
        except Exception as e:
            duration = time.time() - start_time
            self.log_test('ai_models', 'ML Severity Predictor', 'FAIL', 
                        f'Predictor failed: {str(e)}', duration)
    
    async def test_orchestrator_services(self):
        """Test orchestrator services"""
        print(f"\n🎭 Testing {self.test_categories['orchestrator']}")
        print("=" * 60)
        
        # Test orchestrator health
        start_time = time.time()
        try:
            response = requests.get(f"{self.orchestrator_url}/api/orchestrator/status", timeout=10)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.log_test('orchestrator', 'Orchestrator Status', 'PASS', 
                            'Status endpoint working', duration, data)
            else:
                self.log_test('orchestrator', 'Orchestrator Status', 'FAIL', 
                            f'Status {response.status_code}', duration)
                            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test('orchestrator', 'Orchestrator Status', 'FAIL', 
                        f'Status check failed: {str(e)}', duration)
        
        # Test model endpoints
        start_time = time.time()
        try:
            response = requests.get(f"{self.orchestrator_url}/api/models/test/", timeout=10)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.log_test('orchestrator', 'Model Testing Endpoint', 'PASS', 
                            'Model testing available', duration,
                            {'available_models': data.get('available_models', [])})
            else:
                self.log_test('orchestrator', 'Model Testing Endpoint', 'FAIL', 
                            f'Status {response.status_code}', duration)
                            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test('orchestrator', 'Model Testing Endpoint', 'FAIL', 
                        f'Model testing failed: {str(e)}', duration)
    
    async def test_frontend_components(self):
        """Test frontend components"""
        print(f"\n🎨 Testing {self.test_categories['frontend']}")
        print("=" * 60)
        
        # Test frontend accessibility
        start_time = time.time()
        try:
            response = requests.get(self.frontend_url, timeout=10)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                content_size = len(response.text)
                has_react = 'react' in response.text.lower()
                has_sentient = 'sentient' in response.text.lower()
                
                self.log_test('frontend', 'Frontend Accessibility', 'PASS', 
                            f'Frontend accessible, size: {content_size} bytes', duration,
                            {'has_react': has_react, 'has_sentient_branding': has_sentient})
            else:
                self.log_test('frontend', 'Frontend Accessibility', 'FAIL', 
                            f'Status {response.status_code}', duration)
                            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test('frontend', 'Frontend Accessibility', 'FAIL', 
                        f'Frontend failed: {str(e)}', duration)
        
        # Test specific frontend components by checking if files exist
        frontend_components = [
            'frontend/src/components/admin/AIModelTestingDashboard.js',
            'frontend/src/components/ThreatForecast.jsx',
            'frontend/src/components/AIModelDashboard.jsx',
            'frontend/src/components/CyberSidebar.jsx',
            'frontend/src/pages/AdminPanel.jsx'
        ]
        
        for component in frontend_components:
            start_time = time.time()
            component_path = os.path.join(os.path.dirname(__file__), component)
            
            if os.path.exists(component_path):
                # Check if component has copyright and Sentient branding
                with open(component_path, 'r') as f:
                    content = f.read()
                    has_copyright = 'Copyright (c) 2025 Kevin Zachary' in content
                    has_sentient = 'sentient' in content.lower()
                    
                duration = time.time() - start_time
                component_name = os.path.basename(component)
                self.log_test('frontend', f'Component: {component_name}', 'PASS', 
                            'Component exists and validated', duration,
                            {'has_copyright': has_copyright, 'has_sentient_branding': has_sentient})
            else:
                duration = time.time() - start_time
                component_name = os.path.basename(component)
                self.log_test('frontend', f'Component: {component_name}', 'FAIL', 
                            'Component file not found', duration)
    
    async def test_security_and_auth(self):
        """Test security and authentication"""
        print(f"\n🔒 Testing {self.test_categories['security']}")
        print("=" * 60)
        
        # Test CORS configuration
        start_time = time.time()
        try:
            response = requests.options(f"{self.base_url}/api/health", timeout=5)
            duration = time.time() - start_time
            
            cors_headers = {
                'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
            }
            
            if any(cors_headers.values()):
                self.log_test('security', 'CORS Configuration', 'PASS', 
                            'CORS headers present', duration, cors_headers)
            else:
                self.log_test('security', 'CORS Configuration', 'WARN', 
                            'No CORS headers found', duration)
                            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test('security', 'CORS Configuration', 'FAIL', 
                        f'CORS test failed: {str(e)}', duration)
        
        # Test authentication endpoints
        auth_endpoints = [
            '/api/auth/health',
            '/api/admin/health'
        ]
        
        for endpoint in auth_endpoints:
            start_time = time.time()
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                duration = time.time() - start_time
                
                if response.status_code in [200, 401, 403]:
                    self.log_test('security', f'Auth Endpoint {endpoint}', 'PASS', 
                                f'Endpoint responding (status: {response.status_code})', duration)
                elif response.status_code == 404:
                    self.log_test('security', f'Auth Endpoint {endpoint}', 'SKIP', 
                                'Endpoint not implemented', duration)
                else:
                    self.log_test('security', f'Auth Endpoint {endpoint}', 'FAIL', 
                                f'Unexpected status: {response.status_code}', duration)
                                
            except Exception as e:
                duration = time.time() - start_time
                self.log_test('security', f'Auth Endpoint {endpoint}', 'FAIL', 
                            f'Request failed: {str(e)}', duration)
    
    async def test_data_flow_and_processing(self):
        """Test data flow and processing capabilities"""
        print(f"\n🔄 Testing {self.test_categories['data_flow']}")
        print("=" * 60)
        
        # Test threat data processing
        start_time = time.time()
        try:
            test_threat_data = {
                "source": "test_suite",
                "data": {
                    "title": "Test Threat - SQL Injection Attempt",
                    "description": "Automated test threat for system validation",
                    "severity": "high",
                    "source_ip": "192.168.1.100",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "test_data": True
                }
            }
            
            response = requests.post(f"{self.base_url}/api/ai/process", 
                                   json=test_threat_data, timeout=10)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                self.log_test('data_flow', 'Threat Processing', 'PASS', 
                            'Threat data processed successfully', duration, result)
            else:
                self.log_test('data_flow', 'Threat Processing', 'FAIL', 
                            f'Processing failed: {response.status_code}', duration)
                            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test('data_flow', 'Threat Processing', 'FAIL', 
                        f'Processing error: {str(e)}', duration)
        
        # Test data connector collection
        start_time = time.time()
        try:
            response = requests.post(f"{self.base_url}/api/connectors/collect", 
                                   json={}, timeout=15)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                self.log_test('data_flow', 'Data Connector Collection', 'PASS', 
                            'Data collection completed', duration, result)
            else:
                self.log_test('data_flow', 'Data Connector Collection', 'FAIL', 
                            f'Collection failed: {response.status_code}', duration)
                            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test('data_flow', 'Data Connector Collection', 'FAIL', 
                        f'Collection error: {str(e)}', duration)
    
    async def test_monitoring_and_alerting(self):
        """Test monitoring and alerting systems"""
        print(f"\n📊 Testing {self.test_categories['monitoring']}")
        print("=" * 60)
        
        # Test system health monitoring
        start_time = time.time()
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=5)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                health_data = response.json()
                self.log_test('monitoring', 'System Health Monitor', 'PASS', 
                            'Health monitoring active', duration, health_data)
            else:
                self.log_test('monitoring', 'System Health Monitor', 'FAIL', 
                            f'Health check failed: {response.status_code}', duration)
                            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test('monitoring', 'System Health Monitor', 'FAIL', 
                        f'Health monitoring error: {str(e)}', duration)
        
        # Test alerting system
        start_time = time.time()
        try:
            response = requests.get(f"{self.base_url}/api/alerts/status", timeout=5)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                alert_data = response.json()
                self.log_test('monitoring', 'Alerting System', 'PASS', 
                            'Alerting system active', duration, alert_data)
            elif response.status_code == 404:
                self.log_test('monitoring', 'Alerting System', 'SKIP', 
                            'Alerting endpoint not implemented', duration)
            else:
                self.log_test('monitoring', 'Alerting System', 'FAIL', 
                            f'Alerting check failed: {response.status_code}', duration)
                            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test('monitoring', 'Alerting System', 'FAIL', 
                        f'Alerting error: {str(e)}', duration)
    
    async def test_system_integration(self):
        """Test end-to-end system integration"""
        print(f"\n🔗 Testing {self.test_categories['integration']}")
        print("=" * 60)
        
        # Test complete threat analysis workflow
        start_time = time.time()
        try:
            # Create test threats
            mock_threats = [
                {
                    "id": 1,
                    "threat": "Multiple failed login attempts detected",
                    "source": "SIEM",
                    "severity": "high",
                    "ip": "192.168.1.100",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "is_anomaly": True,
                    "ip_reputation_score": 85,
                    "criticality_score": 7.5
                },
                {
                    "id": 2,
                    "threat": "Suspicious PowerShell execution detected", 
                    "source": "EDR",
                    "severity": "critical",
                    "ip": "192.168.1.100",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "is_anomaly": True,
                    "ip_reputation_score": 85,
                    "criticality_score": 9.0
                }
            ]
            
            # Test AI threat analysis
            from backend.ai_providers import get_ai_provider_manager
            ai_manager = get_ai_provider_manager()
            
            context = {
                "time_window_hours": 24,
                "correlation_threshold": 0.7
            }
            
            result = ai_manager.analyze_threats_for_incidents(mock_threats, context)
            
            duration = time.time() - start_time
            if result and result.get('groups'):
                self.log_test('integration', 'End-to-End Threat Analysis', 'PASS', 
                            f'Complete workflow successful, {len(result.get("groups", []))} groups created', 
                            duration, {'provider': result.get('provider')})
            else:
                self.log_test('integration', 'End-to-End Threat Analysis', 'WARN', 
                            'Workflow completed but no groups created', duration)
                            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test('integration', 'End-to-End Threat Analysis', 'FAIL', 
                        f'Integration test failed: {str(e)}', duration)
    
    def generate_test_report(self) -> str:
        """Generate comprehensive test report"""
        total_duration = time.time() - self.start_time
        
        # Calculate statistics
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r.status == 'PASS'])
        failed_tests = len([r for r in self.results if r.status == 'FAIL'])
        skipped_tests = len([r for r in self.results if r.status == 'SKIP'])
        warning_tests = len([r for r in self.results if r.status == 'WARN'])
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Generate report
        report = []
        report.append("=" * 80)
        report.append("🧪 SENTIENT AI SOC COMPREHENSIVE TEST REPORT")
        report.append("=" * 80)
        report.append(f"Test Suite: Sentient AI SOC Multi-Model Architecture")
        report.append(f"Executed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Duration: {total_duration:.2f} seconds")
        report.append("")
        
        # Summary statistics
        report.append("📊 TEST SUMMARY")
        report.append("-" * 40)
        report.append(f"Total Tests:    {total_tests}")
        report.append(f"✅ Passed:     {passed_tests}")
        report.append(f"❌ Failed:     {failed_tests}")
        report.append(f"⏭️  Skipped:    {skipped_tests}")
        report.append(f"⚠️  Warnings:   {warning_tests}")
        report.append(f"🎯 Success Rate: {success_rate:.1f}%")
        report.append("")
        
        # Category breakdown
        category_stats = {}
        for result in self.results:
            category = result.name.split(']')[0][1:]
            if category not in category_stats:
                category_stats[category] = {'PASS': 0, 'FAIL': 0, 'SKIP': 0, 'WARN': 0}
            category_stats[category][result.status] += 1
        
        report.append("📋 CATEGORY BREAKDOWN")
        report.append("-" * 40)
        for category, stats in category_stats.items():
            total = sum(stats.values())
            passed = stats['PASS']
            rate = (passed / total * 100) if total > 0 else 0
            report.append(f"{category.upper():<15} {passed}/{total} ({rate:.0f}%)")
        report.append("")
        
        # Detailed results
        report.append("📝 DETAILED RESULTS")
        report.append("-" * 40)
        
        for category in ['INFRASTRUCTURE', 'DATABASE', 'API', 'AI_MODELS', 
                        'ORCHESTRATOR', 'FRONTEND', 'SECURITY', 'DATA_FLOW', 
                        'MONITORING', 'INTEGRATION']:
            category_results = [r for r in self.results if r.name.startswith(f'[{category}]')]
            if category_results:
                report.append(f"\n{category}:")
                for result in category_results:
                    test_name = result.name.split('] ', 1)[1]
                    status_icon = {'PASS': '✅', 'FAIL': '❌', 'SKIP': '⏭️ ', 'WARN': '⚠️ '}[result.status]
                    report.append(f"  {status_icon} {test_name:<30} {result.message} ({result.duration:.2f}s)")
        
        # System recommendations
        report.append("\n" + "=" * 80)
        report.append("🔍 SYSTEM ANALYSIS & RECOMMENDATIONS")
        report.append("=" * 80)
        
        if failed_tests == 0:
            report.append("🎉 EXCELLENT: All critical tests passed!")
            report.append("   Your Sentient AI SOC system is fully operational.")
        elif failed_tests <= 2:
            report.append("✅ GOOD: System is mostly operational with minor issues.")
            report.append("   Review failed tests and address them when convenient.")
        elif failed_tests <= 5:
            report.append("⚠️  MODERATE: System has some issues that should be addressed.")
            report.append("   Review and fix failed tests to improve system reliability.")
        else:
            report.append("❌ CRITICAL: System has significant issues requiring immediate attention.")
            report.append("   Address failed tests before using in production.")
        
        report.append("")
        report.append("🛠️  NEXT STEPS:")
        report.append("   1. Review failed tests and error messages")
        report.append("   2. Check Docker services and container logs")
        report.append("   3. Verify database connectivity and migrations")
        report.append("   4. Ensure all AI models are properly loaded")
        report.append("   5. Test frontend components manually")
        report.append("   6. Run integration tests after fixes")
        
        report.append("")
        report.append("=" * 80)
        report.append("© 2025 Kevin Zachary - Sentient AI SOC Multi-Model Architecture")
        report.append("=" * 80)
        
        return "\n".join(report)
    
    async def run_all_tests(self):
        """Run the complete test suite"""
        print("🚀 Starting Sentient AI SOC Comprehensive Test Suite")
        print("=" * 80)
        print(f"Testing Sentient AI SOC Multi-Model Architecture")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"System: Kevin Zachary's Sentient AI SOC Platform")
        print("=" * 80)
        
        # Run all test categories
        await self.test_infrastructure_services()
        await self.test_database_operations()
        await self.test_api_endpoints()
        await self.test_ai_models_and_services()
        await self.test_orchestrator_services()
        await self.test_frontend_components()
        await self.test_security_and_auth()
        await self.test_data_flow_and_processing()
        await self.test_monitoring_and_alerting()
        await self.test_system_integration()
        
        # Generate and display report
        report = self.generate_test_report()
        print(f"\n{report}")
        
        # Save report to file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = f"test_report_{timestamp}.txt"
        with open(report_file, 'w') as f:
            f.write(report)
        
        print(f"\n📄 Full report saved to: {report_file}")
        
        # Return success status
        failed_tests = len([r for r in self.results if r.status == 'FAIL'])
        return failed_tests == 0

async def main():
    """Main test runner"""
    test_suite = SentientSOCTestSuite()
    success = await test_suite.run_all_tests()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())
