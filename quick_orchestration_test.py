#!/usr/bin/env python3
"""
Quick test to verify AI Orchestration is working
"""
import requests
import json

def test_orchestration():
    print("🧪 Testing AI Orchestration System...")
    
    # Test backend health
    try:
        response = requests.get("http://localhost:8001/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is healthy")
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Backend connection failed: {e}")
        return
    
    # Test orchestration endpoint
    try:
        response = requests.post(
            "http://localhost:8001/api/v1/incidents/orchestrate",
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ AI Orchestration endpoint working!")
            print(f"   Threats analyzed: {result.get('threats_analyzed', 0)}")
            print(f"   Incidents created: {result.get('incidents_created', 0)}")
            print(f"   Status: {result.get('status')}")
            
            # Test frontend
            try:
                frontend_response = requests.get("http://localhost:3000/", timeout=5)
                if frontend_response.status_code == 200:
                    print("✅ Frontend is accessible")
                    print("\n🎉 AI Orchestration system is working!")
                    print("   Go to http://localhost:3000/dashboard")
                    print("   Click 'Incidents' → 'AI Orchestration' button")
                else:
                    print(f"❌ Frontend not accessible: {frontend_response.status_code}")
            except Exception as e:
                print(f"⚠️ Frontend check failed: {e}")
                
        else:
            print(f"❌ Orchestration failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Orchestration test failed: {e}")

if __name__ == "__main__":
    test_orchestration()
