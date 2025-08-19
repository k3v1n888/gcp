#!/usr/bin/env python3
"""
Test if frontend can access the orchestration endpoint
"""
import requests
import json

def test_frontend_backend_connection():
    print("🧪 Testing Frontend → Backend Connection...")
    
    # Test what the frontend should be calling
    frontend_url = "http://localhost:8001/api/v1/incidents/orchestrate"
    
    try:
        # Simulate frontend request
        response = requests.post(
            frontend_url,
            headers={
                "Content-Type": "application/json",
                "Origin": "http://localhost:3000"  # Simulate browser origin
            },
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Frontend → Backend connection WORKING!")
            print(f"   Status: {result.get('status')}")
            print(f"   Incidents created: {result.get('incidents_created')}")
            print(f"   Threats analyzed: {result.get('threats_analyzed')}")
            print("\n🎉 The AI Orchestration button should now work!")
            print("   Try clicking it in the browser at http://localhost:3000/dashboard")
            return True
        else:
            print(f"❌ Backend returned: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_frontend_backend_connection()
