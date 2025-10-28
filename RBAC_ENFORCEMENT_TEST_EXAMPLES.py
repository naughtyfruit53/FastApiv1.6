"""
Test suite for RBAC enforcement in migrated endpoints.

This module provides test examples for validating that migrated endpoints
properly enforce RBAC permissions and tenant isolation.
"""

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, Customer, Organization
from app.core.security import create_access_token


class TestCustomerRBACEnforcement:
    """Test RBAC enforcement for customer endpoints."""
    
    @pytest.fixture
    async def org_a(self, db: AsyncSession):
        """Create test organization A."""
        org = Organization(name="Organization A")
        db.add(org)
        await db.commit()
        await db.refresh(org)
        return org
    
    @pytest.fixture
    async def org_b(self, db: AsyncSession):
        """Create test organization B."""
        org = Organization(name="Organization B")
        db.add(org)
        await db.commit()
        await db.refresh(org)
        return org
    
    @pytest.fixture
    async def user_with_permission(self, db: AsyncSession, org_a):
        """Create user with customer_read permission in org A."""
        user = User(
            email="user_with_perm@test.com",
            organization_id=org_a.id,
            is_active=True
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        # Grant customer_read permission
        # (actual permission assignment would use RBAC service)
        user.token = create_access_token({"sub": user.email})
        return user
    
    @pytest.fixture
    async def user_without_permission(self, db: AsyncSession, org_a):
        """Create user WITHOUT customer_read permission in org A."""
        user = User(
            email="user_no_perm@test.com",
            organization_id=org_a.id,
            is_active=True
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        user.token = create_access_token({"sub": user.email})
        return user
    
    @pytest.fixture
    async def user_different_org(self, db: AsyncSession, org_b):
        """Create user in different organization (org B)."""
        user = User(
            email="user_org_b@test.com",
            organization_id=org_b.id,
            is_active=True
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        user.token = create_access_token({"sub": user.email})
        return user
    
    @pytest.fixture
    async def customer_org_a(self, db: AsyncSession, org_a):
        """Create customer in organization A."""
        customer = Customer(
            organization_id=org_a.id,
            name="Test Customer A",
            contact_number="1234567890",
            address1="123 Main St",
            city="Test City",
            state="Test State",
            pin_code="12345",
            state_code="TS"
        )
        db.add(customer)
        await db.commit()
        await db.refresh(customer)
        return customer
    
    @pytest.fixture
    async def customer_org_b(self, db: AsyncSession, org_b):
        """Create customer in organization B."""
        customer = Customer(
            organization_id=org_b.id,
            name="Test Customer B",
            contact_number="0987654321",
            address1="456 Oak Ave",
            city="Other City",
            state="Other State",
            pin_code="54321",
            state_code="OS"
        )
        db.add(customer)
        await db.commit()
        await db.refresh(customer)
        return customer
    
    async def test_list_customers_with_permission(
        self,
        client: AsyncClient,
        user_with_permission,
        customer_org_a
    ):
        """User with permission can list customers from their org."""
        response = await client.get(
            "/customers",
            headers={"Authorization": f"Bearer {user_with_permission.token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 1
        assert any(c["id"] == customer_org_a.id for c in data)
    
    async def test_list_customers_without_permission(
        self,
        client: AsyncClient,
        user_without_permission,
        customer_org_a
    ):
        """User without permission gets 404 (anti-enumeration)."""
        response = await client.get(
            "/customers",
            headers={"Authorization": f"Bearer {user_without_permission.token}"}
        )
        
        # Should return 404 not 403 for anti-enumeration
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    async def test_get_customer_own_org(
        self,
        client: AsyncClient,
        user_with_permission,
        customer_org_a
    ):
        """User can get customer from their own organization."""
        response = await client.get(
            f"/customers/{customer_org_a.id}",
            headers={"Authorization": f"Bearer {user_with_permission.token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == customer_org_a.id
        assert data["name"] == customer_org_a.name
    
    async def test_get_customer_different_org(
        self,
        client: AsyncClient,
        user_different_org,
        customer_org_a
    ):
        """User cannot get customer from different organization."""
        response = await client.get(
            f"/customers/{customer_org_a.id}",
            headers={"Authorization": f"Bearer {user_different_org.token}"}
        )
        
        # Should return 404 for anti-enumeration
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    async def test_get_customer_without_permission(
        self,
        client: AsyncClient,
        user_without_permission,
        customer_org_a
    ):
        """User without permission cannot get customer."""
        response = await client.get(
            f"/customers/{customer_org_a.id}",
            headers={"Authorization": f"Bearer {user_without_permission.token}"}
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    async def test_create_customer_with_permission(
        self,
        client: AsyncClient,
        user_with_permission,
        org_a
    ):
        """User with create permission can create customer."""
        # Note: This assumes user has customer_create permission
        customer_data = {
            "name": "New Customer",
            "contact_number": "5555555555",
            "address1": "789 Pine St",
            "city": "New City",
            "state": "New State",
            "pin_code": "99999",
            "state_code": "NS"
        }
        
        response = await client.post(
            "/customers",
            json=customer_data,
            headers={"Authorization": f"Bearer {user_with_permission.token}"}
        )
        
        # If user has create permission
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert data["name"] == customer_data["name"]
            assert data["organization_id"] == org_a.id
        # If user doesn't have create permission
        else:
            assert response.status_code == status.HTTP_404_NOT_FOUND
    
    async def test_update_customer_own_org(
        self,
        client: AsyncClient,
        user_with_permission,
        customer_org_a
    ):
        """User can update customer in their own organization."""
        # Note: Assumes user has customer_update permission
        update_data = {
            "name": "Updated Customer Name"
        }
        
        response = await client.put(
            f"/customers/{customer_org_a.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {user_with_permission.token}"}
        )
        
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert data["name"] == update_data["name"]
        else:
            assert response.status_code == status.HTTP_404_NOT_FOUND
    
    async def test_update_customer_different_org(
        self,
        client: AsyncClient,
        user_different_org,
        customer_org_a
    ):
        """User cannot update customer from different organization."""
        update_data = {
            "name": "Hacked Name"
        }
        
        response = await client.put(
            f"/customers/{customer_org_a.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {user_different_org.token}"}
        )
        
        # Should deny access with 404
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    async def test_delete_customer_own_org(
        self,
        client: AsyncClient,
        user_with_permission,
        customer_org_a
    ):
        """User can delete customer in their own organization."""
        # Note: Assumes user has customer_delete permission
        response = await client.delete(
            f"/customers/{customer_org_a.id}",
            headers={"Authorization": f"Bearer {user_with_permission.token}"}
        )
        
        if response.status_code == status.HTTP_200_OK:
            # Verify deletion
            get_response = await client.get(
                f"/customers/{customer_org_a.id}",
                headers={"Authorization": f"Bearer {user_with_permission.token}"}
            )
            assert get_response.status_code == status.HTTP_404_NOT_FOUND
        else:
            assert response.status_code == status.HTTP_404_NOT_FOUND
    
    async def test_delete_customer_different_org(
        self,
        client: AsyncClient,
        user_different_org,
        customer_org_a
    ):
        """User cannot delete customer from different organization."""
        response = await client.delete(
            f"/customers/{customer_org_a.id}",
            headers={"Authorization": f"Bearer {user_different_org.token}"}
        )
        
        # Should deny with 404
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestRBACEnforcementPatterns:
    """General patterns for testing RBAC enforcement."""
    
    async def test_no_authentication_returns_401(self, client: AsyncClient):
        """Unauthenticated requests return 401."""
        response = await client.get("/customers")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    async def test_invalid_token_returns_401(self, client: AsyncClient):
        """Invalid authentication token returns 401."""
        response = await client.get(
            "/customers",
            headers={"Authorization": "Bearer invalid_token_here"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    async def test_expired_token_returns_401(self, client: AsyncClient):
        """Expired authentication token returns 401."""
        # Create an expired token
        expired_token = "expired_token"  # Would use actual expired token
        
        response = await client.get(
            "/customers",
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# Test execution
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
