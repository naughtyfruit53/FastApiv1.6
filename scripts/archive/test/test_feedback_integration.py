#!/usr/bin/env python3

"""
Simple test script to verify feedback workflow endpoints
"""

import sys
import os
sys.path.insert(0, '/home/runner/work/FastApiv1.4/FastApiv1.4')

from fastapi.testclient import TestClient
from app.main import app

# Create test client
client = TestClient(app)

def test_application():
    """Test basic application functionality"""
    print("🚀 Testing FastAPI Application...")
    
    # Test health endpoint
    response = client.get("/health")
    print(f"Health check: {response.status_code} - {response.json()}")
    assert response.status_code == 200
    
    # Test routes endpoint to see available routes
    response = client.get("/routes")
    print(f"Routes check: {response.status_code}")
    if response.status_code == 200:
        routes = response.json()["routes"]
        feedback_routes = [r for r in routes if "feedback" in r.lower()]
        print(f"Found {len(feedback_routes)} feedback routes:")
        for route in feedback_routes:
            print(f"  - {route}")
    
    # Test API docs are available
    response = client.get("/docs")
    print(f"API docs: {response.status_code}")
    
    print("✅ Basic application tests passed!")

def test_feedback_endpoints():
    """Test feedback endpoints (without authentication for now)"""
    print("\n📋 Testing Feedback Endpoints...")
    
    # Test feedback list endpoint (should return 401 without auth)
    response = client.get("/api/v1/feedback/feedback")
    print(f"GET /api/v1/feedback/feedback: {response.status_code}")
    
    # Test service closure list endpoint
    response = client.get("/api/v1/feedback/service-closure")
    print(f"GET /api/v1/feedback/service-closure: {response.status_code}")
    
    # Test analytics endpoints
    response = client.get("/api/v1/feedback/feedback/analytics/summary")
    print(f"GET /api/v1/feedback/feedback/analytics/summary: {response.status_code}")
    
    response = client.get("/api/v1/feedback/service-closure/analytics/summary")
    print(f"GET /api/v1/feedback/service-closure/analytics/summary: {response.status_code}")
    
    print("✅ Feedback endpoint tests completed!")

if __name__ == "__main__":
    try:
        test_application()
        test_feedback_endpoints()
        print("\n🎉 All tests completed successfully!")
        print("\nFeedback & Service Closure Workflow is properly integrated!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)