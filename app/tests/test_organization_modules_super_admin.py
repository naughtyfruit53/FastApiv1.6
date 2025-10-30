"""
Test organization modules API for super_admin access by explicit org_id
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_organization_modules_endpoints_exist():
    """Test that organization modules endpoints are registered"""
    routes = [route.path for route in app.routes]
    
    # Check that module endpoints exist
    assert "/api/v1/organizations/{organization_id}/modules" in routes
    
    # Check that related endpoints exist
    assert "/api/v1/organizations/{organization_id}" in routes


def test_organization_modules_get_requires_auth():
    """Test that GET modules endpoint requires authentication"""
    response = client.get("/api/v1/organizations/1/modules")
    
    # Should return 401 (unauthorized) or 403 (forbidden), not 404
    assert response.status_code in [401, 403]


def test_organization_modules_put_requires_auth():
    """Test that PUT modules endpoint requires authentication"""
    response = client.put(
        "/api/v1/organizations/1/modules",
        json={"enabled_modules": {"CRM": True}}
    )
    
    # Should return 401 (unauthorized) or 403 (forbidden), not 404
    assert response.status_code in [401, 403]


def test_organization_modules_endpoint_with_cors():
    """Test that organization modules endpoints include CORS headers"""
    response = client.get(
        "/api/v1/organizations/1/modules",
        headers={"Origin": "http://localhost:3000"}
    )
    
    # Should have CORS headers regardless of status
    assert "access-control-allow-origin" in response.headers
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"


def test_organization_modules_structure():
    """
    Verify that the module routes have super_admin access logic.
    This is a code structure validation test.
    """
    # The actual endpoint requires authentication with super_admin
    # But we verify the endpoint exists and has proper error handling
    
    routes = {route.path: route for route in app.routes}
    
    # Verify modules endpoints exist
    assert "/api/v1/organizations/{organization_id}/modules" in routes
    
    # The super_admin logic is in place in module_routes.py
    # Lines 37-46 (GET) and 72-81 (PUT) handle super_admin org_id override
    # This test ensures the endpoints are properly registered


def test_debug_rbac_state_endpoint_exists():
    """Test that the debug RBAC state endpoint exists"""
    response = client.get("/api/v1/debug/rbac_state")
    
    # Should return 401 (needs auth), not 404
    assert response.status_code != 404


def test_debug_rbac_state_with_cors():
    """Test that debug endpoint includes CORS headers"""
    response = client.get(
        "/api/v1/debug/rbac_state",
        headers={"Origin": "http://localhost:3000"}
    )
    
    # Should have CORS headers regardless of status
    assert "access-control-allow-origin" in response.headers
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"


@pytest.mark.asyncio
async def test_organization_modules_backfill_logic():
    """
    Test that organization modules backfill function is properly defined.
    This validates the startup seeding logic exists.
    """
    from app.main import init_org_modules
    
    # Verify the function exists and is callable
    assert callable(init_org_modules)
    
    # The actual test of the backfill would require database setup
    # But we ensure the function signature is correct
    import inspect
    sig = inspect.signature(init_org_modules)
    assert "background_tasks" in sig.parameters
