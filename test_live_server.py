"""
Live HTTP verification of CivicTrack-AI server
"""
import time
import requests
import subprocess
import sys

def verify_live_server():
    python_exe = r"C:\Users\ADMIN\AppData\Local\Python\pythoncore-3.14-64\python.exe"
    app_script = r"C:\Users\ADMIN\.gemini\antigravity\scratch\roadintel-ai\app.py"
    
    print("Starting Flask process...")
    proc = subprocess.Popen([python_exe, app_script], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(3)
    
    try:
        # 1. Test Home page
        r1 = requests.get("http://127.0.0.1:5000/", timeout=5)
        print(f"GET / -> Status {r1.status_code}")
        assert r1.status_code == 200
        assert "CivicTrack" in r1.text, "Branding CivicTrack missing from home page"
        assert "Detect My Location" in r1.text, "Detect My Location button missing from home page"
        assert "leaflet" in r1.text.lower(), "Leaflet missing from home page"
        print("  [PASS] Home page contains CivicTrack-AI, Leaflet, and Detect My Location")
        
        # 2. Test API Reports
        r2 = requests.get("http://127.0.0.1:5000/api/reports", timeout=5)
        print(f"GET /api/reports -> Status {r2.status_code}")
        assert r2.status_code == 200
        data = r2.json()
        assert data.get('success') is True
        reports = data.get('reports', [])
        assert len(reports) > 0, "No reports returned from API"
        first = reports[0]
        print(f"  [PASS] API reports returned {len(reports)} entries. Sample location: {first.get('location_name')}")
        assert "latitude" in first and "longitude" in first, "Coordinates missing in report"
        
        # 3. Test Journey Planner page
        r3 = requests.get("http://127.0.0.1:5000/journey-planner", timeout=5)
        print(f"GET /journey-planner -> Status {r3.status_code}")
        assert r3.status_code == 200
        assert "Coimbatore" in r3.text, "Coimbatore preset missing in journey planner"
        print("  [PASS] Safe Journey Planner page rendered with Coimbatore route presets")
        
        print("\n==========================================")
        print("[SUCCESS] LIVE HTTP VERIFICATION PASSED!")
        print("==========================================")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except Exception:
            proc.kill()

if __name__ == '__main__':
    verify_live_server()
