"""
Financial Modeling Models - DCF, WACC, Valuation, and Forecasting Models
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON, Index, UniqueConstraint, Date, Numeric, Enum
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, date
from decimal import Decimal
import enum
from typing import Optional, Dict, List

from .base import Base


class ValuationMethodType(enum.Enum):
    """Valuation method types"""
    DCF = "dcf"
    TRADING_COMPS = "trading_comps"
    TRANSACTION_COMPS = "transaction_comps"
    ASSET_BASED = "asset_based"
    REVENUE_MULTIPLE = "revenue_multiple"
    EBITDA_MULTIPLE = "ebitda_multiple"


class ScenarioType(enum.Enum):
    """Scenario analysis types"""
    BASE_CASE = "base_case"
    BEST_CASE = "best_case"
    WORST_CASE = "worst_case"
    CUSTOM = "custom"


class FinancialModel(Base):
    """Core financial model for DCF and valuation analysis"""
    __tablename__ = "financial_models"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Model identification
    model_name: Mapped[str] = mapped_column(String(200), nullable=False)
    model_type: Mapped[ValuationMethodType] = mapped_column(Enum(ValuationMethodType), nullable=False, index=True)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False, default="1.0")
    
    # Analysis period
    analysis_start_date: Mapped[date] = mapped_column(Date, nullable=False)
    analysis_end_date: Mapped[date] = mapped_column(Date, nullable=False)
    forecast_years: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    
    # Model data (JSON structure for flexibility)
    assumptions: Mapped[Dict] = mapped_column(JSON, nullable=False)  # Revenue growth, margins, etc.
    projections: Mapped[Dict] = mapped_column(JSON, nullable=False)  # Financial projections
    valuation_results: Mapped[Dict] = mapped_column(JSON, nullable=False)  # Valuation outputs
    
    # Status and metadata
    is_approved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_template: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    template_category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Audit trail
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    approved_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    created_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[created_by_id])
    approved_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[approved_by_id])
    scenarios: Mapped[List["ScenarioAnalysis"]] = relationship("ScenarioAnalysis", back_populates="financial_model")
    
    __table_args__ = (
        Index('idx_fin_model_org_type', 'organization_id', 'model_type'),
        Index('idx_fin_model_template', 'is_template', 'template_category'),
    )


class DCFModel(Base):
    """Discounted Cash Flow specific model"""
    __tablename__ = "dcf_models"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    financial_model_id: Mapped[int] = mapped_column(Integer, ForeignKey("financial_models.id"), nullable=False, index=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # WACC Components
    cost_of_equity: Mapped[Decimal] = mapped_column(Numeric(8, 4), nullable=False)  # %
    cost_of_debt: Mapped[Decimal] = mapped_column(Numeric(8, 4), nullable=False)  # %
    tax_rate: Mapped[Decimal] = mapped_column(Numeric(8, 4), nullable=False)  # %
    debt_to_equity_ratio: Mapped[Decimal] = mapped_column(Numeric(8, 4), nullable=False)
    wacc: Mapped[Decimal] = mapped_column(Numeric(8, 4), nullable=False)  # Calculated WACC
    
    # Terminal Value
    terminal_growth_rate: Mapped[Decimal] = mapped_column(Numeric(8, 4), nullable=False)  # %
    terminal_value_multiple: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 2), nullable=True)  # EV/EBITDA multiple
    terminal_value: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    
    # DCF Results
    pv_of_fcf: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)  # Present value of FCF
    pv_of_terminal_value: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    enterprise_value: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    equity_value: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    
    # Per share calculations
    shares_outstanding: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 0), nullable=True)
    value_per_share: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    
    # Cash Flow projections (JSON for yearly data)
    cash_flow_projections: Mapped[Dict] = mapped_column(JSON, nullable=False)
    
    # Metadata
    calculated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    financial_model: Mapped["FinancialModel"] = relationship("FinancialModel")
    organization: Mapped["Organization"] = relationship("Organization")
    
    __table_args__ = (
        Index('idx_dcf_model_org', 'organization_id'),
    )


class ScenarioAnalysis(Base):
    """Scenario analysis for sensitivity testing"""
    __tablename__ = "scenario_analysis"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    financial_model_id: Mapped[int] = mapped_column(Integer, ForeignKey("financial_models.id"), nullable=False, index=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Scenario identification
    scenario_name: Mapped[str] = mapped_column(String(200), nullable=False)
    scenario_type: Mapped[ScenarioType] = mapped_column(Enum(ScenarioType), nullable=False, index=True)
    scenario_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Scenario assumptions (what changes from base case)
    assumption_changes: Mapped[Dict] = mapped_column(JSON, nullable=False)
    
    # Results
    scenario_results: Mapped[Dict] = mapped_column(JSON, nullable=False)
    variance_from_base: Mapped[Dict] = mapped_column(JSON, nullable=True)  # % change from base case
    
    # Risk metrics
    probability: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)  # 0-100%
    risk_adjusted_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2), nullable=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    created_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    financial_model: Mapped["FinancialModel"] = relationship("FinancialModel", back_populates="scenarios")
    organization: Mapped["Organization"] = relationship("Organization")
    created_by: Mapped[Optional["User"]] = relationship("User")
    
    __table_args__ = (
        Index('idx_scenario_org_type', 'organization_id', 'scenario_type'),
    )


class TradingComparables(Base):
    """Trading comparables (public company multiples)"""
    __tablename__ = "trading_comparables"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Company information
    company_name: Mapped[str] = mapped_column(String(200), nullable=False)
    ticker_symbol: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, index=True)
    industry: Mapped[str] = mapped_column(String(100), nullable=False)
    market_cap: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2), nullable=True)
    
    # Financial metrics
    revenue_ttm: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2), nullable=True)  # Trailing twelve months
    ebitda_ttm: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2), nullable=True)
    net_income_ttm: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2), nullable=True)
    
    # Multiples
    ev_revenue_multiple: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 2), nullable=True)
    ev_ebitda_multiple: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 2), nullable=True)
    pe_ratio: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 2), nullable=True)
    
    # Additional metrics
    additional_metrics: Mapped[Optional[Dict]] = mapped_column(JSON, nullable=True)
    
    # Data source and date
    data_source: Mapped[str] = mapped_column(String(100), nullable=False, default="manual")
    as_of_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    created_by: Mapped[Optional["User"]] = relationship("User")
    
    __table_args__ = (
        Index('idx_trading_comps_industry', 'industry', 'is_active'),
        Index('idx_trading_comps_date', 'as_of_date'),
    )


class TransactionComparables(Base):
    """Transaction comparables (M&A multiples)"""
    __tablename__ = "transaction_comparables"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Transaction details
    target_company: Mapped[str] = mapped_column(String(200), nullable=False)
    acquirer_company: Mapped[str] = mapped_column(String(200), nullable=False)
    transaction_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    transaction_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2), nullable=True)
    
    # Company details
    industry: Mapped[str] = mapped_column(String(100), nullable=False)
    target_revenue: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2), nullable=True)
    target_ebitda: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2), nullable=True)
    
    # Transaction multiples
    ev_revenue_multiple: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 2), nullable=True)
    ev_ebitda_multiple: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 2), nullable=True)
    
    # Transaction characteristics
    transaction_type: Mapped[str] = mapped_column(String(50), nullable=False)  # acquisition, merger, etc.
    control_premium: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 2), nullable=True)  # %
    synergies_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2), nullable=True)
    
    # Additional details
    transaction_details: Mapped[Optional[Dict]] = mapped_column(JSON, nullable=True)
    
    # Data source
    data_source: Mapped[str] = mapped_column(String(100), nullable=False, default="manual")
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    created_by: Mapped[Optional["User"]] = relationship("User")
    
    __table_args__ = (
        Index('idx_transaction_comps_industry', 'industry', 'is_active'),
        Index('idx_transaction_comps_date', 'transaction_date'),
    )


class FinancialModelTemplate(Base):
    """Pre-built financial model templates"""
    __tablename__ = "financial_model_templates"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Template identification
    template_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    template_category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    industry: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Template structure
    model_type: Mapped[ValuationMethodType] = mapped_column(Enum(ValuationMethodType), nullable=False)
    default_assumptions: Mapped[Dict] = mapped_column(JSON, nullable=False)
    projection_structure: Mapped[Dict] = mapped_column(JSON, nullable=False)
    
    # Configuration
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)  # Available to all orgs
    complexity_level: Mapped[str] = mapped_column(String(20), default="intermediate", nullable=False)  # basic, intermediate, advanced
    
    # Usage tracking
    usage_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    created_by: Mapped[Optional["User"]] = relationship("User")
    
    __table_args__ = (
        Index('idx_template_category_industry', 'template_category', 'industry'),
        Index('idx_template_active_public', 'is_active', 'is_public'),
    )


class ModelAuditTrail(Base):
    """Audit trail for financial model changes"""
    __tablename__ = "model_audit_trail"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    financial_model_id: Mapped[int] = mapped_column(Integer, ForeignKey("financial_models.id"), nullable=False, index=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Change details
    action_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # create, update, approve, etc.
    field_changed: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    old_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    new_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Change reason
    change_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # User and timestamp
    changed_by_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    changed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # IP and session info
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    financial_model: Mapped["FinancialModel"] = relationship("FinancialModel")
    organization: Mapped["Organization"] = relationship("Organization")
    changed_by: Mapped["User"] = relationship("User")
    
    __table_args__ = (
        Index('idx_audit_model_date', 'financial_model_id', 'changed_at'),
        Index('idx_audit_action_date', 'action_type', 'changed_at'),
    )