#!/usr/bin/env python3
"""
Validation script for platform role implementation

This script validates that the platform role refactor is correctly implemented:
1. Checks role enum definitions
2. Validates permission mappings
3. Verifies no legacy app_user references
4. Tests basic permission logic

Usage:
    python scripts/validate_platform_roles.py
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.schemas.user import UserRole, PlatformUserRole
from app.core.permissions import PermissionChecker, Permission


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(text: str):
    """Print a formatted header"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{text}{Colors.RESET}")
    print("=" * 60)


def print_success(text: str):
    """Print success message"""
    print(f"{Colors.GREEN}✓{Colors.RESET} {text}")


def print_error(text: str):
    """Print error message"""
    print(f"{Colors.RED}✗{Colors.RESET} {text}")


def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠{Colors.RESET} {text}")


def validate_role_enums() -> bool:
    """Validate role enum definitions"""
    print_header("1. Validating Role Enums")
    
    success = True
    
    # Check PlatformUserRole
    try:
        assert hasattr(PlatformUserRole, 'SUPER_ADMIN')
        assert hasattr(PlatformUserRole, 'APP_ADMIN')
        assert PlatformUserRole.SUPER_ADMIN.value == 'super_admin'
        assert PlatformUserRole.APP_ADMIN.value == 'app_admin'
        assert len(PlatformUserRole) == 2
        print_success("PlatformUserRole enum correctly defined")
    except AssertionError as e:
        print_error(f"PlatformUserRole enum validation failed: {e}")
        success = False
    
    # Check UserRole includes platform roles
    try:
        assert hasattr(UserRole, 'SUPER_ADMIN')
        assert hasattr(UserRole, 'APP_ADMIN')
        assert UserRole.SUPER_ADMIN.value == 'super_admin'
        assert UserRole.APP_ADMIN.value == 'app_admin'
        print_success("UserRole enum includes platform roles")
    except AssertionError as e:
        print_error(f"UserRole enum validation failed: {e}")
        success = False
    
    # Check no app_user role
    try:
        user_role_values = [role.value for role in UserRole]
        platform_role_values = [role.value for role in PlatformUserRole]
        assert 'app_user' not in user_role_values
        assert 'app_user' not in platform_role_values
        print_success("No app_user role found (as expected)")
    except AssertionError:
        print_error("Found app_user role (should not exist)")
        success = False
    
    return success


def validate_permission_mappings() -> bool:
    """Validate permission mappings"""
    print_header("2. Validating Permission Mappings")
    
    success = True
    
    # Check super_admin permissions
    try:
        super_admin_perms = PermissionChecker.PLATFORM_ROLE_PERMISSIONS.get('super_admin', [])
        
        required_super_admin_perms = [
            Permission.SUPER_ADMIN,
            Permission.MANAGE_USERS,
            Permission.CREATE_USERS,
            Permission.RESET_ANY_PASSWORD,
            Permission.RESET_ANY_DATA,
            Permission.FACTORY_RESET,
            Permission.DELETE_ORGANIZATIONS,
        ]
        
        for perm in required_super_admin_perms:
            assert perm in super_admin_perms, f"Missing {perm}"
        
        print_success(f"super_admin has all required permissions ({len(super_admin_perms)} total)")
    except AssertionError as e:
        print_error(f"super_admin permission validation failed: {e}")
        success = False
    
    # Check app_admin permissions
    try:
        app_admin_perms = PermissionChecker.PLATFORM_ROLE_PERMISSIONS.get('app_admin', [])
        
        # Permissions app_admin SHOULD have
        required_app_admin_perms = [
            Permission.PLATFORM_ADMIN,
            Permission.MANAGE_ORGANIZATIONS,
            Permission.CREATE_ORGANIZATIONS,
            Permission.VIEW_AUDIT_LOGS,
        ]
        
        for perm in required_app_admin_perms:
            assert perm in app_admin_perms, f"Missing {perm}"
        
        print_success(f"app_admin has required permissions ({len(app_admin_perms)} total)")
    except AssertionError as e:
        print_error(f"app_admin permission validation failed: {e}")
        success = False
    
    # Check app_admin restrictions
    try:
        app_admin_perms = PermissionChecker.PLATFORM_ROLE_PERMISSIONS.get('app_admin', [])
        
        # Permissions app_admin should NOT have
        forbidden_app_admin_perms = [
            Permission.MANAGE_USERS,
            Permission.CREATE_USERS,
            Permission.DELETE_USERS,
            Permission.RESET_ANY_PASSWORD,
            Permission.RESET_ANY_DATA,
            Permission.FACTORY_RESET,
            Permission.DELETE_ORGANIZATIONS,
            Permission.VIEW_ALL_AUDIT_LOGS,
        ]
        
        for perm in forbidden_app_admin_perms:
            assert perm not in app_admin_perms, f"Should not have {perm}"
        
        print_success("app_admin properly restricted (no dangerous permissions)")
    except AssertionError as e:
        print_error(f"app_admin restriction validation failed: {e}")
        success = False
    
    # Check no platform_admin key
    try:
        assert 'platform_admin' not in PermissionChecker.PLATFORM_ROLE_PERMISSIONS
        print_success("No platform_admin key found (correctly renamed to app_admin)")
    except AssertionError:
        print_error("Found platform_admin key (should be app_admin)")
        success = False
    
    # Check no app_user key
    try:
        assert 'app_user' not in PermissionChecker.ROLE_PERMISSIONS
        assert 'app_user' not in PermissionChecker.PLATFORM_ROLE_PERMISSIONS
        print_success("No app_user key found in permission mappings")
    except AssertionError:
        print_error("Found app_user key in permission mappings")
        success = False
    
    return success


