# Revised: v1/app/models/vouchers.py

# revised fastapi_migration/app/models/vouchers.py

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean, UniqueConstraint, Index
from sqlalchemy.orm import relationship, declared_attr
from sqlalchemy.sql import func
from app.core.database import Base

class BaseVoucher(Base):
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Multi-tenant field - REQUIRED for all vouchers
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    voucher_number = Column(String, nullable=False, index=True)
    date = Column(DateTime(timezone=True), nullable=False)
    total_amount = Column(Float, nullable=False, default=0.0)
    cgst_amount = Column(Float, default=0.0)
    sgst_amount = Column(Float, default=0.0)
    igst_amount = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    status = Column(String, default="draft")  # draft, confirmed, cancelled
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    @declared_attr
    def created_by(cls):
        return Column(Integer, ForeignKey("users.id"))

    @declared_attr
    def created_by_user(cls):
        return relationship("User", foreign_keys=[cls.created_by])

class VoucherItemBase(Base):
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Float, nullable=False)
    unit = Column(String, nullable=False)
    unit_price = Column(Float, nullable=False)
    discount_percentage = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    taxable_amount = Column(Float, nullable=False)
    gst_rate = Column(Float, default=0.0)
    cgst_amount = Column(Float, default=0.0)
    sgst_amount = Column(Float, default=0.0)
    igst_amount = Column(Float, default=0.0)
    total_amount = Column(Float, nullable=False)
    
    @declared_attr
    def product(cls):
        return relationship("Product")

class SimpleVoucherItemBase(Base):
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Float, nullable=False)
    unit = Column(String, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    
    @declared_attr
    def product(cls):
        return relationship("Product")

# Purchase Order
class PurchaseOrder(BaseVoucher):
    __tablename__ = "purchase_orders"
    
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)
    delivery_date = Column(DateTime(timezone=True))
    payment_terms = Column(String)
    terms_conditions = Column(Text)
    
    vendor = relationship("Vendor")
    items = relationship("PurchaseOrderItem", back_populates="purchase_order", cascade="all, delete-orphan")
    
    __table_args__ = (
        # Unique voucher number per organization
        UniqueConstraint('organization_id', 'voucher_number', name='uq_po_org_voucher_number'),
        Index('idx_po_org_vendor', 'organization_id', 'vendor_id'),
        Index('idx_po_org_date', 'organization_id', 'date'),
        Index('idx_po_org_status', 'organization_id', 'status'),
    )

class PurchaseOrderItem(SimpleVoucherItemBase):
    __tablename__ = "purchase_order_items"
    
    purchase_order_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=False)
    delivered_quantity = Column(Float, default=0.0)
    pending_quantity = Column(Float, nullable=False)
    
    purchase_order = relationship("PurchaseOrder", back_populates="items")

# Goods Receipt Note (GRN) - Enhanced for auto-population from PO
class GoodsReceiptNote(BaseVoucher):
    __tablename__ = "goods_receipt_notes"
    
    purchase_order_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=False)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)
    grn_date = Column(DateTime(timezone=True), nullable=False)
    challan_number = Column(String)
    challan_date = Column(DateTime(timezone=True))
    transport_mode = Column(String)
    vehicle_number = Column(String)
    lr_rr_number = Column(String)
    inspection_status = Column(String, default="pending")  # pending, completed, rejected
    
    purchase_order = relationship("PurchaseOrder")
    vendor = relationship("Vendor")
    items = relationship("GoodsReceiptNoteItem", back_populates="grn", cascade="all, delete-orphan")
    
    __table_args__ = (
        # Unique voucher number per organization
        UniqueConstraint('organization_id', 'voucher_number', name='uq_grn_org_voucher_number'),
        Index('idx_grn_org_po', 'organization_id', 'purchase_order_id'),
        Index('idx_grn_org_vendor', 'organization_id', 'vendor_id'),
        Index('idx_grn_org_date', 'organization_id', 'grn_date'),
    )

