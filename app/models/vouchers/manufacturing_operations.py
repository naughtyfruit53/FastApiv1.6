# app/models/vouchers/manufacturing_operations.py

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func  # Added import for func
from app.core.database import Base
from .base import BaseVoucher, VoucherItemBase, SimpleVoucherItemBase

class MaterialIssue(BaseVoucher):
    __tablename__ = "material_issues"
    
    # Reference to Manufacturing Order (optional for non-production issues)
    manufacturing_order_id = Column(Integer, ForeignKey("manufacturing_orders.id"), nullable=True)
    
    # Issue Details
    issued_to_department = Column(String)
    issued_to_employee = Column(String)
    purpose = Column(String, default="production")
    destination = Column(String)  # Enhanced: destination tracking
    
    # Time tracking - Enhanced
    issue_time = Column(DateTime(timezone=True))
    expected_return_time = Column(DateTime(timezone=True))
    
    # Approval and tracking
    approved_by = Column(Integer, ForeignKey("users.id"))
    approval_date = Column(DateTime(timezone=True))
    
    # Relationships
    manufacturing_order = relationship("ManufacturingOrder", back_populates="material_issues")
    items = relationship("MaterialIssueItem", back_populates="material_issue", cascade="all, delete-orphan")
    approved_by_user = relationship("User", foreign_keys=[approved_by])
    
    __table_args__ = (
        UniqueConstraint('organization_id', 'voucher_number', name='uq_mi_org_voucher_number'),
        Index('idx_mi_org_mo', 'organization_id', 'manufacturing_order_id'),
        Index('idx_mi_org_date', 'organization_id', 'date'),
        Index('idx_mi_org_dept', 'organization_id', 'issued_to_department'),
    )

class MaterialIssueItem(VoucherItemBase):
    __tablename__ = "material_issue_items"
    
    material_issue_id = Column(Integer, ForeignKey("material_issues.id"), nullable=False)
    
    # Enhanced: Batch/Lot tracking
    batch_number = Column(String)
    lot_number = Column(String)
    expiry_date = Column(DateTime(timezone=True))
    
    # Enhanced: Warehouse tracking
    warehouse_location = Column(String)
    bin_location = Column(String)
    
    # Relationships
    material_issue = relationship("MaterialIssue", back_populates="items")

# Manufacturing Journal Voucher - NEW
class ManufacturingJournalVoucher(BaseVoucher):
    __tablename__ = "manufacturing_journal_vouchers"
    
    # Reference to Manufacturing Order
    manufacturing_order_id = Column(Integer, ForeignKey("manufacturing_orders.id"), nullable=False)
    bom_id = Column(Integer, ForeignKey("bill_of_materials.id"), nullable=False)
    
    # Manufacturing Details
    date_of_manufacture = Column(DateTime(timezone=True), nullable=False)
    shift = Column(String)
    operator = Column(String)
    supervisor = Column(String)
    machine_used = Column(String)
    
    # Production quantities
    finished_quantity = Column(Float, default=0.0)
    scrap_quantity = Column(Float, default=0.0)
    rework_quantity = Column(Float, default=0.0)
    byproduct_quantity = Column(Float, default=0.0)
    
    # Cost allocation
    material_cost = Column(Float, default=0.0)
    labor_cost = Column(Float, default=0.0)
    overhead_cost = Column(Float, default=0.0)
    total_manufacturing_cost = Column(Float, default=0.0)
    
    # Quality parameters
    quality_grade = Column(String)
    quality_remarks = Column(Text)
    
    # Narration and attachments
    narration = Column(Text)
    attachment_path = Column(String)  # File attachment path
    
    # Approval workflow
    approved_by = Column(Integer, ForeignKey("users.id"))
    approval_date = Column(DateTime(timezone=True))
    
    # Relationships
    manufacturing_order = relationship("ManufacturingOrder")
    bom = relationship("BillOfMaterials")
    approved_by_user = relationship("User", foreign_keys=[approved_by])
    finished_products = relationship("ManufacturingJournalFinishedProduct", back_populates="journal", cascade="all, delete-orphan")
    consumed_materials = relationship("ManufacturingJournalMaterial", back_populates="journal", cascade="all, delete-orphan")
    byproducts = relationship("ManufacturingJournalByproduct", back_populates="journal", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint('organization_id', 'voucher_number', name='uq_mjv_org_voucher_number'),
        Index('idx_mjv_org_mo', 'organization_id', 'manufacturing_order_id'),
        Index('idx_mjv_org_date', 'organization_id', 'date_of_manufacture'),
        Index('idx_mjv_org_bom', 'organization_id', 'bom_id'),
    )

