# app/schemas/vouchers/base.py

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from typing import Dict, Any
from pydantic import field_validator, ConfigDict

# Minimal Chart of Account schema for inclusion in voucher responses
class ChartOfAccountMinimal(BaseModel):
    id: int
    account_code: str
    account_name: str
    account_type: str
    
    model_config = ConfigDict(from_attributes = True)

class VoucherItemBase(BaseModel):
    product_id: int
    quantity: float
    unit: str
    unit_price: float

class VoucherItemWithTax(VoucherItemBase):
    discount_percentage: Optional[float] = None
    discount_amount: Optional[float] = None
    taxable_amount: Optional[float] = None
    gst_rate: Optional[float] = None
    cgst_amount: Optional[float] = None
    sgst_amount: Optional[float] = None
    igst_amount: Optional[float] = None
    total_amount: Optional[float] = None

class SimpleVoucherItem(BaseModel):
    product_id: int
    quantity: float
    unit: str
    unit_price: Optional[float] = 0.0
    description: Optional[str] = None

class VoucherBase(BaseModel):
    voucher_number: str
    date: datetime
    total_amount: Optional[float] = None
    cgst_amount: Optional[float] = None
    sgst_amount: Optional[float] = None
    igst_amount: Optional[float] = None
    discount_amount: Optional[float] = None
    status: str = "draft"
    notes: Optional[str] = None

class VoucherInDBBase(VoucherBase):
    id: int
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes = True)

class ProductMinimal(BaseModel):
    product_name: str

    model_config = ConfigDict(from_attributes = True)

class VendorMinimal(BaseModel):
    id: int
    name: str
    state_code: Optional[str] = None
    gst_number: Optional[str] = None

    model_config = ConfigDict(from_attributes = True)

class PurchaseOrderMinimal(BaseModel):
    id: int
    voucher_number: str

    model_config = ConfigDict(from_attributes = True)

# Email notification schemas
class EmailNotificationBase(BaseModel):
    to_email: EmailStr
    subject: str
    body: str
    voucher_type: Optional[str] = None
    voucher_id: Optional[int] = None

class EmailNotificationCreate(EmailNotificationBase):
    pass

class EmailNotificationInDB(EmailNotificationBase):
    id: int
    organization_id: int
    status: str = "pending"
    sent_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes = True)

# Payment term schemas
class PaymentTermBase(BaseModel):
    name: str
    days: int
    description: Optional[str] = None

class PaymentTermCreate(PaymentTermBase):
    pass

class PaymentTermUpdate(BaseModel):
    name: Optional[str] = None
    days: Optional[int] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class PaymentTermInDB(PaymentTermBase):
    id: int
    organization_id: int
    is_active: bool = True
    
    model_config = ConfigDict(from_attributes = True)

# Enhanced bulk import/export response schemas
class BulkImportResponse(BaseModel):
    message: str
    total_processed: int
    created: int
    updated: int
    errors: List[str] = []
    warnings: List[str] = []
    processing_time_ms: Optional[int] = None
    
class BulkImportError(BaseModel):
    row: int
    field: Optional[str] = None
    value: Optional[str] = None
    error: str
    error_type: str = "validation_error"  # validation_error, business_rule, data_type, etc.
    suggestion: Optional[str] = None  # Helpful suggestion to fix the error
    
class BulkImportWarning(BaseModel):
    row: int
    field: Optional[str] = None
    value: Optional[str] = None
    warning: str
    
class DetailedBulkImportResponse(BaseModel):
    message: str
    total_processed: int
    created: int
    updated: int
    skipped: int
    errors: List[BulkImportError] = []
    warnings: List[BulkImportWarning] = []
    processing_time_ms: Optional[int] = None
    summary: Optional[Dict[str, Any]] = None  # Additional summary information
    
class ExcelImportValidationResponse(BaseModel):
    """Response for Excel file validation before processing"""
    valid: bool
    file_info: Dict[str, Any]
    validation_errors: List[str] = []
    validation_warnings: List[str] = []
    preview_data: List[Dict[str, Any]] = []  # First few rows for preview
    total_rows: int = 0