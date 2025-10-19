# Revised: app/schemas/base.py

from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum
from pydantic import ConfigDict
from app.models import Product

class BaseSchema(BaseModel):
    id: Optional[int] = None
    organization_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class OrganizationStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TRIAL = "trial"
    EXPIRED = "expired"

class PlanType(str, Enum):
    TRIAL = "trial"
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

# Organization schemas
class OrganizationBase(BaseModel):
    name: str
    subdomain: str
    business_type: Optional[str] = None
    industry: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    primary_email: EmailStr
    primary_phone: str
    address1: str
    address2: Optional[str] = None
    city: str
    state: str
    pin_code: str
    country: str = "India"
    gst_number: Optional[str] = None
    pan_number: Optional[str] = None
    cin_number: Optional[str] = None
    
class OrganizationCreate(OrganizationBase):
    admin_email: EmailStr
    admin_password: str
    
    @validator('admin_password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v
    
    @validator('subdomain')
    def validate_subdomain(cls, v):
        if not v.isalnum() or len(v) < 3:
            raise ValueError('Subdomain must be alphanumeric and at least 3 characters')
        return v.lower()

class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    business_type: Optional[str] = None
    industry: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    primary_email: Optional[EmailStr] = None
    primary_phone: Optional[str] = None
    address1: Optional[str] = None
    address2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pin_code: Optional[str] = None
    country: Optional[str] = None
    gst_number: Optional[str] = None
    pan_number: Optional[str] = None
    cin_number: Optional[str] = None
    status: Optional[OrganizationStatus] = None
    plan_type: Optional[PlanType] = None
    max_users: Optional[int] = None
    storage_limit_gb: Optional[int] = None
    features: Optional[Dict[str, Any]] = None
    timezone: Optional[str] = None
    currency: Optional[str] = None
    date_format: Optional[str] = None
    financial_year_start: Optional[str] = None

class OrganizationInDB(OrganizationBase):
    id: int
    status: OrganizationStatus = OrganizationStatus.TRIAL
    plan_type: PlanType = PlanType.TRIAL
    max_users: int = 5
    storage_limit_gb: int = 1
    features: Optional[Dict[str, Any]] = None
    timezone: str = "Asia/Kolkata"
    currency: str = "INR"
    date_format: str = "DD/MM/YYYY"
    financial_year_start: str = "04/01"
    created_at: datetime
    updated_at: Optional[datetime] = None

class OrganizationLicenseCreate(BaseModel):
    organization_name: str
    superadmin_email: EmailStr
    primary_phone: Optional[str] = None
    address1: Optional[str] = None
    pin_code: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    state_code: Optional[str] = None
    gst_number: Optional[str] = None
    max_users: Optional[int] = 5
    
    @validator('organization_name')
    def validate_organization_name(cls, v):
        if len(v.strip()) < 3:
            raise ValueError('Organization name must be at least 3 characters long')
        return v.strip()
    
    @validator('pin_code')
    def validate_pin_code(cls, v):
        if v and (not v.isdigit() or len(v) != 6):
            raise ValueError('Pin code must be exactly 6 digits')
        return v
    
    @validator('primary_phone')
    def validate_phone(cls, v):
        if v is not None:
            clean_number = ''.join(filter(str.isdigit, v))
            if len(clean_number) < 10:
                raise ValueError('Phone number must contain at least 10 digits')
        return v
    
    @validator('gst_number')
    def validate_gst_number(cls, v):
        if v is not None and v.strip() and len(v.strip()) != 15:
            raise ValueError('GST number must be exactly 15 characters')
        return v.strip() if v else None
    
    @validator('max_users')
    def validate_max_users(cls, v):
        if v is not None and v < 1:
            raise ValueError('Maximum users must be at least 1')
        return v

class OrganizationLicenseResponse(BaseModel):
    message: str
    organization_id: int
    organization_name: str
    superadmin_email: str
    subdomain: str
    temp_password: str
    org_code: Optional[str] = None
    email_sent: bool = False
    email_error: Optional[str] = None
    password_display_warning: str = "⚠️ WARNING: This password is shown only once for manual sharing. Please save it securely and share it with the user immediately. It will not be displayed again."

# Password change and reset schemas
class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str
    
    @validator('new_password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class ForgotPasswordModal(BaseModel):
    email: EmailStr

class PasswordResetRequest(BaseModel):
    user_email: EmailStr
    
class PasswordResetResponse(BaseModel):
    message: str
    user_email: str
    new_password: str
    email_sent: bool
    email_error: Optional[str] = None
    must_change_password: bool = True
    password_display_warning: str = "⚠️ WARNING: This password is shown only once for manual sharing. Please save it securely and share it with the user immediately. It will not be displayed again."

class PasswordChangeResponse(BaseModel):
    message: str
    
    model_config = ConfigDict(from_attributes=True)

# Vendor schemas
class VendorBase(BaseModel):
    name: str
    contact_number: str
    email: Optional[EmailStr] = None
    address1: str
    address2: Optional[str] = None
    city: str
    state: str
    pin_code: str
    state_code: str
    gst_number: Optional[str] = None
    pan_number: Optional[str] = None

class VendorCreate(VendorBase):
    payable_account_id: Optional[int] = None


class VendorUpdate(BaseModel):
    name: Optional[str] = None
    contact_number: Optional[str] = None
    email: Optional[EmailStr] = None
    address1: Optional[str] = None
    address2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pin_code: Optional[str] = None
    state_code: Optional[str] = None
    gst_number: Optional[str] = None
    pan_number: Optional[str] = None
    is_active: Optional[bool] = None
    payable_account_id: Optional[int] = None

class VendorInDB(VendorBase):
    id: int
    organization_id: int
    is_active: bool = True
    payable_account_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

# Customer schemas
class CustomerBase(BaseModel):
    name: str
    contact_number: str
    email: Optional[EmailStr] = None
    address1: str
    address2: Optional[str] = None
    city: str
    state: str
    pin_code: str
    state_code: str
    gst_number: Optional[str] = None
    pan_number: Optional[str] = None

class CustomerCreate(CustomerBase):
    company_id: Optional[int] = None
    receivable_account_id: Optional[int] = None

class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    contact_number: Optional[str] = None
    email: Optional[EmailStr] = None
    address1: Optional[str] = None
    address2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pin_code: Optional[str] = None
    state_code: Optional[str] = None
    gst_number: Optional[str] = None
    pan_number: Optional[str] = None
    is_active: Optional[bool] = None
    receivable_account_id: Optional[int] = None

class CustomerInDB(CustomerBase):
    id: int
    organization_id: int
    company_id: Optional[int] = None
    is_active: bool = True
    receivable_account_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

# Product schemas
class ProductBase(BaseModel):
    product_name: str
    hsn_code: Optional[str] = None
    part_number: Optional[str] = None
    unit: str
    unit_price: float
    gst_rate: float = 0.0
    is_gst_inclusive: bool = False
    reorder_level: int = 0
    description: Optional[str] = None
    is_manufactured: bool = False

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    product_name: Optional[str] = None
    hsn_code: Optional[str] = None
    part_number: Optional[str] = None
    unit: Optional[str] = None
    unit_price: Optional[float] = None
    gst_rate: Optional[float] = None
    is_gst_inclusive: Optional[bool] = None
    reorder_level: Optional[int] = None
    description: Optional[str] = None
    is_manufactured: Optional[bool] = None
    is_active: Optional[bool] = None

class ProductFileBase(BaseModel):
    filename: str
    original_filename: str
    file_size: int
    content_type: str

class ProductFileCreate(ProductFileBase):
    pass

class ProductFileInDB(ProductFileBase):
    id: int
    product_id: int
    organization_id: int
    file_path: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class ProductFileResponse(ProductFileBase):
    id: int
    product_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# Customer File Schemas
class CustomerFileBase(BaseModel):
    filename: str
    original_filename: str
    file_size: int
    content_type: str
    file_type: str = "general"

class CustomerFileCreate(CustomerFileBase):
    pass

class CustomerFileInDB(CustomerFileBase):
    id: int
    customer_id: int
    organization_id: int
    file_path: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class CustomerFileResponse(CustomerFileBase):
    id: int
    customer_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# Vendor File Schemas
class VendorFileBase(BaseModel):
    filename: str
    original_filename: str
    file_size: int
    content_type: str
    file_type: str = "general"

class VendorFileCreate(VendorFileBase):
    pass

class VendorFileInDB(VendorFileBase):
    id: int
    vendor_id: int
    organization_id: int
    file_path: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class VendorFileResponse(VendorFileBase):
    id: int
    vendor_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# Stock schemas
class StockResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    quantity: float
    unit: str
    location: Optional[str] = None
    last_updated: datetime
    product_hsn_code: Optional[str] = None
    product_part_number: Optional[str] = None
    unit_price: float
    reorder_level: int
    gst_rate: float
    is_active: bool
    total_value: float
    
    model_config = ConfigDict(from_attributes=True)

class StockBase(BaseModel):
    product_id: int
    quantity: float
    unit: str
    location: Optional[str] = None

class StockCreate(StockBase):
    pass

class StockUpdate(BaseModel):
    quantity: Optional[float] = None
    unit: Optional[str] = None
    location: Optional[str] = None

class StockInDB(StockBase):
    id: int
    organization_id: int
    last_updated: datetime
    
    model_config = ConfigDict(from_attributes=True)

class BulkStockRequest(BaseModel):
    items: List[Dict[str, Any]]

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
    
    model_config = ConfigDict(from_attributes=True)

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
    
    model_config = ConfigDict(from_attributes=True)

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
    error_type: str = "validation_error"
    suggestion: Optional[str] = None
    
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
    summary: Optional[Dict[str, Any]] = None
    
class ExcelImportValidationResponse(BaseModel):
    valid: bool
    file_info: Dict[str, Any]
    validation_errors: List[str] = []
    validation_warnings: List[str] = []
    preview_data: List[Dict[str, Any]] = []
    total_rows: int = 0

# Notification Schemas for Service CRM
class NotificationTemplateBase(BaseModel):
    name: str
    description: Optional[str] = None
    template_type: str
    channel: str
    subject: Optional[str] = None
    body: str
    html_body: Optional[str] = None
    trigger_event: Optional[str] = None
    trigger_conditions: Optional[Dict[str, Any]] = None
    variables: Optional[List[str]] = None
    is_active: bool = True

class NotificationTemplateCreate(NotificationTemplateBase):
    pass

class NotificationTemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    template_type: Optional[str] = None
    channel: Optional[str] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    html_body: Optional[str] = None
    trigger_event: Optional[str] = None
    trigger_conditions: Optional[Dict[str, Any]] = None
    variables: Optional[List[str]] = None
    is_active: Optional[bool] = None

class NotificationTemplateInDB(NotificationTemplateBase):
    id: int
    organization_id: int
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class NotificationLogBase(BaseModel):
    recipient_type: str
    recipient_id: Optional[int] = None
    recipient_identifier: str
    channel: str
    subject: Optional[str] = None
    content: str
    trigger_event: Optional[str] = None
    context_data: Optional[Dict[str, Any]] = None

class NotificationLogCreate(NotificationLogBase):
    template_id: Optional[int] = None

class NotificationLogInDB(NotificationLogBase):
    id: int
    organization_id: int
    template_id: Optional[int] = None
    status: str = "pending"
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    opened_at: Optional[datetime] = None
    clicked_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class NotificationPreferenceBase(BaseModel):
    subject_type: str
    subject_id: int
    notification_type: str
    channel: str
    is_enabled: bool = True
    settings: Optional[Dict[str, Any]] = None

class NotificationPreferenceCreate(NotificationPreferenceBase):
    pass

class NotificationPreferenceUpdate(BaseModel):
    notification_type: Optional[str] = None
    channel: Optional[str] = None
    is_enabled: Optional[bool] = None
    settings: Optional[Dict[str, Any]] = None

class NotificationPreferenceInDB(NotificationPreferenceBase):
    id: int
    organization_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

# Bulk notification request schemas
class BulkNotificationRequest(BaseModel):
    template_id: Optional[int] = None
    subject: Optional[str] = None
    content: str
    channel: str
    recipient_type: str
    recipient_ids: Optional[List[int]] = None
    segment_name: Optional[str] = None
    variables: Optional[Dict[str, Any]] = None
    
class NotificationSendRequest(BaseModel):
    template_id: Optional[int] = None
    recipient_type: str
    recipient_id: int
    channel: str
    variables: Optional[Dict[str, Any]] = None
    override_content: Optional[str] = None
    override_subject: Optional[str] = None

class NotificationSendResponse(BaseModel):
    notification_id: int
    status: str
    message: str
    
class BulkNotificationResponse(BaseModel):
    total_recipient: int
    successful_sends: int
    failed_sends: int
    notification_ids: List[int]
    errors: List[str] = []

# Product response schema
class ProductInDB(ProductBase):
    id: int
    organization_id: int
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class ProductResponse(BaseModel):
    id: int
    product_name: str
    hsn_code: Optional[str] = None
    part_number: Optional[str] = None
    unit: str
    unit_price: float
    gst_rate: float = 0.0
    is_gst_inclusive: bool = False
    reorder_level: int = 0
    description: Optional[str] = None
    is_manufactured: bool = False
    organization_id: int
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None
    files: List[ProductFileResponse] = []
    
    @classmethod
    def from_product(cls, product: Union[Product, Dict[str, Any]]) -> "ProductResponse":
        if isinstance(product, dict):
            files = product.get('files', [])
            files_response = [
                ProductFileResponse(**f) if isinstance(f, dict) else ProductFileResponse.from_orm(f)
                for f in files
            ]
            return cls(
                id=product['id'],
                product_name=product['product_name'],
                hsn_code=product.get('hsn_code'),
                part_number=product.get('part_number'),
                unit=product['unit'],
                unit_price=product['unit_price'],
                gst_rate=product.get('gst_rate', 0.0),
                is_gst_inclusive=product.get('is_gst_inclusive', False),
                reorder_level=product.get('reorder_level', 0),
                description=product.get('description'),
                is_manufactured=product.get('is_manufactured', False),
                organization_id=product['organization_id'],
                is_active=product.get('is_active', True),
                created_at=product['created_at'],
                updated_at=product.get('updated_at'),
                files=files_response
            )
        
        files = getattr(product, 'files', [])
        files_response = [
            ProductFileResponse.from_orm(f) for f in files
        ]
        
        return cls(
            id=product.id,
            product_name=product.product_name,
            hsn_code=product.hsn_code,
            part_number=product.part_number,
            unit=product.unit,
            unit_price=product.unit_price,
            gst_rate=product.gst_rate,
            is_gst_inclusive=product.is_gst_inclusive,
            reorder_level=product.reorder_level,
            description=product.description,
            is_manufactured=product.is_manufactured,
            organization_id=product.organization_id,
            is_active=product.is_active,
            created_at=product.created_at,
            updated_at=product.updated_at,
            files=files_response
        )
    
    model_config = ConfigDict(from_attributes=True)