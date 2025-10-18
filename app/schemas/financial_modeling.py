# app/schemas/financial_modeling.py
"""
Financial Modeling Schemas - Request/Response models for DCF, WACC, and valuation
"""

from pydantic import BaseModel, Field, validator, SkipValidation
from typing import Optional, Dict, List, Any
from datetime import datetime, date
from decimal import Decimal
from enum import Enum

from app.models.financial_modeling_models import ValuationMethodType, ScenarioType

# Base schemas
class FinancialModelBase(BaseModel):
    model_name: str = Field(..., description="Name of the financial model")
    model_type: ValuationMethodType = Field(..., description="Type of valuation method")
    model_version: str = Field(default="1.0", description="Model version")
    analysis_start_date: SkipValidation[date] = Field(..., description="Analysis period start date")
    analysis_end_date: SkipValidation[date] = Field(..., description="Analysis period end date")
    forecast_years: int = Field(default=5, ge=1, le=20, description="Number of forecast years")
    assumptions: Dict[str, Any] = Field(..., description="Model assumptions")
    template_category: Optional[str] = Field(None, description="Template category if creating from template")

class FinancialModelCreate(FinancialModelBase):
    pass

class FinancialModelUpdate(BaseModel):
    model_name: Optional[str] = None
    assumptions: Optional[Dict[str, Any]] = None
    projections: Optional[Dict[str, Any]] = None
    is_approved: Optional[bool] = None

class FinancialModelResponse(FinancialModelBase):
    id: int
    organization_id: int
    projections: Dict[str, Any]
    valuation_results: Dict[str, Any]
    is_approved: bool
    is_template: bool
    created_at: datetime
    updated_at: datetime
    created_by_id: Optional[int]
    approved_by_id: Optional[int]

    class Config:
        from_attributes = True

# DCF specific schemas
class DCFAssumptions(BaseModel):
    """DCF model assumptions"""
    base_revenue: Decimal = Field(..., description="Base year revenue")
    revenue_growth_rates: List[Decimal] = Field(..., description="Annual revenue growth rates")
    
    gross_margin: Decimal = Field(..., description="Gross margin %")
    operating_margin: Decimal = Field(..., description="Operating margin %")
    
    tax_rate: Decimal = Field(..., description="Corporate tax rate %")
    depreciation_rate: Decimal = Field(..., description="Depreciation as % of revenue")
    
    working_capital_change: Decimal = Field(default=Decimal('0'), description="Working capital change as % of revenue")
    
    capex_rate: Decimal = Field(..., description="Capital expenditure as % of revenue")
    
    risk_free_rate: Decimal = Field(..., description="Risk-free rate %")
    market_risk_premium: Decimal = Field(..., description="Market risk premium %")
    beta: Decimal = Field(..., description="Beta coefficient")
    debt_ratio: Decimal = Field(..., description="Debt to total capital ratio")
    cost_of_debt: Decimal = Field(..., description="Cost of debt %")
    
    terminal_growth_rate: Decimal = Field(..., description="Terminal growth rate %")
    
    @validator('revenue_growth_rates')
    def validate_growth_rates(cls, v):
        if len(v) == 0:
            raise ValueError("At least one revenue growth rate is required")
        return v

class DCFModelBase(BaseModel):
    cost_of_equity: Decimal = Field(..., description="Cost of equity %")
    cost_of_debt: Decimal = Field(..., description="Cost of debt %")
    tax_rate: Decimal = Field(..., description="Tax rate %")
    debt_to_equity_ratio: Decimal = Field(..., description="Debt to equity ratio")
    terminal_growth_rate: Decimal = Field(..., description="Terminal growth rate %")
    terminal_value_multiple: Optional[Decimal] = Field(None, description="Terminal value multiple (optional)")
    shares_outstanding: Optional[Decimal] = Field(None, description="Number of shares outstanding")

class DCFModelCreate(DCFModelBase):
    financial_model_id: int = Field(..., description="Associated financial model ID")

class DCFModelResponse(DCFModelBase):
    id: int
    financial_model_id: int
    organization_id: int
    wacc: Decimal
    terminal_value: Decimal
    pv_of_fcf: Decimal
    pv_of_terminal_value: Decimal
    enterprise_value: Decimal
    equity_value: Decimal
    value_per_share: Optional[Decimal]
    cash_flow_projections: Dict[str, Any]
    calculated_at: datetime

    class Config:
        from_attributes = True

# Scenario Analysis schemas
class ScenarioAssumptionChange(BaseModel):
    """Individual assumption change for scenario analysis"""
    assumption_name: str = Field(..., description="Name of the assumption being changed")
    base_value: Any = Field(..., description="Original value from base case")
    scenario_value: Any = Field(..., description="New value for this scenario")
    change_percentage: Optional[Decimal] = Field(None, description="Percentage change from base")

