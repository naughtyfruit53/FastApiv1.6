# app/schemas/vouchers.py

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from typing import Dict, Any
from pydantic import field_validator

# Minimal Chart of Account schema for inclusion in voucher responses
class ChartOfAccountMinimal(BaseModel):
    id: int
    account_code: str
    account_name: str
    account_type: str
    
    class Config:
        from_attributes = True

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
    
    class Config:
        from_attributes = True

class ProductMinimal(BaseModel):
    product_name: str

    class Config:
        from_attributes = True

class VendorMinimal(BaseModel):
    id: int
    name: str
    state_code: Optional[str] = None
    gst_number: Optional[str] = None

    class Config:
        from_attributes = True

class PurchaseOrderMinimal(BaseModel):
    id: int
    voucher_number: str

    class Config:
        from_attributes = True

# Purchase Voucher
class PurchaseVoucherItemCreate(VoucherItemWithTax):
    pass

class PurchaseVoucherItemInDB(PurchaseVoucherItemCreate):
    id: int
    purchase_voucher_id: int
    product: Optional[ProductMinimal] = None

class PurchaseVoucherCreate(VoucherBase):
    vendor_id: int
    purchase_order_id: Optional[int] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    payment_terms: Optional[str] = None
    transport_mode: Optional[str] = None
    vehicle_number: Optional[str] = None
    lr_rr_number: Optional[str] = None
    e_way_bill_number: Optional[str] = None
    additional_charges: Optional[Dict[str, float]] = None
    items: List[PurchaseVoucherItemCreate] = []

class PurchaseVoucherUpdate(BaseModel):
    vendor_id: Optional[int] = None
    purchase_order_id: Optional[int] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    payment_terms: Optional[str] = None
    transport_mode: Optional[str] = None
    vehicle_number: Optional[str] = None
    lr_rr_number: Optional[str] = None
    e_way_bill_number: Optional[str] = None
    additional_charges: Optional[Dict[str, float]] = None
    total_amount: Optional[float] = None
    cgst_amount: Optional[float] = None
    sgst_amount: Optional[float] = None
    igst_amount: Optional[float] = None
    discount_amount: Optional[float] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    items: Optional[List[PurchaseVoucherItemCreate]] = None

class PurchaseVoucherInDB(VoucherInDBBase):
    vendor_id: int
    purchase_order_id: Optional[int]
    invoice_number: Optional[str]
    invoice_date: Optional[datetime]
    due_date: Optional[datetime]
    payment_terms: Optional[str]
    transport_mode: Optional[str]
    vehicle_number: Optional[str]
    lr_rr_number: Optional[str]
    e_way_bill_number: Optional[str]
    additional_charges: Optional[Dict[str, float]] = None
    items: List[PurchaseVoucherItemInDB]
    vendor: Optional[VendorMinimal] = None

# Sales Voucher
class SalesVoucherItemCreate(VoucherItemWithTax):
    hsn_code: Optional[str] = None

class SalesVoucherItemInDB(SalesVoucherItemCreate):
    id: int
    sales_voucher_id: int

class SalesVoucherCreate(VoucherBase):
    customer_id: int
    sales_order_id: Optional[int] = None
    delivery_challan_id: Optional[int] = None
    invoice_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    payment_terms: Optional[str] = None
    place_of_supply: Optional[str] = None
    transport_mode: Optional[str] = None
    vehicle_number: Optional[str] = None
    lr_rr_number: Optional[str] = None
    e_way_bill_number: Optional[str] = None
    additional_charges: Optional[Dict[str, float]] = None
    items: List[SalesVoucherItemCreate] = []

class SalesVoucherUpdate(BaseModel):
    customer_id: Optional[int] = None
    sales_order_id: Optional[int] = None
    delivery_challan_id: Optional[int] = None
    invoice_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    payment_terms: Optional[str] = None
    place_of_supply: Optional[str] = None
    transport_mode: Optional[str] = None
    vehicle_number: Optional[str] = None
    lr_rr_number: Optional[str] = None
    e_way_bill_number: Optional[str] = None
    additional_charges: Optional[Dict[str, float]] = None
    total_amount: Optional[float] = None
    cgst_amount: Optional[float] = None
    sgst_amount: Optional[float] = None
    igst_amount: Optional[float] = None
    discount_amount: Optional[float] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    items: Optional[List[SalesVoucherItemCreate]] = None

