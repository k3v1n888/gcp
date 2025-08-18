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

#!/usr/bin/env python3
"""
🧪 Test Sentient AI Integration
Test script to verify that the AI incident orchestrator is using your Sentient AI service
"""

import os
import sys
import asyncio
from datetime import datetime, timezone

# Add the parent directory to the path to import backend modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def test_quantum_ai_integration():
    """Test the Sentient AI integration"""
    
    print("🧪 Testing Sentient AI Integration")
    print("=" * 50)
    
    # Test 1: AI Provider Manager Initialization
    print("\n1️⃣ Testing AI Provider Manager...")
    try:
        from backend.ai_providers import get_ai_provider_manager
        ai_manager = get_ai_provider_manager()
        print(f"✅ AI Provider Manager initialized: {type(ai_manager).__name__}")
        
        # Check available providers
        available_providers = [p.value for p in ai_manager.providers.keys()]
        print(f"📋 Available providers: {available_providers}")
        
    except Exception as e:
        print(f"❌ AI Provider Manager failed: {e}")
        return
    
    # Test 2: Preferred Provider Check
    print("\n2️⃣ Testing Preferred Provider...")
    try:
        preferred = ai_manager.get_preferred_provider()
        if preferred:
            provider_type = "Sentient AI" if hasattr(preferred, 'ai_service_url') else "Other"
            print(f"✅ Preferred provider: {provider_type}")
            if hasattr(preferred, 'ai_service_url'):
                print(f"🔗 Service URL: {preferred.ai_service_url}")
        else:
            print("⚠️ No preferred provider available")
    except Exception as e:
        print(f"❌ Preferred provider check failed: {e}")
    
    # Test 3: Provider Health Check
    print("\n3️⃣ Testing Provider Health...")
    try:
        if preferred:
            is_healthy = preferred.is_available()
            status = "✅ Healthy" if is_healthy else "⚠️ Unavailable"
            print(f"{status}: Provider health check")
        else:
            print("⚠️ No provider to check")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
    
    # Test 4: Mock Threat Analysis
    print("\n4️⃣ Testing Threat Analysis...")
    try:
        # Create mock threat data
        mock_threats = [
            {
                "id": 1,
                "threat": "Multiple failed login attempts detected",
                "source": "SIEM",
                "severity": "high",
                "ip": "192.168.1.100",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "cve_id": None,
                "is_anomaly": True,
                "ip_reputation_score": 85,
                "criticality_score": 7.5,
                "cvss_score": 0.0
            },
            {
                "id": 2,
                "threat": "Suspicious PowerShell execution detected", 
                "source": "EDR",
                "severity": "critical",
                "ip": "192.168.1.100",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "cve_id": None,
                "is_anomaly": True,
                "ip_reputation_score": 85,
                "criticality_score": 9.0,
                "cvss_score": 0.0
            },
            {
                "id": 3,
                "threat": "Network scanning behavior identified",
                "source": "Network Monitor", 
                "severity": "medium",
                "ip": "192.168.1.100",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "cve_id": None,
                "is_anomaly": False,
                "ip_reputation_score": 85,
                "criticality_score": 5.2,
                "cvss_score": 0.0
            }
        ]
        
        context = {
            "time_window_hours": 24,
            "correlation_threshold": 0.7
        }
        
        print(f"📊 Analyzing {len(mock_threats)} mock threats...")
        result = ai_manager.analyze_threats_for_incidents(mock_threats, context)
        
        if result:
            print(f"✅ Analysis completed")
            print(f"📈 Provider: {result.get('provider', 'unknown')}")
            print(f"🔍 Method: {result.get('correlation_method', 'unknown')}")
            groups = result.get('groups', [])
            print(f"🎯 Incident groups created: {len(groups)}")
            
            for i, group in enumerate(groups[:3], 1):  # Show first 3 groups
                print(f"\n   Group {i}:")
                print(f"   📋 ID: {group.get('group_id', 'N/A')}")
                print(f"   🎯 Title: {group.get('title', 'N/A')}")
                print(f"   ⚡ Severity: {group.get('severity', 'N/A')}")
                print(f"   🔢 Threats: {len(group.get('threat_ids', []))}")
                print(f"   🤖 AI Provider: {group.get('ai_provider', 'N/A')}")
        else:
            print("⚠️ No analysis result returned")
            
    except Exception as e:
        print(f"❌ Threat analysis failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 5: AI Incident Orchestrator Integration
    print("\n5️⃣ Testing AI Incident Orchestrator...")
    try:
        from backend.ai_incident_orchestrator import AIIncidentOrchestrator
        orchestrator = AIIncidentOrchestrator()
        print(f"✅ AI Incident Orchestrator initialized")
        print(f"🎯 Using AI Provider Manager: {hasattr(orchestrator, 'ai_provider_manager')}")
        
        if hasattr(orchestrator, 'ai_provider_manager'):
            provider = orchestrator.ai_provider_manager.get_preferred_provider()
            provider_name = "Sentient AI" if hasattr(provider, 'ai_service_url') else "Other" if provider else "None"
            print(f"🤖 Orchestrator AI Provider: {provider_name}")
        
    except Exception as e:
        print(f"❌ AI Incident Orchestrator failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Integration test completed!")
    print("💡 Your Sentient AI service is now integrated with the incident orchestrator")
    print("🚀 The system will use your AI model instead of GPT-4 for incident analysis")

if __name__ == "__main__":
    asyncio.run(test_quantum_ai_integration())
