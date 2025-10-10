# app/schemas/vouchers/financial.py

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from typing import Dict, Any
from pydantic import field_validator, ConfigDict
from .base import *

# Credit Note
class CreditNoteItemCreate(SimpleVoucherItem):
    pass

class CreditNoteItemInDB(CreditNoteItemCreate):
    id: int
    credit_note_id: int

class CreditNoteCreate(VoucherBase):
    customer_id: Optional[int] = None
    vendor_id: Optional[int] = None
    reference_voucher_type: Optional[str] = None
    reference_voucher_id: Optional[int] = None
    reason: str
    items: List[CreditNoteItemCreate] = []

class CreditNoteUpdate(BaseModel):
    customer_id: Optional[int] = None
    vendor_id: Optional[int] = None
    reference_voucher_type: Optional[str] = None
    reference_voucher_id: Optional[int] = None
    reason: Optional[str] = None
    total_amount: Optional[float] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    items: Optional[List[CreditNoteItemCreate]] = None

class CreditNoteInDB(VoucherInDBBase):
    customer_id: Optional[int]
    vendor_id: Optional[int]
    reference_voucher_type: Optional[str]
    reference_voucher_id: Optional[int]
    reason: str
    items: List[CreditNoteItemInDB]

# Debit Note
class DebitNoteItemCreate(SimpleVoucherItem):
    pass

class DebitNoteItemInDB(DebitNoteItemCreate):
    id: int
    debit_note_id: int

class DebitNoteCreate(VoucherBase):
    customer_id: Optional[int] = None
    vendor_id: Optional[int] = None
    reference_voucher_type: Optional[str] = None
    reference_voucher_id: Optional[int] = None
    reason: str
    items: List[DebitNoteItemCreate] = []

class DebitNoteUpdate(BaseModel):
    customer_id: Optional[int] = None
    vendor_id: Optional[int] = None
    reference_voucher_type: Optional[str] = None
    reference_voucher_id: Optional[int] = None
    reason: Optional[str] = None
    total_amount: Optional[float] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    items: Optional[List[DebitNoteItemCreate]] = None

class DebitNoteInDB(VoucherInDBBase):
    customer_id: Optional[int]
    vendor_id: Optional[int]
    reference_voucher_type: Optional[str]
    reference_voucher_id: Optional[int]
    reason: str
    items: List[DebitNoteItemInDB]

# Payment Voucher
class PaymentVoucherCreate(VoucherBase):
    entity_id: int
    entity_type: str = "Vendor"
    payment_method: Optional[str] = None
    reference: Optional[str] = None
    chart_account_id: int

class PaymentVoucherUpdate(BaseModel):
    entity_id: Optional[int] = None
    entity_type: Optional[str] = None
    payment_method: Optional[str] = None
    reference: Optional[str] = None
    total_amount: Optional[float] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    chart_account_id: Optional[int] = None

class PaymentVoucherInDB(VoucherInDBBase):
    entity_id: int
    entity_type: str
    payment_method: Optional[str]
    reference: Optional[str]
    chart_account_id: int
    entity: Optional[Dict[str, Any]] = None
    chart_account: Optional[ChartOfAccountMinimal] = None

# Receipt Voucher
class ReceiptVoucherCreate(VoucherBase):
    entity_id: int
    entity_type: str = "Customer"
    receipt_method: Optional[str] = None
    reference: Optional[str] = None
    chart_account_id: int

class ReceiptVoucherUpdate(BaseModel):
    entity_id: Optional[int] = None
    entity_type: Optional[str] = None
    receipt_method: Optional[str] = None
    reference: Optional[str] = None
    total_amount: Optional[float] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    chart_account_id: Optional[int] = None

class ReceiptVoucherInDB(VoucherInDBBase):
    entity_id: int
    entity_type: str
    receipt_method: Optional[str]
    reference: Optional[str]
    chart_account_id: int
    entity: Optional[Dict[str, Any]] = None
    chart_account: Optional[ChartOfAccountMinimal] = None

# Contra Voucher
class ContraVoucherCreate(VoucherBase):
    from_account: str
    to_account: str
    chart_account_id: int

class ContraVoucherUpdate(BaseModel):
    from_account: Optional[str] = None
    to_account: Optional[str] = None
    total_amount: Optional[float] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    chart_account_id: Optional[int] = None

class ContraVoucherInDB(VoucherInDBBase):
    from_account: str
    to_account: str
    chart_account_id: int
    chart_account: Optional[ChartOfAccountMinimal] = None

# Journal Voucher
class JournalVoucherCreate(VoucherBase):
    entries: str  # JSON string
    chart_account_id: int

class JournalVoucherUpdate(BaseModel):
    entries: Optional[str] = None
    total_amount: Optional[float] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    chart_account_id: Optional[int] = None
    notes: Optional[str] = None

class JournalVoucherInDB(VoucherInDBBase):
    entries: str
    chart_account_id: int
    chart_account: Optional[ChartOfAccountMinimal] = None

# Inter Department Voucher
class InterDepartmentVoucherItemCreate(SimpleVoucherItem):
    pass

class InterDepartmentVoucherItemInDB(InterDepartmentVoucherItemCreate):
    id: int
    inter_department_voucher_id: int

class InterDepartmentVoucherCreate(VoucherBase):
    from_department: str
    to_department: str
    items: List[InterDepartmentVoucherItemCreate] = []

class InterDepartmentVoucherUpdate(BaseModel):
    from_department: Optional[str] = None
    to_department: Optional[str] = None
    total_amount: Optional[float] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    items: Optional[List[InterDepartmentVoucherItemCreate]] = None

class InterDepartmentVoucherInDB(VoucherInDBBase):
    from_department: str
    to_department: str
    items: List[InterDepartmentVoucherItemInDB]