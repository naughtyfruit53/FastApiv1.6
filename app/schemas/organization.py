# app/schemas/organization.py

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, List
from datetime import datetime
import enum


class OrganizationBase(BaseModel):
    name: str = Field(..., max_length=100)
    subdomain: str = Field(..., max_length=100)


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    subdomain: Optional[str] = Field(None, max_length=100)
    # Business details
    business_type: Optional[str] = Field(None, max_length=100)
    industry: Optional[str] = Field(None, max_length=100)
    website: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    # Contact information
    primary_email: Optional[str] = Field(None, max_length=255)
    primary_phone: Optional[str] = Field(None, max_length=20)
    # Address
    address1: Optional[str] = Field(None, max_length=255)
    address2: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    pin_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=100)
    state_code: Optional[str] = Field(None, max_length=10)
    # Legal details
    gst_number: Optional[str] = Field(None, max_length=50)
    pan_number: Optional[str] = Field(None, max_length=50)
    cin_number: Optional[str] = Field(None, max_length=50)
    # Settings
    timezone: Optional[str] = Field(None, max_length=100)
    currency: Optional[str] = Field(None, max_length=10)
    date_format: Optional[str] = Field(None, max_length=50)
    financial_year_start: Optional[str] = Field(None, max_length=10)


class OrganizationInDB(OrganizationBase):
    id: int
    # Business details
    business_type: Optional[str] = None
    industry: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    # Contact information
    primary_email: str
    primary_phone: str
    # Address
    address1: str
    address2: Optional[str] = None
    city: str
    state: str
    pin_code: str
    country: Optional[str] = "India"
    state_code: Optional[str] = None
    # Legal details
    gst_number: Optional[str] = None
    pan_number: Optional[str] = None
    cin_number: Optional[str] = None
    # Settings
    timezone: Optional[str] = "Asia/Kolkata"
    currency: Optional[str] = "INR"
    date_format: Optional[str] = "DD/MM/YYYY"
    financial_year_start: Optional[str] = "04/01"
    # Module access
    enabled_modules: Optional[Dict] = None
    # Metadata
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class OrganizationLicenseCreate(BaseModel):
    license_type: str = Field("trial", max_length=50)
    license_duration_months: Optional[int] = None
    organization_id: Optional[int] = None
    superadmin_email: str = Field(..., max_length=255)
    primary_phone: str = Field(..., max_length=20)
    address1: str = Field(..., max_length=255)
    city: str = Field(..., max_length=100)
    state: str = Field(..., max_length=100)
    pin_code: str = Field(..., max_length=20)
    gst_number: Optional[str] = Field(None, max_length=50)
    organization_name: str = Field(..., max_length=100)
    max_users: int = Field(..., ge=1)
    enabled_modules: Optional[Dict] = None
    state_code: str = Field(..., max_length=10)


class OrganizationLicenseResponse(BaseModel):
    organization_name: str
    subdomain: str
    superadmin_email: str
    temp_password: str
    license_type: str
    license_status: str = Field(..., description="Derived status: 'active' or 'trial'")
    license_issued_date: Optional[datetime] = None
    license_expiry_date: Optional[datetime] = None


class VoucherCounterResetPeriod(str, enum.Enum):
    """Voucher counter reset period options"""
    NEVER = "never"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUALLY = "annually"


class OrganizationSettingsBase(BaseModel):
    mail_1_level_up_enabled: bool = False
    auto_send_notifications: bool = True
    voucher_prefix: Optional[str] = Field(None, max_length=5)
    voucher_prefix_enabled: bool = False
    voucher_counter_reset_period: VoucherCounterResetPeriod = VoucherCounterResetPeriod.ANNUALLY
    voucher_format_template_id: Optional[int] = None
    custom_settings: Optional[Dict] = None
    # Terms & Conditions for different voucher types
    purchase_order_terms: Optional[str] = Field(None, max_length=2000)
    purchase_voucher_terms: Optional[str] = Field(None, max_length=2000)
    sales_order_terms: Optional[str] = Field(None, max_length=2000)
    sales_voucher_terms: Optional[str] = Field(None, max_length=2000)
    quotation_terms: Optional[str] = Field(None, max_length=2000)
    proforma_invoice_terms: Optional[str] = Field(None, max_length=2000)
    delivery_challan_terms: Optional[str] = Field(None, max_length=2000)
    grn_terms: Optional[str] = Field(None, max_length=2000)
    manufacturing_terms: Optional[str] = Field(None, max_length=2000)
    # Tally Sync Integration fields
    tally_enabled: bool = False
    tally_host: Optional[str] = Field(None, max_length=255)
    tally_port: Optional[int] = Field(None, ge=1, le=65535)
    tally_company_name: Optional[str] = Field(None, max_length=255)
    tally_sync_frequency: Optional[str] = Field(None, max_length=50)
    tally_last_sync: Optional[datetime] = None


