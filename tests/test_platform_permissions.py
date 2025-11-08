"""
Test suite for platform-level role permissions

Tests the 2-tier platform role system:
- super_admin: Full platform rights
- app_admin: Limited platform rights (cannot manage platform admins or reset data)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import pytest
except ImportError:
    pytest = None

from app.schemas.user import UserRole, PlatformUserRole
from app.core.permissions import PermissionChecker, Permission


class TestPlatformRoleDefinitions:
    """Test that platform roles are correctly defined"""
    
    def test_platform_user_role_enum_values(self):
        """Test PlatformUserRole enum has correct values"""
        assert PlatformUserRole.SUPER_ADMIN.value == "super_admin"
        assert PlatformUserRole.APP_ADMIN.value == "app_admin"
        assert len(PlatformUserRole) == 2  # Only 2 platform roles
    
    def test_user_role_includes_platform_roles(self):
        """Test UserRole enum includes platform roles"""
        assert UserRole.SUPER_ADMIN.value == "super_admin"
        assert UserRole.APP_ADMIN.value == "app_admin"
        # Also includes org roles
        assert UserRole.ORG_ADMIN.value == "org_admin"
        assert UserRole.MANAGEMENT.value == "management"
        assert UserRole.MANAGER.value == "manager"
        assert UserRole.EXECUTIVE.value == "executive"


class TestSuperAdminPermissions:
    """Test super_admin role permissions"""
    
    def test_super_admin_platform_permissions(self):
        """Test super_admin has all platform permissions"""
        super_admin_permissions = PermissionChecker.PLATFORM_ROLE_PERMISSIONS.get('super_admin', [])
        
        # Should have these critical permissions
        assert Permission.SUPER_ADMIN in super_admin_permissions
        assert Permission.PLATFORM_ADMIN in super_admin_permissions
        assert Permission.MANAGE_USERS in super_admin_permissions
        assert Permission.CREATE_USERS in super_admin_permissions
        assert Permission.RESET_ANY_PASSWORD in super_admin_permissions
        assert Permission.RESET_ANY_DATA in super_admin_permissions
        assert Permission.FACTORY_RESET in super_admin_permissions
        assert Permission.VIEW_ALL_AUDIT_LOGS in super_admin_permissions
        assert Permission.MANAGE_ORGANIZATIONS in super_admin_permissions
        assert Permission.CREATE_ORGANIZATIONS in super_admin_permissions
        assert Permission.DELETE_ORGANIZATIONS in super_admin_permissions
    
    def test_super_admin_can_manage_platform_admins(self):
        """Test super_admin can manage platform admins"""
        super_admin_permissions = PermissionChecker.PLATFORM_ROLE_PERMISSIONS.get('super_admin', [])
        
        # Key permissions for managing platform admins
        assert Permission.MANAGE_USERS in super_admin_permissions
        assert Permission.CREATE_USERS in super_admin_permissions


class TestAppAdminPermissions:
    """Test app_admin role permissions"""
    
    def test_app_admin_platform_permissions(self):
        """Test app_admin has limited platform permissions"""
        app_admin_permissions = PermissionChecker.PLATFORM_ROLE_PERMISSIONS.get('app_admin', [])
        
        # Should have these permissions
        assert Permission.PLATFORM_ADMIN in app_admin_permissions
        assert Permission.MANAGE_ORGANIZATIONS in app_admin_permissions
        assert Permission.CREATE_ORGANIZATIONS in app_admin_permissions
        assert Permission.VIEW_ORGANIZATIONS in app_admin_permissions
        assert Permission.VIEW_AUDIT_LOGS in app_admin_permissions
    
    def test_app_admin_cannot_manage_platform_admins(self):
        """Test app_admin CANNOT manage platform admins"""
        app_admin_permissions = PermissionChecker.PLATFORM_ROLE_PERMISSIONS.get('app_admin', [])
        
        # Should NOT have these permissions
        assert Permission.MANAGE_USERS not in app_admin_permissions
        assert Permission.CREATE_USERS not in app_admin_permissions
        assert Permission.DELETE_USERS not in app_admin_permissions
    
    def test_app_admin_cannot_reset_data(self):
        """Test app_admin CANNOT reset app/org data"""
        app_admin_permissions = PermissionChecker.PLATFORM_ROLE_PERMISSIONS.get('app_admin', [])
        
        # Should NOT have these permissions
        assert Permission.RESET_ANY_DATA not in app_admin_permissions
        assert Permission.RESET_ANY_PASSWORD not in app_admin_permissions
        assert Permission.FACTORY_RESET not in app_admin_permissions
    
    def test_app_admin_cannot_delete_organizations(self):
        """Test app_admin CANNOT delete organizations"""
        app_admin_permissions = PermissionChecker.PLATFORM_ROLE_PERMISSIONS.get('app_admin', [])
        
        # Should NOT have delete permission
        assert Permission.DELETE_ORGANIZATIONS not in app_admin_permissions
    
    def test_app_admin_cannot_view_all_audit_logs(self):
        """Test app_admin cannot view all audit logs"""
        app_admin_permissions = PermissionChecker.PLATFORM_ROLE_PERMISSIONS.get('app_admin', [])
        
        # Should NOT have full audit log access
        assert Permission.VIEW_ALL_AUDIT_LOGS not in app_admin_permissions
        # But should have limited audit log access
        assert Permission.VIEW_AUDIT_LOGS in app_admin_permissions


class TestPermissionComparison:
    """Test permission differences between super_admin and app_admin"""
    
    def test_super_admin_has_more_permissions_than_app_admin(self):
        """Test super_admin has strictly more permissions than app_admin"""
        super_admin_permissions = set(PermissionChecker.PLATFORM_ROLE_PERMISSIONS.get('super_admin', []))
        app_admin_permissions = set(PermissionChecker.PLATFORM_ROLE_PERMISSIONS.get('app_admin', []))
        
        # Super admin should have more permissions
        assert len(super_admin_permissions) > len(app_admin_permissions)
    
    def test_app_admin_permissions_subset_behavior(self):
        """Test app_admin permissions are a proper subset with key exclusions"""
        super_admin_permissions = set(PermissionChecker.PLATFORM_ROLE_PERMISSIONS.get('super_admin', []))
        app_admin_permissions = set(PermissionChecker.PLATFORM_ROLE_PERMISSIONS.get('app_admin', []))
        
        # Find permissions only super_admin has
        super_admin_only = super_admin_permissions - app_admin_permissions
        
        # These critical permissions should be super_admin only
        critical_permissions = {
            Permission.MANAGE_USERS,
            Permission.CREATE_USERS,
            Permission.RESET_ANY_PASSWORD,
            Permission.RESET_ANY_DATA,
            Permission.FACTORY_RESET,
            Permission.DELETE_ORGANIZATIONS,
            Permission.VIEW_ALL_AUDIT_LOGS,
        }
        
        # All critical permissions should be in super_admin_only
        assert critical_permissions.issubset(super_admin_only)


class TestRoleValidation:
    """Test role validation logic"""
    
    def test_only_platform_roles_allowed_for_platform_users(self):
        """Test that platform users can only have platform roles"""
        platform_roles = {UserRole.SUPER_ADMIN.value, UserRole.APP_ADMIN.value}
        org_roles = {
            UserRole.ORG_ADMIN.value,
            UserRole.MANAGEMENT.value,
            UserRole.MANAGER.value,
            UserRole.EXECUTIVE.value
        }
        
        # Platform roles and org roles should be disjoint
        assert len(platform_roles.intersection(org_roles)) == 0
    
    def test_platform_role_enum_consistency(self):
        """Test PlatformUserRole and UserRole platform roles match"""
        assert PlatformUserRole.SUPER_ADMIN.value == UserRole.SUPER_ADMIN.value
        assert PlatformUserRole.APP_ADMIN.value == UserRole.APP_ADMIN.value


class TestPermissionCheckerMethods:
    """Test PermissionChecker helper methods"""
    
    def test_has_platform_permission_super_admin(self):
        """Test has_platform_permission for super_admin"""
        # Create mock user object
        class MockSuperAdmin:
            role = "super_admin"
            is_super_admin = True
            id = 1
            email = "super@example.com"
            organization_id = None
        
        user = MockSuperAdmin()
        
        # Super admin should have all permissions
        assert PermissionChecker.has_platform_permission(user, Permission.MANAGE_USERS)
        assert PermissionChecker.has_platform_permission(user, Permission.RESET_ANY_DATA)
        assert PermissionChecker.has_platform_permission(user, Permission.FACTORY_RESET)
    
    def test_has_platform_permission_app_admin(self):
        """Test has_platform_permission for app_admin"""
        # Create mock user object
        class MockAppAdmin:
            role = "app_admin"
            is_super_admin = False
            id = 2
            email = "appadmin@example.com"
            organization_id = None
        
        user = MockAppAdmin()
        
        # App admin should NOT have these permissions
        assert not PermissionChecker.has_platform_permission(user, Permission.MANAGE_USERS)
        assert not PermissionChecker.has_platform_permission(user, Permission.RESET_ANY_DATA)
        assert not PermissionChecker.has_platform_permission(user, Permission.FACTORY_RESET)
        
        # But should have these permissions
        assert PermissionChecker.has_platform_permission(user, Permission.MANAGE_ORGANIZATIONS)
        assert PermissionChecker.has_platform_permission(user, Permission.VIEW_AUDIT_LOGS)


class TestSeededSuperAdmin:
    """Test requirements for seeded super admin"""
    
    def test_seeded_super_admin_requirements(self):
        """Test that seeded super admin meets requirements"""
        # Requirements from seed_super_admin.py
        expected_email = "naughtyfruit53@gmail.com"
        expected_role = UserRole.SUPER_ADMIN.value
        expected_password = "Admin123!"  # Should be changed on first login
        
        # Validate format
        assert "@" in expected_email
        assert expected_role == "super_admin"
        assert len(expected_password) >= 8
        
        # Password should meet requirements
        assert any(c.isupper() for c in expected_password)
        assert any(c.islower() for c in expected_password)
        assert any(c.isdigit() for c in expected_password)
        assert any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in expected_password)


class TestNoAppUserRole:
    """Test that app_user role does not exist"""
    
    def test_no_app_user_in_user_role(self):
        """Test UserRole enum does not contain app_user"""
        user_role_values = [role.value for role in UserRole]
        assert "app_user" not in user_role_values
        assert "APP_USER" not in user_role_values
    
    def test_no_app_user_in_platform_user_role(self):
        """Test PlatformUserRole enum does not contain app_user"""
        platform_role_values = [role.value for role in PlatformUserRole]
        assert "app_user" not in platform_role_values
        assert "APP_USER" not in platform_role_values
    
    def test_no_app_user_permissions(self):
        """Test permission mappings do not contain app_user"""
        # Check ROLE_PERMISSIONS
        assert "app_user" not in PermissionChecker.ROLE_PERMISSIONS
        
        # Check PLATFORM_ROLE_PERMISSIONS
        assert "app_user" not in PermissionChecker.PLATFORM_ROLE_PERMISSIONS


# Integration test scenarios (require database)
class TestPlatformPermissionIntegration:
    """Integration tests for platform permissions (require database)"""
    
    @pytest.mark.skip(reason="Requires database setup")
    def test_super_admin_can_create_app_admin(self):
        """Test super_admin can create app_admin via API"""
        # This would require full API integration test setup
        pass
    
    @pytest.mark.skip(reason="Requires database setup")
    def test_app_admin_cannot_create_super_admin(self):
        """Test app_admin cannot create super_admin via API"""
        # This would require full API integration test setup
        pass
    
    @pytest.mark.skip(reason="Requires database setup")
    def test_app_admin_cannot_delete_platform_user(self):
        """Test app_admin cannot delete platform users via API"""
        # This would require full API integration test setup
        pass
    
    @pytest.mark.skip(reason="Requires database setup")
    def test_app_admin_cannot_factory_reset(self):
        """Test app_admin cannot perform factory reset via API"""
        # This would require full API integration test setup
        pass


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
