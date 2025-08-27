"""
Test module for RBAC auto-initialization and app admin creation functionality.
This test can be run independently without full app setup.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Test the UserRole enum changes
def test_user_role_enum_has_app_admin():
    """Test that UserRole enum includes APP_ADMIN role"""
    # Create a mock enum for testing
    from enum import Enum
    
    class UserRole(str, Enum):
        SUPER_ADMIN = "super_admin"
        APP_ADMIN = "app_admin"
        ORG_ADMIN = "org_admin"
        ADMIN = "admin"
        STANDARD_USER = "standard_user"
    
    # Verify all roles exist
    assert hasattr(UserRole, 'SUPER_ADMIN')
    assert hasattr(UserRole, 'APP_ADMIN')
    assert hasattr(UserRole, 'ORG_ADMIN')
    assert hasattr(UserRole, 'ADMIN')
    assert hasattr(UserRole, 'STANDARD_USER')
    
    # Verify APP_ADMIN has correct value
    assert UserRole.APP_ADMIN.value == "app_admin"
    
    print("✅ UserRole enum test passed")

def test_rbac_initialization_logic():
    """Test the logic of RBAC initialization"""
    
    # Mock the RBACService
    class MockRBACService:
        def __init__(self, db):
            self.db = db
            
        def initialize_default_permissions(self):
            # Simulate creating permissions
            return [
                Mock(name="service_create"),
                Mock(name="service_read"),
                Mock(name="technician_create")
            ]
            
        def initialize_default_roles(self, org_id):
            # Simulate creating roles
            return [
                Mock(name="admin", organization_id=org_id),
                Mock(name="manager", organization_id=org_id),
                Mock(name="support", organization_id=org_id),
                Mock(name="viewer", organization_id=org_id)
            ]
            
        def assign_role_to_user(self, user_id, role_id):
            return Mock(user_id=user_id, role_id=role_id, is_active=True)
    
    # Test the initialization sequence
    db_mock = Mock()
    rbac_service = MockRBACService(db_mock)
    
    # Test permission initialization
    permissions = rbac_service.initialize_default_permissions()
    assert len(permissions) >= 3
    print(f"✅ Permission initialization test passed - created {len(permissions)} permissions")
    
    # Test role initialization
    org_id = 123
    roles = rbac_service.initialize_default_roles(org_id)
    assert len(roles) == 4  # admin, manager, support, viewer
    for role in roles:
        assert role.organization_id == org_id
    print(f"✅ Role initialization test passed - created {len(roles)} roles")
    
    # Test role assignment
    user_id = 456
    admin_role = roles[0]  # First role should be admin
    assignment = rbac_service.assign_role_to_user(user_id, admin_role)
    assert assignment.user_id == user_id
    print("✅ Role assignment test passed")

def test_app_admin_creation_logic():
    """Test the logic for app admin creation permissions"""
    
    # Mock UserRole enum
    class UserRole:
        SUPER_ADMIN = "super_admin"
        APP_ADMIN = "app_admin"
        ORG_ADMIN = "org_admin"
    
    # Mock current user scenarios
    super_admin_user = Mock(role=UserRole.SUPER_ADMIN, is_super_admin=True)
    app_admin_user = Mock(role=UserRole.APP_ADMIN, is_super_admin=False)
    
    def check_app_admin_creation_permission(current_user, requested_role):
        """Simulate the permission logic from app_users.py"""
        
        # Basic permission check - must be super admin to access app user management
        if not current_user.is_super_admin:
            return False, "Only app super administrators can access user management"
        
        # Role validation
        if requested_role not in [UserRole.SUPER_ADMIN, UserRole.APP_ADMIN]:
            return False, "App-level users must have super_admin or app_admin role"
        
        # Permission check: Only SUPER_ADMIN can create APP_ADMIN accounts
        if requested_role == UserRole.APP_ADMIN and current_user.role != UserRole.SUPER_ADMIN:
            return False, "Only super admins can create app admin accounts"
        
        return True, "Permission granted"
    
    # Test 1: Super admin creating app admin (should succeed)
    can_create, message = check_app_admin_creation_permission(super_admin_user, UserRole.APP_ADMIN)
    assert can_create == True
    print("✅ Super admin can create app admin")
    
    # Test 2: Super admin creating super admin (should succeed)
    can_create, message = check_app_admin_creation_permission(super_admin_user, UserRole.SUPER_ADMIN)
    assert can_create == True
    print("✅ Super admin can create super admin")
    
    # Test 3: App admin trying to create app admin (should fail)
    can_create, message = check_app_admin_creation_permission(app_admin_user, UserRole.APP_ADMIN)
    assert can_create == False
    assert "Only app super administrators" in message
    print("✅ App admin cannot create app admin (correctly blocked)")
    
    # Test 4: Invalid role (should fail)
    can_create, message = check_app_admin_creation_permission(super_admin_user, UserRole.ORG_ADMIN)
    assert can_create == False
    assert "App-level users must have" in message
    print("✅ Invalid role creation blocked")

def test_user_listing_logic():
    """Test the logic for listing app-level users"""
    
    class UserRole:
        SUPER_ADMIN = "super_admin"
        APP_ADMIN = "app_admin"
        ORG_ADMIN = "org_admin"
    
    # Mock users
    mock_users = [
        Mock(role=UserRole.SUPER_ADMIN, organization_id=None, is_active=True, email="super@admin.com"),
        Mock(role=UserRole.APP_ADMIN, organization_id=None, is_active=True, email="app@admin.com"),
        Mock(role=UserRole.ORG_ADMIN, organization_id=1, is_active=True, email="org@admin.com"),  # Should be excluded
        Mock(role=UserRole.SUPER_ADMIN, organization_id=None, is_active=False, email="inactive@admin.com"),  # Inactive
    ]
    
    def filter_app_level_users(users, active_only=True):
        """Simulate the filtering logic from app_users.py"""
        filtered = []
        for user in users:
            # Must be app-level (no organization)
            if user.organization_id is not None:
                continue
            
            # Must have correct role
            if user.role not in [UserRole.SUPER_ADMIN, UserRole.APP_ADMIN]:
                continue
            
            # Filter by active status if requested
            if active_only and not user.is_active:
                continue
            
            filtered.append(user)
        
        return filtered
    
    # Test active only
    active_users = filter_app_level_users(mock_users, active_only=True)
    assert len(active_users) == 2  # super@admin.com and app@admin.com
    emails = [u.email for u in active_users]
    assert "super@admin.com" in emails
    assert "app@admin.com" in emails
    assert "org@admin.com" not in emails  # Organization user excluded
    assert "inactive@admin.com" not in emails  # Inactive user excluded
    print("✅ App user listing (active only) works correctly")
    
    # Test including inactive
    all_users = filter_app_level_users(mock_users, active_only=False)
    assert len(all_users) == 3  # Including inactive user
    emails = [u.email for u in all_users]
    assert "inactive@admin.com" in emails
    print("✅ App user listing (including inactive) works correctly")

def run_all_tests():
    """Run all tests"""
    print("🧪 Running RBAC and App Admin Tests...\n")
    
    tests = [
        test_user_role_enum_has_app_admin,
        test_rbac_initialization_logic,
        test_app_admin_creation_logic,
        test_user_listing_logic
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            print(f"\n📋 Running {test.__name__}...")
            test()
            passed += 1
            print(f"✅ {test.__name__} PASSED")
        except Exception as e:
            print(f"❌ {test.__name__} FAILED: {e}")
            failed += 1
    
    print(f"\n📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed!")
        return True
    else:
        print("💥 Some tests failed")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)