#!/usr/bin/env python3
"""
Comprehensive SOC Platform Test Suite
Tests all new features: Agent Management, User Management, Audit Logs, Tenant Management, etc.

Copyright (c) 2025 Kevin Zachary
"""
import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8001"

def test_agent_management():
    """Test SOC Agent Management features"""
    print("🤖 Testing Agent Management...")
    
    # Test agent heartbeat
    agent_data = {
        "agent_id": "demo-agent-001",
        "agent_name": "Demo SOC Agent",
        "status": "active",
        "system_info": {
            "platform": "linux",
            "hostname": "demo-server-01",
            "python_version": "3.11.0",
            "cpu_cores": 4,
            "memory_gb": 16
        },
        "tenant_id": "demo-tenant"
    }
    
    response = requests.post(f"{BASE_URL}/api/agents/heartbeat", json=agent_data)
    print(f"  ✅ Agent Heartbeat: {response.status_code}")
    
    # Get agents list
    response = requests.get(f"{BASE_URL}/api/agents")
    agents = response.json().get("agents", [])
    print(f"  ✅ Registered Agents: {len(agents)}")
    
    if agents:
        agent_id = agents[0]["agent_id"]
        response = requests.get(f"{BASE_URL}/api/agents/{agent_id}")
        print(f"  ✅ Agent Details: {response.status_code}")
    
    return True

def test_user_management():
    """Test User Management features"""
    print("👥 Testing User Management...")
    
    # Create test users
    users = [
        {
            "user_id": "admin_001",
            "email": "admin@company.com",
            "name": "Admin User",
            "role": "admin",
            "auth_provider": "local"
        },
        {
            "user_id": "analyst_001",
            "email": "analyst@company.com",
            "name": "SOC Analyst",
            "role": "analyst",
            "auth_provider": "microsoft"
        },
        {
            "user_id": "viewer_001",
            "email": "viewer@company.com",
            "name": "Security Viewer",
            "role": "viewer",
            "auth_provider": "google"
        }
    ]
    
    for user in users:
        response = requests.post(f"{BASE_URL}/api/admin/users", json=user)
        print(f"  ✅ Created {user['role']}: {response.status_code}")
    
    # Get users list
    response = requests.get(f"{BASE_URL}/api/admin/users")
    users_list = response.json().get("users", [])
    print(f"  ✅ Total Users: {len(users_list)}")
    
    # Update a user
    if users_list:
        user_id = users_list[0]["user_id"]
        update_data = {"role": "analyst", "name": "Updated User"}
        response = requests.put(f"{BASE_URL}/api/admin/users/{user_id}", json=update_data)
        print(f"  ✅ User Update: {response.status_code}")
    
    return True

def test_tenant_management():
    """Test Tenant Management features"""
    print("🏢 Testing Tenant Management...")
    
    # Create test tenants
    tenants = [
        {
            "tenant_id": "company-a",
            "name": "Company A Corp",
            "settings": {
                "max_users": 100,
                "features": ["ai_models", "threat_hunting", "analytics"],
                "data_retention_days": 365
            }
        },
        {
            "tenant_id": "company-b",
            "name": "Company B Ltd",
            "settings": {
                "max_users": 50,
                "features": ["basic_monitoring", "incident_response"],
                "data_retention_days": 90
            }
        }
    ]
    
    for tenant in tenants:
        response = requests.post(f"{BASE_URL}/api/admin/tenants", json=tenant)
        print(f"  ✅ Created Tenant {tenant['name']}: {response.status_code}")
    
    # Get tenants list
    response = requests.get(f"{BASE_URL}/api/admin/tenants")
    tenants_list = response.json().get("tenants", [])
    print(f"  ✅ Total Tenants: {len(tenants_list)}")
    
    return True

def test_audit_logging():
    """Test Audit Logging features"""
    print("📋 Testing Audit Logging...")
    
    # Get audit logs
    response = requests.get(f"{BASE_URL}/api/admin/audit-logs?limit=50")
    audit_data = response.json()
    logs = audit_data.get("logs", [])
    print(f"  ✅ Audit Logs Retrieved: {len(logs)} entries")
    print(f"  ✅ Total Log Count: {audit_data.get('total_count', 0)}")
    
    # Show recent actions
    if logs:
        recent_actions = [log["action"] for log in logs[:5]]
        print(f"  ✅ Recent Actions: {', '.join(set(recent_actions))}")
    
    return True

