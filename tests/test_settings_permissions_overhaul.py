"""
Tests for Settings & GST Permissions Overhaul
Tests for org_admin/management RBAC, voucher settings restrictions, user CRUD, and GST permissions
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.user_models import User, Organization
from app.models.rbac_models import ServicePermission, ServiceRole, ServiceRolePermission
from app.core.security import get_password_hash
import json


class TestGSTPermissions:
    """Test GST search permissions for org_admin and management"""
    
    def test_gst_search_org_admin_success(self, client: TestClient, test_db: Session, org_admin_user: User):
        """Test that org_admin can search GST numbers"""
        # This test assumes the migration has been run and permissions are seeded
        token = self.get_token(client, org_admin_user.email, "testpass123")
        
        # Valid GST format (27 = Maharashtra state code)
        gst_number = "27AABCU9603R1ZM"
        
        response = client.get(
            f"/api/v1/gst/search/{gst_number}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Should not get 403 Forbidden
        assert response.status_code in [200, 400], f"Unexpected status: {response.status_code}, {response.json()}"
        
    def test_gst_search_management_success(self, client: TestClient, test_db: Session):
        """Test that management role can search GST numbers"""
        # Create a management user
        org = Organization(
            name="Test Org",
            subdomain="testorg",
            status="active",
            primary_email="test@testorg.com",
            state_code="27"
        )
        test_db.add(org)
        test_db.commit()
        test_db.refresh(org)
        
        mgmt_user = User(
            email="management@testorg.com",
            full_name="Management User",
            hashed_password=get_password_hash("testpass123"),
            role="management",
            organization_id=org.id,
            is_active=True
        )
        test_db.add(mgmt_user)
        test_db.commit()
        test_db.refresh(mgmt_user)
        
        token = self.get_token(client, mgmt_user.email, "testpass123")
        
        gst_number = "27AABCU9603R1ZM"
        response = client.get(
            f"/api/v1/gst/search/{gst_number}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Should not get 403 Forbidden
        assert response.status_code in [200, 400], f"Unexpected status: {response.status_code}"
    
    def test_gst_search_executive_denied(self, client: TestClient, test_db: Session):
        """Test that executive role cannot search GST without permission"""
        org = Organization(
            name="Test Org",
            subdomain="testorg",
            status="active",
            primary_email="test@testorg.com",
            state_code="27"
        )
        test_db.add(org)
        test_db.commit()
        test_db.refresh(org)
        
        exec_user = User(
            email="executive@testorg.com",
            full_name="Executive User",
            hashed_password=get_password_hash("testpass123"),
            role="executive",
            organization_id=org.id,
            is_active=True
        )
        test_db.add(exec_user)
        test_db.commit()
        test_db.refresh(exec_user)
        
        token = self.get_token(client, exec_user.email, "testpass123")
        
        gst_number = "27AABCU9603R1ZM"
        response = client.get(
            f"/api/v1/gst/search/{gst_number}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Should get 403 Forbidden (no permission)
        assert response.status_code == 403
    
    @staticmethod
    def get_token(client: TestClient, email: str, password: str) -> str:
        """Helper to get authentication token"""
        response = client.post(
            "/api/v1/token",
            data={"username": email, "password": password}
        )
        return response.json()["access_token"]


class TestVoucherSettingsRestrictions:
    """Test voucher prefix and counter reset period restrictions"""
    
    def test_voucher_prefix_update_org_admin_success(self, client: TestClient, test_db: Session, org_admin_user: User):
        """Test that org_admin can update voucher prefix"""
        token = self.get_token(client, org_admin_user.email, "testpass123")
        
        update_data = {
            "voucher_prefix": "TEST",
            "voucher_prefix_enabled": True,
            "voucher_counter_reset_period": "annually"
        }
        
        response = client.put(
            "/api/v1/organizations/settings/",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code in [200, 201], f"Failed: {response.json()}"
        data = response.json()
        assert data["voucher_prefix"] == "TEST"
        assert data["voucher_prefix_enabled"] is True
    
    def test_voucher_prefix_update_management_denied(self, client: TestClient, test_db: Session):
        """Test that management role cannot update voucher prefix"""
        org = Organization(
            name="Test Org",
            subdomain="testorg",
            status="active",
            primary_email="test@testorg.com",
            state_code="27"
        )
        test_db.add(org)
        test_db.commit()
        test_db.refresh(org)
        
        mgmt_user = User(
            email="management@testorg.com",
            full_name="Management User",
            hashed_password=get_password_hash("testpass123"),
            role="management",
            organization_id=org.id,
            is_active=True
        )
        test_db.add(mgmt_user)
        test_db.commit()
        test_db.refresh(mgmt_user)
        
        token = self.get_token(client, mgmt_user.email, "testpass123")
        
        update_data = {
            "voucher_prefix": "MGMT",
            "voucher_prefix_enabled": True
        }
        
        response = client.put(
            "/api/v1/organizations/settings/",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Should get 403 or fields should be ignored
        assert response.status_code in [200, 403]
        if response.status_code == 200:
            # Fields should not be updated
            data = response.json()
            assert data.get("voucher_prefix") != "MGMT", "Management should not be able to update prefix"
    
    def test_counter_reset_period_update_org_admin_success(self, client: TestClient, test_db: Session, org_admin_user: User):
        """Test that org_admin can update counter reset period"""
        token = self.get_token(client, org_admin_user.email, "testpass123")
        
        update_data = {
            "voucher_counter_reset_period": "monthly"
        }
        
        response = client.put(
            "/api/v1/organizations/settings/",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code in [200, 201]
        data = response.json()
        assert data["voucher_counter_reset_period"] == "monthly"
    
    def test_other_settings_update_management_success(self, client: TestClient, test_db: Session):
        """Test that management can update other (non-restricted) settings"""
        org = Organization(
            name="Test Org",
            subdomain="testorg",
            status="active",
            primary_email="test@testorg.com",
            state_code="27"
        )
        test_db.add(org)
        test_db.commit()
        test_db.refresh(org)
        
        mgmt_user = User(
            email="management@testorg.com",
            full_name="Management User",
            hashed_password=get_password_hash("testpass123"),
            role="management",
            organization_id=org.id,
            is_active=True
        )
        test_db.add(mgmt_user)
        test_db.commit()
        test_db.refresh(mgmt_user)
        
        token = self.get_token(client, mgmt_user.email, "testpass123")
        
        update_data = {
            "auto_send_notifications": False,
            "mail_1_level_up_enabled": True,
            "purchase_order_terms": "Net 30 days"
        }
        
        response = client.put(
            "/api/v1/organizations/settings/",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code in [200, 201]
        data = response.json()
        assert data["auto_send_notifications"] is False
        assert data["mail_1_level_up_enabled"] is True
    
    @staticmethod
    def get_token(client: TestClient, email: str, password: str) -> str:
        """Helper to get authentication token"""
        response = client.post(
            "/api/v1/token",
            data={"username": email, "password": password}
        )
        return response.json()["access_token"]


class TestUserCRUDOperations:
    """Test org_admin user create/delete operations"""
    
    def test_org_admin_create_manager_success(self, client: TestClient, test_db: Session, org_admin_user: User):
        """Test that org_admin can create a manager"""
        token = self.get_token(client, org_admin_user.email, "testpass123")
        
        user_data = {
            "email": "newmanager@testorg.com",
            "full_name": "New Manager",
            "password": "SecurePass123!",
            "role": "manager",
            "department": "Sales",
            "designation": "Sales Manager",
            "assigned_modules": {"crm": True, "sales": True}
        }
        
        response = client.post(
            "/api/v1/org-users/users",
            json=user_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code in [200, 201], f"Failed: {response.json()}"
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["role"] == "manager"
    
    def test_org_admin_delete_user_success(self, client: TestClient, test_db: Session, org_admin_user: User):
        """Test that org_admin can delete a user"""
        # Create a user to delete
        org_id = org_admin_user.organization_id
        user_to_delete = User(
            email="todelete@testorg.com",
            full_name="Delete Me",
            hashed_password=get_password_hash("testpass123"),
            role="manager",
            organization_id=org_id,
            is_active=True
        )
        test_db.add(user_to_delete)
        test_db.commit()
        test_db.refresh(user_to_delete)
        
        token = self.get_token(client, org_admin_user.email, "testpass123")
        
        response = client.delete(
            f"/api/v1/org-users/users/{user_to_delete.id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "deleted" in data["message"].lower()
        
        # Verify user is marked inactive
        test_db.refresh(user_to_delete)
        assert user_to_delete.is_active is False
    
    def test_org_admin_cannot_delete_self(self, client: TestClient, test_db: Session, org_admin_user: User):
        """Test that org_admin cannot delete themselves"""
        token = self.get_token(client, org_admin_user.email, "testpass123")
        
        response = client.delete(
            f"/api/v1/org-users/users/{org_admin_user.id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 400
        assert "cannot delete your own account" in response.json()["detail"].lower()
    
    def test_org_admin_cannot_delete_super_admin(self, client: TestClient, test_db: Session, org_admin_user: User):
        """Test that org_admin cannot delete super_admin"""
        # Create a super admin user
        org_id = org_admin_user.organization_id
        super_admin = User(
            email="superadmin@testorg.com",
            full_name="Super Admin",
            hashed_password=get_password_hash("testpass123"),
            role="super_admin",
            is_super_admin=True,
            organization_id=org_id,
            is_active=True
        )
        test_db.add(super_admin)
        test_db.commit()
        test_db.refresh(super_admin)
        
        token = self.get_token(client, org_admin_user.email, "testpass123")
        
        response = client.delete(
            f"/api/v1/org-users/users/{super_admin.id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 403
        assert "cannot delete super admin" in response.json()["detail"].lower()
    
    def test_management_delete_manager_success(self, client: TestClient, test_db: Session):
        """Test that management can delete managers"""
        org = Organization(
            name="Test Org",
            subdomain="testorg",
            status="active",
            primary_email="test@testorg.com",
            state_code="27"
        )
        test_db.add(org)
        test_db.commit()
        test_db.refresh(org)
        
        mgmt_user = User(
            email="management@testorg.com",
            full_name="Management User",
            hashed_password=get_password_hash("testpass123"),
            role="management",
            organization_id=org.id,
            is_active=True
        )
        test_db.add(mgmt_user)
        test_db.commit()
        test_db.refresh(mgmt_user)
        
        manager_to_delete = User(
            email="manager@testorg.com",
            full_name="Manager User",
            hashed_password=get_password_hash("testpass123"),
            role="manager",
            organization_id=org.id,
            is_active=True
        )
        test_db.add(manager_to_delete)
        test_db.commit()
        test_db.refresh(manager_to_delete)
        
        token = self.get_token(client, mgmt_user.email, "testpass123")
        
        response = client.delete(
            f"/api/v1/org-users/users/{manager_to_delete.id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
    
    def test_management_cannot_delete_org_admin(self, client: TestClient, test_db: Session):
        """Test that management cannot delete org_admin"""
        org = Organization(
            name="Test Org",
            subdomain="testorg",
            status="active",
            primary_email="test@testorg.com",
            state_code="27"
        )
        test_db.add(org)
        test_db.commit()
        test_db.refresh(org)
        
        mgmt_user = User(
            email="management@testorg.com",
            full_name="Management User",
            hashed_password=get_password_hash("testpass123"),
            role="management",
            organization_id=org.id,
            is_active=True
        )
        test_db.add(mgmt_user)
        test_db.commit()
        test_db.refresh(mgmt_user)
        
        org_admin = User(
            email="orgadmin@testorg.com",
            full_name="Org Admin",
            hashed_password=get_password_hash("testpass123"),
            role="org_admin",
            organization_id=org.id,
            is_active=True
        )
        test_db.add(org_admin)
        test_db.commit()
        test_db.refresh(org_admin)
        
        token = self.get_token(client, mgmt_user.email, "testpass123")
        
        response = client.delete(
            f"/api/v1/org-users/users/{org_admin.id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 403
    
    @staticmethod
    def get_token(client: TestClient, email: str, password: str) -> str:
        """Helper to get authentication token"""
        response = client.post(
            "/api/v1/token",
            data={"username": email, "password": password}
        )
        return response.json()["access_token"]


class TestPermissionSeeding:
    """Test that permissions are properly seeded by migration"""
    
    def test_gst_permissions_exist(self, test_db: Session):
        """Test that GST permissions were created"""
        gst_perms = test_db.query(ServicePermission).filter(
            ServicePermission.module == "gst"
        ).all()
        
        assert len(gst_perms) >= 3, "Should have at least 3 GST permissions"
        perm_names = [p.name for p in gst_perms]
        assert "gst_read" in perm_names
        assert "gst_view" in perm_names
    
    def test_settings_permissions_exist(self, test_db: Session):
        """Test that settings permissions were created"""
        settings_perms = test_db.query(ServicePermission).filter(
            ServicePermission.module == "settings"
        ).all()
        
        assert len(settings_perms) >= 5, "Should have multiple settings permissions"
        perm_names = [p.name for p in settings_perms]
        assert "settings_read" in perm_names
        assert "settings_view" in perm_names
        assert "settings_update" in perm_names
    
    def test_voucher_restricted_permissions_exist(self, test_db: Session):
        """Test that voucher-restricted permissions were created"""
        voucher_perms = test_db.query(ServicePermission).filter(
            ServicePermission.name.like("settings_voucher%")
        ).all()
        
        assert len(voucher_perms) >= 2, "Should have voucher-specific permissions"
        perm_names = [p.name for p in voucher_perms]
        assert any("prefix" in p for p in perm_names)
        assert any("counter" in p for p in perm_names)
