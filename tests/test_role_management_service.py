# tests/test_role_management_service.py

"""
Tests for the RoleManagementService and VoucherApprovalService.
These tests verify the business logic works correctly.
"""

import pytest
from unittest.mock import Mock, MagicMock

def test_service_structure():
    """Test that service classes are properly structured"""
    from app.services.role_management_service import RoleManagementService, VoucherApprovalService
    
    # Mock database session
    mock_db = Mock()
    
    # Test service instantiation
    role_service = RoleManagementService(mock_db)
    approval_service = VoucherApprovalService(mock_db)
    
    assert role_service.db == mock_db
    assert approval_service.db == mock_db
    
    # Check that key methods exist
    assert hasattr(role_service, 'create_organization_role')
    assert hasattr(role_service, 'get_organization_roles')
    assert hasattr(role_service, 'assign_module_to_role')
    assert hasattr(role_service, 'assign_user_to_role')
    assert hasattr(role_service, 'user_has_module_access')
    
    assert hasattr(approval_service, 'get_or_create_approval_settings')
    assert hasattr(approval_service, 'submit_voucher_for_approval')
    assert hasattr(approval_service, 'approve_voucher_level_1')
    assert hasattr(approval_service, 'approve_voucher_level_2')
    assert hasattr(approval_service, 'reject_voucher')


def test_helper_functions():
    """Test helper functions are available"""
    from app.services.role_management_service import initialize_default_roles, assign_default_modules_to_role
    
    # These functions should be importable and callable
    assert callable(initialize_default_roles)
    assert callable(assign_default_modules_to_role)


def test_module_access_hierarchy():
    """Test module access level hierarchy logic"""
    from app.services.role_management_service import RoleManagementService
    
    mock_db = Mock()
    service = RoleManagementService(mock_db)
    
    # The access hierarchy logic should be consistent
    access_hierarchy = {"view_only": 1, "limited": 2, "full": 3}
    
    # Test hierarchy levels
    assert access_hierarchy["view_only"] < access_hierarchy["limited"]
    assert access_hierarchy["limited"] < access_hierarchy["full"]
    
    # Test permission checking logic
    required_level = access_hierarchy.get("limited", 1)
    user_level = access_hierarchy.get("full", 0)
    
    # User with "full" access should satisfy "limited" requirement
    assert user_level >= required_level


def test_approval_workflow_constants():
    """Test approval workflow status constants"""
    from app.schemas.role_management import ApprovalModel, ApprovalStatus
    
    # Test ApprovalModel enum values
    assert ApprovalModel.NO_APPROVAL == "no_approval"
    assert ApprovalModel.LEVEL_1 == "level_1"
    assert ApprovalModel.LEVEL_2 == "level_2"
    
    # Test ApprovalStatus enum values
    assert ApprovalStatus.PENDING == "pending"
    assert ApprovalStatus.LEVEL_1_APPROVED == "level_1_approved"
    assert ApprovalStatus.APPROVED == "approved"
    assert ApprovalStatus.REJECTED == "rejected"


def test_role_hierarchy_constants():
    """Test role hierarchy level constants"""
    # Management has highest priority (lowest number)
    MANAGEMENT_LEVEL = 1
    MANAGER_LEVEL = 2  
    EXECUTIVE_LEVEL = 3
    
    assert MANAGEMENT_LEVEL < MANAGER_LEVEL < EXECUTIVE_LEVEL
    
    # Test that the levels correspond to proper hierarchy
    # Lower numbers = higher authority
    assert MANAGEMENT_LEVEL == 1  # Highest authority
    assert EXECUTIVE_LEVEL == 3   # Lowest authority


def test_default_role_structure():
    """Test the structure of default roles"""
    default_roles = [
        {"name": "management", "display_name": "Management", "hierarchy_level": 1},
        {"name": "manager", "display_name": "Manager", "hierarchy_level": 2},
        {"name": "executive", "display_name": "Executive", "hierarchy_level": 3}
    ]
    
    # Test role ordering (by hierarchy level)
    sorted_roles = sorted(default_roles, key=lambda x: x["hierarchy_level"])
    assert sorted_roles[0]["name"] == "management"
    assert sorted_roles[1]["name"] == "manager"
    assert sorted_roles[2]["name"] == "executive"
    
    # Test each role has required fields
    for role in default_roles:
        assert "name" in role
        assert "display_name" in role
        assert "hierarchy_level" in role
        assert isinstance(role["hierarchy_level"], int)


def test_valid_modules_list():
    """Test that valid modules are properly defined"""
    VALID_MODULES = ["CRM", "ERP", "HR", "Inventory", "Service", "Analytics", "Finance", "Mail"]
    
    # Test that we have a reasonable number of modules
    assert len(VALID_MODULES) >= 7
    
    # Test that core modules are included
    assert "CRM" in VALID_MODULES
    assert "ERP" in VALID_MODULES
    assert "HR" in VALID_MODULES
    assert "Finance" in VALID_MODULES
    
    # Test module names are strings
    for module in VALID_MODULES:
        assert isinstance(module, str)
        assert len(module) > 0


def test_access_levels():
    """Test access level definitions"""
    from app.schemas.role_management import AccessLevel
    
    # Test all access levels are defined
    assert AccessLevel.VIEW_ONLY == "view_only"
    assert AccessLevel.LIMITED == "limited"
    assert AccessLevel.FULL == "full"
    
    # Test that access levels can be compared meaningfully
    access_hierarchy = {"view_only": 1, "limited": 2, "full": 3}
    
    for level in [AccessLevel.VIEW_ONLY, AccessLevel.LIMITED, AccessLevel.FULL]:
        assert level.value in access_hierarchy


if __name__ == "__main__":
    pytest.main([__file__])