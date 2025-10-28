# tests/test_comprehensive_rbac.py
"""
Tests for comprehensive RBAC system extension
"""

import pytest
from app.core.modules_registry import (
    get_all_modules,
    get_module_submodules,
    validate_module,
    validate_submodule,
    get_default_enabled_modules,
    ModuleName
)
from app.services.rbac_permissions import (
    get_comprehensive_permissions,
    get_default_role_permissions,
    get_module_permissions,
    get_submodule_permissions
)


class TestModulesRegistry:
    """Test module registry functionality"""
    
    def test_get_all_modules(self):
        """Test getting all modules"""
        modules = get_all_modules()
        assert isinstance(modules, list)
        assert len(modules) > 0
        # Check for core modules
        assert "CRM" in modules
        assert "ERP" in modules
        assert "HR" in modules
        assert "Manufacturing" in modules
        assert "Finance" in modules
    
    def test_get_module_submodules(self):
        """Test getting submodules for a module"""
        crm_submodules = get_module_submodules("CRM")
        assert isinstance(crm_submodules, list)
        assert len(crm_submodules) > 0
        assert "leads" in crm_submodules
        assert "opportunities" in crm_submodules
        assert "contacts" in crm_submodules
    
    def test_validate_module(self):
        """Test module validation"""
        assert validate_module("CRM") is True
        assert validate_module("ERP") is True
        assert validate_module("InvalidModule") is False
    
    def test_validate_submodule(self):
        """Test submodule validation"""
        assert validate_submodule("CRM", "leads") is True
        assert validate_submodule("CRM", "opportunities") is True
        assert validate_submodule("CRM", "invalid_submodule") is False
        assert validate_submodule("InvalidModule", "leads") is False
    
    def test_get_default_enabled_modules(self):
        """Test getting default enabled modules"""
        modules = get_default_enabled_modules()
        assert isinstance(modules, dict)
        assert len(modules) > 0
        # All modules should be enabled by default
        assert all(enabled for enabled in modules.values())
    
    def test_module_name_enum(self):
        """Test ModuleName enum"""
        assert ModuleName.CRM.value == "CRM"
        assert ModuleName.ERP.value == "ERP"
        assert ModuleName.MANUFACTURING.value == "Manufacturing"


class TestRBACPermissions:
    """Test RBAC permissions functionality"""
    
    def test_get_comprehensive_permissions(self):
        """Test getting comprehensive permissions"""
        permissions = get_comprehensive_permissions()
        assert isinstance(permissions, list)
        assert len(permissions) > 0
        
        # Check structure of permission tuples
        for perm in permissions[:5]:  # Check first 5
            assert isinstance(perm, tuple)
            assert len(perm) == 5
            name, display_name, description, module, action = perm
            assert isinstance(name, str)
            assert isinstance(display_name, str)
            assert isinstance(description, str)
            assert isinstance(module, str)
            assert isinstance(action, str)
        
        # Check for legacy permissions
        perm_names = [p[0] for p in permissions]
        assert "service_create" in perm_names
        assert "crm_lead_read" in perm_names
    
    def test_get_default_role_permissions(self):
        """Test getting default role permissions"""
        role_perms = get_default_role_permissions()
        assert isinstance(role_perms, dict)
        
        # Check all roles exist
        assert "admin" in role_perms
        assert "manager" in role_perms
        assert "support" in role_perms
        assert "viewer" in role_perms
        
        # Admin should have most permissions
        assert len(role_perms["admin"]) > len(role_perms["manager"])
        assert len(role_perms["manager"]) > len(role_perms["support"])
        assert len(role_perms["support"]) > len(role_perms["viewer"])
        
        # Viewer should only have read permissions
        viewer_perms = role_perms["viewer"]
        for perm in viewer_perms[:10]:  # Check first 10
            assert "read" in perm or "view" in perm
    
    def test_get_module_permissions(self):
        """Test getting permissions for a specific module"""
        crm_perms = get_module_permissions("CRM")
        assert isinstance(crm_perms, list)
        assert len(crm_perms) > 0
        
        # All should be CRM-related
        for perm in crm_perms:
            assert "crm" in perm[3].lower()
    
    def test_get_submodule_permissions(self):
        """Test getting permissions for a specific submodule"""
        leads_perms = get_submodule_permissions("CRM", "leads")
        assert isinstance(leads_perms, list)
        assert len(leads_perms) > 0
        
        # Should have CRUD permissions
        perm_names = [p[0] for p in leads_perms]
        assert any("create" in name for name in perm_names)
        assert any("read" in name for name in perm_names)
        assert any("update" in name for name in perm_names)
        assert any("delete" in name for name in perm_names)


