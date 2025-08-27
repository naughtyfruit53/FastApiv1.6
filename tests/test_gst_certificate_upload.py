"""
Test GST certificate upload functionality for customers and vendors
"""

import pytest
import os
import tempfile
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.core.database import get_db
from app.models.base import Customer, Vendor, CustomerFile, VendorFile, Organization, User


def test_customer_gst_certificate_upload_endpoint_exists():
    """Test that customer GST certificate upload endpoints are properly registered"""
    client = TestClient(app)
    
    # Test that the endpoint exists and returns appropriate error for unauthenticated request
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
        tmp_file.write(b'%PDF-1.4 fake pdf content')
        tmp_file_path = tmp_file.name
    
    try:
        with open(tmp_file_path, 'rb') as f:
            response = client.post(
                "/api/v1/customers/1/files",
                files={"file": ("test.pdf", f, "application/pdf")},
                data={"file_type": "gst_certificate"}
            )
        
        # Should return 401 or 403 for unauthenticated request, not 404
        assert response.status_code in [401, 403, 422], f"Expected auth error, got {response.status_code}"
        
    finally:
        os.unlink(tmp_file_path)


def test_vendor_gst_certificate_upload_endpoint_exists():
    """Test that vendor GST certificate upload endpoints are properly registered"""
    client = TestClient(app)
    
    # Test that the endpoint exists and returns appropriate error for unauthenticated request
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
        tmp_file.write(b'%PDF-1.4 fake pdf content')
        tmp_file_path = tmp_file.name
    
    try:
        with open(tmp_file_path, 'rb') as f:
            response = client.post(
                "/api/v1/vendors/1/files",
                files={"file": ("test.pdf", f, "application/pdf")},
                data={"file_type": "gst_certificate"}
            )
        
        # Should return 401 or 403 for unauthenticated request, not 404
        assert response.status_code in [401, 403, 422], f"Expected auth error, got {response.status_code}"
        
    finally:
        os.unlink(tmp_file_path)


def test_customer_file_retrieval_endpoint_exists():
    """Test that customer file retrieval endpoints are properly registered"""
    client = TestClient(app)
    
    # Test that the endpoint exists
    response = client.get("/api/v1/customers/1/files")
    
    # Should return 401 or 403 for unauthenticated request, not 404
    assert response.status_code in [401, 403, 422], f"Expected auth error, got {response.status_code}"


def test_vendor_file_retrieval_endpoint_exists():
    """Test that vendor file retrieval endpoints are properly registered"""
    client = TestClient(app)
    
    # Test that the endpoint exists
    response = client.get("/api/v1/vendors/1/files")
    
    # Should return 401 or 403 for unauthenticated request, not 404
    assert response.status_code in [401, 403, 422], f"Expected auth error, got {response.status_code}"


def test_routes_registration():
    """Test that all expected GST certificate routes are registered"""
    from app.main import app
    
    expected_routes = [
        ("POST", "/api/v1/customers/{customer_id}/files"),
        ("GET", "/api/v1/customers/{customer_id}/files"),
        ("GET", "/api/v1/customers/{customer_id}/files/{file_id}/download"),
        ("DELETE", "/api/v1/customers/{customer_id}/files/{file_id}"),
        ("POST", "/api/v1/vendors/{vendor_id}/files"),
        ("GET", "/api/v1/vendors/{vendor_id}/files"),
        ("GET", "/api/v1/vendors/{vendor_id}/files/{file_id}/download"),
        ("DELETE", "/api/v1/vendors/{vendor_id}/files/{file_id}"),
    ]
    
    # Get all registered routes
    registered_routes = []
    for route in app.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            for method in route.methods:
                if method != 'HEAD':  # Skip HEAD method
                    registered_routes.append((method, route.path))
    
    # Check that our expected routes are registered
    for expected_method, expected_path in expected_routes:
        # Convert parameterized path to check if similar routes exist
        base_path = expected_path.replace('{customer_id}', '').replace('{vendor_id}', '').replace('{file_id}', '')
        
        # Find matching routes
        matching_routes = [
            (method, path) for method, path in registered_routes 
            if method == expected_method and (
                'customers' in path and 'files' in path if 'customers' in expected_path
                else 'vendors' in path and 'files' in path
            )
        ]
        
        assert len(matching_routes) > 0, f"Route {expected_method} {expected_path} not found in registered routes"


def test_voucher_number_service_import():
    """Test that VoucherNumberService is properly imported in financial vouchers"""
    
    # Test that we can import VoucherNumberService from the voucher service
    try:
        from app.services.voucher_service import VoucherNumberService
        assert VoucherNumberService is not None
        assert hasattr(VoucherNumberService, 'generate_voucher_number')
    except ImportError as e:
        pytest.fail(f"Failed to import VoucherNumberService: {e}")
    
    # Test that payment voucher can import VoucherNumberService
    try:
        from app.api.v1.vouchers.payment_voucher import VoucherNumberService
        assert VoucherNumberService is not None
    except ImportError as e:
        pytest.fail(f"Failed to import VoucherNumberService in payment_voucher: {e}")


if __name__ == "__main__":
    # Run the tests
    test_customer_gst_certificate_upload_endpoint_exists()
    test_vendor_gst_certificate_upload_endpoint_exists()
    test_customer_file_retrieval_endpoint_exists()
    test_vendor_file_retrieval_endpoint_exists()
    test_routes_registration()
    test_voucher_number_service_import()
    print("All GST certificate upload tests passed!")