class GoodsReceiptNoteItem(Base):
    __tablename__ = "goods_receipt_note_items"
    
    id = Column(Integer, primary_key=True, index=True)
    grn_id = Column(Integer, ForeignKey("goods_receipt_notes.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    po_item_id = Column(Integer, ForeignKey("purchase_order_items.id"))
    ordered_quantity = Column(Float, nullable=False)
    received_quantity = Column(Float, nullable=False)
    accepted_quantity = Column(Float, nullable=False)
    rejected_quantity = Column(Float, default=0.0)
    unit = Column(String, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_cost = Column(Float, nullable=False)
    remarks = Column(Text)
    # Quality control fields
    batch_number = Column(String)
    expiry_date = Column(DateTime(timezone=True))
    quality_status = Column(String, default="pending")  # pending, passed, failed
    
    grn = relationship("GoodsReceiptNote", back_populates="items")
    product = relationship("Product")
    po_item = relationship("PurchaseOrderItem")

# Purchase Voucher - Enhanced for auto-population from GRN
class PurchaseVoucher(BaseVoucher):
    __tablename__ = "purchase_vouchers"
    
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)
    purchase_order_id = Column(Integer, ForeignKey("purchase_orders.id"))
    grn_id = Column(Integer, ForeignKey("goods_receipt_notes.id"))  # Auto-populate from GRN
    invoice_number = Column(String)
    invoice_date = Column(DateTime(timezone=True))
    due_date = Column(DateTime(timezone=True))
    payment_terms = Column(String)
    transport_mode = Column(String)
    vehicle_number = Column(String)
    lr_rr_number = Column(String)
    e_way_bill_number = Column(String)
    
    vendor = relationship("Vendor")
    purchase_order = relationship("PurchaseOrder")
    grn = relationship("GoodsReceiptNote")
    items = relationship("PurchaseVoucherItem", back_populates="purchase_voucher", cascade="all, delete-orphan")
    
    __table_args__ = (
        # Unique voucher number per organization
        UniqueConstraint('organization_id', 'voucher_number', name='uq_pv_org_voucher_number'),
        Index('idx_pv_org_vendor', 'organization_id', 'vendor_id'),
        Index('idx_pv_org_po', 'organization_id', 'purchase_order_id'),
        Index('idx_pv_org_grn', 'organization_id', 'grn_id'),
        Index('idx_pv_org_date', 'organization_id', 'date'),
    )

class PurchaseVoucherItem(VoucherItemBase):
    __tablename__ = "purchase_voucher_items"
    
    purchase_voucher_id = Column(Integer, ForeignKey("purchase_vouchers.id"), nullable=False)
    grn_item_id = Column(Integer, ForeignKey("goods_receipt_note_items.id"))  # Link to GRN item
    
    purchase_voucher = relationship("PurchaseVoucher", back_populates="items")
    grn_item = relationship("GoodsReceiptNoteItem")

# Sales Order
class SalesOrder(BaseVoucher):
    __tablename__ = "sales_orders"
    
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    delivery_date = Column(DateTime(timezone=True))
    payment_terms = Column(String)
    terms_conditions = Column(Text)
    
    customer = relationship("Customer")
    items = relationship("SalesOrderItem", back_populates="sales_order", cascade="all, delete-orphan")
    
    __table_args__ = (
        # Unique voucher number per organization
        UniqueConstraint('organization_id', 'voucher_number', name='uq_so_org_voucher_number'),
        Index('idx_so_org_customer', 'organization_id', 'customer_id'),
        Index('idx_so_org_date', 'organization_id', 'date'),
        Index('idx_so_org_status', 'organization_id', 'status'),
    )

class SalesOrderItem(SimpleVoucherItemBase):
    __tablename__ = "sales_order_items"
    
    sales_order_id = Column(Integer, ForeignKey("sales_orders.id"), nullable=False)
    delivered_quantity = Column(Float, default=0.0)
    pending_quantity = Column(Float, nullable=False)
    
    sales_order = relationship("SalesOrder", back_populates="items")

# Sales Voucher - Enhanced for auto-population from delivery challan
class SalesVoucher(BaseVoucher):
    __tablename__ = "sales_vouchers"
    
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    sales_order_id = Column(Integer, ForeignKey("sales_orders.id"))
    delivery_challan_id = Column(Integer, ForeignKey("delivery_challans.id"))  # Auto-populate from challan
    invoice_date = Column(DateTime(timezone=True))
    due_date = Column(DateTime(timezone=True))
    payment_terms = Column(String)
    place_of_supply = Column(String)
    transport_mode = Column(String)
    vehicle_number = Column(String)
    lr_rr_number = Column(String)
    e_way_bill_number = Column(String)
    voucher_type = Column(String, nullable=False, default="sales", index=True)
    
    customer = relationship("Customer")
    sales_order = relationship("SalesOrder")
    delivery_challan = relationship("DeliveryChallan")
    items = relationship("SalesVoucherItem", back_populates="sales_voucher", cascade="all, delete-orphan")
    
    __table_args__ = (
        # Unique voucher number per organization
        UniqueConstraint('organization_id', 'voucher_number', name='uq_sv_org_voucher_number'),
        Index('idx_sv_org_customer', 'organization_id', 'customer_id'),
        Index('idx_sv_org_so', 'organization_id', 'sales_order_id'),
        Index('idx_sv_org_challan', 'organization_id', 'delivery_challan_id'),
        Index('idx_sv_org_date', 'organization_id', 'date'),
    )

class SalesVoucherItem(VoucherItemBase):
    __tablename__ = "sales_voucher_items"
    
    sales_voucher_id = Column(Integer, ForeignKey("sales_vouchers.id"), nullable=False)
    delivery_challan_item_id = Column(Integer, ForeignKey("delivery_challan_items.id"))  # Link to challan item
    hsn_code = Column(String)
    
    sales_voucher = relationship("SalesVoucher", back_populates="items")
    challan_item = relationship("DeliveryChallanItem")

# Delivery Challan - Enhanced for auto-population from SO
class DeliveryChallan(BaseVoucher):
    __tablename__ = "delivery_challans"
    
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    sales_order_id = Column(Integer, ForeignKey("sales_orders.id"))
    delivery_date = Column(DateTime(timezone=True))
    transport_mode = Column(String)
    vehicle_number = Column(String)
    lr_rr_number = Column(String)
    destination = Column(String)
    
    customer = relationship("Customer")
    sales_order = relationship("SalesOrder")
    items = relationship("DeliveryChallanItem", back_populates="delivery_challan", cascade="all, delete-orphan")
    
    __table_args__ = (
        # Unique voucher number per organization
        UniqueConstraint('organization_id', 'voucher_number', name='uq_dc_org_voucher_number'),
        Index('idx_dc_org_customer', 'organization_id', 'customer_id'),
        Index('idx_dc_org_so', 'organization_id', 'sales_order_id'),
        Index('idx_dc_org_date', 'organization_id', 'delivery_date'),
    )

class DeliveryChallanItem(SimpleVoucherItemBase):
    __tablename__ = "delivery_challan_items"
    
    delivery_challan_id = Column(Integer, ForeignKey("delivery_challans.id"), nullable=False)
    so_item_id = Column(Integer, ForeignKey("sales_order_items.id"))  # Link to SO item
    
    delivery_challan = relationship("DeliveryChallan", back_populates="items")
    so_item = relationship("SalesOrderItem")

# Proforma Invoice
class ProformaInvoice(BaseVoucher):
    __tablename__ = "proforma_invoices"
    
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    valid_until = Column(DateTime(timezone=True))
    payment_terms = Column(String)
    terms_conditions = Column(Text)
    
    customer = relationship("Customer")
    items = relationship("ProformaInvoiceItem", back_populates="proforma_invoice", cascade="all, delete-orphan")
    
    __table_args__ = (
        # Unique voucher number per organization
        UniqueConstraint('organization_id', 'voucher_number', name='uq_pi_org_voucher_number'),
        Index('idx_pi_org_customer', 'organization_id', 'customer_id'),
        Index('idx_pi_org_date', 'organization_id', 'date'),
    )

class ProformaInvoiceItem(VoucherItemBase):
    __tablename__ = "proforma_invoice_items"
    
    proforma_invoice_id = Column(Integer, ForeignKey("proforma_invoices.id"), nullable=False)
    proforma_invoice = relationship("ProformaInvoice", back_populates="items")

# Quotation
class Quotation(BaseVoucher):
    __tablename__ = "quotations"
    
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    valid_until = Column(DateTime(timezone=True))
    payment_terms = Column(String)
    terms_conditions = Column(Text)
    
    customer = relationship("Customer")
    items = relationship("QuotationItem", back_populates="quotation", cascade="all, delete-orphan")
    
    __table_args__ = (
        # Unique voucher number per organization
        UniqueConstraint('organization_id', 'voucher_number', name='uq_quotation_org_voucher_number'),
        Index('idx_quotation_org_customer', 'organization_id', 'customer_id'),
        Index('idx_quotation_org_date', 'organization_id', 'date'),
    )

class QuotationItem(SimpleVoucherItemBase):
    __tablename__ = "quotation_items"
    
    quotation_id = Column(Integer, ForeignKey("quotations.id"), nullable=False)
    quotation = relationship("Quotation", back_populates="items")

# Credit Note
class CreditNote(BaseVoucher):
    __tablename__ = "credit_notes"
    
    customer_id = Column(Integer, ForeignKey("customers.id"))
    vendor_id = Column(Integer, ForeignKey("vendors.id"))
    reference_voucher_type = Column(String)
    reference_voucher_id = Column(Integer)
    reason = Column(String, nullable=False)
    
    customer = relationship("Customer")
    vendor = relationship("Vendor")
    items = relationship("CreditNoteItem", back_populates="credit_note", cascade="all, delete-orphan")
    
    __table_args__ = (
        # Unique voucher number per organization
        UniqueConstraint('organization_id', 'voucher_number', name='uq_cn_org_voucher_number'),
        Index('idx_cn_org_customer', 'organization_id', 'customer_id'),
        Index('idx_cn_org_vendor', 'organization_id', 'vendor_id'),
        Index('idx_cn_org_date', 'organization_id', 'date'),
    )

class CreditNoteItem(SimpleVoucherItemBase):
    __tablename__ = "credit_note_items"
    
    credit_note_id = Column(Integer, ForeignKey("credit_notes.id"), nullable=False)
    credit_note = relationship("CreditNote", back_populates="items")

# Debit Note
class DebitNote(BaseVoucher):
    __tablename__ = "debit_notes"
    
    customer_id = Column(Integer, ForeignKey("customers.id"))
    vendor_id = Column(Integer, ForeignKey("vendors.id"))
    reference_voucher_type = Column(String)
    reference_voucher_id = Column(Integer)
    reason = Column(String, nullable=False)
    
    customer = relationship("Customer")
    vendor = relationship("Vendor")
    items = relationship("DebitNoteItem", back_populates="debit_note", cascade="all, delete-orphan")
    
    __table_args__ = (
        # Unique voucher number per organization
        UniqueConstraint('organization_id', 'voucher_number', name='uq_dn_org_voucher_number'),
        Index('idx_dn_org_customer', 'organization_id', 'customer_id'),
        Index('idx_dn_org_vendor', 'organization_id', 'vendor_id'),
        Index('idx_dn_org_date', 'organization_id', 'date'),
    )

class DebitNoteItem(SimpleVoucherItemBase):
    __tablename__ = "debit_note_items"
    
    debit_note_id = Column(Integer, ForeignKey("debit_notes.id"), nullable=False)
    debit_note = relationship("DebitNote", back_populates="items")

# Payment Voucher
class PaymentVoucher(BaseVoucher):
    __tablename__ = "payment_vouchers"
    
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)
    payment_method = Column(String)
    reference = Column(String)
    bank_account = Column(String)
    
    vendor = relationship("Vendor")
    
    __table_args__ = (
        UniqueConstraint('organization_id', 'voucher_number', name='uq_pv_payment_org_voucher_number'),
        Index('idx_pv_payment_org_vendor', 'organization_id', 'vendor_id'),
        Index('idx_pv_payment_org_date', 'organization_id', 'date'),
    )

# Receipt Voucher
class ReceiptVoucher(BaseVoucher):
    __tablename__ = "receipt_vouchers"
    
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    receipt_method = Column(String)
    reference = Column(String)
    bank_account = Column(String)
    
    customer = relationship("Customer")
    
    __table_args__ = (
        # Unique voucher number per organization
        UniqueConstraint('organization_id', 'voucher_number', name='uq_rv_org_voucher_number'),
        Index('idx_rv_org_customer', 'organization_id', 'customer_id'),
        Index('idx_rv_org_date', 'organization_id', 'date'),
    )

# Purchase Return (Rejection In)
class PurchaseReturn(BaseVoucher):
    __tablename__ = "purchase_returns"
    
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)
    reference_voucher_id = Column(Integer, ForeignKey("purchase_vouchers.id"))
    reason = Column(Text)
    
    vendor = relationship("Vendor")
    reference_voucher = relationship("PurchaseVoucher")
    items = relationship("PurchaseReturnItem", back_populates="purchase_return", cascade="all, delete-orphan")
    
    __table_args__ = (
        # Unique voucher number per organization
        UniqueConstraint('organization_id', 'voucher_number', name='uq_pr_org_voucher_number'),
        Index('idx_pr_org_vendor', 'organization_id', 'vendor_id'),
        Index('idx_pr_org_date', 'organization_id', 'date'),
    )

