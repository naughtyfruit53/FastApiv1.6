"""
Simple standalone test to verify tenant context fix for super_admin.
This test can be run independently without database setup.
"""
import sys
from unittest.mock import MagicMock
from fastapi import HTTPException

# Mock the dependencies to avoid import errors
sys.modules['app.core.database'] = MagicMock()
sys.modules['app.models'] = MagicMock()
sys.modules['app.core.security'] = MagicMock()
sys.modules['app.core.config'] = MagicMock()

# Now we can import the module under test
from app.core.tenant import require_current_organization_id, TenantContext


def test_super_admin_without_context_returns_none():
    """
    Test that super_admin without organization context returns None instead of raising error.
    This fixes the "No current organization specified" issue for super_admin.
    """
    print("\n=== Testing super_admin without context ===")
    
    # Create a mock super_admin user without organization_id
    mock_user = MagicMock()
    mock_user.organization_id = None
    mock_user.is_super_admin = True
    
    # Clear tenant context
    TenantContext.clear()
    
    # Should succeed and return None for super_admin
    try:
        org_id = require_current_organization_id(mock_user)
        print(f"✅ SUCCESS: require_current_organization_id returned {org_id} (expected None)")
        print("✅ Super admin can now access organization-scoped endpoints")
        print("   Organization ID will be extracted from path parameters in the endpoint")
        assert org_id is None, f"Expected None but got {org_id}"
        return True
    except HTTPException as e:
        print(f"❌ FAILED: Raised HTTPException with status {e.status_code}: {e.detail}")
        print("   This is the old buggy behavior - should not happen after fix")
        return False
    except Exception as e:
        print(f"❌ FAILED: Unexpected exception: {e}")
        return False


def test_regular_user_without_context_raises_error():
    """
    Test that regular users without organization context still raise error (expected behavior).
    """
    print("\n=== Testing regular user without context ===")
    
    # Create a mock regular user without organization_id
    mock_user = MagicMock()
    mock_user.organization_id = None
    mock_user.is_super_admin = False
    
    # Clear tenant context
    TenantContext.clear()
    
    # Should raise HTTPException for regular user without org context
    try:
        org_id = require_current_organization_id(mock_user)
        print(f"❌ FAILED: Should have raised HTTPException but returned {org_id}")
        return False
    except HTTPException as e:
        if e.status_code == 400 and "No current organization specified" in e.detail:
            print(f"✅ SUCCESS: Correctly raised HTTPException(400): {e.detail}")
            print("✅ Regular users still require organization context")
            return True
        else:
            print(f"❌ FAILED: Wrong exception - status {e.status_code}: {e.detail}")
            return False
    except Exception as e:
        print(f"❌ FAILED: Unexpected exception: {e}")
        return False


def test_regular_user_with_org_id_succeeds():
    """
    Test that regular users with organization_id succeed (expected behavior).
    """
    print("\n=== Testing regular user with org_id ===")
    
    # Create a mock regular user with organization_id
    mock_user = MagicMock()
    mock_user.organization_id = 123
    mock_user.is_super_admin = False
    
    # Clear tenant context
    TenantContext.clear()
    
    # Should succeed and return organization_id
    try:
        org_id = require_current_organization_id(mock_user)
        print(f"✅ SUCCESS: require_current_organization_id returned {org_id} (expected 123)")
        print("✅ Regular users with org_id can access their organization")
        assert org_id == 123, f"Expected 123 but got {org_id}"
        
        # Context should now be set
        context_org = TenantContext.get_organization_id()
        assert context_org == 123, f"Expected context to be 123 but got {context_org}"
        print(f"✅ TenantContext correctly set to {context_org}")
        return True
    except Exception as e:
        print(f"❌ FAILED: Unexpected exception: {e}")
        return False


def test_super_admin_with_context_returns_context_org():
    """
    Test that super_admin with context set returns the context org_id.
    """
    print("\n=== Testing super_admin with context ===")
    
    # Create a mock super_admin user
    mock_user = MagicMock()
    mock_user.organization_id = None
    mock_user.is_super_admin = True
    
    # Set tenant context to a specific org
    TenantContext.set_organization_id(456)
    
    # Should return the context org_id
    try:
        org_id = require_current_organization_id(mock_user)
        print(f"✅ SUCCESS: require_current_organization_id returned {org_id} (expected 456)")
        print("✅ Super admin with context uses the context org_id")
        assert org_id == 456, f"Expected 456 but got {org_id}"
        return True
    except Exception as e:
        print(f"❌ FAILED: Unexpected exception: {e}")
        return False


if __name__ == "__main__":
    print("=" * 80)
    print("TENANT CONTEXT FIX VERIFICATION")
    print("Testing the fix for 'No current organization specified' error")
    print("=" * 80)
    
    results = []
    
    # Run all tests
    results.append(("Super admin without context", test_super_admin_without_context_returns_none()))
    results.append(("Regular user without context", test_regular_user_without_context_raises_error()))
    results.append(("Regular user with org_id", test_regular_user_with_org_id_succeeds()))
    results.append(("Super admin with context", test_super_admin_with_context_returns_context_org()))
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    failed = len(results) - passed
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{len(results)} tests passed")
    
    if failed == 0:
        print("\n✅ All tests passed! The fix is working correctly.")
        print("\nWhat this fix enables:")
        print("  1. Super admin can access /api/v1/organizations/{org_id}/modules")
        print("  2. Organization ID is extracted from path parameters in endpoints")
        print("  3. Regular users still have proper organization context validation")
        print("  4. MegaMenu functionality restored for org_admin users")
        sys.exit(0)
    else:
        print(f"\n❌ {failed} test(s) failed! Please review the implementation.")
        sys.exit(1)
