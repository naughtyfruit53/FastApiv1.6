# app/models/order_book_models.py

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy.types import Date  # Added import for Date
from app.core.database import Base
from typing import List, Optional, Dict, Any
from datetime import datetime, date

class Order(Base):
    __tablename__ = "orders"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Order details
    order_number: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    customer_id: Mapped[int] = mapped_column(Integer, ForeignKey("customers.id"), nullable=False)
    sales_order_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("sales_orders.id"), nullable=True)  # Link to sales order
    order_date: Mapped[date] = mapped_column(Date, nullable=False, default=func.current_date())
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    
    # Status and workflow
    status: Mapped[str] = mapped_column(String, nullable=False, default="pending")
    workflow_stage: Mapped[str] = mapped_column(String, nullable=False, default="order_received")
    
    # Financial
    total_amount: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    created_by_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    organization = relationship("Organization")
    customer = relationship("Customer")
    sales_order = relationship("SalesOrder")
    created_by = relationship("User")
    items: Mapped[List["OrderItem"]] = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    workflow_history: Mapped[List["WorkflowHistory"]] = relationship("WorkflowHistory", back_populates="order", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint('organization_id', 'order_number', name='uq_order_org_number'),
        Index('idx_order_org_customer', 'organization_id', 'customer_id'),
        Index('idx_order_org_status', 'organization_id', 'status'),
        Index('idx_order_org_stage', 'organization_id', 'workflow_stage'),
        Index('idx_order_org_date', 'organization_id', 'order_date')
    )

class OrderItem(Base):
    __tablename__ = "order_items"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    order_id: Mapped[int] = mapped_column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"), nullable=False)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product")
    
    __table_args__ = (
        Index('idx_order_item_order', 'order_id'),
        Index('idx_order_item_product', 'product_id')
    )

class WorkflowHistory(Base):
    __tablename__ = "order_workflow_history"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    order_id: Mapped[int] = mapped_column(Integer, ForeignKey("orders.id"), nullable=False)
    from_stage: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    to_stage: Mapped[str] = mapped_column(String, nullable=False)
    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    changed_by_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    order = relationship("Order", back_populates="workflow_history")
    changed_by = relationship("User")
    
    __table_args__ = (
        Index('idx_workflow_history_order', 'order_id'),
        Index('idx_workflow_history_changed_at', 'changed_at')
    )