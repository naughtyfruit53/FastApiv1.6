"""
Tests for organization-scoped user management and invitation flows
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.base import User, Organization
from app.schemas.user import UserRole
from app.core.security import get_password_hash
import json


class TestOrganizationScopedUserManagement:
    """Test organization-scoped user management endpoints"""
    
    def setup_method(self):
        """Setup test data for each test"""
        self.test_org1_data = {
            "name": "Test Organization 1",
            "subdomain": "testorg1",
            "status": "active",
            "primary_email": "admin@testorg1.com",
            "primary_phone": "+1234567890",
            "address1": "123 Test Street",
            "city": "Test City",
            "state": "Test State",
            "pin_code": "12345",
            "country": "Test Country",
            "max_users": 10
        }
        
        self.test_org2_data = {
            "name": "Test Organization 2", 
            "subdomain": "testorg2",
            "status": "active",
            "primary_email": "admin@testorg2.com",
            "primary_phone": "+1234567891",
            "address1": "456 Test Avenue",
            "city": "Test City 2",
            "state": "Test State 2",
            "pin_code": "54321",
            "country": "Test Country 2",
            "max_users": 5
        }
        
        self.test_user_data = {
            "email": "newuser@testorg1.com",
            "username": "newuser",
            "full_name": "New Test User",
            "password": "SecurePass123!",
            "role": "standard_user",
            "department": "IT",
            "designation": "Developer"
        }

    def test_get_organization_users_success(self, client: TestClient, test_db: Session, org_admin_user: User):
        """Test successfully getting users in an organization"""
        # Get the admin user's organization
        org_id = org_admin_user.organization_id
        
        # Get token for org admin
        token = self.get_token(client, org_admin_user.email, "testpass123")
        
        response = client.get(
            f"/api/v1/organizations/{org_id}/users",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        users = response.json()
        assert len(users) >= 1  # At least the admin user
        assert any(user["email"] == org_admin_user.email for user in users)

    def test_get_organization_users_forbidden_other_org(self, client: TestClient, test_db: Session, org_admin_user: User):
        """Test that users cannot access other organization's users"""
        # Create another organization
        other_org = Organization(**self.test_org2_data)
        test_db.add(other_org)
        test_db.commit()
        test_db.refresh(other_org)
        
        # Get token for org admin
        token = self.get_token(client, org_admin_user.email, "testpass123")
        
        response = client.get(
            f"/api/v1/organizations/{other_org.id}/users",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 403
        assert "Access denied" in response.json()["detail"]

    def test_create_user_in_organization_success(self, client: TestClient, test_db: Session, org_admin_user: User):
        """Test successfully creating a user in an organization"""
        org_id = org_admin_user.organization_id
        token = self.get_token(client, org_admin_user.email, "testpass123")
        
        response = client.post(
            f"/api/v1/organizations/{org_id}/users",
            json=self.test_user_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        created_user = response.json()
        assert created_user["email"] == self.test_user_data["email"]
        assert created_user["organization_id"] == org_id
        assert created_user["role"] == self.test_user_data["role"]

    def test_create_user_in_organization_duplicate_email(self, client: TestClient, test_db: Session, org_admin_user: User):
        """Test creating user with duplicate email in same organization fails"""
        org_id = org_admin_user.organization_id
        token = self.get_token(client, org_admin_user.email, "testpass123")
        
        # Use org admin's email (already exists)
        duplicate_user_data = self.test_user_data.copy()
        duplicate_user_data["email"] = org_admin_user.email
        
        response = client.post(
            f"/api/v1/organizations/{org_id}/users",
            json=duplicate_user_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]

    def test_create_org_admin_requires_super_admin(self, client: TestClient, test_db: Session, org_admin_user: User):
        """Test that only super admins can create org admin users"""
        org_id = org_admin_user.organization_id
        token = self.get_token(client, org_admin_user.email, "testpass123")
        
        org_admin_data = self.test_user_data.copy()
        org_admin_data["role"] = "org_admin"
        
        response = client.post(
            f"/api/v1/organizations/{org_id}/users",
            json=org_admin_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 403
        assert "super administrators" in response.json()["detail"]

    def test_update_user_in_organization_success(self, client: TestClient, test_db: Session, org_admin_user: User, test_user: User):
        """Test successfully updating a user in an organization"""
        org_id = org_admin_user.organization_id
        token = self.get_token(client, org_admin_user.email, "testpass123")
        
        update_data = {
            "full_name": "Updated Test User",
            "department": "HR"
        }
        
        response = client.put(
            f"/api/v1/organizations/{org_id}/users/{test_user.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        updated_user = response.json()
        assert updated_user["full_name"] == update_data["full_name"]
        assert updated_user["department"] == update_data["department"]

    def test_delete_user_from_organization_success(self, client: TestClient, test_db: Session, org_admin_user: User):
        """Test successfully deleting a user from an organization"""
        org_id = org_admin_user.organization_id
        token = self.get_token(client, org_admin_user.email, "testpass123")
        
        # Create a user to delete
        user_to_delete = User(
            organization_id=org_id,
            email="delete@testorg.com",
            username="deleteuser",
            full_name="Delete Test User",
            hashed_password=get_password_hash("password123"),
            role=UserRole.STANDARD_USER.value,
            is_active=True
        )
        test_db.add(user_to_delete)
        test_db.commit()
        test_db.refresh(user_to_delete)
        
        response = client.delete(
            f"/api/v1/organizations/{org_id}/users/{user_to_delete.id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"]
        
        # Verify user is deleted
        deleted_user = test_db.get(User, user_to_delete.id)
        assert deleted_user is None

    def test_cannot_delete_self(self, client: TestClient, test_db: Session, org_admin_user: User):
        """Test that users cannot delete themselves"""
        org_id = org_admin_user.organization_id
        token = self.get_token(client, org_admin_user.email, "testpass123")
        
        response = client.delete(
            f"/api/v1/organizations/{org_id}/users/{org_admin_user.id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 400
        assert "Cannot delete your own account" in response.json()["detail"]

    def test_cannot_delete_last_org_admin(self, client: TestClient, test_db: Session, org_admin_user: User):
        """Test that the last org admin cannot be deleted"""
        org_id = org_admin_user.organization_id
        token = self.get_token(client, org_admin_user.email, "testpass123")
        
        # Create another admin to try to delete the main admin
        another_admin = User(
            organization_id=org_id,
            email="admin2@testorg.com",
            username="admin2",
            full_name="Another Admin",
            hashed_password=get_password_hash("password123"),
            role=UserRole.ORG_ADMIN.value,
            is_active=True
        )
        test_db.add(another_admin)
        test_db.commit()
        test_db.refresh(another_admin)
        
        # Get token for the other admin
        token2 = self.get_token(client, another_admin.email, "password123")
        
        # Try to delete the original admin (should work since there are 2 admins)
        response = client.delete(
            f"/api/v1/organizations/{org_id}/users/{org_admin_user.id}",
            headers={"Authorization": f"Bearer {token2}"}
        )
        
        assert response.status_code == 200
        
        # Now try to delete the last admin (should fail)
        response = client.delete(
            f"/api/v1/organizations/{org_id}/users/{another_admin.id}",
            headers={"Authorization": f"Bearer {token2}"}
        )
        
        assert response.status_code == 400
        assert "last organization administrator" in response.json()["detail"]

    def get_token(self, client: TestClient, email: str, password: str) -> str:
        """Helper method to get authentication token"""
        response = client.post(
            "/api/auth/login/email",
            json={"email": email, "password": password}
        )
        return response.json()["access_token"]


class TestOrganizationInvitationManagement:
    """Test organization invitation management endpoints"""
    
    def test_list_organization_invitations(self, client: TestClient, test_db: Session, org_admin_user: User):
        """Test listing organization invitations"""
        org_id = org_admin_user.organization_id
        token = self.get_token(client, org_admin_user.email, "testpass123")
        
        # Create a pending invitation (user with must_change_password=True)
        pending_user = User(
            organization_id=org_id,
            email="pending@testorg.com",
            username="pendinguser",
            full_name="Pending User",
            hashed_password=get_password_hash("temppass123"),
            role=UserRole.STANDARD_USER.value,
            is_active=True,
            must_change_password=True
        )
        test_db.add(pending_user)
        test_db.commit()
        
        response = client.get(
            f"/api/v1/organizations/{org_id}/invitations",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        invitations = response.json()
        assert len(invitations) >= 1
        pending_invitation = next((inv for inv in invitations if inv["email"] == "pending@testorg.com"), None)
        assert pending_invitation is not None
        assert pending_invitation["status"] == "pending"

    def test_resend_organization_invitation(self, client: TestClient, test_db: Session, org_admin_user: User):
        """Test resending an organization invitation"""
        org_id = org_admin_user.organization_id
        token = self.get_token(client, org_admin_user.email, "testpass123")
        
        # Create a pending invitation
        pending_user = User(
            organization_id=org_id,
            email="resend@testorg.com",
            username="resenduser",
            full_name="Resend User",
            hashed_password=get_password_hash("temppass123"),
            role=UserRole.STANDARD_USER.value,
            is_active=True,
            must_change_password=True
        )
        test_db.add(pending_user)
        test_db.commit()
        test_db.refresh(pending_user)
        
        response = client.post(
            f"/api/v1/organizations/{org_id}/invitations/{pending_user.id}/resend",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        assert "resent" in response.json()["message"]

    def test_cancel_organization_invitation(self, client: TestClient, test_db: Session, org_admin_user: User):
        """Test cancelling an organization invitation"""
        org_id = org_admin_user.organization_id
        token = self.get_token(client, org_admin_user.email, "testpass123")
        
        # Create a pending invitation
        pending_user = User(
            organization_id=org_id,
            email="cancel@testorg.com",
            username="canceluser",
            full_name="Cancel User",
            hashed_password=get_password_hash("temppass123"),
            role=UserRole.STANDARD_USER.value,
            is_active=True,
            must_change_password=True
        )
        test_db.add(pending_user)
        test_db.commit()
        test_db.refresh(pending_user)
        
        response = client.delete(
            f"/api/v1/organizations/{org_id}/invitations/{pending_user.id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        assert "cancelled" in response.json()["message"]
        
        # Verify user is deleted
        deleted_user = test_db.get(User, pending_user.id)
        assert deleted_user is None

    def get_token(self, client: TestClient, email: str, password: str) -> str:
        """Helper method to get authentication token"""
        response = client.post(
            "/api/auth/login/email",
            json={"email": email, "password": password}
        )
        return response.json()["access_token"]


class TestPermissionEnforcement:
    """Test permission enforcement for user management"""
    
    def test_standard_user_cannot_manage_users(self, client: TestClient, test_db: Session, test_user: User):
        """Test that standard users cannot manage other users"""
        org_id = test_user.organization_id
        token = self.get_token(client, test_user.email, "testpass123")
        
        # Try to list users
        response = client.get(
            f"/api/v1/organizations/{org_id}/users",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 403
        assert "Only organization administrators" in response.json()["detail"]

    def test_org_admin_can_manage_users_in_own_org_only(self, client: TestClient, test_db: Session, org_admin_user: User):
        """Test that org admins can only manage users in their own organization"""
        # Create another organization
        other_org = Organization(
            name="Other Organization",
            subdomain="otherorg",
            status="active",
            primary_email="admin@otherorg.com",
            primary_phone="+1234567892",
            address1="789 Other Street",
            city="Other City",
            state="Other State",
            pin_code="67890",
            country="Other Country",
            max_users=5
        )
        test_db.add(other_org)
        test_db.commit()
        test_db.refresh(other_org)
        
        token = self.get_token(client, org_admin_user.email, "testpass123")
        
        # Try to access other organization's users
        response = client.get(
            f"/api/v1/organizations/{other_org.id}/users",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 403
        assert "Access denied" in response.json()["detail"]

    def get_token(self, client: TestClient, email: str, password: str) -> str:
        """Helper method to get authentication token"""
        response = client.post(
            "/api/auth/login/email",
            json={"email": email, "password": password}
        )
        return response.json()["access_token"]