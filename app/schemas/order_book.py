# app/schemas/order_book.py

from pydantic import BaseModel
from datetime import date, datetime
from typing import List, Optional

class OrderItemSchema(BaseModel):
    id: Optional[int] = None
    product_id: int
    quantity: float
    unit_price: float
    amount: float

class WorkflowHistorySchema(BaseModel):
    id: Optional[int] = None
    from_stage: Optional[str]
    to_stage: str
    changed_at: datetime
    changed_by_id: int
    notes: Optional[str]

class OrderSchema(BaseModel):
    id: Optional[int] = None
    order_number: str
    customer_id: int
    sales_order_id: Optional[int]
    order_date: date
    due_date: date
    status: str
    workflow_stage: str
    total_amount: float
    created_at: datetime
    updated_at: Optional[datetime]
    created_by_id: int
    items: List[OrderItemSchema] = []
    workflow_history: List[WorkflowHistorySchema] = []

    class Config:
        orm_mode = True

class OrderCreateSchema(BaseModel):
    customer_id: int
    order_date: date
    due_date: date
    total_amount: float
    items: List[OrderItemSchema]

class WorkflowUpdateSchema(BaseModel):
    workflow_stage: str
    notes: Optional[str] = None

class StatusUpdateSchema(BaseModel):
    status: str