class SalesVoucherInDB(VoucherInDBBase):
    customer_id: int
    sales_order_id: Optional[int]
    delivery_challan_id: Optional[int]
    invoice_date: Optional[datetime]
    due_date: Optional[datetime]
    payment_terms: Optional[str]
    place_of_supply: Optional[str]
    transport_mode: Optional[str]
    vehicle_number: Optional[str]
    lr_rr_number: Optional[str]
    e_way_bill_number: Optional[str]
    additional_charges: Optional[Dict[str, float]] = None
    items: List[SalesVoucherItemInDB]

# Purchase Order
class PurchaseOrderItemCreate(VoucherItemWithTax):
    discount_amount: Optional[float] = 0.0
    description: Optional[str] = None

class PurchaseOrderItemInDB(VoucherItemWithTax):
    id: int
    purchase_order_id: int
    delivered_quantity: Optional[float] = 0.0
    pending_quantity: Optional[float] = None
    product: Optional[ProductMinimal] = None
    discount_amount: float = 0.0
    description: Optional[str] = None

    @field_validator('discount_amount', mode='before')
    @classmethod
    def default_discount(cls, v):
        return v if v is not None else 0.0

class PurchaseOrderCreate(VoucherBase):
    vendor_id: int
    delivery_date: Optional[datetime] = None
    payment_terms: Optional[str] = None
    terms_conditions: Optional[str] = None
    line_discount_type: Optional[str] = None
    total_discount_type: Optional[str] = None
    total_discount: Optional[float] = 0.0
    round_off: Optional[float] = 0.0
    additional_charges: Optional[Dict[str, float]] = None
    items: List[PurchaseOrderItemCreate] = []

class PurchaseOrderUpdate(BaseModel):
    vendor_id: Optional[int] = None
    delivery_date: Optional[datetime] = None
    payment_terms: Optional[str] = None
    terms_conditions: Optional[str] = None
    line_discount_type: Optional[str] = None
    total_discount_type: Optional[str] = None
    total_discount: Optional[float] = None
    round_off: Optional[float] = None
    additional_charges: Optional[Dict[str, float]] = None
    total_amount: Optional[float] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    items: Optional[List[PurchaseOrderItemCreate]] = None

class PurchaseOrderInDB(VoucherInDBBase):
    vendor_id: int
    delivery_date: Optional[datetime]
    payment_terms: Optional[str]
    terms_conditions: Optional[str]
    line_discount_type: Optional[str]
    total_discount_type: Optional[str]
    total_discount: float
    round_off: float = 0.0  # Added default to prevent validation errors on existing data
    additional_charges: Optional[Dict[str, float]] = None
    items: List[PurchaseOrderItemInDB]
    vendor: Optional[VendorMinimal] = None
    grn_status: Optional[str] = None  # GRN status: "pending", "partial", "complete"
    color_status: Optional[str] = None  # Color coding: "red", "yellow", "green"
    transporter_name: Optional[str] = None  # Tracking information
    tracking_number: Optional[str] = None
    tracking_link: Optional[str] = None

    @field_validator('round_off', mode='before')
    @classmethod
    def handle_none_round_off(cls, v):
        return 0.0 if v is None else v

class PurchaseOrderAutoPopulateResponse(BaseModel):
    vendor_id: int
    purchase_order_id: int
    delivery_date: Optional[datetime] = None
    payment_terms: Optional[str] = None
    terms_conditions: Optional[str] = None
    items: List[PurchaseVoucherItemCreate]

# Sales Order
class SalesOrderItemCreate(VoucherItemWithTax):
    description: Optional[str] = None

class SalesOrderItemInDB(SalesOrderItemCreate):
    id: int
    sales_order_id: int
    delivered_quantity: float = 0.0
    pending_quantity: float
    product: Optional[ProductMinimal] = None

