# app/models/product_models.py
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON, Index, UniqueConstraint, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.core.database import Base
from typing import List, Optional
from datetime import datetime, date
from pydantic import BaseModel  # Add Pydantic import

# SQLAlchemy Models
class Product(Base):
    __tablename__ = "products"
  
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
  
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_product_organization_id"), nullable=False, index=True)
    company_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("companies.id", name="fk_product_company_id"), nullable=True, index=True)
  
    # Product details
    product_name: Mapped[str] = mapped_column("name", String, nullable=False, index=True)
    hsn_code: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    part_number: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    unit: Mapped[str] = mapped_column(String, nullable=False)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False)
    gst_rate: Mapped[float] = mapped_column(Float, default=0.0)
    is_gst_inclusive: Mapped[bool] = mapped_column(Boolean, default=False)
    reorder_level: Mapped[int] = mapped_column(Integer, default=0)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_manufactured: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
  
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
  
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="products")
    company: Mapped[Optional["Company"]] = relationship("Company", back_populates="products")
    files: Mapped[List["ProductFile"]] = relationship("ProductFile", back_populates="product", cascade="all, delete-orphan")
    
    # Enhanced inventory relationships
    tracking_config: Mapped[List["app.models.enhanced_inventory_models.ProductTracking"]] = relationship(
        "app.models.enhanced_inventory_models.ProductTracking",
        back_populates="product"
    )
    warehouse_stock: Mapped[List["app.models.enhanced_inventory_models.WarehouseStock"]] = relationship(
        "app.models.enhanced_inventory_models.WarehouseStock",
        back_populates="product"
    )
    stock_movements: Mapped[List["app.models.enhanced_inventory_models.StockMovement"]] = relationship(
        "app.models.enhanced_inventory_models.StockMovement",
        back_populates="product"
    )
  
    __table_args__ = (
        UniqueConstraint('organization_id', 'name', name='uq_product_org_name'),
        UniqueConstraint('organization_id', 'part_number', name='uq_product_org_part_number'),
        Index('idx_product_org_name', 'organization_id', 'name'),
        Index('idx_product_org_active', 'organization_id', 'is_active'),
        Index('idx_product_org_hsn', 'organization_id', 'hsn_code'),
    )

class ProductFile(Base):
    __tablename__ = "product_files"
  
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
  
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_product_file_organization_id"), nullable=False, index=True)
  
    # File details
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id", name="fk_product_file_product_id"), nullable=False)
    filename: Mapped[str] = mapped_column(String, nullable=False)
    original_filename: Mapped[str] = mapped_column(String, nullable=False)
    file_path: Mapped[str] = mapped_column(String, nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    content_type: Mapped[str] = mapped_column(String, nullable=False)
  
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
  
    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="files")
    organization: Mapped["Organization"] = relationship("Organization")
  
    __table_args__ = (
        Index('idx_product_file_org_product', 'organization_id', 'product_id'),
    )

class Stock(Base):
    __tablename__ = "stock"
  
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
  
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_stock_organization_id"), nullable=False, index=True)
  
    # Stock details
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id", name="fk_stock_product_id"), nullable=False)
    quantity: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    unit: Mapped[str] = mapped_column(String, nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    last_updated: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
  
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="stock_entries")
    product: Mapped["Product"] = relationship("Product", backref="stock_entries")
  
    __table_args__ = (
        UniqueConstraint('organization_id', 'product_id', 'location', name='uq_stock_org_product_location'),
        Index('idx_stock_org_product', 'organization_id', 'product_id'),
        Index('idx_stock_org_location', 'organization_id', 'location'),
    )