class ManufacturingJournalFinishedProduct(Base):
    __tablename__ = "manufacturing_journal_finished_products"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    journal_id = Column(Integer, ForeignKey("manufacturing_journal_vouchers.id"), nullable=False)
    
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Float, nullable=False)
    unit = Column(String, nullable=False)
    unit_cost = Column(Float, default=0.0)
    total_cost = Column(Float, default=0.0)
    
    # Quality tracking
    quality_grade = Column(String)
    batch_number = Column(String)
    lot_number = Column(String)
    
    journal = relationship("ManufacturingJournalVoucher", back_populates="finished_products")
    product = relationship("Product")

class ManufacturingJournalMaterial(Base):
    __tablename__ = "manufacturing_journal_materials"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    journal_id = Column(Integer, ForeignKey("manufacturing_journal_vouchers.id"), nullable=False)
    
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)  # Raw material/component
    quantity_consumed = Column(Float, nullable=False)
    unit = Column(String, nullable=False)
    unit_cost = Column(Float, default=0.0)
    total_cost = Column(Float, default=0.0)
    
    # Tracking
    batch_number = Column(String)
    lot_number = Column(String)
    
    journal = relationship("ManufacturingJournalVoucher", back_populates="consumed_materials")
    product = relationship("Product")

class ManufacturingJournalByproduct(Base):
    __tablename__ = "manufacturing_journal_byproducts"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    journal_id = Column(Integer, ForeignKey("manufacturing_journal_vouchers.id"), nullable=False)
    
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)  # Byproduct
    quantity = Column(Float, nullable=False)
    unit = Column(String, nullable=False)
    unit_value = Column(Float, default=0.0)  # Recovery value
    total_value = Column(Float, default=0.0)
    
    # Tracking
    batch_number = Column(String)
    condition = Column(String)  # Good, Damaged, etc.
    
    journal = relationship("ManufacturingJournalVoucher", back_populates="byproducts")
    product = relationship("Product")

# Material Receipt Voucher - NEW
class MaterialReceiptVoucher(BaseVoucher):
    __tablename__ = "material_receipt_vouchers"
    
    # Source tracking
    manufacturing_order_id = Column(Integer, ForeignKey("manufacturing_orders.id"))
    source_type = Column(String, nullable=False)  # 'return', 'purchase', 'transfer'
    source_reference = Column(String)  # Reference to source document
    
    # Receipt details
    received_from_department = Column(String)
    received_from_employee = Column(String)
    received_by_employee = Column(String)
    receipt_time = Column(DateTime(timezone=True))
    
    # Inspection details
    inspection_required = Column(Boolean, default=False)
    inspection_status = Column(String, default="pending")  # pending, passed, failed, partial
    inspector_name = Column(String)
    inspection_date = Column(DateTime(timezone=True))
    inspection_remarks = Column(Text)
    
    # Physical condition
    condition_on_receipt = Column(String)  # Good, Damaged, Expired, etc.
    
    # Approval workflow
    approved_by = Column(Integer, ForeignKey("users.id"))
    approval_date = Column(DateTime(timezone=True))
    
    # Relationships
    manufacturing_order = relationship("ManufacturingOrder")
    approved_by_user = relationship("User", foreign_keys=[approved_by])
    items = relationship("MaterialReceiptItem", back_populates="receipt", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint('organization_id', 'voucher_number', name='uq_mrv_org_voucher_number'),
        Index('idx_mrv_org_mo', 'organization_id', 'manufacturing_order_id'),
        Index('idx_mrv_org_date', 'organization_id', 'date'),
        Index('idx_mrv_org_source', 'organization_id', 'source_type'),
    )

