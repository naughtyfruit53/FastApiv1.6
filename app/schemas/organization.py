# app/schemas/organization.py

from pydantic import BaseModel
from typing import Optional, Dict, List
from datetime import datetime

class OrganizationBase(BaseModel):
    name: str
    subdomain: Optional[str] = None
    primary_email: str
    primary_phone: str
    address1: str
    city: str
    state: str
    pin_code: str
    gst_number: Optional[str] = None

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    primary_email: Optional[str] = None
    primary_phone: Optional[str] = None
    address1: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pin_code: Optional[str] = None
    gst_number: Optional[str] = None

class OrganizationInDB(OrganizationBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    enabled_modules: Optional[Dict[str, bool]] = None

class OrganizationLicenseCreate(BaseModel):
    organization_name: str
    subdomain: Optional[str] = None
    superadmin_email: str
    primary_phone: str
    address1: str
    pin_code: str
    city: str
    state: str
    state_code: str
    gst_number: Optional[str] = None
    max_users: int = 5
    enabled_modules: Optional[Dict[str, bool]] = None

class OrganizationLicenseResponse(BaseModel):
    organization_id: int
    organization_name: str
    subdomain: str
    superadmin_email: str
    temp_password: str
    message: str

class RecentActivity(BaseModel):
    id: str
    type: str
    title: str
    description: str
    timestamp: str
    user_name: Optional[str] = None

class RecentActivityResponse(BaseModel):
    activities: List[RecentActivity]
    total_count: int
    generated_at: str

class TotalInventoryValue(BaseModel):
    total_value: float