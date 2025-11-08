"""
Test CORS hardening - ensuring CORS headers are present on all responses including errors
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_cors_on_404_error():
    """Test that CORS headers are present on 404 error responses"""
    response = client.get(
        "/api/v1/nonexistent-endpoint",
        headers={"Origin": "http://localhost:3000"}
    )
    
    assert response.status_code == 404
    assert "access-control-allow-origin" in response.headers
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
    assert response.headers["access-control-allow-credentials"] == "true"


def test_cors_on_500_error_simulation():
    """
    Test that CORS headers are present even when an internal server error occurs.
    We'll test this by calling an endpoint that might fail.
    """
    # Try to access a protected endpoint without authentication - should give 401, not 500
    # But the CORS headers should still be present
    response = client.get(
        "/api/v1/rbac/permissions",
        headers={"Origin": "http://localhost:3000"}
    )
    
    # Should have CORS headers regardless of status code
    assert "access-control-allow-origin" in response.headers
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
    assert response.headers["access-control-allow-credentials"] == "true"


def test_cors_preflight_options_request():
    """Test that OPTIONS preflight request returns proper CORS headers"""
    response = client.options(
        "/api/v1/rbac/permissions",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Authorization, Content-Type"
        }
    )
    
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
    assert response.headers["access-control-allow-credentials"] == "true"
    assert "GET" in response.headers.get("access-control-allow-methods", "")


def test_cors_with_invalid_origin():
    """Test that CORS headers are not added for origins not in allowed list"""
    response = client.get(
        "/api/v1/health",
        headers={"Origin": "http://evil-site.com"}
    )
    
    # Should not include CORS headers for invalid origin
    # The response should still succeed but without CORS headers
    assert response.status_code == 200
    assert "access-control-allow-origin" not in response.headers


def test_cors_with_valid_origin_http_127():
    """Test CORS with http://127.0.0.1:3000 origin"""
    response = client.get(
        "/api/v1/health",
        headers={"Origin": "http://127.0.0.1:3000"}
    )
    
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://127.0.0.1:3000"
    assert response.headers["access-control-allow-credentials"] == "true"


def test_cors_on_unauthorized_request():
    """Test that CORS headers are present on 401 Unauthorized responses"""
    # Try to access a protected endpoint without proper authentication
    response = client.post(
        "/api/v1/auth/login/email",
        json={"email": "nonexistent@example.com", "password": "wrong"},
        headers={"Origin": "http://localhost:3000"}
    )
    
    # Should be unauthorized but with CORS headers
    assert response.status_code == 401
    assert "access-control-allow-origin" in response.headers
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
    assert response.headers["access-control-allow-credentials"] == "true"


def test_health_endpoint_with_cors():
    """Test that health endpoint works and includes CORS headers"""
    response = client.get(
        "/api/v1/health",
        headers={"Origin": "http://localhost:3000"}
    )
    
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
    assert response.headers["access-control-allow-credentials"] == "true"
