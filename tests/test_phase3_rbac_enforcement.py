"""
Tests for Phase 3 RBAC enforcement migration.
Tests CRM, Service Desk, Notification, HR, and Order Book modules.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.core.enforcement import require_access, TenantEnforcement, RBACEnforcement


class TestCRMEnforcement:
    """Test CRM module enforcement"""
    
    def test_crm_module_uses_require_access(self):
        """Verify CRM module imports and uses require_access"""
        import app.api.v1.crm as crm_module
        
        # Check that require_access is imported
        assert hasattr(crm_module, 'require_access')
        
        # Check source for require_access usage
        import inspect
        source = inspect.getsource(crm_module)
        assert 'require_access("crm"' in source
        
    def test_crm_permissions_defined(self):
        """Verify CRM permissions are used correctly"""
        import app.api.v1.crm as crm_module
        import inspect
        
        source = inspect.getsource(crm_module)
        
        # Check for correct permission usage
        assert 'require_access("crm", "read")' in source
        assert 'require_access("crm", "create")' in source
        assert 'require_access("crm", "update")' in source
        assert 'require_access("crm", "delete")' in source
        
    def test_crm_no_old_dependencies(self):
        """Verify CRM doesn't use old auth patterns"""
        import app.api.v1.crm as crm_module
        import inspect
        
        source = inspect.getsource(crm_module)
        
        # Should not have old imports
        assert 'core_get_current_user' not in source
        assert 'require_current_organization_id' not in source
        
    def test_crm_auth_tuple_extraction(self):
        """Verify CRM extracts user and org_id from auth tuple"""
        import app.api.v1.crm as crm_module
        import inspect
        
        source = inspect.getsource(crm_module)
        
        # Should extract auth tuple
        assert 'current_user, org_id = auth' in source
        

class TestServiceDeskEnforcement:
    """Test Service Desk module enforcement"""
    
    def test_service_desk_uses_require_access(self):
        """Verify Service Desk module uses require_access"""
        import app.api.v1.service_desk as service_module
        
        assert hasattr(service_module, 'require_access')
        
        import inspect
        source = inspect.getsource(service_module)
        assert 'require_access("service"' in source
        
    def test_service_desk_permissions(self):
        """Verify Service Desk permissions"""
        import app.api.v1.service_desk as service_module
        import inspect
        
        source = inspect.getsource(service_module)
        
        assert 'require_access("service", "read")' in source
        assert 'require_access("service", "create")' in source
        assert 'require_access("service", "update")' in source
        assert 'require_access("service", "delete")' in source
        
    def test_service_desk_no_old_patterns(self):
        """Verify Service Desk doesn't use old patterns"""
        import app.api.v1.service_desk as service_module
        import inspect
        
        source = inspect.getsource(service_module)
        
        assert 'require_current_organization_id' not in source
        

class TestNotificationEnforcement:
    """Test Notification module enforcement"""
    
    def test_notification_uses_require_access(self):
        """Verify Notification module uses require_access"""
        import app.api.notifications as notification_module
        
        assert hasattr(notification_module, 'require_access')
        
        import inspect
        source = inspect.getsource(notification_module)
        assert 'require_access("notification"' in source
        
    def test_notification_permissions(self):
        """Verify Notification permissions"""
        import app.api.notifications as notification_module
        import inspect
        
        source = inspect.getsource(notification_module)
        
        assert 'require_access("notification", "read")' in source
        assert 'require_access("notification", "create")' in source
        
    def test_notification_no_old_imports(self):
        """Verify Notification doesn't have old imports"""
        import app.api.notifications as notification_module
        import inspect
        
        source = inspect.getsource(notification_module)
        
        # Should not import old dependencies
        assert 'from app.api.v1.auth import get_current_active_user' not in source
        assert 'require_current_organization_id' not in source
        

class TestHREnforcement:
    """Test HR module enforcement"""
    
    def test_hr_uses_require_access(self):
        """Verify HR module uses require_access"""
        import app.api.v1.hr as hr_module
        
        assert hasattr(hr_module, 'require_access')
        
        import inspect
        source = inspect.getsource(hr_module)
        assert 'require_access("hr"' in source
        
    def test_hr_permissions(self):
        """Verify HR permissions"""
        import app.api.v1.hr as hr_module
        import inspect
        
        source = inspect.getsource(hr_module)
        
        assert 'require_access("hr", "read")' in source
        assert 'require_access("hr", "create")' in source
        assert 'require_access("hr", "update")' in source
        assert 'require_access("hr", "delete")' in source
        
    def test_hr_no_current_user_org_id(self):
        """Verify HR doesn't use current_user.organization_id"""
        import app.api.v1.hr as hr_module
        import inspect
        
        source = inspect.getsource(hr_module)
        
        # Should use org_id from auth tuple instead
        assert 'current_user.organization_id' not in source
        

