# app/schemas/entitlement_schemas.py

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict
from datetime import datetime


class SubmoduleResponse(BaseModel):
    """Submodule response schema"""
    id: int
    submodule_key: str
    display_name: str
    description: Optional[str] = None
    menu_path: Optional[str] = None
    permission_key: Optional[str] = None
    sort_order: int
    is_active: bool

    class Config:
        from_attributes = True


class ModuleResponse(BaseModel):
    """Module response schema"""
    id: int
    module_key: str
    display_name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    sort_order: int
    is_active: bool
    submodules: List[SubmoduleResponse] = []

    class Config:
        from_attributes = True


class ModulesListResponse(BaseModel):
    """Response for GET /admin/modules"""
    modules: List[ModuleResponse]


class SubmoduleEntitlementResponse(BaseModel):
    """Submodule entitlement in org entitlements response"""
    submodule_id: int
    submodule_key: str
    submodule_display_name: str
    enabled: bool
    effective_status: str  # 'enabled', 'disabled', 'trial'
    source: Optional[str] = None

    class Config:
        from_attributes = True


class ModuleEntitlementResponse(BaseModel):
    """Module entitlement response"""
    module_id: int
    module_key: str
    module_display_name: str
    status: str  # 'enabled', 'disabled', 'trial'
    trial_expires_at: Optional[datetime] = None
    source: str
    submodules: List[SubmoduleEntitlementResponse] = []

    class Config:
        from_attributes = True


class OrgEntitlementsResponse(BaseModel):
    """Response for GET /admin/orgs/{orgId}/entitlements"""
    org_id: int
    org_name: str
    entitlements: List[ModuleEntitlementResponse]


class ModuleChange(BaseModel):
    """Module-level change in PUT request"""
    module_key: str = Field(..., description="Module key to update")
    status: str = Field(..., description="New status: enabled, disabled, or trial")
    trial_expires_at: Optional[datetime] = Field(None, description="Trial expiration date (required if status is trial)")
    source: Optional[str] = Field(None, description="Source of the change (e.g., manual, subscription)")

    @validator('status')
    def validate_status(cls, v):
        if v not in ['enabled', 'disabled', 'trial']:
            raise ValueError("status must be one of: enabled, disabled, trial")
        return v

    @validator('trial_expires_at')
    def validate_trial_expiry(cls, v, values):
        if values.get('status') == 'trial' and v is None:
            raise ValueError("trial_expires_at is required when status is trial")
        return v


class SubmoduleChange(BaseModel):
    """Submodule-level change in PUT request"""
    module_key: str = Field(..., description="Module key")
    submodule_key: str = Field(..., description="Submodule key to update")
    enabled: bool = Field(..., description="Whether submodule is enabled")
    source: Optional[str] = Field(None, description="Source of the change (e.g., manual, subscription)")


class EntitlementChanges(BaseModel):
    """Changes to apply in PUT request"""
    modules: List[ModuleChange] = Field(default_factory=list, description="Module-level changes")
    submodules: List[SubmoduleChange] = Field(default_factory=list, description="Submodule-level changes")


class UpdateEntitlementsRequest(BaseModel):
    """Request for PUT /admin/orgs/{orgId}/entitlements"""
    reason: str = Field(..., description="Reason for the entitlement change", min_length=10, max_length=500)
    changes: EntitlementChanges = Field(..., description="Changes to apply")


class UpdateEntitlementsResponse(BaseModel):
    """Response for PUT /admin/orgs/{orgId}/entitlements"""
    success: bool
    message: str
    event_id: int
    updated_entitlements: OrgEntitlementsResponse


class AppEntitlementSubmodules(BaseModel):
    """Submodules map for app entitlements"""
    # Map of submodule_key to enabled boolean
    pass


class AppModuleEntitlement(BaseModel):
    """Module entitlement for app use"""
    module_key: str
    status: str  # 'enabled', 'disabled', 'trial'
    trial_expires_at: Optional[datetime] = None
    submodules: Dict[str, bool] = Field(default_factory=dict, description="Map of submodule_key to enabled status")

    class Config:
        from_attributes = True


class AppEntitlementsResponse(BaseModel):
    """Response for GET /orgs/{orgId}/entitlements (app use)"""
    org_id: int
    entitlements: Dict[str, AppModuleEntitlement] = Field(default_factory=dict, description="Map of module_key to entitlement")


class EntitlementEventResponse(BaseModel):
    """Entitlement event response"""
    id: int
    org_id: int
    event_type: str
    actor_user_id: Optional[int] = None
    actor_name: Optional[str] = None
    reason: Optional[str] = None
    payload: Optional[Dict] = None
    created_at: datetime

    class Config:
        from_attributes = True


class EntitlementEventsResponse(BaseModel):
    """Response for entitlement events list"""
    events: List[EntitlementEventResponse]
    total: int
    page: int = 1
    per_page: int = 50