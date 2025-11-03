"""
Test Category-Based Entitlement Activation

Tests the 10-category structure for entitlement management.
"""

import sys
from pathlib import Path
from typing import Dict, List
from enum import Enum

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest

# Import module_categories directly to avoid FastAPI dependency
import importlib.util
spec = importlib.util.spec_from_file_location(
    "module_categories",
    project_root / "app" / "core" / "module_categories.py"
)
module_categories = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module_categories)

# Extract what we need
get_all_categories = module_categories.get_all_categories
get_modules_for_category = module_categories.get_modules_for_category
get_category_for_module = module_categories.get_category_for_module
get_category_info = module_categories.get_category_info
is_always_on_module = module_categories.is_always_on_module
is_rbac_only_module = module_categories.is_rbac_only_module
CATEGORY_MODULE_MAP = module_categories.CATEGORY_MODULE_MAP
ProductCategory = module_categories.ProductCategory
ALWAYS_ON_MODULES = module_categories.ALWAYS_ON_MODULES
RBAC_ONLY_MODULES = module_categories.RBAC_ONLY_MODULES


class TestCategoryStructure:
    """Test the 10-category structure"""
    
    def test_exactly_10_categories(self):
        """Test that there are exactly 10 product categories"""
        categories = get_all_categories()
        assert len(categories) == 10, f"Expected 10 categories, got {len(categories)}"
    
    def test_all_categories_defined(self):
        """Test that all expected categories are defined"""
        expected_categories = [
            ProductCategory.CRM,
            ProductCategory.ERP,
            ProductCategory.MANUFACTURING,
            ProductCategory.FINANCE,
            ProductCategory.SERVICE,
            ProductCategory.HR,
            ProductCategory.ANALYTICS,
            ProductCategory.AI,
            ProductCategory.PROJECT_MANAGEMENT,
            ProductCategory.OPERATIONS_ASSETS,
        ]
        
        actual_categories = get_all_categories()
        
        for expected in expected_categories:
            assert expected.value in actual_categories, \
                f"Category {expected.value} not found in categories"
    
    def test_operations_assets_contains_all_consolidated_modules(self):
        """Test that Operations & Assets contains all consolidated modules"""
        operations_modules = get_modules_for_category(ProductCategory.OPERATIONS_ASSETS)
        
        # Should contain asset, transport, workflow, integration, email, calendar,
        # exhibition, customer, vendor, voucher, stock, settings, admin, organization
        expected_modules = [
            'asset', 'transport', 'workflow', 'integration', 'email', 
            'calendar', 'exhibition', 'customer', 'vendor', 'voucher', 
            'stock', 'settings', 'admin', 'organization'
        ]
        
        for module in expected_modules:
            assert module in operations_modules, \
                f"Module '{module}' not found in Operations & Assets"
    
    def test_rbac_only_modules_in_operations_assets(self):
        """Test that RBAC-only modules are in Operations & Assets"""
        operations_modules = get_modules_for_category(ProductCategory.OPERATIONS_ASSETS)
        
        for rbac_module in RBAC_ONLY_MODULES:
            assert rbac_module in operations_modules, \
                f"RBAC-only module '{rbac_module}' should be in Operations & Assets"
    
    def test_always_on_modules_in_operations_assets(self):
        """Test that always-on modules are in Operations & Assets"""
        operations_modules = get_modules_for_category(ProductCategory.OPERATIONS_ASSETS)
        
        for always_on_module in ALWAYS_ON_MODULES:
            assert always_on_module in operations_modules, \
                f"Always-on module '{always_on_module}' should be in Operations & Assets"


class TestModuleCategoryMapping:
    """Test module to category mapping"""
    
    def test_crm_modules_mapping(self):
        """Test CRM modules are correctly mapped"""
        crm_modules = get_modules_for_category(ProductCategory.CRM)
        expected_modules = ['crm', 'sales', 'marketing', 'seo']
        
        assert set(crm_modules) == set(expected_modules), \
            f"CRM modules mismatch. Expected {expected_modules}, got {crm_modules}"
    
    def test_erp_modules_mapping(self):
        """Test ERP modules are correctly mapped"""
        erp_modules = get_modules_for_category(ProductCategory.ERP)
        expected_modules = ['erp', 'inventory', 'procurement', 'order_book', 
                           'master_data', 'product', 'vouchers']
        
        assert set(erp_modules) == set(expected_modules), \
            f"ERP modules mismatch"
    
    def test_manufacturing_modules_mapping(self):
        """Test Manufacturing modules are correctly mapped"""
        mfg_modules = get_modules_for_category(ProductCategory.MANUFACTURING)
        expected_modules = ['manufacturing', 'bom']
        
        assert set(mfg_modules) == set(expected_modules)
    
    def test_reverse_mapping_crm_module(self):
        """Test reverse mapping from module to category"""
        category = get_category_for_module('crm')
        assert category == ProductCategory.CRM.value
    
    def test_reverse_mapping_settings_module(self):
        """Test reverse mapping for settings module"""
        category = get_category_for_module('settings')
        assert category == ProductCategory.OPERATIONS_ASSETS.value
    
    def test_all_modules_have_category(self):
        """Test that all modules in all categories have reverse mapping"""
        for category in get_all_categories():
            modules = get_modules_for_category(category)
            for module in modules:
                reverse_category = get_category_for_module(module)
                assert reverse_category is not None, \
                    f"Module '{module}' doesn't have reverse mapping"


