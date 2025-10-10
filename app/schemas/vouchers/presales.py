# app/schemas/vouchers/presales.py

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from typing import Dict, Any
from pydantic import field_validator, ConfigDict
from .base import *

# Proforma Invoice
class ProformaInvoiceItemCreate(VoucherItemWithTax):
    description: Optional[str] = None  # Added to align

class ProformaInvoiceItemInDB(ProformaInvoiceItemCreate):
    id: int
    proforma_invoice_id: int
    product: Optional[ProductMinimal] = None  # Added to align

class ProformaInvoiceCreate(VoucherBase):
    customer_id: int
    valid_until: Optional[datetime] = None
    payment_terms: Optional[str] = None
    terms_conditions: Optional[str] = None
    parent_id: Optional[int] = None  # For revisions
    revision_number: Optional[int] = 0
    additional_charges: Optional[Dict[str, float]] = None
    items: List[ProformaInvoiceItemCreate] = []

class ProformaInvoiceUpdate(BaseModel):
    customer_id: Optional[int] = None
    valid_until: Optional[datetime] = None
    payment_terms: Optional[str] = None
    terms_conditions: Optional[str] = None
    total_amount: Optional[float] = None
    cgst_amount: Optional[float] = None
    sgst_amount: Optional[float] = None
    igst_amount: Optional[float] = None
    discount_amount: Optional[float] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    parent_id: Optional[int] = None  # For revisions
    revision_number: Optional[int] = None
    additional_charges: Optional[Dict[str, float]] = None
    items: Optional[List[ProformaInvoiceItemCreate]] = None

class ProformaInvoiceInDB(VoucherInDBBase):
    customer_id: int
    valid_until: Optional[datetime]
    payment_terms: Optional[str]
    terms_conditions: Optional[str]
    parent_id: Optional[int]
    revision_number: Optional[int] = 0
    additional_charges: Optional[Dict[str, float]] = None
    items: List[ProformaInvoiceItemInDB]

# Quotation
class QuotationItemCreate(VoucherItemWithTax):
    description: Optional[str] = None

class QuotationItemInDB(QuotationItemCreate):
    id: int
    quotation_id: int
    product: Optional[ProductMinimal] = None

class QuotationCreate(VoucherBase):
    customer_id: int
    valid_until: Optional[datetime] = None
    payment_terms: Optional[str] = None
    terms_conditions: Optional[str] = None
    line_discount_type: Optional[str] = None
    total_discount_type: Optional[str] = None
    total_discount: Optional[float] = 0.0
    round_off: Optional[float] = 0.0
    parent_id: Optional[int] = None  # For revisions
    revision_number: Optional[int] = 0
    additional_charges: Optional[Dict[str, float]] = None
    items: List[QuotationItemCreate] = []

class QuotationUpdate(BaseModel):
    customer_id: Optional[int] = None
    valid_until: Optional[datetime] = None
    payment_terms: Optional[str] = None
    terms_conditions: Optional[str] = None
    line_discount_type: Optional[str] = None
    total_discount_type: Optional[str] = None
    total_discount: Optional[float] = None
    round_off: Optional[float] = None
    total_amount: Optional[float] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    parent_id: Optional[int] = None  # For revisions
    revision_number: Optional[int] = None
    additional_charges: Optional[Dict[str, float]] = None
    items: Optional[List[QuotationItemCreate]] = None

class QuotationInDB(VoucherInDBBase):
    customer_id: int
    valid_until: Optional[datetime]
    payment_terms: Optional[str]
    terms_conditions: Optional[str]
    line_discount_type: Optional[str]
    total_discount_type: Optional[str]
    total_discount: Optional[float] = 0.0
    round_off: Optional[float] = 0.0
    parent_id: Optional[int]
    revision_number: Optional[int] = 0
    additional_charges: Optional[Dict[str, float]] = None
    items: List[QuotationItemInDB]