class PurchaseReturnItem(VoucherItemBase):
    __tablename__ = "purchase_return_items"
    
    purchase_return_id = Column(Integer, ForeignKey("purchase_returns.id"), nullable=False)
    purchase_return = relationship("PurchaseReturn", back_populates="items")

# Sales Return (Rejection Out)
class SalesReturn(BaseVoucher):
    __tablename__ = "sales_returns"
    
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    reference_voucher_id = Column(Integer, ForeignKey("sales_vouchers.id"))
    reason = Column(Text)
    
    customer = relationship("Customer")
    reference_voucher = relationship("SalesVoucher")
    items = relationship("SalesReturnItem", back_populates="sales_return", cascade="all, delete-orphan")
    
    __table_args__ = (
        # Unique voucher number per organization
        UniqueConstraint('organization_id', 'voucher_number', name='uq_sr_org_voucher_number'),
        Index('idx_sr_org_customer', 'organization_id', 'customer_id'),
        Index('idx_sr_org_date', 'organization_id', 'date'),
    )

class SalesReturnItem(VoucherItemBase):
    __tablename__ = "sales_return_items"
    
    sales_return_id = Column(Integer, ForeignKey("sales_returns.id"), nullable=False)
    sales_return = relationship("SalesReturn", back_populates="items")

