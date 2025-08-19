#!/usr/bin/env python3
"""
Complete system status check for AI Orchestration
"""
import requests
import time

def check_all_services():
    print("🔍 AI Orchestration System Status Check")
    print("=" * 50)
    
    services = [
        ("Frontend", "http://localhost:3000/", "GET"),
        ("Backend Health", "http://localhost:8001/api/health", "GET"),
        ("Backend Orchestration", "http://localhost:8001/api/v1/incidents/orchestrate", "POST"),
        ("Backend Incidents", "http://localhost:8001/api/incidents", "GET"),
    ]
    
    all_good = True
    
    for name, url, method in services:
        try:
            if method == "GET":
                response = requests.get(url, timeout=5)
            else:
                response = requests.post(url, 
                    headers={"Content-Type": "application/json"}, 
                    timeout=10)
            
            if response.status_code == 200:
                print(f"✅ {name}: OK ({response.status_code})")
                if "orchestrate" in url:
                    data = response.json()
                    print(f"   └─ Created {data.get('incidents_created', 0)} incidents")
            else:
                print(f"❌ {name}: Failed ({response.status_code})")
                all_good = False
                
        except Exception as e:
            print(f"❌ {name}: Error ({e})")
            all_good = False
    
    print("\n" + "=" * 50)
    if all_good:
        print("🎉 ALL SERVICES WORKING!")
        print("\n📋 Next Steps:")
        print("1. Go to http://localhost:3000/dashboard")
        print("2. Click 'Incidents' tab")
        print("3. Click 'AI Orchestration' tab")
        print("4. Click the purple 'Run AI Orchestration' button")
        print("5. Should work without errors now!")
    else:
        print("⚠️  Some services have issues")
    
    return all_good

if __name__ == "__main__":
    check_all_services()
