# app/schemas/role_management.py

from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# Enums for role hierarchy and approval models

class RoleHierarchyLevel(str, Enum):
    MANAGEMENT = "management"
    MANAGER = "manager" 
    EXECUTIVE = "executive"


class AccessLevel(str, Enum):
    FULL = "full"
    LIMITED = "limited"
    VIEW_ONLY = "view_only"


class ApprovalModel(str, Enum):
    NO_APPROVAL = "no_approval"
    LEVEL_1 = "level_1" 
    LEVEL_2 = "level_2"


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    LEVEL_1_APPROVED = "level_1_approved"
    APPROVED = "approved"
    REJECTED = "rejected"


# Organization Role Schemas

class OrganizationRoleBase(BaseModel):
    name: str
    display_name: str
    description: Optional[str] = None
    hierarchy_level: int
    is_active: bool = True


class OrganizationRoleCreate(OrganizationRoleBase):
    organization_id: int
    
    @validator('hierarchy_level')
    def validate_hierarchy_level(cls, v):
        if v not in [1, 2, 3]:  # 1=Management, 2=Manager, 3=Executive
            raise ValueError('hierarchy_level must be 1 (Management), 2 (Manager), or 3 (Executive)')
        return v


class OrganizationRoleUpdate(BaseModel):
    display_name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class OrganizationRoleInDB(OrganizationRoleBase):
    id: int
    organization_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by_id: Optional[int] = None
    
    class Config:
        from_attributes = True


# Role Module Assignment Schemas

class RoleModuleAssignmentBase(BaseModel):
    module_name: str
    access_level: AccessLevel = AccessLevel.FULL
    permissions: Optional[Dict[str, Any]] = None
    is_active: bool = True


class RoleModuleAssignmentCreate(RoleModuleAssignmentBase):
    organization_id: int
    role_id: int
    
    @validator('module_name')
    def validate_module_name(cls, v):
        valid_modules = ["CRM", "ERP", "HR", "Inventory", "Service", "Analytics", "Finance", "Mail"]
        if v not in valid_modules:
            raise ValueError(f'module_name must be one of: {", ".join(valid_modules)}')
        return v


class RoleModuleAssignmentUpdate(BaseModel):
    access_level: Optional[AccessLevel] = None
    permissions: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class RoleModuleAssignmentInDB(RoleModuleAssignmentBase):
    id: int
    organization_id: int
    role_id: int
    created_at: datetime
    assigned_by_id: Optional[int] = None
    
    class Config:
        from_attributes = True


# User Organization Role Assignment Schemas

class UserOrganizationRoleBase(BaseModel):
    is_active: bool = True
    manager_assignments: Optional[Dict[str, int]] = None  # {"CRM": manager_user_id}


class UserOrganizationRoleCreate(UserOrganizationRoleBase):
    organization_id: int
    user_id: int
    role_id: int


class UserOrganizationRoleUpdate(BaseModel):
    is_active: Optional[bool] = None
    manager_assignments: Optional[Dict[str, int]] = None


class UserOrganizationRoleInDB(UserOrganizationRoleBase):
    id: int
    organization_id: int
    user_id: int
    role_id: int
    assigned_by_id: Optional[int] = None
    assigned_at: datetime
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Organization Approval Settings Schemas

class OrganizationApprovalSettingsBase(BaseModel):
    approval_model: ApprovalModel = ApprovalModel.NO_APPROVAL
    level_2_approvers: Optional[Dict[str, List[int]]] = None  # {"user_ids": [1, 2, 3]}
    auto_approve_threshold: Optional[float] = None
    escalation_timeout_hours: Optional[int] = 72


class OrganizationApprovalSettingsCreate(OrganizationApprovalSettingsBase):
    organization_id: int
    
    @validator('level_2_approvers')
    def validate_level_2_approvers(cls, v, values):
        if values.get('approval_model') == ApprovalModel.LEVEL_2 and not v:
            raise ValueError('level_2_approvers is required when approval_model is level_2')
        return v


class OrganizationApprovalSettingsUpdate(BaseModel):
    approval_model: Optional[ApprovalModel] = None
    level_2_approvers: Optional[Dict[str, List[int]]] = None
    auto_approve_threshold: Optional[float] = None
    escalation_timeout_hours: Optional[int] = None


class OrganizationApprovalSettingsInDB(OrganizationApprovalSettingsBase):
    id: int
    organization_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    updated_by_id: Optional[int] = None
    
    class Config:
        from_attributes = True


# Voucher Approval Schemas

class VoucherApprovalBase(BaseModel):
    voucher_type: str
    voucher_id: int
    voucher_number: Optional[str] = None
    voucher_amount: Optional[float] = None


class VoucherApprovalCreate(VoucherApprovalBase):
    organization_id: int
    approval_settings_id: int
    submitted_by_id: int


class VoucherApprovalUpdate(BaseModel):
    status: Optional[ApprovalStatus] = None
    current_approver_id: Optional[int] = None
    level_1_comments: Optional[str] = None
    level_2_comments: Optional[str] = None
    final_decision: Optional[str] = None
    rejection_reason: Optional[str] = None


class VoucherApprovalInDB(VoucherApprovalBase):
    id: int
    organization_id: int
    approval_settings_id: int
    submitted_by_id: int
    submitted_at: datetime
    status: ApprovalStatus
    current_approver_id: Optional[int] = None
    
    # Level 1 approval
    level_1_approver_id: Optional[int] = None
    level_1_approved_at: Optional[datetime] = None
    level_1_comments: Optional[str] = None
    
    # Level 2 approval
    level_2_approver_id: Optional[int] = None
    level_2_approved_at: Optional[datetime] = None
    level_2_comments: Optional[str] = None
    
    # Final decision
    final_decision: Optional[str] = None
    final_decision_at: Optional[datetime] = None
    final_decision_by_id: Optional[int] = None
    rejection_reason: Optional[str] = None
    
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Composite response schemas for API endpoints

class OrganizationRoleWithAssignments(OrganizationRoleInDB):
    module_assignments: List[RoleModuleAssignmentInDB] = []
    user_assignments: List[UserOrganizationRoleInDB] = []


class UserWithRoles(BaseModel):
    id: int
    email: str
    full_name: Optional[str] = None
    role: str  # Legacy role field
    is_active: bool
    organization_roles: List[UserOrganizationRoleInDB] = []
    
    class Config:
        from_attributes = True


class VoucherApprovalWithDetails(VoucherApprovalInDB):
    submitted_by_name: Optional[str] = None
    current_approver_name: Optional[str] = None
    level_1_approver_name: Optional[str] = None
    level_2_approver_name: Optional[str] = None
    final_decision_by_name: Optional[str] = None


# Summary schemas for dashboards

class ApprovalSummary(BaseModel):
    pending_approvals: int
    level_1_approved: int
    approved: int
    rejected: int
    user_pending_approvals: int  # Approvals pending for current user


class RoleAssignmentSummary(BaseModel):
    total_users: int
    management_users: int
    manager_users: int
    executive_users: int
    unassigned_users: int