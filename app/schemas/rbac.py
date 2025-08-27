# app/schemas/rbac.py

"""
RBAC schemas for Service CRM role-based access control
"""

from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ServiceRoleType(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    SUPPORT = "support"
    VIEWER = "viewer"


class ServiceModule(str, Enum):
    SERVICE = "service"
    TECHNICIAN = "technician"
    APPOINTMENT = "appointment"
    CUSTOMER_SERVICE = "customer_service"
    WORK_ORDER = "work_order"
    SERVICE_REPORTS = "service_reports"
    CRM_ADMIN = "crm_admin"
    CUSTOMER_FEEDBACK = "customer_feedback"
    SERVICE_CLOSURE = "service_closure"


class ServiceAction(str, Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    EXPORT = "export"
    ADMIN = "admin"
    SUBMIT = "submit"  # For customer feedback submission
    APPROVE = "approve"  # For service closure approval
    CLOSE = "close"  # For service closure


# Service Permission Schemas
class ServicePermissionBase(BaseModel):
    name: str = Field(..., description="Permission name (e.g., service_create)")
    display_name: str = Field(..., description="Human-readable permission name")
    description: Optional[str] = Field(None, description="Permission description")
    module: ServiceModule = Field(..., description="Module this permission applies to")
    action: ServiceAction = Field(..., description="Action this permission allows")
    is_active: bool = Field(True, description="Whether permission is active")


class ServicePermissionCreate(ServicePermissionBase):
    pass


class ServicePermissionUpdate(BaseModel):
    display_name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class ServicePermissionInDB(ServicePermissionBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


# Service Role Schemas
class ServiceRoleBase(BaseModel):
    name: ServiceRoleType = Field(..., description="Role name")
    display_name: str = Field(..., description="Human-readable role name")
    description: Optional[str] = Field(None, description="Role description")
    is_active: bool = Field(True, description="Whether role is active")


class ServiceRoleCreate(ServiceRoleBase):
    organization_id: int = Field(..., description="Organization ID")
    permission_ids: List[int] = Field(default_factory=list, description="List of permission IDs to assign")


class ServiceRoleUpdate(BaseModel):
    display_name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    permission_ids: Optional[List[int]] = None


class ServiceRoleInDB(ServiceRoleBase):
    id: int
    organization_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class ServiceRoleWithPermissions(ServiceRoleInDB):
    permissions: List[ServicePermissionInDB] = Field(default_factory=list)


# User Service Role Assignment Schemas
class UserServiceRoleBase(BaseModel):
    user_id: int = Field(..., description="User ID")
    role_id: int = Field(..., description="Service role ID")
    is_active: bool = Field(True, description="Whether assignment is active")


class UserServiceRoleCreate(UserServiceRoleBase):
    assigned_by_id: Optional[int] = Field(None, description="User ID who made the assignment")


class UserServiceRoleUpdate(BaseModel):
    is_active: Optional[bool] = None


class UserServiceRoleInDB(UserServiceRoleBase):
    id: int
    assigned_by_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


# User with Service Roles
class UserWithServiceRoles(BaseModel):
    id: int
    email: str
    full_name: Optional[str] = None
    role: str  # Regular user role
    is_active: bool
    service_roles: List[ServiceRoleInDB] = Field(default_factory=list)
    
    model_config = ConfigDict(from_attributes=True)


# Service Role Assignment Request
class RoleAssignmentRequest(BaseModel):
    user_id: int = Field(..., description="User ID to assign role to")
    role_ids: List[int] = Field(..., description="List of service role IDs to assign")


class RoleAssignmentResponse(BaseModel):
    success: bool
    message: str
    assignments: List[UserServiceRoleInDB] = Field(default_factory=list)


# Permission Check Schemas
class PermissionCheckRequest(BaseModel):
    user_id: int = Field(..., description="User ID to check")
    permission: str = Field(..., description="Permission to check")
    organization_id: Optional[int] = Field(None, description="Organization context")


class PermissionCheckResponse(BaseModel):
    has_permission: bool
    user_id: int
    permission: str
    source: str = Field(..., description="Source of permission (role_name or 'system')")


# Bulk Operations
class BulkRoleAssignmentRequest(BaseModel):
    user_ids: List[int] = Field(..., description="List of user IDs")
    role_ids: List[int] = Field(..., description="List of role IDs to assign")
    replace_existing: bool = Field(False, description="Whether to replace existing role assignments")


class BulkRoleAssignmentResponse(BaseModel):
    success: bool
    message: str
    successful_assignments: int
    failed_assignments: int
    details: List[str] = Field(default_factory=list)