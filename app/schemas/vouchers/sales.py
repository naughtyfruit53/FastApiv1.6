# app/schemas/vouchers/sales.py

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from typing import Dict, Any
from pydantic import field_validator, ConfigDict
from .base import *

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