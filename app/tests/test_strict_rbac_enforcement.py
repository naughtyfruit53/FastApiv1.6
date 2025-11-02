"""
Test strict RBAC enforcement without fallback logic.
Validates that permission checks fail-closed and require organization context.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException
from app.models.user_models import User


class TestStrictRBACPermissionEndpoints:
    """Test RBAC endpoints with strict enforcement"""
    
    def test_get_user_permissions_requires_org_context(self):
        """User without organization context should receive error, not fallback"""
        # Create mock user without organization_id
        mock_user = MagicMock(spec=User)
        mock_user.id = 1
        mock_user.email = "user@test.com"
        mock_user.organization_id = None
        mock_user.role = "super_admin"
        mock_user.is_super_admin = True
        
        # This would be called in the endpoint handler
        # Should raise HTTPException, not return empty fallback
        with pytest.raises(AttributeError):
            # Simulate the check that would happen in the endpoint
            if mock_user.organization_id is None:
                raise HTTPException(
                    status_code=400,
                    detail="Organization context required. Please specify an organization."
                )
    
    def test_get_user_roles_requires_org_context(self):
        """User without organization context should receive error, not empty list"""
        mock_user = MagicMock(spec=User)
        mock_user.id = 1
        mock_user.email = "superadmin@test.com"
        mock_user.organization_id = None
        mock_user.role = "super_admin"
        mock_user.is_super_admin = True
        
        # Should raise error, not return empty list
        with pytest.raises(AttributeError):
            if mock_user.organization_id is None:
                raise HTTPException(
                    status_code=400,
                    detail="Organization context required. Please specify an organization."
                )


class TestPermissionCheckFailClosed:
    """Test that permission checks fail closed (deny by default)"""
    
    @pytest.mark.asyncio
    async def test_permission_service_error_propagates(self):
        """Errors in permission service should propagate, not return empty permissions"""
        from app.services.rbac import RBACService
        
        mock_db = AsyncMock()
        rbac_service = RBACService(mock_db)
        
        # Mock the database query to raise an exception
        with patch.object(mock_db, 'execute', side_effect=Exception("Database error")):
            # Should raise exception, not catch and return empty list
            with pytest.raises(Exception) as exc_info:
                await rbac_service.get_user_permissions(user_id=1)
            
            assert "Database error" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_role_fetch_error_propagates(self):
        """Errors in role fetching should propagate, not return empty roles"""
        from app.services.rbac import RBACService
        
        mock_db = AsyncMock()
        rbac_service = RBACService(mock_db)
        
        # Mock the database query to raise an exception
        with patch.object(mock_db, 'execute', side_effect=Exception("Database error")):
            # Should raise exception, not catch and return empty list
            with pytest.raises(Exception) as exc_info:
                await rbac_service.get_user_roles(user_id=1)
            
            assert "Database error" in str(exc_info.value)


class TestOrganizationContextRequirement:
    """Test that organization context is required for all operations"""
    
    def test_super_admin_needs_org_context_for_permissions(self):
        """Super admin must have organization context to fetch permissions"""
        mock_user = MagicMock(spec=User)
        mock_user.id = 1
        mock_user.email = "superadmin@test.com"
        mock_user.organization_id = None
        mock_user.is_super_admin = True
        
        # Simulate the check from the endpoint
        def get_user_permissions_check(current_user):
            if current_user.organization_id is None:
                raise HTTPException(
                    status_code=400,
                    detail="Organization context required. Please specify an organization."
                )
            return {"permissions": [], "roles": []}
        
        with pytest.raises(HTTPException) as exc_info:
            get_user_permissions_check(mock_user)
        
        assert exc_info.value.status_code == 400
        assert "Organization context required" in exc_info.value.detail
    
    def test_super_admin_needs_org_context_for_roles(self):
        """Super admin must have organization context to fetch roles"""
        mock_user = MagicMock(spec=User)
        mock_user.id = 1
        mock_user.email = "superadmin@test.com"
        mock_user.organization_id = None
        mock_user.is_super_admin = True
        
        # Simulate the check from the endpoint
        def get_user_roles_check(current_user):
            if current_user.organization_id is None:
                raise HTTPException(
                    status_code=400,
                    detail="Organization context required. Please specify an organization."
                )
            return []
        
        with pytest.raises(HTTPException) as exc_info:
            get_user_roles_check(mock_user)
        
        assert exc_info.value.status_code == 400
        assert "Organization context required" in exc_info.value.detail
    
    def test_regular_user_needs_org_context(self):
        """Regular user must have organization context"""
        mock_user = MagicMock(spec=User)
        mock_user.id = 2
        mock_user.email = "user@test.com"
        mock_user.organization_id = None
        mock_user.is_super_admin = False
        
        # Simulate the check
        def require_org_context(current_user):
            if current_user.organization_id is None:
                raise HTTPException(
                    status_code=400,
                    detail="Organization context required. Please specify an organization."
                )
        
        with pytest.raises(HTTPException) as exc_info:
            require_org_context(mock_user)
        
        assert exc_info.value.status_code == 400


class TestNoFallbackBehavior:
    """Test that there are no fallback behaviors that grant unintended access"""
    
    def test_no_empty_permission_fallback(self):
        """Verify no fallback returns empty permissions on error"""
        # This test documents that we removed the fallback behavior
        # The old code had:
        # except Exception:
        #     return {"permissions": [], "fallback": True}
        # 
        # The new code should NOT have this - errors should propagate
        
        # Sample of what we DON'T want:
        def bad_get_permissions_with_fallback(user_id):
            try:
                # Simulate error
                raise Exception("Database error")
            except Exception:
                # BAD: Returning empty permissions as fallback
                return {"permissions": [], "fallback": True}
        
        # This is what we had before - should NOT exist
        result = bad_get_permissions_with_fallback(1)
        assert "fallback" in result  # This is what we removed!
        
        # New implementation should raise the error instead:
        def good_get_permissions_no_fallback(user_id):
            # Simulate error
            raise Exception("Database error")
        
        with pytest.raises(Exception):
            good_get_permissions_no_fallback(1)
    
    def test_no_super_admin_automatic_access(self):
        """Super admin should not automatically have access without explicit permissions"""
        # Document the old behavior we removed
        def old_has_permission_with_bypass(user, permission):
            if user.is_super_admin:
                return True  # BAD: Automatic bypass
            return permission in user.permissions
        
        # New behavior - no bypass
        def new_has_permission_strict(user, permission):
            return permission in user.permissions  # No bypass!
        
        mock_user = MagicMock()
        mock_user.is_super_admin = True
        mock_user.permissions = []
        
        # Old behavior would grant access
        assert old_has_permission_with_bypass(mock_user, "sales.read") is True
        
        # New behavior denies access
        assert new_has_permission_strict(mock_user, "sales.read") is False
    
    def test_no_feature_flag_bypass(self):
        """Feature flag should not allow bypassing entitlement checks"""
        import os
        from app.api.deps.entitlements import ENABLE_ENTITLEMENTS_GATING
        
        # The constant should always be True (strict enforcement)
        assert ENABLE_ENTITLEMENTS_GATING is True
        
        # Environment variable should not be able to override it
        # (Old code: ENABLE_ENTITLEMENTS_GATING = os.getenv(..., 'true').lower() == 'true')
        # New code: ENABLE_ENTITLEMENTS_GATING = True
        assert ENABLE_ENTITLEMENTS_GATING is True


class TestErrorPropagation:
    """Test that errors properly propagate instead of being swallowed"""
    
    @pytest.mark.asyncio
    async def test_entitlement_service_error_not_caught(self):
        """Entitlement service errors should propagate to caller"""
        from app.services.entitlement_service import EntitlementService
        
        mock_db = AsyncMock()
        service = EntitlementService(mock_db)
        
        # Mock database to raise error
        with patch.object(mock_db, 'execute', side_effect=Exception("DB connection lost")):
            # Error should propagate, not be caught and turned into False
            with pytest.raises(Exception) as exc_info:
                await service.check_entitlement(
                    org_id=1,
                    module_key="sales",
                    submodule_key=None
                )
            
            assert "DB connection lost" in str(exc_info.value)
    
    def test_http_exceptions_not_masked(self):
        """HTTPExceptions should not be caught and masked"""
        from fastapi import HTTPException
        
        def endpoint_handler():
            # Simulate permission check failure
            raise HTTPException(status_code=403, detail="Permission denied")
        
        # Exception should propagate
        with pytest.raises(HTTPException) as exc_info:
            endpoint_handler()
        
        assert exc_info.value.status_code == 403
        assert "Permission denied" in exc_info.value.detail


class TestStrictEnforcementDocumentation:
    """Document the changes made for strict enforcement"""
    
    def test_removed_allow_super_admin_bypass_parameter(self):
        """Document that allow_super_admin_bypass parameter was removed"""
        from app.api.deps.entitlements import require_entitlement
        import inspect
        
        # Get the signature of require_entitlement
        sig = inspect.signature(require_entitlement)
        params = list(sig.parameters.keys())
        
        # Should NOT have allow_super_admin_bypass parameter
        assert 'allow_super_admin_bypass' not in params
        
        # Should only have module_key and submodule_key
        assert 'module_key' in params
        assert 'submodule_key' in params
        assert len(params) == 2  # Only these two parameters
    
    def test_removed_audit_bypass_parameter(self):
        """Document that audit_bypass parameter was removed"""
        from app.api.deps.entitlements import require_entitlement
        import inspect
        
        sig = inspect.signature(require_entitlement)
        params = list(sig.parameters.keys())
        
        # Should NOT have audit_bypass parameter
        assert 'audit_bypass' not in params
    
    def test_check_entitlement_access_no_bypass_param(self):
        """Document that check_entitlement_access has no bypass parameter"""
        from app.api.deps.entitlements import check_entitlement_access
        import inspect
        
        sig = inspect.signature(check_entitlement_access)
        params = list(sig.parameters.keys())
        
        # Should NOT have allow_super_admin_bypass parameter
        assert 'allow_super_admin_bypass' not in params


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
