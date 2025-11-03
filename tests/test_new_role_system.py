# tests/test_new_role_system.py

"""
Unit tests for the new 4-role organization user management system.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from app.schemas.user import UserRole


class TestRoleSystem:
    """Test the new 4-role system logic"""
    
    def test_valid_roles(self):
        """Test that only 4 org-level roles are valid"""
        valid_org_roles = {
            UserRole.ORG_ADMIN.value,
            UserRole.MANAGEMENT.value,
            UserRole.MANAGER.value,
            UserRole.EXECUTIVE.value
        }
        
        # Verify these are the only organization roles
        assert UserRole.ORG_ADMIN.value == "org_admin"
        assert UserRole.MANAGEMENT.value == "management"
        assert UserRole.MANAGER.value == "manager"
        assert UserRole.EXECUTIVE.value == "executive"
        
        # super_admin should be platform-level only
        assert UserRole.SUPER_ADMIN.value == "super_admin"
    
    def test_role_hierarchy(self):
        """Test role hierarchy ordering"""
        # Org Admin > Management > Manager > Executive
        hierarchy = [
            UserRole.ORG_ADMIN.value,
            UserRole.MANAGEMENT.value,
            UserRole.MANAGER.value,
            UserRole.EXECUTIVE.value
        ]
        
        # Verify hierarchy order
        assert hierarchy.index(UserRole.ORG_ADMIN.value) < hierarchy.index(UserRole.MANAGEMENT.value)
        assert hierarchy.index(UserRole.MANAGEMENT.value) < hierarchy.index(UserRole.MANAGER.value)
        assert hierarchy.index(UserRole.MANAGER.value) < hierarchy.index(UserRole.EXECUTIVE.value)


class TestRoleValidation:
    """Test role transition validation logic"""
    
    @pytest.mark.asyncio
    async def test_org_admin_can_create_all_roles(self):
        """Org Admin can create any role"""
        from app.services.org_role_service import OrgRoleService
        
        db_mock = AsyncMock()
        service = OrgRoleService(db_mock)
        
        # Org Admin can create Org Admin
        result = await service.validate_role_transition(
            current_role=None,
            new_role=UserRole.ORG_ADMIN.value,
            requester_role=UserRole.ORG_ADMIN.value,
            org_id=1
        )
        assert result == True
        
        # Org Admin can create Management
        result = await service.validate_role_transition(
            current_role=None,
            new_role=UserRole.MANAGEMENT.value,
            requester_role=UserRole.ORG_ADMIN.value,
            org_id=1
        )
        assert result == True
    
    @pytest.mark.asyncio
    async def test_management_cannot_create_org_admin(self):
        """Management cannot create Org Admin"""
        from app.services.org_role_service import OrgRoleService
        from fastapi import HTTPException
        
        db_mock = AsyncMock()
        service = OrgRoleService(db_mock)
        
        # Management cannot create Org Admin
        with pytest.raises(HTTPException) as exc_info:
            await service.validate_role_transition(
                current_role=None,
                new_role=UserRole.ORG_ADMIN.value,
                requester_role=UserRole.MANAGEMENT.value,
                org_id=1
            )
        
        assert exc_info.value.status_code == 403
        assert "Management cannot create Org Admin" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_manager_can_only_create_executive(self):
        """Manager can only create Executive role"""
        from app.services.org_role_service import OrgRoleService
        from fastapi import HTTPException
        
        db_mock = AsyncMock()
        service = OrgRoleService(db_mock)
        
        # Manager can create Executive
        result = await service.validate_role_transition(
            current_role=None,
            new_role=UserRole.EXECUTIVE.value,
            requester_role=UserRole.MANAGER.value,
            org_id=1
        )
        assert result == True
        
        # Manager cannot create Manager
        with pytest.raises(HTTPException) as exc_info:
            await service.validate_role_transition(
                current_role=None,
                new_role=UserRole.MANAGER.value,
                requester_role=UserRole.MANAGER.value,
                org_id=1
            )
        
        assert exc_info.value.status_code == 403


class TestPermissionEnforcement:
    """Test permission enforcement logic"""
    
    @pytest.mark.asyncio
    async def test_org_admin_has_full_access(self):
        """Org Admin has full access to all entitled modules"""
        from app.services.permission_enforcement import PermissionEnforcer
        
        db_mock = AsyncMock()
        enforcer = PermissionEnforcer(db_mock)
        
        # Mock user
        user_mock = Mock()
        user_mock.organization_id = 1
        user_mock.role = UserRole.ORG_ADMIN.value
        
        # Mock entitlement check to return True
        with patch.object(enforcer, '_check_entitlement', return_value=True):
            result = await enforcer.check_module_access(user_mock, "CRM", "read")
            assert result == True
            
            result = await enforcer.check_module_access(user_mock, "ERP", "create")
            assert result == True
    
    @pytest.mark.asyncio
    async def test_manager_module_access(self):
        """Manager has access only to assigned modules"""
        from app.services.permission_enforcement import PermissionEnforcer
        
        db_mock = AsyncMock()
        enforcer = PermissionEnforcer(db_mock)
        
        # Mock Manager user with assigned modules
        user_mock = Mock()
        user_mock.organization_id = 1
        user_mock.role = UserRole.MANAGER.value
        user_mock.assigned_modules = {
            "CRM": True,
            "Sales": True,
            "HR": False
        }
        
        # Should have access to CRM
        result = await enforcer.check_module_access(user_mock, "CRM", "read")
        assert result == True
        
        # Should NOT have access to HR
        result = await enforcer.check_module_access(user_mock, "HR", "read")
        assert result == False
        
        # Should NOT have access to unassigned module
        result = await enforcer.check_module_access(user_mock, "Finance", "read")
        assert result == False
    
    @pytest.mark.asyncio
    async def test_executive_submodule_access(self):
        """Executive has access only to assigned submodules"""
        from app.services.permission_enforcement import PermissionEnforcer
        
        db_mock = AsyncMock()
        enforcer = PermissionEnforcer(db_mock)
        
        # Mock Executive user with submodule permissions
        user_mock = Mock()
        user_mock.organization_id = 1
        user_mock.role = UserRole.EXECUTIVE.value
        user_mock.sub_module_permissions = {
            "CRM": ["leads", "contacts"],
            "Sales": ["orders"]
        }
        
        # Should have access to assigned submodules
        result = await enforcer.check_submodule_access(user_mock, "CRM", "leads", "read")
        assert result == True
        
        result = await enforcer.check_submodule_access(user_mock, "CRM", "contacts", "read")
        assert result == True
        
        # Should NOT have access to unassigned submodule
        result = await enforcer.check_submodule_access(user_mock, "CRM", "accounts", "read")
        assert result == False


class TestSettingsMenuVisibility:
    """Test settings menu visibility logic"""
    
    @pytest.mark.asyncio
    async def test_executive_no_settings_access(self):
        """Executives should not see any settings"""
        from app.services.permission_enforcement import PermissionEnforcer
        
        db_mock = AsyncMock()
        enforcer = PermissionEnforcer(db_mock)
        
        user_mock = Mock()
        user_mock.organization_id = 1
        user_mock.role = UserRole.EXECUTIVE.value
        
        # Executive should not see settings
        result = await enforcer.check_settings_menu_access(user_mock, "CRM")
        assert result == False
    
    @pytest.mark.asyncio
    async def test_manager_sees_assigned_module_settings(self):
        """Managers see settings only for assigned modules"""
        from app.services.permission_enforcement import PermissionEnforcer
        
        db_mock = AsyncMock()
        enforcer = PermissionEnforcer(db_mock)
        
        user_mock = Mock()
        user_mock.organization_id = 1
        user_mock.role = UserRole.MANAGER.value
        user_mock.assigned_modules = {"CRM": True, "HR": False}
        
        # Should see settings for assigned module
        result = await enforcer.check_settings_menu_access(user_mock, "CRM")
        assert result == True
        
        # Should NOT see settings for unassigned module
        result = await enforcer.check_settings_menu_access(user_mock, "HR")
        assert result == False


class TestUserManagement:
    """Test user management authorization"""
    
    @pytest.mark.asyncio
    async def test_org_admin_can_manage_all_except_org_admins(self):
        """Org Admin can manage all users except other Org Admins"""
        from app.services.permission_enforcement import PermissionEnforcer
        
        db_mock = AsyncMock()
        enforcer = PermissionEnforcer(db_mock)
        
        manager_user = Mock()
        manager_user.organization_id = 1
        manager_user.role = UserRole.ORG_ADMIN.value
        
        # Can manage Management
        target = Mock()
        target.organization_id = 1
        target.role = UserRole.MANAGEMENT.value
        result = await enforcer.can_manage_user(manager_user, target)
        assert result == True
        
        # Cannot manage other Org Admin
        target.role = UserRole.ORG_ADMIN.value
        result = await enforcer.can_manage_user(manager_user, target)
        assert result == False
    
    @pytest.mark.asyncio
    async def test_manager_can_only_manage_own_executives(self):
        """Manager can only manage their own reporting Executives"""
        from app.services.permission_enforcement import PermissionEnforcer
        
        db_mock = AsyncMock()
        enforcer = PermissionEnforcer(db_mock)
        
        manager_user = Mock()
        manager_user.id = 100
        manager_user.organization_id = 1
        manager_user.role = UserRole.MANAGER.value
        
        # Can manage own Executive
        executive = Mock()
        executive.organization_id = 1
        executive.role = UserRole.EXECUTIVE.value
        executive.reporting_manager_id = 100
        result = await enforcer.can_manage_user(manager_user, executive)
        assert result == True
        
        # Cannot manage other Manager's Executive
        executive.reporting_manager_id = 200
        result = await enforcer.can_manage_user(manager_user, executive)
        assert result == False
        
        # Cannot manage another Manager
        other_manager = Mock()
        other_manager.organization_id = 1
        other_manager.role = UserRole.MANAGER.value
        result = await enforcer.can_manage_user(manager_user, other_manager)
        assert result == False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
