"""
Test strict entitlement enforcement without fallback logic.
Validates that all users, including super admins, must have explicit entitlements.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException
from app.api.deps.entitlements import (
    require_entitlement,
    check_entitlement_access,
    EntitlementDeniedError,
    ROLE_SUPER_ADMIN,
    ROLE_ORG_ADMIN,
    ALWAYS_ON_MODULES,
    RBAC_ONLY_MODULES,
)
from app.models.user_models import User


class TestStrictEntitlementEnforcement:
    """Test strict entitlement enforcement - no bypasses"""
    
    @pytest.mark.asyncio
    async def test_super_admin_denied_without_entitlement(self):
        """Super admin without entitlement should be denied access"""
        # Create mock super admin user
        mock_user = MagicMock(spec=User)
        mock_user.id = 1
        mock_user.email = "superadmin@test.com"
        mock_user.role = ROLE_SUPER_ADMIN
        mock_user.organization_id = 100
        
        # Mock database and entitlement service
        mock_db = AsyncMock()
        
        with patch('app.api.deps.entitlements.EntitlementService') as MockService:
            mock_service = MockService.return_value
            # Module is disabled for the organization
            mock_service.check_entitlement = AsyncMock(
                return_value=(False, 'disabled', 'Module not enabled')
            )
            
            # Create the dependency
            dependency = require_entitlement("manufacturing")
            
            # Call the dependency - should raise EntitlementDeniedError
            with pytest.raises(EntitlementDeniedError) as exc_info:
                await dependency(db=mock_db, current_user=mock_user)
            
            # Verify the error details
            assert exc_info.value.status_code == 403
            assert "manufacturing" in str(exc_info.value.detail)
            assert exc_info.value.detail['error_type'] == 'entitlement_denied'
            
            # Verify service was called (no bypass)
            mock_service.check_entitlement.assert_called_once_with(
                org_id=100,
                module_key="manufacturing",
                submodule_key=None
            )
    
    @pytest.mark.asyncio
    async def test_org_admin_denied_without_entitlement(self):
        """Org admin without entitlement should be denied access"""
        mock_user = MagicMock(spec=User)
        mock_user.id = 2
        mock_user.email = "orgadmin@test.com"
        mock_user.role = ROLE_ORG_ADMIN
        mock_user.organization_id = 200
        
        mock_db = AsyncMock()
        
        with patch('app.api.deps.entitlements.EntitlementService') as MockService:
            mock_service = MockService.return_value
            mock_service.check_entitlement = AsyncMock(
                return_value=(False, 'disabled', 'Module not enabled')
            )
            
            dependency = require_entitlement("sales")
            
            with pytest.raises(EntitlementDeniedError) as exc_info:
                await dependency(db=mock_db, current_user=mock_user)
            
            assert exc_info.value.status_code == 403
            assert "sales" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_regular_user_denied_without_entitlement(self):
        """Regular user without entitlement should be denied access"""
        mock_user = MagicMock(spec=User)
        mock_user.id = 3
        mock_user.email = "user@test.com"
        mock_user.role = "user"
        mock_user.organization_id = 300
        
        mock_db = AsyncMock()
        
        with patch('app.api.deps.entitlements.EntitlementService') as MockService:
            mock_service = MockService.return_value
            mock_service.check_entitlement = AsyncMock(
                return_value=(False, 'disabled', 'Module not enabled')
            )
            
            dependency = require_entitlement("inventory")
            
            with pytest.raises(EntitlementDeniedError) as exc_info:
                await dependency(db=mock_db, current_user=mock_user)
            
            assert exc_info.value.status_code == 403
            assert "inventory" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_super_admin_granted_with_entitlement(self):
        """Super admin WITH entitlement should be granted access"""
        mock_user = MagicMock(spec=User)
        mock_user.id = 1
        mock_user.email = "superadmin@test.com"
        mock_user.role = ROLE_SUPER_ADMIN
        mock_user.organization_id = 100
        
        mock_db = AsyncMock()
        
        with patch('app.api.deps.entitlements.EntitlementService') as MockService:
            mock_service = MockService.return_value
            # Module is enabled for the organization
            mock_service.check_entitlement = AsyncMock(
                return_value=(True, 'enabled', 'Module enabled')
            )
            
            dependency = require_entitlement("manufacturing")
            
            # Should NOT raise exception
            result = await dependency(db=mock_db, current_user=mock_user)
            assert result is None  # Dependency returns None on success
            
            # Verify service was called
            mock_service.check_entitlement.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_email_module_always_allowed(self):
        """Email module should always be allowed (non-billable)"""
        mock_user = MagicMock(spec=User)
        mock_user.id = 1
        mock_user.email = "user@test.com"
        mock_user.role = "user"
        mock_user.organization_id = 100
        
        mock_db = AsyncMock()
        
        with patch('app.api.deps.entitlements.EntitlementService') as MockService:
            mock_service = MockService.return_value
            
            dependency = require_entitlement("email")
            
            # Should NOT raise exception and should NOT call service
            result = await dependency(db=mock_db, current_user=mock_user)
            assert result is None
            
            # Service should NOT be called for always-on modules
            mock_service.check_entitlement.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_settings_module_always_allowed(self):
        """Settings module should always be allowed (RBAC-only, non-billable)"""
        mock_user = MagicMock(spec=User)
        mock_user.id = 1
        mock_user.email = "user@test.com"
        mock_user.role = "user"
        mock_user.organization_id = 100
        
        mock_db = AsyncMock()
        
        with patch('app.api.deps.entitlements.EntitlementService') as MockService:
            mock_service = MockService.return_value
            
            dependency = require_entitlement("settings")
            
            # Should NOT raise exception and should NOT call service
            result = await dependency(db=mock_db, current_user=mock_user)
            assert result is None
            
            # Service should NOT be called for RBAC-only modules
            mock_service.check_entitlement.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_submodule_denied_when_disabled(self):
        """User should be denied access to disabled submodule"""
        mock_user = MagicMock(spec=User)
        mock_user.id = 1
        mock_user.email = "user@test.com"
        mock_user.role = "user"
        mock_user.organization_id = 100
        
        mock_db = AsyncMock()
        
        with patch('app.api.deps.entitlements.EntitlementService') as MockService:
            mock_service = MockService.return_value
            # Submodule is disabled
            mock_service.check_entitlement = AsyncMock(
                return_value=(False, 'disabled', 'Submodule not enabled')
            )
            
            dependency = require_entitlement("crm", "lead_management")
            
            with pytest.raises(EntitlementDeniedError) as exc_info:
                await dependency(db=mock_db, current_user=mock_user)
            
            assert exc_info.value.status_code == 403
            assert "crm" in str(exc_info.value.detail)
            assert exc_info.value.detail['submodule_key'] == 'lead_management'


class TestCheckEntitlementAccessHelper:
    """Test the check_entitlement_access helper function"""
    
    @pytest.mark.asyncio
    async def test_super_admin_no_bypass(self):
        """Helper function should not bypass for super admin"""
        mock_user = MagicMock(spec=User)
        mock_user.role = ROLE_SUPER_ADMIN
        
        mock_db = AsyncMock()
        
        with patch('app.api.deps.entitlements.EntitlementService') as MockService:
            mock_service = MockService.return_value
            mock_service.check_entitlement = AsyncMock(
                return_value=(False, 'disabled', 'Module not enabled')
            )
            
            is_entitled, status, reason = await check_entitlement_access(
                module_key="manufacturing",
                submodule_key=None,
                org_id=100,
                db=mock_db,
                user=mock_user
            )
            
            # Should return False (not entitled)
            assert is_entitled is False
            assert status == 'disabled'
            assert reason == 'Module not enabled'
            
            # Service should have been called (no bypass)
            mock_service.check_entitlement.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_always_on_modules_skip_check(self):
        """Always-on modules should skip entitlement check"""
        mock_db = AsyncMock()
        
        with patch('app.api.deps.entitlements.EntitlementService') as MockService:
            mock_service = MockService.return_value
            
            for module in ALWAYS_ON_MODULES:
                is_entitled, status, reason = await check_entitlement_access(
                    module_key=module,
                    submodule_key=None,
                    org_id=100,
                    db=mock_db,
                    user=None
                )
                
                assert is_entitled is True
                assert status == 'enabled'
                assert 'Always-on' in reason
            
            # Service should NOT be called
            mock_service.check_entitlement.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_rbac_only_modules_skip_check(self):
        """RBAC-only modules should skip entitlement check"""
        mock_db = AsyncMock()
        
        with patch('app.api.deps.entitlements.EntitlementService') as MockService:
            mock_service = MockService.return_value
            
            for module in RBAC_ONLY_MODULES:
                is_entitled, status, reason = await check_entitlement_access(
                    module_key=module,
                    submodule_key=None,
                    org_id=100,
                    db=mock_db,
                    user=None
                )
                
                assert is_entitled is True
                assert status == 'enabled'
                assert 'RBAC-only' in reason
            
            # Service should NOT be called
            mock_service.check_entitlement.assert_not_called()


class TestEntitlementDeniedError:
    """Test the EntitlementDeniedError exception"""
    
    def test_error_structure(self):
        """Test that error has correct structure"""
        error = EntitlementDeniedError(
            module_key="sales",
            submodule_key="lead_management",
            entitlement_status="disabled",
            reason="Module not enabled"
        )
        
        assert error.status_code == 403
        assert error.detail['error_type'] == 'entitlement_denied'
        assert error.detail['module_key'] == 'sales'
        assert error.detail['submodule_key'] == 'lead_management'
        assert error.detail['status'] == 'disabled'
        assert error.detail['reason'] == 'Module not enabled'
        assert 'sales' in error.detail['message']
    
    def test_error_without_submodule(self):
        """Test error without submodule key"""
        error = EntitlementDeniedError(
            module_key="inventory",
            entitlement_status="trial_expired",
            reason="Trial period has ended"
        )
        
        assert error.status_code == 403
        assert error.detail['module_key'] == 'inventory'
        assert error.detail['submodule_key'] is None
        assert error.detail['status'] == 'trial_expired'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
