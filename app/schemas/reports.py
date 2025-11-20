# app/schemas/reports.py

from pydantic import BaseModel
from datetime import date
from typing import Optional

class PendingPurchaseOrderSchema(BaseModel):
    id: int
    voucher_number: str
    date: date
    vendor_name: str
    vendor_id: Optional[int]
    total_amount: float
    status: str
    total_ordered_qty: float
    total_received_qty: float
    pending_qty: float
    grn_count: int
    has_tracking: bool
    transporter_name: Optional[str]
    tracking_number: Optional[str]
    tracking_link: Optional[str]
    color_status: str
    days_pending: int

    class Config:
        orm_mode = True