# Contra Voucher
class ContraVoucher(BaseVoucher):
    __tablename__ = "contra_vouchers"
    
    from_account = Column(String, nullable=False)
    to_account = Column(String, nullable=False)
    
    __table_args__ = (
        UniqueConstraint('organization_id', 'voucher_number', name='uq_contra_org_voucher_number'),
        Index('idx_contra_org_from_account', 'organization_id', 'from_account'),
        Index('idx_contra_org_to_account', 'organization_id', 'to_account'),
        Index('idx_contra_org_date', 'organization_id', 'date'),
    )

# Journal Voucher
class JournalVoucher(BaseVoucher):
    __tablename__ = "journal_vouchers"
    
    entries = Column(Text, nullable=False)  # JSON string for entries
    
    __table_args__ = (
        UniqueConstraint('organization_id', 'voucher_number', name='uq_journal_org_voucher_number'),
        Index('idx_journal_org_date', 'organization_id', 'date'),
    )

# Inter Department Voucher
class InterDepartmentVoucher(BaseVoucher):
    __tablename__ = "inter_department_vouchers"
    
    from_department = Column(String, nullable=False)
    to_department = Column(String, nullable=False)
    
    items = relationship("InterDepartmentVoucherItem", back_populates="inter_department_voucher", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint('organization_id', 'voucher_number', name='uq_idv_org_voucher_number'),
        Index('idx_idv_org_from_dept', 'organization_id', 'from_department'),
        Index('idx_idv_org_to_dept', 'organization_id', 'to_department'),
        Index('idx_idv_org_date', 'organization_id', 'date'),
    )