class TestOrderBookEnforcement:
    """Test Order Book module enforcement"""
    
    def test_order_book_uses_require_access(self):
        """Verify Order Book module uses require_access"""
        import app.api.v1.order_book as order_module
        
        assert hasattr(order_module, 'require_access')
        
        import inspect
        source = inspect.getsource(order_module)
        assert 'require_access("order"' in source
        
    def test_order_book_permissions(self):
        """Verify Order Book permissions"""
        import app.api.v1.order_book as order_module
        import inspect
        
        source = inspect.getsource(order_module)
        
        assert 'require_access("order", "read")' in source
        assert 'require_access("order", "create")' in source
        assert 'require_access("order", "update")' in source
        assert 'require_access("order", "delete")' in source
        
    def test_order_book_no_old_imports(self):
        """Verify Order Book doesn't have old imports"""
        import app.api.v1.order_book as order_module
        import inspect
        
        source = inspect.getsource(order_module)
        
        assert 'from app.api.v1.auth import get_current_active_user' not in source
        assert 'require_current_organization_id' not in source
        

class TestEnforcementConsistency:
    """Test consistency across all migrated modules"""
    
    def test_all_modules_import_require_access(self):
        """Verify all modules import require_access"""
        modules = [
            'app.api.v1.crm',
            'app.api.v1.service_desk',
            'app.api.notifications',
            'app.api.v1.hr',
            'app.api.v1.order_book',
        ]
        
        for module_name in modules:
            module = __import__(module_name, fromlist=[''])
            assert hasattr(module, 'require_access'), f"{module_name} should import require_access"
            
    def test_all_modules_compile(self):
        """Verify all migrated modules compile without errors"""
        modules = [
            'app.api.v1.crm',
            'app.api.v1.service_desk',
            'app.api.notifications',
            'app.api.v1.hr',
            'app.api.v1.order_book',
        ]
        
        for module_name in modules:
            try:
                __import__(module_name, fromlist=[''])
            except Exception as e:
                pytest.fail(f"{module_name} failed to compile: {e}")
                
    def test_permission_naming_convention(self):
        """Verify permission naming follows {module}_{action} pattern"""
        import inspect
        
        modules_and_names = [
            ('app.api.v1.crm', 'crm'),
            ('app.api.v1.service_desk', 'service'),
            ('app.api.notifications', 'notification'),
            ('app.api.v1.hr', 'hr'),
            ('app.api.v1.order_book', 'order'),
        ]
        
        for module_path, module_name in modules_and_names:
            module = __import__(module_path, fromlist=[''])
            source = inspect.getsource(module)
            
            # Check for standard CRUD actions
            assert f'require_access("{module_name}", "read")' in source or \
                   f'require_access("{module_name}", "create")' in source, \
                   f"{module_path} should use {module_name}_* permissions"
                   

class TestEnforcementUtilities:
    """Test the enforcement utilities themselves"""
    
    def test_require_access_returns_callable(self):
        """Verify require_access returns a callable dependency"""
        from app.core.enforcement import require_access
        
        dep = require_access("test", "read")
        assert callable(dep)
        
    def test_tenant_enforcement_methods_exist(self):
        """Verify TenantEnforcement has required methods"""
        from app.core.enforcement import TenantEnforcement
        
        assert hasattr(TenantEnforcement, 'get_organization_id')
        assert hasattr(TenantEnforcement, 'enforce_organization_access')
        assert hasattr(TenantEnforcement, 'filter_by_organization')
        
    def test_rbac_enforcement_methods_exist(self):
        """Verify RBACEnforcement has required methods"""
        from app.core.enforcement import RBACEnforcement
        
        assert hasattr(RBACEnforcement, 'check_permission')
        assert hasattr(RBACEnforcement, 'require_module_permission')


class TestModuleSyntax:
    """Test that all migrated modules have correct syntax"""
    
    def test_crm_syntax(self):
        """Test CRM module syntax"""
        import py_compile
        import app.api.v1.crm as crm
        import inspect
        
        # Get module file path
        file_path = inspect.getfile(crm)
        
        try:
            py_compile.compile(file_path, doraise=True)
        except py_compile.PyCompileError as e:
            pytest.fail(f"CRM module has syntax errors: {e}")
            
    def test_service_desk_syntax(self):
        """Test Service Desk module syntax"""
        import py_compile
        import app.api.v1.service_desk as service_desk
        import inspect
        
        file_path = inspect.getfile(service_desk)
        
        try:
            py_compile.compile(file_path, doraise=True)
        except py_compile.PyCompileError as e:
            pytest.fail(f"Service Desk module has syntax errors: {e}")
            
    def test_notification_syntax(self):
        """Test Notification module syntax"""
        import py_compile
        import app.api.notifications as notifications
        import inspect
        
        file_path = inspect.getfile(notifications)
        
        try:
            py_compile.compile(file_path, doraise=True)
        except py_compile.PyCompileError as e:
            pytest.fail(f"Notification module has syntax errors: {e}")
            
    def test_hr_syntax(self):
        """Test HR module syntax"""
        import py_compile
        import app.api.v1.hr as hr
        import inspect
        
        file_path = inspect.getfile(hr)
        
        try:
            py_compile.compile(file_path, doraise=True)
        except py_compile.PyCompileError as e:
            pytest.fail(f"HR module has syntax errors: {e}")
            
    def test_order_book_syntax(self):
        """Test Order Book module syntax"""
        import py_compile
        import app.api.v1.order_book as order_book
        import inspect
        
        file_path = inspect.getfile(order_book)
        
        try:
            py_compile.compile(file_path, doraise=True)
        except py_compile.PyCompileError as e:
            pytest.fail(f"Order Book module has syntax errors: {e}")