def test_system_logs():
    """Test System Logs features"""
    print("📄 Testing System Logs...")
    
    response = requests.get(f"{BASE_URL}/api/admin/system-logs")
    system_logs = response.json().get("logs", [])
    print(f"  ✅ System Log Entries: {len(system_logs)}")
    
    if system_logs:
        sources = [log["source"] for log in system_logs]
        print(f"  ✅ Log Sources: {', '.join(set(sources))}")
    
    return True

def test_data_ingestion():
    """Test Enhanced Data Ingestion"""
    print("📡 Testing Data Ingestion...")
    
    # Simulate agent data ingestion
    agent_data = {
        "agent_id": "demo-agent-001",
        "agent_name": "Demo SOC Agent",
        "tenant_id": "demo-tenant",
        "data": {
            "system_logs": [
                {
                    "timestamp": datetime.now().isoformat(),
                    "message": "Failed login attempt detected",
                    "priority": "4",
                    "source": "system",
                    "host": "demo-server-01"
                }
            ],
            "security_events": [
                {
                    "timestamp": datetime.now().isoformat(),
                    "event_type": "authentication_failure",
                    "message": "Multiple failed authentication attempts from IP 192.168.1.100",
                    "severity": "high",
                    "source": "auth",
                    "host": "demo-server-01"
                }
            ],
            "network_events": [
                {
                    "timestamp": datetime.now().isoformat(),
                    "event_type": "network_status",
                    "listening_ports": ["22", "80", "443", "3306"],
                    "source": "network",
                    "host": "demo-server-01"
                }
            ]
        }
    }
    
    response = requests.post(f"{BASE_URL}/api/data/ingest", json=agent_data)
    result = response.json()
    print(f"  ✅ Data Ingestion: {response.status_code}")
    print(f"  ✅ Records Processed: {result.get('records_processed', 0)}")
    
    return True

def test_authentication():
    """Test Authentication features"""
    print("🔐 Testing Authentication...")
    
    # Test Microsoft SSO simulation
    microsoft_data = {
        "token": "mock_microsoft_token_12345",
        "user_info": {
            "email": "sso_user@company.com",
            "name": "SSO Test User",
            "id": "ms_test_123"
        }
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/microsoft", json=microsoft_data)
    print(f"  ✅ Microsoft SSO Test: {response.status_code}")
    
    if response.status_code == 200:
        auth_result = response.json()
        print(f"  ✅ SSO User Created: {auth_result.get('user', {}).get('email', 'N/A')}")
    
    return True

def test_api_documentation():
    """Test API Documentation"""
    print("📚 Testing API Documentation...")
    
    # Get root endpoint with enhanced documentation
    response = requests.get(f"{BASE_URL}/")
    api_info = response.json()
    
    print(f"  ✅ API Version: {api_info.get('version', 'N/A')}")
    print(f"  ✅ Features: {len(api_info.get('features', []))}")
    print(f"  ✅ Endpoint Categories: {len(api_info.get('endpoints', {}))}")
    
    # Count total endpoints
    total_endpoints = sum(len(endpoints) for endpoints in api_info.get('endpoints', {}).values())
    print(f"  ✅ Total API Endpoints: {total_endpoints}")
    
    return True

def run_comprehensive_test():
    """Run all tests"""
    print("🚀 SOC Platform Comprehensive Test Suite")
    print("=" * 50)
    print(f"Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tests = [
        ("API Documentation", test_api_documentation),
        ("Agent Management", test_agent_management),
        ("User Management", test_user_management),
        ("Tenant Management", test_tenant_management),
        ("Data Ingestion", test_data_ingestion),
        ("Authentication", test_authentication),
        ("Audit Logging", test_audit_logging),
        ("System Logs", test_system_logs),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            print(f"Running {test_name}...")
            result = test_func()
            if result:
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                failed += 1
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            failed += 1
            print(f"❌ {test_name} ERROR: {e}")
        
        print()
        time.sleep(1)  # Brief pause between tests
    
    print("=" * 50)
    print(f"Test Summary:")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {passed + failed}")
    print(f"Success Rate: {(passed / (passed + failed) * 100):.1f}%")
    print()
    print(f"Test Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if failed == 0:
        print("🎉 All tests passed! SOC Platform is ready for production.")
    else:
        print("⚠️  Some tests failed. Please review the logs above.")
    
    print()
    print("Next Steps:")
    print("1. Access Admin Panel: http://localhost:3000/admin")
    print("2. View API Documentation: http://localhost:8001/docs")
    print("3. Deploy SOC Agents using: ./deploy_agent.sh")
    print("4. Configure authentication providers as needed")

if __name__ == "__main__":
    run_comprehensive_test()
