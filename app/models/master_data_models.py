# app/models/master_data_models.py

"""
Master Data Models - Categories, Units, Payment Terms, and Tax Codes
These models provide foundational data structures for business operations
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON, Index, UniqueConstraint, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from decimal import Decimal
import enum

from .base import Base


class CategoryType(enum.Enum):
    """Category types for different business entities"""
    PRODUCT = "product"
    SERVICE = "service"
    EXPENSE = "expense"
    ASSET = "asset"
    GENERAL = "general"


class UnitType(enum.Enum):
    """Unit types for measurement"""
    QUANTITY = "quantity"  # Pieces, Numbers
    WEIGHT = "weight"      # Kg, Grams, Tonnes
    VOLUME = "volume"      # Liters, Cubic meters
    LENGTH = "length"      # Meters, Feet, Inches
    AREA = "area"         # Square meters, Square feet
    TIME = "time"         # Hours, Days, Minutes
    CUSTOM = "custom"     # Custom units


class TaxType(enum.Enum):
    """Tax types for various tax codes"""
    GST = "gst"
    VAT = "vat"
    SERVICE_TAX = "service_tax"
    EXCISE = "excise"
    CUSTOMS = "customs"
    CESS = "cess"
    TDS = "tds"
    TCS = "tcs"


class Category(Base):
    """Categories for products, services, and other business entities"""
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True, index=True)

    # Category identification
    name = Column(String(200), nullable=False, index=True)
    code = Column(String(50), nullable=True, index=True)
    category_type = Column(String(50), nullable=False, default="general", index=True)
    
    # Hierarchy support
    parent_category_id = Column(Integer, ForeignKey("categories.id"), nullable=True, index=True)
    level = Column(Integer, default=0, nullable=False)
    path = Column(String(500), nullable=True)  # Materialized path for hierarchy queries
    
    # Business logic
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    sort_order = Column(Integer, default=0, nullable=False)
    
    # Accounting integration
    default_income_account_id = Column(Integer, ForeignKey("chart_of_accounts.id"), nullable=True)
    default_expense_account_id = Column(Integer, ForeignKey("chart_of_accounts.id"), nullable=True)
    default_asset_account_id = Column(Integer, ForeignKey("chart_of_accounts.id"), nullable=True)
    default_tax_code_id = Column(Integer, ForeignKey("master_tax_codes.id"), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="categories")
    company = relationship("Company", back_populates="categories")
    parent_category = relationship("Category", remote_side=[id], back_populates="sub_categories")
    sub_categories = relationship("Category", back_populates="parent_category")
    default_income_account = relationship("ChartOfAccounts", foreign_keys=[default_income_account_id])
    default_expense_account = relationship("ChartOfAccounts", foreign_keys=[default_expense_account_id])
    default_asset_account = relationship("ChartOfAccounts", foreign_keys=[default_asset_account_id])
    default_tax_code = relationship("TaxCode", primaryjoin="Category.default_tax_code_id == TaxCode.id", back_populates="categories")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('organization_id', 'name', 'category_type', name='uq_category_org_name_name_type'),
        UniqueConstraint('organization_id', 'code', name='uq_category_org_code'),
        Index('idx_category_org_type_active', 'organization_id', 'category_type', 'is_active'),
        Index('idx_category_parent', 'parent_category_id'),
    )


class Unit(Base):
    """Units of measurement for products and services"""
    __tablename__ = "units"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True, index=True)

    # Unit identification
    name = Column(String(100), nullable=False, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    unit_type = Column(String(50), nullable=False, default="quantity", index=True)
    
    # Unit details
    description = Column(Text, nullable=True)
    is_base_unit = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Conversion factors (for unit conversion)
    base_unit_id = Column(Integer, ForeignKey("units.id"), nullable=True, index=True)
    conversion_factor = Column(Numeric(15, 6), default=1.000000, nullable=False)
    conversion_formula = Column(String(500), nullable=True)  # For complex conversions
    
    # Decimal places for calculations
    decimal_places = Column(Integer, default=2, nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="units")
    company = relationship("Company", back_populates="units")
    base_unit = relationship("Unit", remote_side=[id], back_populates="derived_units")
    derived_units = relationship("Unit", back_populates="base_unit")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('organization_id', 'name', name='uq_unit_org_name'),
        UniqueConstraint('organization_id', 'symbol', name='uq_unit_org_symbol'),
        Index('idx_unit_org_type_active', 'organization_id', 'unit_type', 'is_active'),
        Index('idx_unit_base', 'base_unit_id'),
    )


class TaxCode(Base):
    """Tax codes for various tax types and rates"""
    __tablename__ = "master_tax_codes"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True, index=True)

    # Tax code identification
    name = Column(String(200), nullable=False, index=True)
    code = Column(String(50), nullable=False, index=True)
    tax_type = Column(String(50), nullable=False, default="gst", index=True)
    
    # Tax configuration
    tax_rate = Column(Numeric(5, 2), nullable=False)  # Percentage rate
    is_compound = Column(Boolean, default=False, nullable=False)  # Compound tax calculation
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Tax components (for GST: CGST, SGST, IGST)
    components = Column(JSON, nullable=True)  # {"cgst": 9, "sgst": 9} or {"igst": 18}
    
    # Accounting integration
    tax_account_id = Column(Integer, ForeignKey("chart_of_accounts.id"), nullable=True)
    
    # Applicability
    effective_from = Column(DateTime, nullable=True)
    effective_to = Column(DateTime, nullable=True)
    description = Column(Text, nullable=True)
    
    # HSN/SAC codes for GST
    hsn_sac_codes = Column(JSON, nullable=True)  # Array of applicable HSN/SAC codes
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="tax_codes")
    company = relationship("Company", back_populates="tax_codes")
    tax_account = relationship("ChartOfAccounts", back_populates="tax_codes")
    categories = relationship("Category", back_populates="default_tax_code")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('organization_id', 'code', name='uq_tax_code_org_code'),
        Index('idx_tax_code_org_type_active', 'organization_id', 'tax_type', 'is_active'),
        Index('idx_tax_code_rate', 'tax_rate'),
    )


class PaymentTermsExtended(Base):
    """Extended Payment Terms with advanced business logic"""
    __tablename__ = "payment_terms_extended"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True, index=True)

    # Payment term identification
    name = Column(String(200), nullable=False, index=True)
    code = Column(String(50), nullable=True, index=True)
    
    # Payment configuration
    payment_days = Column(Integer, nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Advanced payment terms
    early_payment_discount_days = Column(Integer, nullable=True)
    early_payment_discount_rate = Column(Numeric(5, 2), nullable=True)  # Percentage
    late_payment_penalty_days = Column(Integer, nullable=True)
    late_payment_penalty_rate = Column(Numeric(5, 2), nullable=True)  # Percentage
    
    # Payment schedule (for installment payments)
    payment_schedule = Column(JSON, nullable=True)  # [{"days": 30, "percentage": 50}, {"days": 60, "percentage": 50}]
    
    # Credit configuration
    credit_limit_amount = Column(Numeric(15, 2), nullable=True)
    requires_approval = Column(Boolean, default=False, nullable=False)
    
    # Accounting integration
    discount_account_id = Column(Integer, ForeignKey("chart_of_accounts.id"), nullable=True)
    penalty_account_id = Column(Integer, ForeignKey("chart_of_accounts.id"), nullable=True)
    
    # Business rules
    description = Column(Text, nullable=True)
    terms_conditions = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="payment_terms_extended")
    company = relationship("Company", back_populates="payment_terms_extended")
    discount_account = relationship("ChartOfAccounts", foreign_keys=[discount_account_id])
    penalty_account = relationship("ChartOfAccounts", foreign_keys=[penalty_account_id])
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('organization_id', 'name', name='uq_payment_terms_ext_org_name'),
        UniqueConstraint('organization_id', 'code', name='uq_payment_terms_ext_org_code'),
        Index('idx_payment_terms_ext_org_active', 'organization_id', 'is_active'),
        Index('idx_payment_terms_ext_default', 'is_default'),
    )