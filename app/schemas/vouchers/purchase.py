# app/schemas/vouchers/purchase.py

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import date, datetime
from pydantic import field_validator
from .base import VoucherItemWithTax, VoucherBase, VoucherInDBBase, ProductMinimal, VendorMinimal, PurchaseOrderMinimal

# Purchase Voucher
class PurchaseVoucherItemCreate(VoucherItemWithTax):
    pass

class PurchaseVoucherItemInDB(PurchaseVoucherItemCreate):
    id: int
    purchase_voucher_id: int
    product: Optional[ProductMinimal] = None
    model_config = ConfigDict(from_attributes=True)

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
    model_config = ConfigDict(from_attributes=True)

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
    name_1: Optional[str] = None  # Added to capture SQL alias products_1.name

    model_config = ConfigDict(from_attributes=True)

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
    date: Optional[datetime] = None  # Added to allow updating the main voucher date

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

    model_config = ConfigDict(from_attributes=True)

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
    model_config = ConfigDict(from_attributes=True)

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
    model_config = ConfigDict(from_attributes=True)

class GRNAutoPopulateResponse(BaseModel):
    vendor_id: int
    purchase_order_id: int
    invoice_number: Optional[str] = None
    invoice_date: Optional[datetime] = None
    transport_mode: Optional[str] = None
    vehicle_number: Optional[str] = None
    lr_rr_number: Optional[str] = None
    items: List[PurchaseVoucherItemCreate]

# Purchase Return
class PurchaseReturnItemCreate(VoucherItemWithTax):
    pass

class PurchaseReturnItemInDB(PurchaseReturnItemCreate):
    id: int
    purchase_return_id: int
    model_config = ConfigDict(from_attributes=True)

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
    model_config = ConfigDict(from_attributes=True)