class InterDepartmentVoucherItem(SimpleVoucherItemBase):
    __tablename__ = "inter_department_voucher_items"
    
    inter_department_voucher_id = Column(Integer, ForeignKey("inter_department_vouchers.id"), nullable=False)
    inter_department_voucher = relationship("InterDepartmentVoucher", back_populates="items")

# Bill of Materials (BOM) Models
class BillOfMaterials(Base):
    __tablename__ = "bill_of_materials"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Multi-tenant field - REQUIRED
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # BOM Details
    bom_name = Column(String, nullable=False)
    output_item_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    output_quantity = Column(Float, nullable=False, default=1.0)
    version = Column(String, default="1.0")
    validity_start = Column(DateTime(timezone=True))
    validity_end = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Description and notes
    description = Column(Text)
    notes = Column(Text)
    
    # Costing information
    material_cost = Column(Float, default=0.0)
    labor_cost = Column(Float, default=0.0)
    overhead_cost = Column(Float, default=0.0)
    total_cost = Column(Float, default=0.0)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    output_item = relationship("Product", foreign_keys=[output_item_id])
    components = relationship("BOMComponent", back_populates="bom", cascade="all, delete-orphan")
    created_by_user = relationship("User")
    
    __table_args__ = (
        UniqueConstraint('organization_id', 'bom_name', 'version', name='uq_bom_org_name_version'),
        Index('idx_bom_org_output', 'organization_id', 'output_item_id'),
        Index('idx_bom_org_active', 'organization_id', 'is_active'),
        Index('idx_bom_org_created', 'organization_id', 'created_at'),
    )