class ScenarioAnalysisBase(BaseModel):
    scenario_name: str = Field(..., description="Name of the scenario")
    scenario_type: ScenarioType = Field(..., description="Type of scenario")
    scenario_description: Optional[str] = Field(None, description="Description of the scenario")
    assumption_changes: Dict[str, Any] = Field(..., description="Changes from base case assumptions")
    probability: Optional[Decimal] = Field(None, ge=0, le=100, description="Probability of scenario occurring (0-100%)")

class ScenarioAnalysisCreate(ScenarioAnalysisBase):
    financial_model_id: int = Field(..., description="Associated financial model ID")

class ScenarioAnalysisResponse(ScenarioAnalysisBase):
    id: int
    financial_model_id: int
    organization_id: int
    scenario_results: Dict[str, Any]
    variance_from_base: Optional[Dict[str, Any]]
    risk_adjusted_value: Optional[Decimal]
    created_at: datetime
    created_by_id: Optional[int]

    class Config:
        from_attributes = True

# Trading Comparables schemas
class TradingComparablesBase(BaseModel):
    company_name: str = Field(..., description="Comparable company name")
    ticker_symbol: Optional[str] = Field(None, description="Stock ticker symbol")
    industry: str = Field(..., description="Industry classification")
    market_cap: Optional[Decimal] = Field(None, description="Market capitalization")
    revenue_ttm: Optional[Decimal] = Field(None, description="Trailing twelve months revenue")
    ebitda_ttm: Optional[Decimal] = Field(None, description="Trailing twelve months EBITDA")
    net_income_ttm: Optional[Decimal] = Field(None, description="Trailing twelve months net income")
    ev_revenue_multiple: Optional[Decimal] = Field(None, description="EV/Revenue multiple")
    ev_ebitda_multiple: Optional[Decimal] = Field(None, description="EV/EBITDA multiple")
    pe_ratio: Optional[Decimal] = Field(None, description="Price to earnings ratio")
    additional_metrics: Optional[Dict[str, Any]] = Field(None, description="Additional financial metrics")
    data_source: str = Field(default="manual", description="Source of the data")
    as_of_date: SkipValidation[date] = Field(..., description="Date of the financial data")

class TradingComparablesCreate(TradingComparablesBase):
    pass

class TradingComparablesUpdate(BaseModel):
    company_name: Optional[str] = None
    market_cap: Optional[Decimal] = None
    revenue_ttm: Optional[Decimal] = None
    ebitda_ttm: Optional[Decimal] = None
    net_income_ttm: Optional[Decimal] = None
    ev_revenue_multiple: Optional[Decimal] = None
    ev_ebitda_multiple: Optional[Decimal] = None
    pe_ratio: Optional[Decimal] = None
    additional_metrics: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class TradingComparablesResponse(TradingComparablesBase):
    id: int
    organization_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    created_by_id: Optional[int]

    class Config:
        from_attributes = True

# Transaction Comparables schemas
class TransactionComparablesBase(BaseModel):
    target_company: str = Field(..., description="Target company name")
    acquirer_company: str = Field(..., description="Acquiring company name")
    transaction_date: SkipValidation[date] = Field(..., description="Transaction completion date")
    transaction_value: Optional[Decimal] = Field(None, description="Transaction value")
    industry: str = Field(..., description="Target company industry")
    target_revenue: Optional[Decimal] = Field(None, description="Target company revenue")
    target_ebitda: Optional[Decimal] = Field(None, description="Target company EBITDA")
    ev_revenue_multiple: Optional[Decimal] = Field(None, description="EV/Revenue multiple")
    ev_ebitda_multiple: Optional[Decimal] = Field(None, description="EV/EBITDA multiple")
    transaction_type: str = Field(..., description="Type of transaction (acquisition, merger, etc.)")
    control_premium: Optional[Decimal] = Field(None, description="Control premium %")
    synergies_value: Optional[Decimal] = Field(None, description="Expected synergies value")
    transaction_details: Optional[Dict[str, Any]] = Field(None, description="Additional transaction details")
    data_source: str = Field(default="manual", description="Source of the data")

class TransactionComparablesCreate(TransactionComparablesBase):
    pass

class TransactionComparablesUpdate(BaseModel):
    transaction_value: Optional[Decimal] = None
    target_revenue: Optional[Decimal] = None
    target_ebitda: Optional[Decimal] = None
    ev_revenue_multiple: Optional[Decimal] = None
    ev_ebitda_multiple: Optional[Decimal] = None
    control_premium: Optional[Decimal] = None
    synergies_value: Optional[Decimal] = None
    transaction_details: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class TransactionComparablesResponse(TransactionComparablesBase):
    id: int
    organization_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    created_by_id: Optional[int]

    class Config:
        from_attributes = True

