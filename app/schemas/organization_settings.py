# app/schemas/organization_settings.py

from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import datetime
from enum import Enum


class VoucherCounterResetPeriod(str, Enum):
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


class OrganizationSettingsInDB(OrganizationSettingsBase):
    id: int
    organization_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


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

    class Config:
        from_attributes = True


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

    class Config:
        from_attributes = True


class VoucherFormatTemplateResponse(VoucherFormatTemplateInDB):
    """Response model for voucher format template"""
    pass