class BOMComponent(Base):
    __tablename__ = "bom_components"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Multi-tenant field - REQUIRED
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # BOM Reference
    bom_id = Column(Integer, ForeignKey("bill_of_materials.id"), nullable=False)
    
    # Component Details
    component_item_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity_required = Column(Float, nullable=False)
    unit = Column(String, nullable=False)
    
    # Costing
    unit_cost = Column(Float, default=0.0)
    total_cost = Column(Float, default=0.0)
    
    # Production details
    wastage_percentage = Column(Float, default=0.0)  # Expected wastage
    is_optional = Column(Boolean, default=False)  # Optional component
    sequence = Column(Integer, default=0)  # Order in production
    
    # Notes
    notes = Column(Text)
    
    # Relationships
    bom = relationship("BillOfMaterials", back_populates="components")
    component_item = relationship("Product", foreign_keys=[component_item_id])
    
    __table_args__ = (
        UniqueConstraint('bom_id', 'component_item_id', name='uq_bom_component_item'),
        Index('idx_bom_comp_org_bom', 'organization_id', 'bom_id'),
        Index('idx_bom_comp_org_item', 'organization_id', 'component_item_id'),
    )

# Manufacturing Voucher Models
class ManufacturingOrder(BaseVoucher):
    __tablename__ = "manufacturing_orders"
    
    # Production Details
    bom_id = Column(Integer, ForeignKey("bill_of_materials.id"), nullable=False)
    planned_quantity = Column(Float, nullable=False)
    produced_quantity = Column(Float, default=0.0)
    scrap_quantity = Column(Float, default=0.0)
    
    # Planning
    planned_start_date = Column(DateTime(timezone=True))
    planned_end_date = Column(DateTime(timezone=True))
    actual_start_date = Column(DateTime(timezone=True))
    actual_end_date = Column(DateTime(timezone=True))
    
    # Status
    production_status = Column(String, default="planned")  # planned, in_progress, completed, cancelled
    priority = Column(String, default="medium")  # low, medium, high, urgent
    
    # Department/Location
    production_department = Column(String)
    production_location = Column(String)
    
    # Relationships
    bom = relationship("BillOfMaterials")
    material_issues = relationship("MaterialIssue", back_populates="manufacturing_order", cascade="all, delete-orphan")
    production_entries = relationship("ProductionEntry", back_populates="manufacturing_order", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint('organization_id', 'voucher_number', name='uq_mo_org_voucher_number'),
        Index('idx_mo_org_bom', 'organization_id', 'bom_id'),
        Index('idx_mo_org_status', 'organization_id', 'production_status'),
        Index('idx_mo_org_date', 'organization_id', 'date'),
    )

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

class ProductionEntry(BaseVoucher):
    __tablename__ = "production_entries"
    
    # Reference to Manufacturing Order
    manufacturing_order_id = Column(Integer, ForeignKey("manufacturing_orders.id"), nullable=False)
    
    # Production Details
    shift = Column(String)
    operator = Column(String)
    machine_used = Column(String)
    
    # Quality
    good_quantity = Column(Float, default=0.0)
    rejected_quantity = Column(Float, default=0.0)
    rework_quantity = Column(Float, default=0.0)
    
    # Relationships
    manufacturing_order = relationship("ManufacturingOrder", back_populates="production_entries")
    items = relationship("ProductionEntryItem", back_populates="production_entry", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint('organization_id', 'voucher_number', name='uq_pe_org_voucher_number'),
        Index('idx_pe_org_mo', 'organization_id', 'manufacturing_order_id'),
        Index('idx_pe_org_date', 'organization_id', 'date'),
    )

class ProductionEntryItem(VoucherItemBase):
    __tablename__ = "production_entry_items"
    
    production_entry_id = Column(Integer, ForeignKey("production_entries.id"), nullable=False)
    production_entry = relationship("ProductionEntry", back_populates="items")

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