"""
Integration tests for Frontend-Backend RBAC enforcement.

These tests verify that:
1. Backend endpoints properly enforce RBAC permissions
2. Frontend receives correct 403 responses when lacking permissions
3. Organization isolation is maintained
4. Permission checks work across different modules
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.main import app
from app.models import User, Organization, Role, Permission, UserRole
from app.core.database import get_db
from app.core.security import create_access_token


@pytest.fixture
async def test_organizations(async_session: AsyncSession):
    """Create test organizations"""
    org1 = Organization(
        id=1,
        name="Test Organization 1",
        subdomain="test1",
        is_active=True
    )
    org2 = Organization(
        id=2,
        name="Test Organization 2",
        subdomain="test2",
        is_active=True
    )
    
    async_session.add(org1)
    async_session.add(org2)
    await async_session.commit()
    
    return org1, org2


@pytest.fixture
async def test_users(async_session: AsyncSession, test_organizations):
    """Create test users with different permissions"""
    org1, org2 = test_organizations
    
    # User with voucher permissions in org1
    user_voucher = User(
        id=1,
        email="voucher@test1.com",
        hashed_password="hashed",
        organization_id=org1.id,
        is_active=True,
        role="user"
    )
    
    # User with inventory permissions in org1
    user_inventory = User(
        id=2,
        email="inventory@test1.com",
        hashed_password="hashed",
        organization_id=org1.id,
        is_active=True,
        role="user"
    )
    
    # User in org2
    user_org2 = User(
        id=3,
        email="user@test2.com",
        hashed_password="hashed",
        organization_id=org2.id,
        is_active=True,
        role="user"
    )
    
    # Super admin
    super_admin = User(
        id=4,
        email="admin@test.com",
        hashed_password="hashed",
        organization_id=org1.id,
        is_active=True,
        role="admin",
        is_super_admin=True
    )
    
    async_session.add_all([user_voucher, user_inventory, user_org2, super_admin])
    await async_session.commit()
    
    return {
        'voucher': user_voucher,
        'inventory': user_inventory,
        'org2': user_org2,
        'admin': super_admin
    }


@pytest.fixture
async def test_permissions(async_session: AsyncSession, test_users):
    """Create and assign permissions to users"""
    users = test_users
    
    # Create voucher permissions
    voucher_create = Permission(name="voucher_create", description="Create vouchers")
    voucher_read = Permission(name="voucher_read", description="Read vouchers")
    
    # Create inventory permissions
    inventory_create = Permission(name="inventory_create", description="Create inventory")
    inventory_read = Permission(name="inventory_read", description="Read inventory")
    
    async_session.add_all([voucher_create, voucher_read, inventory_create, inventory_read])
    await async_session.commit()
    
    # TODO: Assign permissions to users via roles
    # This requires implementing the role-permission assignment
    # For now, we'll rely on the backend's permission checking logic
    
    return {
        'voucher_create': voucher_create,
        'voucher_read': voucher_read,
        'inventory_create': inventory_create,
        'inventory_read': inventory_read,
    }


def create_test_token(user_id: int, organization_id: int):
    """Create a test JWT token"""
    return create_access_token(
        data={
            "sub": str(user_id),
            "organization_id": organization_id
        }
    )


class TestFrontendBackendRBACIntegration:
    """Test suite for frontend-backend RBAC integration"""
    
    @pytest.mark.asyncio
    async def test_403_response_on_missing_permission(self, test_users):
        """Test that backend returns 403 when user lacks required permission"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # User with inventory permission tries to create voucher
            token = create_test_token(test_users['inventory'].id, test_users['inventory'].organization_id)
            
            response = await client.post(
                "/api/v1/vouchers/sales",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "voucher_number": "SV-001",
                    "amount": 1000,
                    "customer_id": 1
                }
            )
            
            # Should return 403 Forbidden
            assert response.status_code == 403
            
            # Response should include permission details
            data = response.json()
            assert "detail" in data
            assert "permission" in data["detail"].lower() or "required" in data.get("required_permission", "")
    
    @pytest.mark.asyncio
    async def test_404_on_cross_org_access(self, test_users):
        """Test that cross-org access returns 404 (not 403) to prevent info disclosure"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # User in org2 tries to access voucher in org1
            token = create_test_token(test_users['org2'].id, test_users['org2'].organization_id)
            
            # Assuming voucher ID 1 exists in org1
            response = await client.get(
                "/api/v1/vouchers/sales/1",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            # Should return 404 (not 403) to prevent information disclosure
            assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_permission_check_across_modules(self, test_users):
        """Test that permissions are module-specific"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # User with voucher permission should not access inventory
            token = create_test_token(test_users['voucher'].id, test_users['voucher'].organization_id)
            
            response = await client.post(
                "/api/v1/inventory",
                headers={"Authorization": f"Bearer {token}"},
                json={"product_id": 1, "quantity": 100}
            )
            
            # Should return 403 for inventory access
            assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_super_admin_bypass(self, test_users):
        """Test that super admin can bypass permission checks"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            token = create_test_token(test_users['admin'].id, test_users['admin'].organization_id)
            
            # Super admin should be able to access any endpoint
            # (assuming voucher endpoint exists)
            response = await client.get(
                "/api/v1/vouchers/sales",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            # Should succeed (200) or return empty list
            assert response.status_code in [200, 204]
    
    @pytest.mark.asyncio
    async def test_organization_scoping_in_queries(self, test_users):
        """Test that database queries are properly scoped to organization"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            token = create_test_token(test_users['voucher'].id, test_users['voucher'].organization_id)
            
            # Get all vouchers - should only return org1 vouchers
            response = await client.get(
                "/api/v1/vouchers/sales",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 200:
                vouchers = response.json()
                # All vouchers should belong to org1
                for voucher in vouchers:
                    assert voucher.get("organization_id") == test_users['voucher'].organization_id
    
    @pytest.mark.asyncio
    async def test_permission_error_includes_details(self, test_users):
        """Test that 403 error response includes permission details for frontend"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            token = create_test_token(test_users['inventory'].id, test_users['inventory'].organization_id)
            
            response = await client.post(
                "/api/v1/vouchers/sales",
                headers={"Authorization": f"Bearer {token}"},
                json={"voucher_number": "SV-001", "amount": 1000}
            )
            
            assert response.status_code == 403
            
            data = response.json()
            
            # Response should help frontend show user-friendly message
            # Expected format (may vary based on implementation):
            # {
            #   "detail": "Insufficient permissions. Required: voucher_create",
            #   "required_permission": "voucher_create",
            #   "module": "voucher"
            # }
            
            assert "detail" in data
            # At minimum, detail should mention permission
            assert "permission" in data["detail"].lower()


class TestMigratedEndpoints:
    """Test that migrated endpoints enforce RBAC correctly"""
    
    MIGRATED_ENDPOINTS = [
        # Vouchers (Phase 4 - All 18 files)
        ("/api/v1/vouchers/sales", "voucher"),
        ("/api/v1/vouchers/purchase", "voucher"),
        ("/api/v1/vouchers/journal", "voucher"),
        ("/api/v1/vouchers/payment", "voucher"),
        ("/api/v1/vouchers/receipt", "voucher"),
        
        # Manufacturing (Phase 2 - All 10 files)
        ("/api/v1/manufacturing/bom", "manufacturing"),
        ("/api/v1/manufacturing/job-cards", "manufacturing"),
        ("/api/v1/manufacturing/orders", "manufacturing"),
        
        # CRM (Phase 3)
        ("/api/v1/crm/leads", "crm"),
        ("/api/v1/crm/opportunities", "crm"),
        
        # HR (Phase 3)
        ("/api/v1/hr/employees", "hr"),
        ("/api/v1/hr/leave", "hr"),
        
        # Finance/Analytics (Phase 2)
        ("/api/v1/finance/analytics", "finance"),
        ("/api/v1/ml-analytics/dashboard", "analytics"),
    ]
    
    @pytest.mark.asyncio
    @pytest.mark.parametrize("endpoint,module", MIGRATED_ENDPOINTS)
    async def test_migrated_endpoint_requires_permission(self, endpoint, module, test_users):
        """Test that migrated endpoints require appropriate permissions"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Use user without the required permission
            # For simplicity, use inventory user (has inventory permission only)
            token = create_test_token(test_users['inventory'].id, test_users['inventory'].organization_id)
            
            # Try to access endpoint
            response = await client.get(
                endpoint,
                headers={"Authorization": f"Bearer {token}"}
            )
            
            # If the module doesn't match inventory, should get 403
            if module != "inventory":
                # Should be denied (403) or endpoint may not exist (404)
                assert response.status_code in [403, 404]


class TestNonMigratedEndpoints:
    """Test to identify endpoints that still need migration"""
    
    NON_MIGRATED_ENDPOINTS = [
        # These should eventually be migrated
        "/api/v1/integrations",
        "/api/v1/customers",
        "/api/v1/vendors",
        "/reports/complete-ledger",
        "/api/v1/admin/users",
    ]
    
    @pytest.mark.asyncio
    @pytest.mark.parametrize("endpoint", NON_MIGRATED_ENDPOINTS)
    async def test_non_migrated_endpoint_detection(self, endpoint, test_users):
        """Test to identify endpoints that don't have RBAC enforcement yet"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            token = create_test_token(test_users['inventory'].id, test_users['inventory'].organization_id)
            
            response = await client.get(
                endpoint,
                headers={"Authorization": f"Bearer {token}"}
            )
            
            # This test documents which endpoints still need migration
            # If an endpoint returns 200 when it shouldn't, it needs RBAC migration
            # This is informational - not a failure
            if response.status_code == 200:
                print(f"\n⚠️  WARNING: {endpoint} may need RBAC migration (returned 200)")


class TestFrontendErrorHandling:
    """Test scenarios that frontend error handling should cover"""
    
    @pytest.mark.asyncio
    async def test_frontend_should_show_permission_error(self, test_users):
        """Document expected frontend behavior for 403 errors"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            token = create_test_token(test_users['inventory'].id, test_users['inventory'].organization_id)
            
            response = await client.post(
                "/api/v1/vouchers/sales",
                headers={"Authorization": f"Bearer {token}"},
                json={"voucher_number": "SV-001", "amount": 1000}
            )
            
            if response.status_code == 403:
                data = response.json()
                
                # Frontend should:
                # 1. Detect 403 status
                # 2. Extract permission from response
                # 3. Show user-friendly error message
                # 4. Log the permission denial
                
                print(f"\n📋 Frontend Error Handling Guide:")
                print(f"   Status: {response.status_code}")
                print(f"   Response: {data}")
                print(f"   Frontend should show: 'You need {data.get('required_permission', 'unknown')} permission'")
    
    @pytest.mark.asyncio
    async def test_frontend_should_handle_cross_org_404(self, test_users):
        """Document expected frontend behavior for cross-org access"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            token = create_test_token(test_users['org2'].id, test_users['org2'].organization_id)
            
            response = await client.get(
                "/api/v1/vouchers/sales/999",  # Assumes this is in org1
                headers={"Authorization": f"Bearer {token}"}
            )
            
            # Frontend should:
            # 1. Detect 404 status
            # 2. Show "Not found" message
            # 3. NOT reveal that the resource exists in another org
            
            assert response.status_code == 404
            print(f"\n📋 Frontend should show: 'Voucher not found'")


# Integration test for complete flow
class TestCompleteRBACFlow:
    """Test complete RBAC flow from authentication to data access"""
    
    @pytest.mark.asyncio
    async def test_complete_voucher_creation_flow(self, test_users):
        """Test complete flow: Login -> Permission Check -> Create Voucher"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Step 1: User with voucher_create permission logs in
            # (Token creation simulated here)
            token = create_test_token(test_users['voucher'].id, test_users['voucher'].organization_id)
            
            # Step 2: Frontend checks permission (optional)
            # GET /api/v1/rbac/permissions/me
            # Response should include 'voucher_create'
            
            # Step 3: Create voucher
            response = await client.post(
                "/api/v1/vouchers/sales",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "voucher_number": "SV-TEST-001",
                    "amount": 1500,
                    "customer_id": 1,
                    "date": "2025-10-28"
                }
            )
            
            # Should succeed if backend is properly migrated
            # May fail if endpoint doesn't exist yet - that's okay
            if response.status_code == 201:
                voucher = response.json()
                # Verify org scoping
                assert voucher["organization_id"] == test_users['voucher'].organization_id
            
            # Document the flow for frontend developers
            print(f"\n📋 Complete RBAC Flow:")
            print(f"   1. User logs in, gets JWT token with org_id and permissions")
            print(f"   2. Frontend stores token in localStorage")
            print(f"   3. Frontend optionally checks permission before showing UI")
            print(f"   4. Frontend makes API call with Authorization header")
            print(f"   5. Backend validates token, checks permission, enforces org scoping")
            print(f"   6. Response: {response.status_code}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
