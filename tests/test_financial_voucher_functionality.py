"""
Test financial voucher numbering system and startup functionality
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


def test_payment_voucher_next_number_endpoint_exists():
    """Test that payment voucher next number endpoint exists"""
    client = TestClient(app)
    
    response = client.get("/api/v1/payment-vouchers/next-number")
    
    # Should return 401 or 403 for unauthenticated request, not 404
    assert response.status_code in [401, 403, 422], f"Expected auth error, got {response.status_code}"


def test_receipt_voucher_next_number_endpoint_exists():
    """Test that receipt voucher next number endpoint exists"""
    client = TestClient(app)
    
    response = client.get("/api/v1/receipt-vouchers/next-number")
    
    # Should return 401 or 403 for unauthenticated request, not 404
    assert response.status_code in [401, 403, 422], f"Expected auth error, got {response.status_code}"


def test_journal_voucher_next_number_endpoint_exists():
    """Test that journal voucher next number endpoint exists"""
    client = TestClient(app)
    
    response = client.get("/api/v1/journal-vouchers/next-number")
    
    # Should return 401 or 403 for unauthenticated request, not 404
    assert response.status_code in [401, 403, 422], f"Expected auth error, got {response.status_code}"


def test_contra_voucher_next_number_endpoint_exists():
    """Test that contra voucher next number endpoint exists"""
    client = TestClient(app)
    
    response = client.get("/api/v1/contra-vouchers/next-number")
    
    # Should return 401 or 403 for unauthenticated request, not 404
    assert response.status_code in [401, 403, 422], f"Expected auth error, got {response.status_code}"


def test_financial_voucher_list_endpoints_exist():
    """Test that all financial voucher list endpoints exist"""
    client = TestClient(app)
    
    voucher_types = [
        "payment-vouchers",
        "receipt-vouchers", 
        "journal-vouchers",
        "contra-vouchers"
    ]
    
    for voucher_type in voucher_types:
        response = client.get(f"/api/v1/{voucher_type}/")
        
        # Should return 401 or 403 for unauthenticated request, not 404
        assert response.status_code in [401, 403, 422], f"Expected auth error for {voucher_type}, got {response.status_code}"


def test_financial_voucher_create_endpoints_exist():
    """Test that all financial voucher create endpoints exist"""
    client = TestClient(app)
    
    voucher_types = [
        "payment-vouchers",
        "receipt-vouchers", 
        "journal-vouchers",
        "contra-vouchers"
    ]
    
    for voucher_type in voucher_types:
        # Test with empty payload to verify endpoint exists
        response = client.post(f"/api/v1/{voucher_type}/", json={})
        
        # Should return 401, 403, or 422 for unauthenticated/invalid request, not 404
        assert response.status_code in [401, 403, 422], f"Expected auth/validation error for {voucher_type}, got {response.status_code}"


def test_voucher_number_service_functionality():
    """Test VoucherNumberService basic functionality"""
    
    try:
        from app.services.voucher_service import VoucherNumberService
        
        # Test that generate_voucher_number method exists and has correct signature
        import inspect
        sig = inspect.signature(VoucherNumberService.generate_voucher_number)
        expected_params = ['db', 'prefix', 'organization_id', 'model']
        
        actual_params = list(sig.parameters.keys())
        assert actual_params == expected_params, f"Expected params {expected_params}, got {actual_params}"
        
    except ImportError as e:
        pytest.fail(f"Failed to import VoucherNumberService: {e}")


def test_financial_voucher_routes_registered():
    """Test that financial voucher routes are properly registered"""
    from app.main import app
    
    # Get all registered routes
    registered_routes = []
    for route in app.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            for method in route.methods:
                if method != 'HEAD':  # Skip HEAD method
                    registered_routes.append((method, route.path))
    
    # Expected financial voucher routes
    expected_financial_routes = [
        ("GET", "payment-vouchers"),
        ("POST", "payment-vouchers"),
        ("GET", "payment-vouchers/next-number"),
        ("GET", "receipt-vouchers"),
        ("POST", "receipt-vouchers"), 
        ("GET", "receipt-vouchers/next-number"),
        ("GET", "journal-vouchers"),
        ("POST", "journal-vouchers"),
        ("GET", "journal-vouchers/next-number"),
        ("GET", "contra-vouchers"),
        ("POST", "contra-vouchers"),
        ("GET", "contra-vouchers/next-number"),
    ]
    
    # Check that financial voucher routes exist
    for expected_method, expected_path_part in expected_financial_routes:
        matching_routes = [
            (method, path) for method, path in registered_routes 
            if method == expected_method and expected_path_part in path
        ]
        
        assert len(matching_routes) > 0, f"Route {expected_method} with path containing '{expected_path_part}' not found"


if __name__ == "__main__":
    # Run the tests
    test_payment_voucher_next_number_endpoint_exists()
    test_receipt_voucher_next_number_endpoint_exists()
    test_journal_voucher_next_number_endpoint_exists()
    test_contra_voucher_next_number_endpoint_exists()
    test_financial_voucher_list_endpoints_exist()
    test_financial_voucher_create_endpoints_exist()
    test_voucher_number_service_functionality()
    test_financial_voucher_routes_registered()
    print("All financial voucher tests passed!")