class OrganizationSettingsCreate(OrganizationSettingsBase):
    organization_id: int


class OrganizationSettingsUpdate(BaseModel):
    mail_1_level_up_enabled: Optional[bool] = None
    auto_send_notifications: Optional[bool] = None
    voucher_prefix: Optional[str] = Field(None, max_length=5)
    voucher_prefix_enabled: Optional[bool] = None
    voucher_counter_reset_period: Optional[VoucherCounterResetPeriod] = None
    voucher_format_template_id: Optional[int] = None
    custom_settings: Optional[Dict] = None
    # Terms & Conditions for different voucher types
    purchase_order_terms: Optional[str] = Field(None, max_length=2000)
    purchase_voucher_terms: Optional[str] = Field(None, max_length=2000)
    sales_order_terms: Optional[str] = Field(None, max_length=2000)
    sales_voucher_terms: Optional[str] = Field(None, max_length=2000)
    quotation_terms: Optional[str] = Field(None, max_length=2000)
    proforma_invoice_terms: Optional[str] = Field(None, max_length=2000)
    delivery_challan_terms: Optional[str] = Field(None, max_length=2000)
    grn_terms: Optional[str] = Field(None, max_length=2000)
    manufacturing_terms: Optional[str] = Field(None, max_length=2000)
    # Tally Sync Integration fields
    tally_enabled: Optional[bool] = None
    tally_host: Optional[str] = Field(None, max_length=255)
    tally_port: Optional[int] = Field(None, ge=1, le=65535)
    tally_company_name: Optional[str] = Field(None, max_length=255)
    tally_sync_frequency: Optional[str] = Field(None, max_length=50)
    tally_last_sync: Optional[datetime] = None


class OrganizationSettingsInDB(OrganizationSettingsBase):
    id: int
    organization_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class OrganizationSettingsResponse(OrganizationSettingsInDB):
    """Response model for organization settings"""
    pass


class VoucherEmailTemplateBase(BaseModel):
    voucher_type: str
    entity_type: str
    subject_template: str = Field(..., max_length=500)
    body_template: str
    is_active: bool = True


class VoucherEmailTemplateCreate(VoucherEmailTemplateBase):
    organization_id: int


class VoucherEmailTemplateUpdate(BaseModel):
    subject_template: Optional[str] = Field(None, max_length=500)
    body_template: Optional[str] = None
    is_active: Optional[bool] = None


class VoucherEmailTemplateInDB(VoucherEmailTemplateBase):
    id: int
    organization_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class VoucherEmailTemplateResponse(VoucherEmailTemplateInDB):
    """Response model for voucher email template"""
    pass


class VoucherFormatTemplateBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    template_config: Dict
    preview_image_url: Optional[str] = Field(None, max_length=500)
    is_system_template: bool = False
    is_active: bool = True


class VoucherFormatTemplateCreate(VoucherFormatTemplateBase):
    pass


class VoucherFormatTemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    template_config: Optional[Dict] = None
    preview_image_url: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None


class VoucherFormatTemplateInDB(VoucherFormatTemplateBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class VoucherFormatTemplateResponse(VoucherFormatTemplateInDB):
    """Response model for voucher format template"""
    pass


class RecentActivity(BaseModel):
    id: int
    action: str
    entity_type: str
    entity_id: Optional[int] = None  # Changed to Optional to allow None
    user_id: int
    organization_id: int
    description: Optional[str] = None
    created_at: datetime
    user_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class RecentActivityResponse(BaseModel):
    activities: List[RecentActivity]


class TotalInventoryValue(BaseModel):
    total_value: float
    currency: str
    last_updated: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)