def validate_permission_hierarchy() -> bool:
    """Validate permission hierarchy"""
    print_header("3. Validating Permission Hierarchy")
    
    success = True
    
    try:
        super_admin_perms = set(PermissionChecker.PLATFORM_ROLE_PERMISSIONS.get('super_admin', []))
        app_admin_perms = set(PermissionChecker.PLATFORM_ROLE_PERMISSIONS.get('app_admin', []))
        
        # super_admin should have more permissions
        assert len(super_admin_perms) > len(app_admin_perms)
        print_success(f"super_admin has more permissions ({len(super_admin_perms)}) than app_admin ({len(app_admin_perms)})")
        
        # Check critical permission differences
        super_admin_only = super_admin_perms - app_admin_perms
        critical_perms = {
            Permission.MANAGE_USERS,
            Permission.CREATE_USERS,
            Permission.RESET_ANY_PASSWORD,
            Permission.RESET_ANY_DATA,
            Permission.FACTORY_RESET,
        }
        
        assert critical_perms.issubset(super_admin_only)
        print_success(f"Critical permissions are super_admin only: {len(critical_perms)} permissions")
        
    except AssertionError as e:
        print_error(f"Permission hierarchy validation failed: {e}")
        success = False
    
    return success


def validate_mock_permission_checks() -> bool:
    """Validate permission checker with mock users"""
    print_header("4. Validating Permission Checker Logic")
    
    success = True
    
    # Mock super_admin user
    class MockSuperAdmin:
        role = "super_admin"
        is_super_admin = True
        id = 1
        email = "super@example.com"
        organization_id = None
    
    # Mock app_admin user
    class MockAppAdmin:
        role = "app_admin"
        is_super_admin = False
        id = 2
        email = "appadmin@example.com"
        organization_id = None
    
    try:
        super_admin = MockSuperAdmin()
        
        # Super admin should have these permissions
        assert PermissionChecker.has_platform_permission(super_admin, Permission.MANAGE_USERS)
        assert PermissionChecker.has_platform_permission(super_admin, Permission.RESET_ANY_DATA)
        assert PermissionChecker.has_platform_permission(super_admin, Permission.FACTORY_RESET)
        
        print_success("super_admin permission checks working correctly")
    except AssertionError as e:
        print_error(f"super_admin permission check failed: {e}")
        success = False
    
    try:
        app_admin = MockAppAdmin()
        
        # App admin should NOT have these permissions
        assert not PermissionChecker.has_platform_permission(app_admin, Permission.MANAGE_USERS)
        assert not PermissionChecker.has_platform_permission(app_admin, Permission.RESET_ANY_DATA)
        assert not PermissionChecker.has_platform_permission(app_admin, Permission.FACTORY_RESET)
        
        # But should have these
        assert PermissionChecker.has_platform_permission(app_admin, Permission.MANAGE_ORGANIZATIONS)
        
        print_success("app_admin permission checks working correctly")
    except AssertionError as e:
        print_error(f"app_admin permission check failed: {e}")
        success = False
    
    return success


def run_validation():
    """Run all validation checks"""
    print(f"\n{Colors.BOLD}Platform Role Validation{Colors.RESET}")
    print("=" * 60)
    print("Validating platform role refactor implementation...")
    
    results = {
        "Role Enums": validate_role_enums(),
        "Permission Mappings": validate_permission_mappings(),
        "Permission Hierarchy": validate_permission_hierarchy(),
        "Permission Checker": validate_mock_permission_checks(),
    }
    
    # Summary
    print_header("Validation Summary")
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for check, result in results.items():
        if result:
            print_success(f"{check}: PASSED")
        else:
            print_error(f"{check}: FAILED")
    
    print("\n" + "=" * 60)
    
    if passed == total:
        print(f"{Colors.GREEN}{Colors.BOLD}✓ ALL VALIDATIONS PASSED ({passed}/{total}){Colors.RESET}")
        print("\nPlatform role implementation is correct!")
        return 0
    else:
        print(f"{Colors.RED}{Colors.BOLD}✗ SOME VALIDATIONS FAILED ({passed}/{total}){Colors.RESET}")
        print(f"\nPlease review the failed checks above.")
        return 1


if __name__ == "__main__":
    try:
        exit_code = run_validation()
        sys.exit(exit_code)
    except Exception as e:
        print_error(f"Validation script failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