class TestBackwardCompatibility:
    """Test backward compatibility of RBAC changes"""
    
    def test_legacy_modules_included(self):
        """Test that legacy module names are still supported"""
        modules = get_all_modules()
        # Core legacy modules should exist
        assert "CRM" in modules
        assert "ERP" in modules
        assert "HR" in modules
        assert "Inventory" in modules
        assert "Service" in modules
        assert "Analytics" in modules
        assert "Finance" in modules
    
    def test_legacy_permissions_included(self):
        """Test that legacy permissions are still included"""
        permissions = get_comprehensive_permissions()
        perm_names = [p[0] for p in permissions]
        
        # Check for legacy permissions
        legacy_perms = [
            "service_create", "service_read", "service_update", "service_delete",
            "crm_lead_read", "crm_lead_create", "crm_opportunity_read",
            "mail:dashboard:read", "mail:emails:read"
        ]
        
        for legacy_perm in legacy_perms:
            assert legacy_perm in perm_names, f"Legacy permission {legacy_perm} not found"
    
    def test_default_enabled_modules_covers_legacy(self):
        """Test that default enabled modules include legacy modules"""
        default_modules = get_default_enabled_modules()
        
        # All legacy modules should be enabled by default
        legacy_modules = ["CRM", "ERP", "HR", "Inventory", "Service", "Analytics", "Finance"]
        for module in legacy_modules:
            assert module in default_modules
            assert default_modules[module] is True


class TestModuleHierarchy:
    """Test module hierarchy and relationships"""
    
    def test_all_modules_have_submodules(self):
        """Test that all defined modules have submodules"""
        modules = get_all_modules()
        
        for module in modules:
            submodules = get_module_submodules(module)
            # Most modules should have at least one submodule
            # (Some might not, but most should)
            if module not in ["Exhibition", "AB_Testing"]:  # Small modules might have fewer
                assert len(submodules) > 0, f"Module {module} has no submodules"
    
    def test_submodules_generate_permissions(self):
        """Test that submodules generate proper permissions"""
        # Get ERP submodules
        erp_submodules = get_module_submodules("ERP")
        assert len(erp_submodules) > 0
        
        # Each submodule should have permissions
        for submodule in erp_submodules[:3]:  # Test first 3
            perms = get_submodule_permissions("ERP", submodule)
            assert len(perms) >= 4, f"Submodule {submodule} should have at least CRUD permissions"


class TestRoleHierarchy:
    """Test role hierarchy and permission assignment"""
    
    def test_role_hierarchy_respected(self):
        """Test that role hierarchy is properly maintained"""
        role_perms = get_default_role_permissions()
        
        # Admin should have more permissions than everyone
        admin_count = len(role_perms["admin"])
        manager_count = len(role_perms["manager"])
        support_count = len(role_perms["support"])
        viewer_count = len(role_perms["viewer"])
        
        assert admin_count > manager_count
        assert manager_count > support_count
        assert support_count > viewer_count
    
    def test_viewer_only_read_permissions(self):
        """Test that viewer role only has read permissions"""
        role_perms = get_default_role_permissions()
        viewer_perms = role_perms["viewer"]
        
        # All viewer permissions should be read-only
        for perm in viewer_perms:
            assert "read" in perm or "view" in perm, f"Viewer has non-read permission: {perm}"
    
    def test_manager_no_admin_permissions(self):
        """Test that manager role doesn't have admin permissions"""
        role_perms = get_default_role_permissions()
        manager_perms = role_perms["manager"]
        
        # Manager should not have admin permissions (with some CRM exceptions)
        admin_perms = [p for p in manager_perms if "admin" in p and "crm" not in p]
        assert len(admin_perms) == 0, f"Manager has admin permissions: {admin_perms}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
