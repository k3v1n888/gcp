#!/usr/bin/env python3
"""
Frontend Integration Test for XAI and Analyst Feedback
Tests the complete integration between backend API and frontend components
"""

import requests
import json


def test_threat_detail_with_xai():
    """Test that threat detail includes proper XAI structure for frontend"""
    print("🎯 Testing Threat Detail with XAI Integration")
    print("=" * 50)
    
    # Test threat detail endpoint
    response = requests.get("http://localhost:8001/api/threats/1")
    if response.status_code != 200:
        print(f"❌ API Error: {response.status_code}")
        return False
    
    data = response.json()
    
    # Check basic threat info
    print(f"📍 Threat ID: {data.get('id')}")
    print(f"🔍 Description: {data.get('description')}")
    print(f"⚡ Severity: {data.get('severity')}")
    
    # Check XAI explanation structure (expected by ModelExplanation.jsx)
    if 'xai_explanation' not in data:
        print("❌ Missing xai_explanation in response")
        return False
    
    xai = data['xai_explanation']
    print(f"\n🧠 XAI Explanation Check:")
    
    # Check required fields for frontend
    required_fields = ['base_value', 'features', 'shap_values']
    for field in required_fields:
        if field in xai:
            print(f"  ✅ {field}: Present")
            if field == 'features':
                print(f"     Features count: {len(xai[field])}")
                print(f"     Feature names: {list(xai[field].keys())}")
            elif field == 'shap_values':
                print(f"     SHAP values length: {len(xai[field][0]) if xai[field] else 0}")
            elif field == 'base_value':
                print(f"     Base value: {xai[field]}")
        else:
            print(f"  ❌ {field}: Missing")
            return False
    
    # Check MITRE ATT&CK integration
    if 'mitre_attck' in data:
        mitre = data['mitre_attck']
        print(f"\n🎯 MITRE ATT&CK Integration:")
        print(f"  Technique: {mitre.get('technique_id')} - {mitre.get('technique_name')}")
        print(f"  Tactic: {mitre.get('tactic')} ({mitre.get('tactic_id')})")
        print(f"  ✅ MITRE data present")
    else:
        print("❌ Missing MITRE ATT&CK data")
        return False
    
    # Check analyst feedback
    if 'analyst_feedback' in data and data['analyst_feedback']:
        feedback = data['analyst_feedback']
        print(f"\n📝 Analyst Feedback:")
        print(f"  Type: {feedback.get('feedback_type')}")
        print(f"  Confidence: {feedback.get('confidence_level')}/5")
        print(f"  ✅ Feedback data present")
    else:
        print("📝 No analyst feedback (this is optional)")
    
    print("\n✅ Threat detail structure is compatible with frontend!")
    return True


def test_analyst_feedback_submission():
    """Test analyst feedback submission"""
    print("\n🎯 Testing Analyst Feedback Submission")
    print("=" * 50)
    
    feedback_data = {
        "feedback_type": "confirmation",
        "explanation": "Frontend integration test - XAI explanation is working correctly",
        "confidence_level": 5,
        "analyst_id": "frontend_test_analyst"
    }
    
    response = requests.post(
        "http://localhost:8001/api/threats/1/feedback",
        json=feedback_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            print(f"✅ Feedback submitted successfully (ID: {result.get('feedback_id')})")
            return True
        else:
            print(f"❌ Feedback submission failed: {result.get('message')}")
    else:
        print(f"❌ API error: {response.status_code}")
    
    return False


def test_response_plan():
    """Test response plan endpoint"""
    print("\n🎯 Testing AI Response Plan Generation")
    print("=" * 50)
    
    response = requests.get("http://localhost:8001/api/threats/1/response-plan")
    if response.status_code != 200:
        print(f"❌ API Error: {response.status_code}")
        return False
    
    data = response.json()
    
    if 'response_plan' in data:
        plan = data['response_plan']
        print("✅ Response plan generated")
        print(f"  Immediate actions: {len(plan.get('immediate_actions', []))}")
        print(f"  Investigation steps: {len(plan.get('investigation_steps', []))}")
        print(f"  Containment measures: {len(plan.get('containment_measures', []))}")
        return True
    else:
        print("❌ Missing response plan")
        return False


def test_frontend_endpoints():
    """Test all endpoints that frontend uses"""
    print("\n🎯 Testing All Frontend Endpoints")
    print("=" * 50)
    
    endpoints = [
        ("/api/threats", "Threats list"),
        ("/api/threats/1", "Threat detail"),
        ("/api/threats/1/feedback", "Threat feedback"),
        ("/api/threats/1/response-plan", "Response plan"),
        ("/api/analyst/feedback/summary", "Feedback summary")
    ]
    
    for endpoint, description in endpoints:
        try:
            if endpoint == "/api/threats/1/feedback" and "feedback" in description:
                # This is a GET request for feedback history
                response = requests.get(f"http://localhost:8001{endpoint}")
            else:
                response = requests.get(f"http://localhost:8001{endpoint}")
            
            if response.status_code == 200:
                print(f"  ✅ {description}: Working")
            else:
                print(f"  ❌ {description}: Error {response.status_code}")
        except Exception as e:
            print(f"  ❌ {description}: Exception {e}")


def main():
    """Run all tests"""
    print("🚀 Frontend Integration Test Suite")
    print("🎯 Testing XAI Model & Analyst Feedback Integration")
    print("=" * 60)
    
    # Test core functionality
    threat_detail_ok = test_threat_detail_with_xai()
    feedback_ok = test_analyst_feedback_submission()
    response_plan_ok = test_response_plan()
    
    # Test all endpoints
    test_frontend_endpoints()
    
    print("\n" + "=" * 60)
    print("📋 INTEGRATION TEST SUMMARY")
    print("=" * 60)
    
    if threat_detail_ok and feedback_ok and response_plan_ok:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Frontend should now display:")
        print("   • XAI explanations with feature impacts")
        print("   • MITRE ATT&CK technique mappings")
        print("   • Analyst feedback collection forms")
        print("   • AI response plan recommendations")
        print("\n🔗 Visit the frontend at: http://localhost:3000/dashboard")
        print("🎯 Click on any threat to see the XAI analysis")
    else:
        print("❌ Some tests failed - check the errors above")


if __name__ == "__main__":
    main()
