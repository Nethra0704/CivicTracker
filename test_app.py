"""
Verification test suite for CivicTrack-AI
Tests models, AI engine, journey planner, and Flask routes.
"""

import os
import json
from app import app
from models import get_all_reports, get_report_stats, verify_user
from ai_engine import get_ai_engine
from route_engine import plan_safe_journey

def run_tests():
    print(">>> 1. Testing Models & Database...")
    reports = get_all_reports()
    assert len(reports) > 0, "No reports found in DB"
    print(f"    Found {len(reports)} reports in DB.")
    
    stats = get_report_stats()
    print(f"    Stats: {stats}")
    assert stats['total'] > 0
    
    user = verify_user('citizen1', 'password123')
    assert user is not None, "citizen1 auth failed"
    print(f"    citizen1 verified successfully: {user['username']} ({user['role']})")
    
    auth_user = verify_user('authority_pwd', 'admin123')
    assert auth_user is not None, "authority auth failed"
    print(f"    authority_pwd verified: {auth_user['username']} ({auth_user['role']})")

    print("\n>>> 2. Testing AI Engine...")
    ai = get_ai_engine()
    test_desc = "Massive 20cm deep pothole crater in middle of road causing fatal accidents and skidding."
    res = ai.analyze(None, test_desc, "Pothole")
    print(f"    AI Severity: {res['severity_score']}, Priority: {res['priority']}, Confidence: {res['confidence_score']}%")
    assert res['priority'] == 'High', f"Expected High priority, got {res['priority']}"
    assert res['severity_score'] >= 70

    print("\n>>> 3. Testing Safe Journey Planner Engine...")
    plan = plan_safe_journey("Gandhipuram, Coimbatore", "Peelamedu, Coimbatore")
    print(f"    Route: {plan['start_location']} -> {plan['destination']}")
    print(f"    Distance: {plan['distance_km']} km, Travel Time: {plan['travel_time']}")
    print(f"    Safety Level: {plan['safety_level']}, Tolls: {plan['toll_count']}, Traffic: {plan['traffic_level']}")
    print(f"    Hazards Along Corridor: {len(plan['hazards'])}")
    assert len(plan['waypoints']) > 0
    assert plan['safety_level'] in ['Safe', 'Moderate Risk', 'High Risk']

    print("\n>>> 4. Testing Flask Endpoints with Test Client...")
    client = app.test_client()
    
    # Home
    resp = client.get('/')
    assert resp.status_code == 200
    assert b"CivicTrack" in resp.data
    print("    GET / -> 200 OK")

    # API Reports
    resp = client.get('/api/reports')
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data['success'] is True
    print(f"    GET /api/reports -> 200 OK ({data['count']} reports)")

    # API Plan Journey
    resp = client.post('/api/journey/plan', json={
        'start_location': 'RS Puram, Coimbatore',
        'destination': 'Coimbatore Airport, Coimbatore'
    })
    assert resp.status_code == 200
    plan_data = json.loads(resp.data)
    assert plan_data['success'] is True
    print(f"    POST /api/journey/plan -> 200 OK (Safety: {plan_data['plan']['safety_level']})")

    # API AI Preview
    resp = client.post('/api/ai/analyze-preview', json={
        'description': 'Small hairline cosmetic surface crack',
        'category': 'Road Crack'
    })
    assert resp.status_code == 200
    preview_data = json.loads(resp.data)
    assert preview_data['success'] is True
    print(f"    POST /api/ai/analyze-preview -> 200 OK (Priority: {preview_data['analysis']['priority']})")

    print("\n==========================================")
    print("[SUCCESS] ALL 4 TEST SUITES PASSED FLAWLESSLY!")
    print("==========================================")

if __name__ == '__main__':
    run_tests()