# Template schemas
class FinancialModelTemplateBase(BaseModel):
    template_name: str = Field(..., description="Template name")
    template_category: str = Field(..., description="Template category")
    industry: Optional[str] = Field(None, description="Industry focus")
    description: Optional[str] = Field(None, description="Template description")
    model_type: ValuationMethodType = Field(..., description="Type of valuation model")
    default_assumptions: Dict[str, Any] = Field(..., description="Default assumptions for the template")
    projection_structure: Dict[str, Any] = Field(..., description="Structure of financial projections")
    complexity_level: str = Field(default="intermediate", description="Complexity level (basic, intermediate, advanced)")
    is_public: bool = Field(default=True, description="Available to all organizations")

class FinancialModelTemplateCreate(FinancialModelTemplateBase):
    pass

class FinancialModelTemplateResponse(FinancialModelTemplateBase):
    id: int
    is_active: bool
    usage_count: int
    created_at: datetime
    updated_at: datetime
    created_by_id: Optional[int]

    class Config:
        from_attributes = True

# Valuation summary schemas
class ValuationSummary(BaseModel):
    """Summary of all valuation methods for a company"""
    dcf_valuation: Optional[Decimal] = Field(None, description="DCF valuation result")
    dcf_value_per_share: Optional[Decimal] = Field(None, description="DCF value per share")
    
    trading_comps_valuation: Optional[Dict[str, Decimal]] = Field(None, description="Trading comparables valuation")
    transaction_comps_valuation: Optional[Dict[str, Decimal]] = Field(None, description="Transaction comparables valuation")
    
    valuation_range_low: Optional[Decimal] = Field(None, description="Low end of valuation range")
    valuation_range_high: Optional[Decimal] = Field(None, description="High end of valuation range")
    weighted_average_valuation: Optional[Decimal] = Field(None, description="Weighted average of all methods")
    
    method_weights: Optional[Dict[str, Decimal]] = Field(None, description="Weights assigned to each method")
    
    analysis_date: SkipValidation[date] = Field(..., description="Date of the valuation analysis")

class ComprehensiveValuationRequest(BaseModel):
    """Request for comprehensive valuation using multiple methods"""
    company_name: str = Field(..., description="Company being valued")
    
    dcf_assumptions: Optional[DCFAssumptions] = Field(None, description="DCF model assumptions")
    
    industry_filter: Optional[str] = Field(None, description="Industry filter for comparables")
    size_range: Optional[Dict[str, Decimal]] = Field(None, description="Size range for comparables selection")
    
    dcf_weight: Decimal = Field(default=Decimal('0.4'), description="Weight for DCF method")
    trading_comps_weight: Decimal = Field(default=Decimal('0.3'), description="Weight for trading comparables")
    transaction_comps_weight: Decimal = Field(default=Decimal('0.3'), description="Weight for transaction comparables")
    
    @validator('dcf_weight', 'trading_comps_weight', 'transaction_comps_weight')
    def validate_weights(cls, v):
        if v < 0 or v > 1:
            raise ValueError("Weights must be between 0 and 1")
        return v

class RatioAnalysis(BaseModel):
    """Financial ratio analysis results"""
    current_ratio: Optional[Decimal] = Field(None, description="Current ratio")
    quick_ratio: Optional[Decimal] = Field(None, description="Quick ratio")
    cash_ratio: Optional[Decimal] = Field(None, description="Cash ratio")
    
    gross_margin: Optional[Decimal] = Field(None, description="Gross profit margin %")
    operating_margin: Optional[Decimal] = Field(None, description="Operating margin %")
    net_margin: Optional[Decimal] = Field(None, description="Net profit margin %")
    roa: Optional[Decimal] = Field(None, description="Return on assets %")
    roe: Optional[Decimal] = Field(None, description="Return on equity %")
    
    debt_to_equity: Optional[Decimal] = Field(None, description="Debt to equity ratio")
    debt_to_assets: Optional[Decimal] = Field(None, description="Debt to assets ratio")
    interest_coverage: Optional[Decimal] = Field(None, description="Interest coverage ratio")
    
    asset_turnover: Optional[Decimal] = Field(None, description="Asset turnover ratio")
    inventory_turnover: Optional[Decimal] = Field(None, description="Inventory turnover ratio")
    receivables_turnover: Optional[Decimal] = Field(None, description="Receivables turnover ratio")
    
    analysis_period: str = Field(..., description="Period of analysis")
    benchmark_comparison: Optional[Dict[str, Any]] = Field(None, description="Industry benchmark comparison")

# Audit trail schema
class ModelAuditTrailResponse(BaseModel):
    id: int
    financial_model_id: int
    action_type: str
    field_changed: Optional[str]
    old_value: Optional[str]
    new_value: Optional[str]
    change_reason: Optional[str]
    changed_by_id: int
    changed_at: datetime
    ip_address: Optional[str]

    class Config:
        from_attributes = True