class MaterialReceiptItem(VoucherItemBase):
    __tablename__ = "material_receipt_items"
    
    receipt_id = Column(Integer, ForeignKey("material_receipt_vouchers.id"), nullable=False)
    
    # Enhanced tracking
    batch_number = Column(String)
    lot_number = Column(String)
    expiry_date = Column(DateTime(timezone=True))
    
    # Warehouse tracking
    warehouse_location = Column(String)
    bin_location = Column(String)
    
    # Quality tracking
    quality_status = Column(String)  # Accepted, Rejected, Hold
    inspection_remarks = Column(Text)
    
    # Condition tracking
    received_quantity = Column(Float)  # Actual received
    accepted_quantity = Column(Float)  # Accepted after inspection
    rejected_quantity = Column(Float)  # Rejected quantity
    
    receipt = relationship("MaterialReceiptVoucher", back_populates="items")

# Job Card/Job Work Voucher - NEW
class JobCardVoucher(BaseVoucher):
    __tablename__ = "job_card_vouchers"
    
    # Job details
    job_type = Column(String, nullable=False)  # 'outsourcing', 'subcontracting', 'processing'
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)
    manufacturing_order_id = Column(Integer, ForeignKey("manufacturing_orders.id"))
    
    # Job specifications
    job_description = Column(Text, nullable=False)
    job_category = Column(String)  # Machining, Assembly, Finishing, etc.
    expected_completion_date = Column(DateTime(timezone=True))
    actual_completion_date = Column(DateTime(timezone=True))
    
    # Material tracking
    materials_supplied_by = Column(String, default="company")  # 'company', 'vendor', 'mixed'
    
    # Delivery terms
    delivery_address = Column(Text)
    transport_mode = Column(String)
    
    # Job status
    job_status = Column(String, default="planned")  # planned, in_progress, completed, cancelled
    
    # Quality requirements
    quality_specifications = Column(Text)
    quality_check_required = Column(Boolean, default=True)
    
    # Approval workflow
    approved_by = Column(Integer, ForeignKey("users.id"))
    approval_date = Column(DateTime(timezone=True))
    
    # Relationships
    vendor = relationship("Vendor")
    manufacturing_order = relationship("ManufacturingOrder")
    approved_by_user = relationship("User", foreign_keys=[approved_by])
    supplied_materials = relationship("JobCardSuppliedMaterial", back_populates="job_card", cascade="all, delete-orphan")
    received_outputs = relationship("JobCardReceivedOutput", back_populates="job_card", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint('organization_id', 'voucher_number', name='uq_jcv_org_voucher_number'),
        Index('idx_jcv_org_vendor', 'organization_id', 'vendor_id'),
        Index('idx_jcv_org_mo', 'organization_id', 'manufacturing_order_id'),
        Index('idx_jcv_org_date', 'organization_id', 'date'),
        Index('idx_jcv_org_status', 'organization_id', 'job_status'),
    )

class JobCardSuppliedMaterial(Base):
    __tablename__ = "job_card_supplied_materials"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    job_card_id = Column(Integer, ForeignKey("job_card_vouchers.id"), nullable=False)
    
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity_supplied = Column(Float, nullable=False)
    unit = Column(String, nullable=False)
    unit_rate = Column(Float, default=0.0)
    total_value = Column(Float, default=0.0)
    
    # Tracking
    batch_number = Column(String)
    lot_number = Column(String)
    supply_date = Column(DateTime(timezone=True))
    
    job_card = relationship("JobCardVoucher", back_populates="supplied_materials")
    product = relationship("Product")

