"""
Test entitlement helper functions for case-insensitive normalization
"""
import pytest
from app.utils.entitlement_helpers import (
    normalize_enabled_modules,
    check_module_enabled,
    ensure_organization_module
)


class TestNormalizeEnabledModules:
    """Test normalize_enabled_modules function"""
    
    def test_normalize_mixed_case_keys(self):
        """Test that keys are normalized to lowercase"""
        input_modules = {
            "CRM": True,
            "ERP": True,
            "Manufacturing": True
        }
        
        result = normalize_enabled_modules(input_modules)
        
        assert result == {
            "crm": True,
            "erp": True,
            "manufacturing": True
        }
    
    def test_normalize_string_boolean_values(self):
        """Test that string boolean values are converted to proper booleans"""
        input_modules = {
            "crm": "true",
            "erp": "True",
            "manufacturing": "1",
            "finance": "yes",
            "service": "enabled",
            "hr": "false",
            "analytics": "0"
        }
        
        result = normalize_enabled_modules(input_modules)
        
        assert result == {
            "crm": True,
            "erp": True,
            "manufacturing": True,
            "finance": True,
            "service": True,
            "hr": False,
            "analytics": False
        }
    
    def test_normalize_numeric_values(self):
        """Test that numeric values are converted to booleans"""
        input_modules = {
            "crm": 1,
            "erp": 0,
            "manufacturing": 100,
            "finance": -1
        }
        
        result = normalize_enabled_modules(input_modules)
        
        assert result == {
            "crm": True,
            "erp": False,
            "manufacturing": True,
            "finance": True
        }
    
    def test_normalize_empty_dict(self):
        """Test that empty dict returns empty dict"""
        result = normalize_enabled_modules({})
        assert result == {}
    
    def test_normalize_none(self):
        """Test that None returns empty dict"""
        result = normalize_enabled_modules(None)
        assert result == {}
    
    def test_normalize_preserves_boolean_values(self):
        """Test that proper boolean values are preserved"""
        input_modules = {
            "crm": True,
            "erp": False
        }
        
        result = normalize_enabled_modules(input_modules)
        
        assert result == {
            "crm": True,
            "erp": False
        }


class TestCheckModuleEnabled:
    """Test check_module_enabled function"""
    
    def test_check_enabled_module_case_insensitive(self):
        """Test that module checking is case-insensitive"""
        modules = {
            "CRM": True,
            "ERP": False
        }
        
        assert check_module_enabled(modules, "crm") is True
        assert check_module_enabled(modules, "CRM") is True
        assert check_module_enabled(modules, "Crm") is True
        assert check_module_enabled(modules, "erp") is False
        assert check_module_enabled(modules, "ERP") is False
    
    def test_check_nonexistent_module(self):
        """Test that checking non-existent module returns False"""
        modules = {"crm": True}
        
        assert check_module_enabled(modules, "manufacturing") is False
    
    def test_check_with_string_boolean(self):
        """Test checking module with string boolean value"""
        modules = {
            "CRM": "true",
            "ERP": "false"
        }
        
        assert check_module_enabled(modules, "crm") is True
        assert check_module_enabled(modules, "erp") is False
    
    def test_check_empty_modules(self):
        """Test that empty modules dict returns False"""
        assert check_module_enabled({}, "crm") is False
    
    def test_check_none_modules(self):
        """Test that None modules returns False"""
        assert check_module_enabled(None, "crm") is False


class TestEnsureOrganizationModule:
    """Test ensure_organization_module function"""
    
    def test_ensure_adds_organization_module(self):
        """Test that organization module is added if missing"""
        input_modules = {
            "crm": True,
            "erp": True
        }
        
        result = ensure_organization_module(input_modules)
        
        assert "organization" in result
        assert result["organization"] is True
        assert result["crm"] is True
        assert result["erp"] is True
    
    def test_ensure_keeps_existing_organization_module(self):
        """Test that existing organization module is kept as True"""
        input_modules = {
            "crm": True,
            "organization": True
        }
        
        result = ensure_organization_module(input_modules)
        
        assert result["organization"] is True
    
    def test_ensure_overrides_false_organization_module(self):
        """Test that False organization module is overridden to True"""
        input_modules = {
            "crm": True,
            "organization": False
        }
        
        result = ensure_organization_module(input_modules)
        
        assert result["organization"] is True
    
    def test_ensure_with_empty_dict(self):
        """Test that empty dict gets organization module"""
        result = ensure_organization_module({})
        
        assert result == {"organization": True}
    
    def test_ensure_with_none(self):
        """Test that None gets converted to dict with organization module"""
        result = ensure_organization_module(None)
        
        assert result == {"organization": True}
    
    def test_ensure_normalizes_all_keys(self):
        """Test that all keys are normalized while ensuring organization"""
        input_modules = {
            "CRM": True,
            "ERP": "true",
            "Manufacturing": 1
        }
        
        result = ensure_organization_module(input_modules)
        
        assert result == {
            "crm": True,
            "erp": True,
            "manufacturing": True,
            "organization": True
        }