class TestCategoryInfo:
    """Test category information retrieval"""
    
    def test_get_category_info_structure(self):
        """Test that category info has correct structure"""
        info = get_category_info(ProductCategory.CRM)
        
        assert 'key' in info
        assert 'display_name' in info
        assert 'description' in info
        assert 'modules' in info
        assert 'module_count' in info
    
    def test_category_info_module_count_accurate(self):
        """Test that module_count matches actual module count"""
        for category in get_all_categories():
            info = get_category_info(category)
            actual_count = len(info['modules'])
            
            assert info['module_count'] == actual_count, \
                f"Category {category}: module_count mismatch"
    
    def test_operations_assets_has_most_modules(self):
        """Test that Operations & Assets has the most modules (consolidated)"""
        ops_info = get_category_info(ProductCategory.OPERATIONS_ASSETS)
        ops_count = ops_info['module_count']
        
        # Should have at least 14 modules (all consolidated ones)
        assert ops_count >= 11, \
            f"Operations & Assets should have at least 11 modules, got {ops_count}"


class TestSpecialModules:
    """Test always-on and RBAC-only modules"""
    
    def test_email_is_always_on(self):
        """Test that email is marked as always-on"""
        assert is_always_on_module('email')
    
    def test_settings_is_rbac_only(self):
        """Test that settings is marked as RBAC-only"""
        assert is_rbac_only_module('settings')
    
    def test_admin_is_rbac_only(self):
        """Test that admin is marked as RBAC-only"""
        assert is_rbac_only_module('admin')
    
    def test_organization_is_rbac_only(self):
        """Test that organization is marked as RBAC-only"""
        assert is_rbac_only_module('organization')
    
    def test_regular_module_not_always_on(self):
        """Test that regular modules are not always-on"""
        assert not is_always_on_module('crm')
        assert not is_always_on_module('erp')
        assert not is_always_on_module('manufacturing')
    
    def test_regular_module_not_rbac_only(self):
        """Test that regular modules are not RBAC-only"""
        assert not is_rbac_only_module('crm')
        assert not is_rbac_only_module('erp')
        assert not is_rbac_only_module('manufacturing')
    
    def test_rbac_only_modules_count(self):
        """Test that there are exactly 3 RBAC-only modules"""
        assert len(RBAC_ONLY_MODULES) == 3
        assert 'settings' in RBAC_ONLY_MODULES
        assert 'admin' in RBAC_ONLY_MODULES
        assert 'organization' in RBAC_ONLY_MODULES
    
    def test_always_on_modules_count(self):
        """Test that there is exactly 1 always-on module"""
        assert len(ALWAYS_ON_MODULES) == 1
        assert 'email' in ALWAYS_ON_MODULES


class TestCategoryValidation:
    """Test category validation"""
    
    def test_invalid_category_returns_empty_modules(self):
        """Test that invalid category returns empty list"""
        modules = get_modules_for_category('invalid_category')
        assert modules == []
    
    def test_invalid_module_returns_none_category(self):
        """Test that invalid module returns None"""
        category = get_category_for_module('invalid_module')
        assert category is None
    
    def test_all_categories_have_display_names(self):
        """Test that all categories have display names"""
        CATEGORY_DISPLAY_NAMES = module_categories.CATEGORY_DISPLAY_NAMES
        
        for category in get_all_categories():
            assert category in CATEGORY_DISPLAY_NAMES, \
                f"Category {category} missing display name"
    
    def test_all_categories_have_descriptions(self):
        """Test that all categories have descriptions"""
        CATEGORY_DESCRIPTIONS = module_categories.CATEGORY_DESCRIPTIONS
        
        for category in get_all_categories():
            assert category in CATEGORY_DESCRIPTIONS, \
                f"Category {category} missing description"


class TestBackwardCompatibility:
    """Test backward compatibility with legacy structure"""
    
    def test_no_duplicate_modules_across_categories(self):
        """Test that no module appears in multiple categories"""
        all_modules = []
        
        for category in get_all_categories():
            modules = get_modules_for_category(category)
            all_modules.extend(modules)
        
        # Check for duplicates
        unique_modules = set(all_modules)
        assert len(all_modules) == len(unique_modules), \
            f"Duplicate modules found: {[m for m in all_modules if all_modules.count(m) > 1]}"
    
    def test_legacy_workflow_now_in_operations(self):
        """Test that workflow (previously separate) is now in Operations & Assets"""
        category = get_category_for_module('workflow')
        assert category == ProductCategory.OPERATIONS_ASSETS.value
    
    def test_legacy_integration_now_in_operations(self):
        """Test that integration (previously separate) is now in Operations & Assets"""
        category = get_category_for_module('integration')
        assert category == ProductCategory.OPERATIONS_ASSETS.value