class SalesOrderCreate(VoucherBase):
    customer_id: int
    delivery_date: Optional[datetime] = None
    payment_terms: Optional[str] = None
    terms_conditions: Optional[str] = None
    additional_charges: Optional[Dict[str, float]] = None
    items: List[SalesOrderItemCreate] = []

class SalesOrderUpdate(BaseModel):
    customer_id: Optional[int] = None
    delivery_date: Optional[datetime] = None
    payment_terms: Optional[str] = None
    terms_conditions: Optional[str] = None
    additional_charges: Optional[Dict[str, float]] = None
    total_amount: Optional[float] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    items: Optional[List[SalesOrderItemCreate]] = None

class SalesOrderInDB(VoucherInDBBase):
    customer_id: int
    delivery_date: Optional[datetime]
    payment_terms: Optional[str]
    terms_conditions: Optional[str]
    additional_charges: Optional[Dict[str, float]] = None
    items: List[SalesOrderItemInDB]

class SalesOrderAutoPopulateResponse(BaseModel):
    customer_id: int
    sales_order_id: int
    delivery_date: Optional[datetime] = None
    payment_terms: Optional[str] = None
    terms_conditions: Optional[str] = None
    place_of_supply: Optional[str] = None
    items: List[SalesVoucherItemCreate]

# GRN
class GRNItemCreate(BaseModel):
    product_id: int
    po_item_id: Optional[int] = None
    ordered_quantity: float
    received_quantity: float
    accepted_quantity: float
    rejected_quantity: float = 0.0
    unit: str
    unit_price: float
    total_cost: float
    remarks: Optional[str] = None

class GRNItemInDB(GRNItemCreate):
    id: int
    grn_id: int
    product: Optional[ProductMinimal] = None

class GRNCreate(VoucherBase):
    purchase_order_id: int
    vendor_id: int
    grn_date: datetime
    challan_number: Optional[str] = None
    challan_date: Optional[datetime] = None
    transport_mode: Optional[str] = None
    vehicle_number: Optional[str] = None
    lr_rr_number: Optional[str] = None
    additional_charges: Optional[Dict[str, float]] = None
    items: List[GRNItemCreate] = []

class GRNUpdate(BaseModel):
    purchase_order_id: Optional[int] = None
    vendor_id: Optional[int] = None
    grn_date: Optional[datetime] = None
    challan_number: Optional[str] = None
    challan_date: Optional[datetime] = None
    transport_mode: Optional[str] = None
    vehicle_number: Optional[str] = None
    lr_rr_number: Optional[str] = None
    additional_charges: Optional[Dict[str, float]] = None
    total_amount: Optional[float] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    items: Optional[List[GRNItemCreate]] = None

class GRNInDB(VoucherInDBBase):
    purchase_order_id: int
    vendor_id: int
    grn_date: datetime
    challan_number: Optional[str]
    challan_date: Optional[datetime]
    transport_mode: Optional[str]
    vehicle_number: Optional[str]
    lr_rr_number: Optional[str]
    additional_charges: Optional[Dict[str, float]] = None
    items: List[GRNItemInDB]
    vendor: Optional[VendorMinimal] = None
    purchase_order: Optional[PurchaseOrderMinimal] = None

class GRNAutoPopulateResponse(BaseModel):
    vendor_id: int
    purchase_order_id: int
    invoice_number: Optional[str] = None
    invoice_date: Optional[datetime] = None
    transport_mode: Optional[str] = None
    vehicle_number: Optional[str] = None
    lr_rr_number: Optional[str] = None
    items: List[PurchaseVoucherItemCreate]

# Delivery Challan
class DeliveryChallanItemCreate(BaseModel):
    product_id: int
    quantity: float
    unit: str
    description: Optional[str] = None

class DeliveryChallanItemInDB(DeliveryChallanItemCreate):
    id: int
    delivery_challan_id: int