class InventoryTransaction(Base):
    __tablename__ = "inventory_transactions"
  
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
  
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_inventory_transaction_organization_id"), nullable=False, index=True)
  
    # Transaction details
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id", name="fk_inventory_transaction_product_id"), nullable=False)
    transaction_type: Mapped[str] = mapped_column(String, nullable=False)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String, nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String, nullable=True)
  
    # Reference information
    reference_type: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    reference_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    reference_number: Mapped[Optional[str]] = mapped_column(String, nullable=True)
  
    # Transaction metadata
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    unit_cost: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    total_cost: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
  
    # Stock levels after transaction
    stock_before: Mapped[float] = mapped_column(Float, nullable=False)
    stock_after: Mapped[float] = mapped_column(Float, nullable=False)
  
    # User tracking
    created_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_inventory_transaction_created_by_id"), nullable=True)
  
    # Metadata
    transaction_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
  
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    product: Mapped["Product"] = relationship("Product")
    created_by: Mapped[Optional["User"]] = relationship("User")
  
    __table_args__ = (
        Index('idx_inventory_transaction_org_product', 'organization_id', 'product_id'),
        Index('idx_inventory_transaction_org_type', 'organization_id', 'transaction_type'),
        Index('idx_inventory_transaction_org_date', 'organization_id', 'transaction_date'),
        Index('idx_inventory_transaction_reference', 'reference_type', 'reference_id'),
        Index('idx_inventory_transaction_created_at', 'created_at'),
    )

class JobParts(Base):
    __tablename__ = "job_parts"
  
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
  
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_job_parts_organization_id"), nullable=False, index=True)
  
    # Job and product references
    job_id: Mapped[int] = mapped_column(Integer, ForeignKey("installation_jobs.id", name="fk_job_parts_job_id"), nullable=False)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id", name="fk_job_parts_product_id"), nullable=False)
  
    # Quantity and usage details
    quantity_required: Mapped[float] = mapped_column(Float, nullable=False)
    quantity_used: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    unit: Mapped[str] = mapped_column(String, nullable=False)
  
    # Status tracking
    status: Mapped[str] = mapped_column(String, nullable=False, default="planned")
  
    # Usage details
    location_used: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
  
    # Cost tracking
    unit_cost: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    total_cost: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
  
    # User tracking
    allocated_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_job_parts_allocated_by_id"), nullable=True)
    used_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_job_parts_used_by_id"), nullable=True)
  
    # Metadata
    allocated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    used_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
  
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    job: Mapped["InstallationJob"] = relationship("InstallationJob", back_populates="parts_used")
    product: Mapped["Product"] = relationship("Product")
    allocated_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[allocated_by_id])
    used_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[used_by_id])
  
    __table_args__ = (
        UniqueConstraint('job_id', 'product_id', name='uq_job_parts_job_product'),
        Index('idx_job_parts_org_product', 'organization_id', 'product_id'),
        Index('idx_job_parts_org_status', 'organization_id', 'status'),
        Index('idx_job_parts_used_at', 'used_at'),
    )

class InventoryAlert(Base):
    __tablename__ = "inventory_alerts"
  
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
  
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_inventory_alert_organization_id"), nullable=False, index=True)
  
    # Alert details
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id", name="fk_inventory_alert_product_id"), nullable=False)
    alert_type: Mapped[str] = mapped_column(String, nullable=False)
    current_stock: Mapped[float] = mapped_column(Float, nullable=False)
    reorder_level: Mapped[float] = mapped_column(Float, nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String, nullable=True)
  
    # Alert status
    status: Mapped[str] = mapped_column(String, nullable=False, default="active")
    priority: Mapped[str] = mapped_column(String, nullable=False, default="medium")
  
    # Response tracking
    acknowledged_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_inventory_alert_acknowledged_by_id"), nullable=True)
    acknowledged_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
  
    # Additional details
    message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    suggested_order_quantity: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
  
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
  
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    product: Mapped["Product"] = relationship("Product")
    acknowledged_by: Mapped[Optional["User"]] = relationship("User")
  
    __table_args__ = (
        Index('idx_inventory_alert_org_product', 'organization_id', 'product_id'),
        Index('idx_inventory_alert_org_status', 'organization_id', 'status'),
        Index('idx_inventory_alert_org_priority', 'organization_id', 'priority'),
        Index('idx_inventory_alert_type', 'alert_type'),
        Index('idx_inventory_alert_created_at', 'created_at'),
    )

# Pydantic Schemas
class StockWithProduct(BaseModel):
    id: Optional[int] = None
    organization_id: Optional[int] = None
    product_id: Optional[int] = None
    quantity: float = 0.0
    unit: Optional[str] = None
    location: Optional[str] = None
    last_updated: Optional[datetime] = None  # Make optional to handle None values
    product_name: str
    product_hsn_code: Optional[str] = None
    product_part_number: Optional[str] = None
    unit_price: float
    reorder_level: int
    gst_rate: float
    is_active: bool
    total_value: float

    class Config:
        orm_mode = True