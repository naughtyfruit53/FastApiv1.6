# app/schemas/master_data.py
"""
Master Data Schemas - Categories, Units, Payment Terms, and Tax Codes
These schemas provide validation and serialization for master data operations
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from decimal import Decimal
from enum import Enum


class CategoryTypeEnum(str, Enum):
    """Category types for different business entities"""
    PRODUCT = "product"
    SERVICE = "service"
    EXPENSE = "expense"
    ASSET = "asset"
    GENERAL = "general"


class UnitTypeEnum(str, Enum):
    """Unit types for measurement"""
    QUANTITY = "quantity"
    WEIGHT = "weight"
    VOLUME = "volume"
    LENGTH = "length"
    AREA = "area"
    TIME = "time"
    CUSTOM = "custom"


class TaxTypeEnum(str, Enum):
    """Tax types for various tax codes"""
    GST = "gst"
    VAT = "vat"
    SERVICE_TAX = "service_tax"
    EXCISE = "excise"
    CUSTOMS = "customs"
    CESS = "cess"
    TDS = "tds"
    TCS = "tcs"


# Category Schemas
class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="Category name")
    code: Optional[str] = Field(None, max_length=50, description="Category code")
    category_type: CategoryTypeEnum = Field(CategoryTypeEnum.GENERAL, description="Category type")
    parent_category_id: Optional[int] = Field(None, description="Parent category ID for hierarchy")
    description: Optional[str] = Field(None, description="Category description")
    sort_order: int = Field(0, description="Sort order for display")
    default_income_account_id: Optional[int] = Field(None, description="Default income account")
    default_expense_account_id: Optional[int] = Field(None, description="Default expense account")
    default_asset_account_id: Optional[int] = Field(None, description="Default asset account")
    default_tax_code_id: Optional[int] = Field(None, description="Default tax code")


class CategoryCreate(CategoryBase):
    company_id: Optional[int] = Field(None, description="Company ID for multi-company support")


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    code: Optional[str] = Field(None, max_length=50)
    category_type: Optional[CategoryTypeEnum] = None
    parent_category_id: Optional[int] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None
    default_income_account_id: Optional[int] = None
    default_expense_account_id: Optional[int] = None
    default_asset_account_id: Optional[int] = None
    default_tax_code_id: Optional[int] = None


class CategoryResponse(CategoryBase):
    id: int
    organization_id: int
    company_id: Optional[int]
    level: int
    path: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    # Hierarchy information
    sub_categories: List["CategoryResponse"] = []
    
    class Config:
        from_attributes = True


class CategoryList(BaseModel):
    items: List[CategoryResponse]
    total: int
    page: int
    size: int
    pages: int


class CategoryFilter(BaseModel):
    category_type: Optional[CategoryTypeEnum] = None
    parent_category_id: Optional[int] = None
    is_active: Optional[bool] = None
    search: Optional[str] = None


# Unit Schemas
class UnitBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Unit name")
    symbol: str = Field(..., min_length=1, max_length=20, description="Unit symbol")
    unit_type: UnitTypeEnum = Field(UnitTypeEnum.QUANTITY, description="Unit type")
    description: Optional[str] = Field(None, description="Unit description")
    is_base_unit: bool = Field(False, description="Is this a base unit")
    base_unit_id: Optional[int] = Field(None, description="Base unit for conversion")
    conversion_factor: Decimal = Field(Decimal("1.000000"), description="Conversion factor to base unit")
    conversion_formula: Optional[str] = Field(None, max_length=500, description="Complex conversion formula")
    decimal_places: int = Field(2, ge=0, le=6, description="Decimal places for calculations")


class UnitCreate(UnitBase):
    company_id: Optional[int] = Field(None, description="Company ID for multi-company support")


class UnitUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    symbol: Optional[str] = Field(None, min_length=1, max_length=20)
    unit_type: Optional[UnitTypeEnum] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    is_base_unit: Optional[bool] = None
    base_unit_id: Optional[int] = None
    conversion_factor: Optional[Decimal] = None
    conversion_formula: Optional[str] = None
    decimal_places: Optional[int] = Field(None, ge=0, le=6)


class UnitResponse(UnitBase):
    id: int
    organization_id: int
    company_id: Optional[int]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    # Conversion information
    derived_units: List["UnitResponse"] = []
    
    class Config:
        from_attributes = True


class UnitList(BaseModel):
    items: List[UnitResponse]
    total: int
    page: int
    size: int
    pages: int


class UnitFilter(BaseModel):
    unit_type: Optional[UnitTypeEnum] = None
    is_base_unit: Optional[bool] = None
    is_active: Optional[bool] = None
    search: Optional[str] = None


class UnitConversion(BaseModel):
    from_unit_id: int
    to_unit_id: int
    value: Decimal
    converted_value: Optional[Decimal] = None
    
    class Config:
        from_attributes = True


# Tax Code Schemas
class TaxCodeBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="Tax code name")
    code: str = Field(..., min_length=1, max_length=50, description="Tax code")
    tax_type: TaxTypeEnum = Field(TaxTypeEnum.GST, description="Tax type")
    tax_rate: Decimal = Field(..., ge=0, le=100, description="Tax rate percentage")
    is_compound: bool = Field(False, description="Is compound tax")
    components: Optional[Dict[str, Any]] = Field(None, description="Tax components")
    tax_account_id: Optional[int] = Field(None, description="Tax account ID")
    effective_from: Optional[datetime] = Field(None, description="Effective from date")
    effective_to: Optional[datetime] = Field(None, description="Effective to date")
    description: Optional[str] = Field(None, description="Tax code description")
    hsn_sac_codes: Optional[List[str]] = Field(None, description="Applicable HSN/SAC codes")


class TaxCodeCreate(TaxCodeBase):
    company_id: Optional[int] = Field(None, description="Company ID for multi-company support")


class TaxCodeUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    code: Optional[str] = Field(None, min_length=1, max_length=50)
    tax_type: Optional[TaxTypeEnum] = None
    tax_rate: Optional[Decimal] = Field(None, ge=0, le=100)
    is_compound: Optional[bool] = None
    is_active: Optional[bool] = None
    components: Optional[Dict[str, Any]] = None
    tax_account_id: Optional[int] = None
    effective_from: Optional[datetime] = None
    effective_to: Optional[datetime] = None
    description: Optional[str] = None
    hsn_sac_codes: Optional[List[str]] = None


class TaxCodeResponse(TaxCodeBase):
    id: int
    organization_id: int
    company_id: Optional[int]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class TaxCodeList(BaseModel):
    items: List[TaxCodeResponse]
    total: int
    page: int
    size: int
    pages: int


class TaxCodeFilter(BaseModel):
    tax_type: Optional[TaxTypeEnum] = None
    is_active: Optional[bool] = None
    hsn_sac_code: Optional[str] = None
    search: Optional[str] = None


class TaxCalculation(BaseModel):
    amount: Decimal
    tax_code_id: int
    calculated_tax: Optional[Decimal] = None
    tax_breakdown: Optional[Dict[str, Decimal]] = None
    
    class Config:
        from_attributes = True


# Payment Terms Extended Schemas
class PaymentScheduleItem(BaseModel):
    days: int = Field(..., ge=0, description="Days from invoice date")
    percentage: Decimal = Field(..., ge=0, le=100, description="Percentage of total amount")


class PaymentTermsExtendedBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="Payment terms name")
    code: Optional[str] = Field(None, max_length=50, description="Payment terms code")
    payment_days: int = Field(..., ge=0, description="Payment days")
    is_default: bool = Field(False, description="Is default payment terms")
    early_payment_discount_days: Optional[int] = Field(None, ge=0, description="Early payment discount days")
    early_payment_discount_rate: Optional[Decimal] = Field(None, ge=0, le=100, description="Early payment discount rate")
    late_payment_penalty_days: Optional[int] = Field(None, ge=0, description="Late payment penalty days")
    late_payment_penalty_rate: Optional[Decimal] = Field(None, ge=0, le=100, description="Late payment penalty rate")
    payment_schedule: Optional[List[PaymentScheduleItem]] = Field(None, description="Payment schedule")
    credit_limit_amount: Optional[Decimal] = Field(None, ge=0, description="Credit limit amount")
    requires_approval: bool = Field(False, description="Requires approval")
    discount_account_id: Optional[int] = Field(None, description="Discount account ID")
    penalty_account_id: Optional[int] = Field(None, description="Penalty account ID")
    description: Optional[str] = Field(None, description="Payment terms description")
    terms_conditions: Optional[str] = Field(None, description="Terms and conditions")

    @validator('payment_schedule')
    def validate_payment_schedule(cls, v):
        if v:
            total_percentage = sum(item.percentage for item in v)
            if total_percentage != 100:
                raise ValueError("Payment schedule percentages must total 100%")
        return v


class PaymentTermsExtendedCreate(PaymentTermsExtendedBase):
    company_id: Optional[int] = Field(None, description="Company ID for multi-company support")


class PaymentTermsExtendedUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    code: Optional[str] = Field(None, max_length=50)
    payment_days: Optional[int] = Field(None, ge=0)
    is_default: Optional[bool] = None
    is_active: Optional[bool] = None
    early_payment_discount_days: Optional[int] = Field(None, ge=0)
    early_payment_discount_rate: Optional[Decimal] = Field(None, ge=0, le=100)
    late_payment_penalty_days: Optional[int] = Field(None, ge=0)
    late_payment_penalty_rate: Optional[Decimal] = Field(None, ge=0, le=100)
    payment_schedule: Optional[List[PaymentScheduleItem]] = None
    credit_limit_amount: Optional[Decimal] = Field(None, ge=0)
    requires_approval: Optional[bool] = None
    discount_account_id: Optional[int] = None
    penalty_account_id: Optional[int] = None
    description: Optional[str] = None
    terms_conditions: Optional[str] = None


class PaymentTermsExtendedResponse(PaymentTermsExtendedBase):
    id: int
    organization_id: int
    company_id: Optional[int]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class PaymentTermsExtendedList(BaseModel):
    items: List[PaymentTermsExtendedResponse]
    total: int
    page: int
    size: int
    pages: int


class PaymentTermsExtendedFilter(BaseModel):
    is_default: Optional[bool] = None
    is_active: Optional[bool] = None
    search: Optional[str] = None


# Bulk operations
class BulkCategoryUpdate(BaseModel):
    category_ids: List[int]
    updates: CategoryUpdate


class BulkUnitUpdate(BaseModel):
    unit_ids: List[int]
    updates: UnitUpdate


class BulkTaxCodeUpdate(BaseModel):
    tax_code_ids: List[int]
    updates: TaxCodeUpdate


class BulkPaymentTermsUpdate(BaseModel):
    payment_terms_ids: List[int]
    updates: PaymentTermsExtendedUpdate


# Master Data Dashboard
class MasterDataStats(BaseModel):
    total_categories: int = 0
    active_categories: int = 0
    total_units: int = 0
    active_units: int = 0
    total_tax_codes: int = 0
    active_tax_codes: int = 0
    total_payment_terms: int = 0
    active_payment_terms: int = 0
    
    class Config:
        from_attributes = True


# Update forward references
CategoryResponse.model_rebuild()
UnitResponse.model_rebuild()