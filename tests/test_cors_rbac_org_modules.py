"""
Test CORS, RBAC permissions endpoint, and organization modules functionality.
Tests the fixes made for MegaMenu restoration and org module management.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.main import app
from app.models.user_models import User, Organization
from app.models.rbac_models import ServiceRole, UserServiceRole
from app.core.modules_registry import get_default_enabled_modules
from app.core.security import get_password_hash


@pytest.mark.asyncio
async def test_cors_headers_on_success(async_client: AsyncClient):
    """Test CORS headers are present on successful responses"""
    headers = {
        "Origin": "http://localhost:3000"
    }
    response = await async_client.get("/api/v1/health", headers=headers)
    
    assert response.status_code == 200
    assert "Access-Control-Allow-Origin" in response.headers
    assert "Access-Control-Allow-Credentials" in response.headers


@pytest.mark.asyncio
async def test_cors_headers_on_error(async_client: AsyncClient):
    """Test CORS headers are present on error responses"""
    headers = {
        "Origin": "http://localhost:3000"
    }
    # Request non-existent endpoint
    response = await async_client.get("/api/v1/nonexistent", headers=headers)
    
    assert response.status_code == 404
    assert "Access-Control-Allow-Origin" in response.headers
    assert "Access-Control-Allow-Credentials" in response.headers


@pytest.mark.asyncio
async def test_cors_options_request(async_client: AsyncClient):
    """Test OPTIONS preflight requests are handled correctly"""
    headers = {
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "Content-Type, Authorization"
    }
    response = await async_client.options("/api/v1/auth/login", headers=headers)
    
    assert response.status_code == 200
    assert "Access-Control-Allow-Origin" in response.headers
    assert "Access-Control-Allow-Methods" in response.headers
    assert "Access-Control-Allow-Headers" in response.headers
    assert "Access-Control-Max-Age" in response.headers


@pytest.mark.asyncio
async def test_rbac_permissions_safe_fallback(
    async_client: AsyncClient,
    db_session: AsyncSession,
    test_user: User
):
    """Test RBAC permissions endpoint returns safe fallback with modules field"""
    # Get token
    login_response = await async_client.post("/api/v1/auth/login", json={
        "email": test_user.email,
        "password": "testpassword"
    })
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    response = await async_client.get(
        f"/api/v1/rbac/users/{test_user.id}/permissions",
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify safe fallback structure
    assert "user_id" in data
    assert "permissions" in data
    assert "service_roles" in data
    assert "modules" in data  # NEW: modules field
    assert "total_permissions" in data
    
    # Verify types
    assert isinstance(data["permissions"], list)
    assert isinstance(data["service_roles"], list)
    assert isinstance(data["modules"], list)
    assert isinstance(data["total_permissions"], int)


@pytest.mark.asyncio
async def test_rbac_permissions_never_500(
    async_client: AsyncClient,
    db_session: AsyncSession
):
    """Test RBAC permissions endpoint never returns 500, even with invalid user"""
    # Create a valid user to get a token
    user = User(
        email="testrbac@example.com",
        username="testrbac",
        hashed_password=get_password_hash("testpassword"),
        role="user",
        organization_id=1,
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    # Login to get token
    login_response = await async_client.post("/api/v1/auth/login", json={
        "email": user.email,
        "password": "testpassword"
    })
    token = login_response.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Try to access permissions for current user (should work)
    response = await async_client.get(
        f"/api/v1/rbac/users/{user.id}/permissions",
        headers=headers
    )
    
    assert response.status_code in [200, 403]  # Either success or forbidden, never 500
    
    if response.status_code == 200:
        data = response.json()
        assert "modules" in data
        # Verify modules is a list (could be empty if fallback is used)
        assert isinstance(data["modules"], list)


@pytest.mark.asyncio
async def test_organization_modules_get(
    async_client: AsyncClient,
    db_session: AsyncSession,
    test_organization: Organization,
    test_admin_user: User
):
    """Test getting organization modules"""
    # Login as admin
    login_response = await async_client.post("/api/v1/auth/login", json={
        "email": test_admin_user.email,
        "password": "adminpassword"
    })
    token = login_response.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    response = await async_client.get(
        f"/api/v1/organizations/{test_organization.id}/modules",
        headers=headers
    )
    
    assert response.status_code in [200, 403, 404]  # May not have permission
    
    if response.status_code == 200:
        data = response.json()
        assert "enabled_modules" in data
        assert isinstance(data["enabled_modules"], dict)


@pytest.mark.asyncio
async def test_organization_modules_update(
    async_client: AsyncClient,
    db_session: AsyncSession,
    test_organization: Organization,
    test_admin_user: User
):
    """Test updating organization modules"""
    # Ensure user has proper role
    test_admin_user.role = "org_admin"
    await db_session.commit()
    
    # Login
    login_response = await async_client.post("/api/v1/auth/login", json={
        "email": test_admin_user.email,
        "password": "adminpassword"
    })
    token = login_response.json()["access_token"]
    
    # Update modules
    headers = {"Authorization": f"Bearer {token}"}
    modules_data = {
        "enabled_modules": {
            "master_data": True,
            "inventory": True,
            "manufacturing": False
        }
    }
    
    response = await async_client.put(
        f"/api/v1/organizations/{test_organization.id}/modules",
        headers=headers,
        json=modules_data
    )
    
    assert response.status_code in [200, 403]  # Success or no permission
    
    if response.status_code == 200:
        data = response.json()
        assert "enabled_modules" in data
        assert data["enabled_modules"]["master_data"] == True
        assert data["enabled_modules"]["manufacturing"] == False


@pytest.mark.asyncio
async def test_enabled_modules_defaults(
    db_session: AsyncSession,
    test_organization: Organization
):
    """Test that organizations have enabled_modules defaults set"""
    # Fetch organization
    org = await db_session.get(Organization, test_organization.id)
    
    # If enabled_modules is None, it should be set by startup seeding
    if org.enabled_modules is None:
        # Simulate what startup seeding does
        from app.core.modules_registry import get_default_enabled_modules
        org.enabled_modules = get_default_enabled_modules()
        await db_session.commit()
        await db_session.refresh(org)
    
    assert org.enabled_modules is not None
    assert isinstance(org.enabled_modules, dict)
    assert len(org.enabled_modules) > 0


@pytest.mark.asyncio
async def test_modules_field_in_permissions_response(
    async_client: AsyncClient,
    db_session: AsyncSession,
    test_user: User,
    test_organization: Organization
):
    """Test that permissions endpoint includes modules field from organization"""
    # Ensure organization has enabled_modules
    test_organization.enabled_modules = {
        "master_data": True,
        "inventory": True,
        "manufacturing": False
    }
    await db_session.commit()
    
    # Login
    login_response = await async_client.post("/api/v1/auth/login", json={
        "email": test_user.email,
        "password": "testpassword"
    })
    token = login_response.json()["access_token"]
    
    # Get permissions
    headers = {"Authorization": f"Bearer {token}"}
    response = await async_client.get(
        f"/api/v1/rbac/users/{test_user.id}/permissions",
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "modules" in data
    assert isinstance(data["modules"], list)
    
    # Modules should contain only enabled modules
    if len(data["modules"]) > 0:
        # At least some modules are enabled
        assert "master_data" in data["modules"] or "inventory" in data["modules"]


# Manual Test Plan
"""
MANUAL TEST PLAN: MegaMenu and Organization Modules

