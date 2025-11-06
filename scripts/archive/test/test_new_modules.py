#!/usr/bin/env python3
"""
Test script for Asset Management and Transport API endpoints
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

# Test data
ASSET_TEST_DATA = {
    "asset_code": "TEST-ASSET-001",
    "asset_name": "Test Equipment",
    "description": "Test equipment for validation",
    "category": "Equipment",
    "subcategory": "Testing",
    "manufacturer": "Test Manufacturer",
    "model": "TM-2024",
    "serial_number": "SN123456",
    "year_of_manufacture": 2024,
    "purchase_cost": 25000.00,
    "purchase_date": "2024-01-15T00:00:00Z",
    "location": "Warehouse A",
    "department": "Manufacturing",
    "status": "active",
    "condition": "good",
    "specifications": "Test specifications",
    "useful_life_years": 10,
    "salvage_value": 2500.00,
    "notes": "Test asset for API validation"
}

CARRIER_TEST_DATA = {
    "carrier_code": "TEST-CARRIER-001",
    "carrier_name": "Test Transport Co.",
    "carrier_type": "road",
    "contact_person": "Test Contact",
    "phone": "+1-555-0123",
    "email": "test@transport.com",
    "city": "Test City",
    "state": "Test State",
    "tracking_capability": True,
    "real_time_updates": False,
    "is_preferred": False,
    "notes": "Test carrier for API validation"
}

def test_endpoints():
    """Test Asset Management and Transport API endpoints"""
    
    print("🚀 Starting API Endpoint Tests")
    print("=" * 50)
    
    # Test Asset Management Endpoints
    print("\n📊 Testing Asset Management Endpoints")
    print("-" * 30)
    
    try:
        # Test asset dashboard
        response = requests.get(f"{API_BASE}/assets/dashboard/summary")
        print(f"✅ Asset Dashboard: {response.status_code}")
        if response.status_code == 200:
            dashboard = response.json()
            print(f"   Total Assets: {dashboard.get('total_assets', 0)}")
        
        # Test get assets
        response = requests.get(f"{API_BASE}/assets/")
        print(f"✅ Get Assets: {response.status_code}")
        
        # Test asset categories
        response = requests.get(f"{API_BASE}/assets/categories/")
        print(f"✅ Asset Categories: {response.status_code}")
        
        # Test maintenance schedules
        response = requests.get(f"{API_BASE}/assets/maintenance-schedules/")
        print(f"✅ Maintenance Schedules: {response.status_code}")
        
        # Test due maintenance
        response = requests.get(f"{API_BASE}/assets/maintenance-schedules/due/")
        print(f"✅ Due Maintenance: {response.status_code}")
        
        # Test maintenance records
        response = requests.get(f"{API_BASE}/assets/maintenance-records/")
        print(f"✅ Maintenance Records: {response.status_code}")
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the FastAPI server is running on localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Asset Management Test Error: {e}")
        return False
    
    # Test Transport Management Endpoints
    print("\n🚛 Testing Transport Management Endpoints")
    print("-" * 30)
    
    try:
        # Test transport dashboard
        response = requests.get(f"{API_BASE}/transport/dashboard/summary")
        print(f"✅ Transport Dashboard: {response.status_code}")
        if response.status_code == 200:
            dashboard = response.json()
            print(f"   Total Carriers: {dashboard.get('total_carriers', 0)}")
        
        # Test get carriers
        response = requests.get(f"{API_BASE}/transport/carriers/")
        print(f"✅ Get Carriers: {response.status_code}")
        
        # Test get routes
        response = requests.get(f"{API_BASE}/transport/routes/")
        print(f"✅ Get Routes: {response.status_code}")
        
        # Test get freight rates
        response = requests.get(f"{API_BASE}/transport/freight-rates/")
        print(f"✅ Get Freight Rates: {response.status_code}")
        
        # Test get shipments
        response = requests.get(f"{API_BASE}/transport/shipments/")
        print(f"✅ Get Shipments: {response.status_code}")
        
    except Exception as e:
        print(f"❌ Transport Management Test Error: {e}")
        return False
    
    print("\n🎉 All endpoint tests completed!")
    print("=" * 50)
    
    return True

def test_create_operations():
    """Test create operations (requires authentication)"""
    
    print("\n🔧 Testing Create Operations")
    print("-" * 30)
    print("Note: These tests require authentication tokens")
    print("Run these manually through the API documentation at /docs")
    
    print("\nSample Asset Data:")
    print(json.dumps(ASSET_TEST_DATA, indent=2))
    
    print("\nSample Carrier Data:")
    print(json.dumps(CARRIER_TEST_DATA, indent=2))

if __name__ == "__main__":
    success = test_endpoints()
    test_create_operations()
    
    if success:
        print("\n✅ Basic endpoint connectivity tests passed!")
        print("🔗 Visit http://localhost:8000/docs to test authenticated endpoints")
    else:
        print("\n❌ Some tests failed. Check the server status.")