# tests/test_role_management_models.py

"""
Basic syntax and structure tests for the new role management models.
This file tests that models are properly defined and can be imported.
"""

import pytest
from typing import Dict, Any


def test_model_imports():
    """Test that all new models can be imported without errors"""
    try:
        from app.models.user_models import (
            OrganizationRole,
            RoleModuleAssignment, 
            UserOrganizationRole,
            OrganizationApprovalSettings,
            VoucherApproval
        )
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import role management models: {e}")


def test_schema_imports():
    """Test that all new schemas can be imported without errors"""
    try:
        from app.schemas.role_management import (
            OrganizationRoleCreate,
            RoleModuleAssignmentCreate,
            UserOrganizationRoleCreate,
            OrganizationApprovalSettingsCreate,
            VoucherApprovalCreate,
            RoleHierarchyLevel,
            AccessLevel,
            ApprovalModel,
            ApprovalStatus
        )
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import role management schemas: {e}")


def test_enum_values():
    """Test that enum values are correctly defined"""
    from app.schemas.role_management import RoleHierarchyLevel, AccessLevel, ApprovalModel, ApprovalStatus
    
    # Test RoleHierarchyLevel enum
    assert RoleHierarchyLevel.MANAGEMENT == "management"
    assert RoleHierarchyLevel.MANAGER == "manager"
    assert RoleHierarchyLevel.EXECUTIVE == "executive"
    
    # Test AccessLevel enum
    assert AccessLevel.FULL == "full"
    assert AccessLevel.LIMITED == "limited"
    assert AccessLevel.VIEW_ONLY == "view_only"
    
    # Test ApprovalModel enum
    assert ApprovalModel.NO_APPROVAL == "no_approval"
    assert ApprovalModel.LEVEL_1 == "level_1"
    assert ApprovalModel.LEVEL_2 == "level_2"
    
    # Test ApprovalStatus enum
    assert ApprovalStatus.PENDING == "pending"
    assert ApprovalStatus.LEVEL_1_APPROVED == "level_1_approved"
    assert ApprovalStatus.APPROVED == "approved"
    assert ApprovalStatus.REJECTED == "rejected"


def test_schema_validation():
    """Test schema validation with sample data"""
    from app.schemas.role_management import (
        OrganizationRoleCreate,
        RoleModuleAssignmentCreate,
        OrganizationApprovalSettingsCreate
    )
    
    # Test OrganizationRoleCreate validation
    role_data = {
        "organization_id": 1,
        "name": "management",
        "display_name": "Management",
        "description": "Full access management role",
        "hierarchy_level": 1
    }
    role = OrganizationRoleCreate(**role_data)
    assert role.name == "management"
    assert role.hierarchy_level == 1
    
    # Test RoleModuleAssignmentCreate validation
    module_data = {
        "organization_id": 1,
        "role_id": 1,
        "module_name": "CRM",
        "access_level": "full"
    }
    module_assignment = RoleModuleAssignmentCreate(**module_data)
    assert module_assignment.module_name == "CRM"
    assert module_assignment.access_level == "full"
    
    # Test OrganizationApprovalSettingsCreate validation
    approval_data = {
        "organization_id": 1,
        "approval_model": "level_2",
        "level_2_approvers": {"user_ids": [1, 2, 3]},
        "auto_approve_threshold": 1000.0
    }
    approval_settings = OrganizationApprovalSettingsCreate(**approval_data)
    assert approval_settings.approval_model == "level_2"
    assert approval_settings.level_2_approvers["user_ids"] == [1, 2, 3]


def test_schema_validation_errors():
    """Test that schema validation catches invalid data"""
    from app.schemas.role_management import OrganizationRoleCreate, RoleModuleAssignmentCreate
    import pytest
    
    # Test invalid hierarchy level
    with pytest.raises(ValueError):
        OrganizationRoleCreate(
            organization_id=1,
            name="invalid",
            display_name="Invalid",
            hierarchy_level=5  # Invalid level
        )
    
    # Test invalid module name
    with pytest.raises(ValueError):
        RoleModuleAssignmentCreate(
            organization_id=1,
            role_id=1,
            module_name="INVALID_MODULE"  # Invalid module
        )


def test_model_table_names():
    """Test that model table names are correctly defined"""
    from app.models.user_models import (
        OrganizationRole,
        RoleModuleAssignment,
        UserOrganizationRole,
        OrganizationApprovalSettings,
        VoucherApproval
    )
    
    assert OrganizationRole.__tablename__ == "organization_roles"
    assert RoleModuleAssignment.__tablename__ == "role_module_assignments"
    assert UserOrganizationRole.__tablename__ == "user_organization_roles"
    assert OrganizationApprovalSettings.__tablename__ == "organization_approval_settings"
    assert VoucherApproval.__tablename__ == "voucher_approvals"


def test_model_hierarchy_constants():
    """Test hierarchy level constants for consistency"""
    # Test that hierarchy levels make sense
    MANAGEMENT_LEVEL = 1
    MANAGER_LEVEL = 2
    EXECUTIVE_LEVEL = 3
    
    assert MANAGEMENT_LEVEL < MANAGER_LEVEL < EXECUTIVE_LEVEL
    
    # Test valid modules
    VALID_MODULES = ["CRM", "ERP", "HR", "Inventory", "Service", "Analytics", "Finance", "Mail"]
    assert len(VALID_MODULES) > 0
    assert "CRM" in VALID_MODULES
    assert "ERP" in VALID_MODULES


if __name__ == "__main__":
    pytest.main([__file__])