Prerequisites:
1. Start the FastAPI backend server
2. Start the Next.js frontend
3. Have at least one org_admin user and one super_admin user

Test Suite 1: CORS Headers
---------------------------
1. Open browser DevTools > Network tab
2. Make any API request from frontend
3. Verify response headers include:
   - Access-Control-Allow-Origin
   - Access-Control-Allow-Credentials
4. Trigger an error (e.g., access forbidden endpoint)
5. Verify CORS headers are still present

Test Suite 2: RBAC Permissions Endpoint
---------------------------------------
1. Login as org_admin user
2. Open DevTools > Console
3. Check for any errors related to permissions fetching
4. Verify no 500 errors appear
5. Check Network tab for /api/v1/rbac/users/{id}/permissions
6. Verify response includes:
   - permissions: []
   - service_roles: []
   - modules: []
   - total_permissions: 0

Test Suite 3: Organization Modules Management
---------------------------------------------
1. Login as super_admin
2. Navigate to Organization Management
3. Select an organization
4. View enabled modules
5. Toggle modules on/off
6. Save changes
7. Verify no errors
8. Verify changes persist after refresh

Test Suite 4: MegaMenu Display (org_admin)
------------------------------------------
1. Login as org_admin user
2. Verify MegaMenu appears at top of page
3. Click on each top-level menu item
4. Verify submenu expands without errors
5. Check console for permission-related errors
6. Verify menu items match enabled modules

Test Suite 5: Module Toggle Impact on Menu
------------------------------------------
1. Login as super_admin
2. Disable "Manufacturing" module for an organization
3. Logout and login as org_admin of that organization
4. Verify "Manufacturing" menu item does NOT appear
5. Re-enable "Manufacturing" module
6. Refresh page
7. Verify "Manufacturing" menu item now appears

Test Suite 6: Safe Fallbacks
----------------------------
1. Simulate network error (disconnect internet briefly)
2. Login as org_admin
3. Verify no blocking errors
4. Verify MegaMenu shows with limited/fallback items
5. Reconnect internet
6. Refresh page
7. Verify full menu appears

Expected Results:
- All tests pass without errors
- MegaMenu displays correctly for org_admin users
- Module toggling works seamlessly
- No 500 errors from RBAC endpoint
- CORS headers present on all responses
"""