class DeliveryChallanCreate(VoucherBase):
    customer_id: int
    sales_order_id: Optional[int] = None
    delivery_date: Optional[datetime] = None
    transport_mode: Optional[str] = None
    vehicle_number: Optional[str] = None
    lr_rr_number: Optional[str] = None
    destination: Optional[str] = None
    items: List[DeliveryChallanItemCreate] = []

class DeliveryChallanUpdate(BaseModel):
    customer_id: Optional[int] = None
    sales_order_id: Optional[int] = None
    delivery_date: Optional[datetime] = None
    transport_mode: Optional[str] = None
    vehicle_number: Optional[str] = None
    lr_rr_number: Optional[str] = None
    destination: Optional[str] = None
    total_amount: Optional[float] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    items: Optional[List[DeliveryChallanItemCreate]] = None

class DeliveryChallanInDB(VoucherInDBBase):
    customer_id: int
    sales_order_id: Optional[int]
    delivery_date: Optional[datetime]
    transport_mode: Optional[str]
    vehicle_number: Optional[str]
    lr_rr_number: Optional[str]
    destination: Optional[str]
    items: List[DeliveryChallanItemInDB]

class DeliveryChallanAutoPopulateResponse(BaseModel):
    customer_id: int
    sales_order_id: int
    delivery_date: Optional[datetime] = None
    transport_mode: Optional[str] = None
    vehicle_number: Optional[str] = None
    lr_rr_number: Optional[str] = None
    destination: Optional[str] = None
    items: List[SalesVoucherItemCreate]

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

# Purchase Return
class PurchaseReturnItemCreate(VoucherItemWithTax):
    pass

class PurchaseReturnItemInDB(PurchaseReturnItemCreate):
    id: int
    purchase_return_id: int

class PurchaseReturnCreate(VoucherBase):
    vendor_id: int
    reference_voucher_id: Optional[int] = None
    reason: Optional[str] = None
    additional_charges: Optional[Dict[str, float]] = None
    items: List[PurchaseReturnItemCreate] = []

class PurchaseReturnUpdate(BaseModel):
    vendor_id: Optional[int] = None
    reference_voucher_id: Optional[int] = None
    reason: Optional[str] = None
    additional_charges: Optional[Dict[str, float]] = None
    total_amount: Optional[float] = None
    cgst_amount: Optional[float] = None
    sgst_amount: Optional[float] = None
    igst_amount: Optional[float] = None
    discount_amount: Optional[float] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    items: Optional[List[PurchaseReturnItemCreate]] = None

class PurchaseReturnInDB(VoucherInDBBase):
    vendor_id: int
    reference_voucher_id: Optional[int]
    reason: Optional[str]
    additional_charges: Optional[Dict[str, float]] = None
    items: List[PurchaseReturnItemInDB]

# Sales Return
class SalesReturnItemCreate(VoucherItemWithTax):
    pass

class SalesReturnItemInDB(SalesReturnItemCreate):
    id: int
    sales_return_id: int

class SalesReturnCreate(VoucherBase):
    customer_id: int
    reference_voucher_id: Optional[int] = None
    reason: Optional[str] = None
    additional_charges: Optional[Dict[str, float]] = None
    items: List[SalesReturnItemCreate] = []

class SalesReturnUpdate(BaseModel):
    customer_id: Optional[int] = None
    reference_voucher_id: Optional[int] = None
    reason: Optional[str] = None
    additional_charges: Optional[Dict[str, float]] = None
    total_amount: Optional[float] = None
    cgst_amount: Optional[float] = None
    sgst_amount: Optional[float] = None
    igst_amount: Optional[float] = None
    discount_amount: Optional[float] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    items: Optional[List[SalesReturnItemCreate]] = None

class SalesReturnInDB(VoucherInDBBase):
    customer_id: int
    reference_voucher_id: Optional[int]
    reason: Optional[str]
    additional_charges: Optional[Dict[str, float]] = None
    items: List[SalesReturnItemInDB]

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
    
    class Config:
        from_attributes = True

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
    
    class Config:
        from_attributes = True

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
    error_type: str = "validation_error"  # validation_error, business_rule, data_type, data_type, etc.
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