class JobCardReceivedOutput(Base):
    __tablename__ = "job_card_received_outputs"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    job_card_id = Column(Integer, ForeignKey("job_card_vouchers.id"), nullable=False)
    
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity_received = Column(Float, nullable=False)
    unit = Column(String, nullable=False)
    unit_rate = Column(Float, default=0.0)
    total_value = Column(Float, default=0.0)
    
    # Quality tracking
    quality_status = Column(String)  # Accepted, Rejected, Rework
    inspection_date = Column(DateTime(timezone=True))
    inspection_remarks = Column(Text)
    
    # Tracking
    batch_number = Column(String)
    receipt_date = Column(DateTime(timezone=True))
    
    job_card = relationship("JobCardVoucher", back_populates="received_outputs")
    product = relationship("Product")

# Stock Journal - NEW
class StockJournal(BaseVoucher):
    __tablename__ = "stock_journals"
    
    # Journal type
    journal_type = Column(String, nullable=False)  # 'transfer', 'assembly', 'disassembly', 'adjustment', 'manufacturing'
    
    # Location tracking
    from_location = Column(String)
    to_location = Column(String)
    from_warehouse = Column(String)
    to_warehouse = Column(String)
    
    # Manufacturing mode specific
    manufacturing_order_id = Column(Integer, ForeignKey("manufacturing_orders.id"))
    bom_id = Column(Integer, ForeignKey("bill_of_materials.id"))
    
    # Transfer details
    transfer_reason = Column(String)
    
    # Assembly/Disassembly details
    assembly_product_id = Column(Integer, ForeignKey("products.id"))  # For assembly/disassembly
    assembly_quantity = Column(Float)
    
    # Physical verification
    physical_verification_done = Column(Boolean, default=False)
    verified_by = Column(String)
    verification_date = Column(DateTime(timezone=True))
    
    # Approval workflow
    approved_by = Column(Integer, ForeignKey("users.id"))
    approval_date = Column(DateTime(timezone=True))
    
    # Relationships
    manufacturing_order = relationship("ManufacturingOrder")
    bom = relationship("BillOfMaterials")
    assembly_product = relationship("Product", foreign_keys=[assembly_product_id])
    approved_by_user = relationship("User", foreign_keys=[approved_by])
    entries = relationship("StockJournalEntry", back_populates="stock_journal", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint('organization_id', 'voucher_number', name='uq_sj_org_voucher_number'),
        Index('idx_sj_org_type', 'organization_id', 'journal_type'),
        Index('idx_sj_org_mo', 'organization_id', 'manufacturing_order_id'),
        Index('idx_sj_org_date', 'organization_id', 'date'),
        Index('idx_sj_org_from_loc', 'organization_id', 'from_location'),
        Index('idx_sj_org_to_loc', 'organization_id', 'to_location'),
    )

class StockJournalEntry(Base):
    __tablename__ = "stock_journal_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    stock_journal_id = Column(Integer, ForeignKey("stock_journals.id"), nullable=False)
    
    # Product details
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    # Quantity tracking
    debit_quantity = Column(Float, default=0.0)  # Quantity added/received
    credit_quantity = Column(Float, default=0.0)  # Quantity removed/issued
    unit = Column(String, nullable=False)
    
    # Value tracking
    unit_rate = Column(Float, default=0.0)
    debit_value = Column(Float, default=0.0)
    credit_value = Column(Float, default=0.0)
    
    # Location tracking
    from_location = Column(String)
    to_location = Column(String)
    from_warehouse = Column(String)
    to_warehouse = Column(String)
    from_bin = Column(String)
    to_bin = Column(String)
    
    # Batch/Lot tracking
    batch_number = Column(String)
    lot_number = Column(String)
    expiry_date = Column(DateTime(timezone=True))
    
    # Manufacturing specific
    transformation_type = Column(String)  # 'consume', 'produce', 'byproduct', 'scrap'
    
    stock_journal = relationship("StockJournal", back_populates="entries")
    product = relationship("Product")