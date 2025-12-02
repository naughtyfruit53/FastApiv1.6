# app/schemas/crm.py

from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from enum import Enum

# Enums
class LeadStatusEnum(str, Enum):
    new = "new"
    contacted = "contacted"
    qualified = "qualified"
    proposal = "proposal"
    negotiation = "negotiation"
    converted = "converted"
    lost = "lost"
    nurturing = "nurturing"

class LeadSourceEnum(str, Enum):
    website = "website"
    referral = "referral"
    email_campaign = "email_campaign"
    social_media = "social_media"
    cold_call = "cold_call"
    trade_show = "trade_show"
    partner = "partner"
    advertisement = "advertisement"
    other = "other"

class OpportunityStageEnum(str, Enum):
    prospecting = "prospecting"
    qualification = "qualification"
    proposal = "proposal"
    negotiation = "negotiation"
    closed_won = "closed_won"
    closed_lost = "closed_lost"

# Lead Schemas
class LeadBase(BaseModel):
    first_name: str = Field(..., description="Lead's first name")
    last_name: str = Field(..., description="Lead's last name")
    email: str = Field(..., description="Lead's email address")
    phone: Optional[str] = Field(None, description="Lead's phone number")
    company: Optional[str] = Field(None, description="Lead's company")
    job_title: Optional[str] = Field(None, description="Lead's job title")
    address1: Optional[str] = Field(None, description="Address line 1")
    address2: Optional[str] = Field(None, description="Address line 2")
    city: Optional[str] = Field(None, description="City")
    state: Optional[str] = Field(None, description="State")
    pin_code: Optional[str] = Field(None, description="PIN code")
    country: Optional[str] = Field(None, description="Country")
    status: LeadStatusEnum = Field(LeadStatusEnum.new, description="Lead status")
    source: LeadSourceEnum = Field(LeadSourceEnum.other, description="Lead source")
    description: Optional[str] = Field(None, description="Lead description")
    notes: Optional[str] = Field(None, description="Lead notes")
    score: int = Field(0, ge=0, le=100, description="Lead score (0-100)")
    is_qualified: bool = Field(False, description="Is lead qualified")
    qualification_notes: Optional[str] = Field(None, description="Qualification notes")
    estimated_value: Optional[float] = Field(None, ge=0, description="Estimated deal value")
    expected_close_date: Optional[date] = Field(None, description="Expected close date")
    assigned_to_id: Optional[int] = Field(None, description="Assigned user ID")
    custom_fields: Optional[Dict[str, Any]] = Field(None, description="Custom fields")
    owner: Optional[str] = Field(None, description="Lead owner")
    industry: Optional[str] = Field(None, description="Lead industry")

class LeadCreate(LeadBase):
    pass

class LeadUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = None
    address1: Optional[str] = None
    address2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pin_code: Optional[str] = None
    country: Optional[str] = None
    status: Optional[LeadStatusEnum] = None
    source: Optional[LeadSourceEnum] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    score: Optional[int] = Field(None, ge=0, le=100)
    is_qualified: Optional[bool] = None
    qualification_notes: Optional[str] = None
    estimated_value: Optional[float] = Field(None, ge=0)
    expected_close_date: Optional[date] = None
    assigned_to_id: Optional[int] = None
    custom_fields: Optional[Dict[str, Any]] = None
    owner: Optional[str] = None
    industry: Optional[str] = None

class LeadInDB(LeadBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    lead_number: str
    converted_to_customer_id: Optional[int] = None
    converted_to_opportunity_id: Optional[int] = None
    converted_at: Optional[datetime] = None
    created_by_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_contacted: Optional[datetime] = None

class Lead(LeadInDB):
    # Additional fields for display (populated from joins)
    assigned_to_name: Optional[str] = Field(None, description="Name of assigned user")
    created_by_name: Optional[str] = Field(None, description="Name of user who created lead")

    @field_validator('status', mode='before')
    @classmethod
    def validate_status(cls, v):
        from app.models.crm_models import LeadStatus
        if isinstance(v, LeadStatus):
            return v.name.lower()
        return v

    @field_validator('source', mode='before')
    @classmethod
    def validate_source(cls, v):
        from app.models.crm_models import LeadSource
        if isinstance(v, LeadSource):
            return v.name.lower()
        return v

# Lead Activity Schemas
class LeadActivityBase(BaseModel):
    activity_type: str = Field(..., description="Activity type (call, email, meeting, note, task)")
    subject: str = Field(..., description="Activity subject")
    description: Optional[str] = Field(None, description="Activity description")
    outcome: Optional[str] = Field(None, description="Activity outcome")
    activity_date: datetime = Field(..., description="Activity date and time")
    duration_minutes: Optional[int] = Field(None, ge=0, description="Activity duration in minutes")

class LeadActivityCreate(LeadActivityBase):
    lead_id: int = Field(..., description="Lead ID")

class LeadActivityUpdate(BaseModel):
    activity_type: Optional[str] = None
    subject: Optional[str] = None
    description: Optional[str] = None
    outcome: Optional[str] = None
    activity_date: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(None, ge=0)

class LeadActivityInDB(LeadActivityBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    lead_id: int
    created_by_id: Optional[int] = None
    created_at: datetime

class LeadActivity(LeadActivityInDB):
    pass

# Opportunity Schemas
class OpportunityBase(BaseModel):
    name: str = Field(..., description="Opportunity name")
    description: Optional[str] = Field(None, description="Opportunity description")
    stage: OpportunityStageEnum = Field(OpportunityStageEnum.prospecting, description="Opportunity stage")
    probability: float = Field(0.0, ge=0, le=100, description="Probability of closing (0-100%)")
    amount: float = Field(..., ge=0, description="Opportunity amount")
    expected_close_date: date = Field(..., description="Expected close date")
    customer_id: Optional[int] = Field(None, description="Customer ID")
    lead_id: Optional[int] = Field(None, description="Lead ID")
    assigned_to_id: Optional[int] = Field(None, description="Assigned user ID")
    competitors: Optional[str] = Field(None, description="Competitors")
    win_reason: Optional[str] = Field(None, description="Win reason")
    loss_reason: Optional[str] = Field(None, description="Loss reason")
    source: LeadSourceEnum = Field(LeadSourceEnum.other, description="Opportunity source")
    custom_fields: Optional[Dict[str, Any]] = Field(None, description="Custom fields")

class OpportunityCreate(OpportunityBase):
    pass

class OpportunityUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    stage: Optional[OpportunityStageEnum] = None
    probability: Optional[float] = Field(None, ge=0, le=100)
    amount: Optional[float] = Field(None, ge=0)
    expected_close_date: Optional[date] = None
    actual_close_date: Optional[date] = None
    customer_id: Optional[int] = None
    lead_id: Optional[int] = None
    assigned_to_id: Optional[int] = None
    competitors: Optional[str] = None
    win_reason: Optional[str] = None
    loss_reason: Optional[str] = None
    source: Optional[LeadSourceEnum] = None
    custom_fields: Optional[Dict[str, Any]] = None

class OpportunityInDB(OpportunityBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    opportunity_number: str
    expected_revenue: float
    actual_close_date: Optional[date] = None
    created_by_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

class Opportunity(OpportunityInDB):
    @field_validator('stage', mode='before')
    @classmethod
    def validate_stage(cls, v):
        from app.models.crm_models import OpportunityStage
        if isinstance(v, OpportunityStage):
            return v.name.lower()
        return v

    @field_validator('source', mode='before')
    @classmethod
    def validate_source(cls, v):
        from app.models.crm_models import LeadSource
        if isinstance(v, LeadSource):
            return v.name.lower()
        return v

# Opportunity Activity Schemas
class OpportunityActivityBase(BaseModel):
    activity_type: str = Field(..., description="Activity type (call, email, meeting, note, task)")
    subject: str = Field(..., description="Activity subject")
    description: Optional[str] = Field(None, description="Activity description")
    outcome: Optional[str] = Field(None, description="Activity outcome")
    activity_date: datetime = Field(..., description="Activity date and time")
    duration_minutes: Optional[int] = Field(None, ge=0, description="Activity duration in minutes")

class OpportunityActivityCreate(OpportunityActivityBase):
    opportunity_id: int = Field(..., description="Opportunity ID")

class OpportunityActivityUpdate(BaseModel):
    activity_type: Optional[str] = None
    subject: Optional[str] = None
    description: Optional[str] = None
    outcome: Optional[str] = None
    activity_date: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(None, ge=0)

class OpportunityActivityInDB(OpportunityActivityBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    opportunity_id: int
    created_by_id: Optional[int] = None
    created_at: datetime

class OpportunityActivity(OpportunityActivityInDB):
    pass

# Opportunity Product Schemas
class OpportunityProductBase(BaseModel):
    product_name: str = Field(..., description="Product name")
    product_description: Optional[str] = Field(None, description="Product description")
    quantity: float = Field(1.0, gt=0, description="Quantity")
    unit_price: float = Field(..., ge=0, description="Unit price")
    discount_percent: float = Field(0.0, ge=0, le=100, description="Discount percentage")
    discount_amount: float = Field(0.0, ge=0, description="Discount amount")
    product_id: Optional[int] = Field(None, description="Product ID from master")

class OpportunityProductCreate(OpportunityProductBase):
    opportunity_id: int = Field(..., description="Opportunity ID")

class OpportunityProductUpdate(BaseModel):
    product_name: Optional[str] = None
    product_description: Optional[str] = None
    quantity: Optional[float] = Field(None, gt=0)
    unit_price: Optional[float] = Field(None, ge=0)
    discount_percent: Optional[float] = Field(None, ge=0, le=100)
    discount_amount: Optional[float] = Field(None, ge=0)
    product_id: Optional[int] = None

class OpportunityProductInDB(OpportunityProductBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    opportunity_id: int
    total_amount: float
    final_amount: float
    created_at: datetime
    updated_at: Optional[datetime] = None

class OpportunityProduct(OpportunityProductInDB):
    pass

# Sales Pipeline Schemas
class SalesPipelineBase(BaseModel):
    name: str = Field(..., description="Pipeline name")
    description: Optional[str] = Field(None, description="Pipeline description")
    is_default: bool = Field(False, description="Is default pipeline")
    is_active: bool = Field(True, description="Is pipeline active")
    stages: Dict[str, Any] = Field(..., description="Stage configurations")

class SalesPipelineCreate(SalesPipelineBase):
    pass

class SalesPipelineUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_default: Optional[bool] = None
    is_active: Optional[bool] = None
    stages: Optional[Dict[str, Any]] = None

class SalesPipelineInDB(SalesPipelineBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    created_by_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

class SalesPipeline(SalesPipelineInDB):
    pass

# Sales Forecast Schemas
class SalesForecastBase(BaseModel):
    forecast_period: str = Field(..., description="Forecast period (monthly, quarterly, yearly)")
    period_start: date = Field(..., description="Period start date")
    period_end: date = Field(..., description="Period end date")
    predicted_revenue: float = Field(..., ge=0, description="Predicted revenue")
    weighted_revenue: float = Field(..., ge=0, description="Weighted revenue")
    committed_revenue: float = Field(..., ge=0, description="Committed revenue")
    best_case_revenue: float = Field(..., ge=0, description="Best case revenue")
    worst_case_revenue: float = Field(..., ge=0, description="Worst case revenue")
    total_opportunities: int = Field(..., ge=0, description="Total opportunities count")
    opportunities_by_stage: Dict[str, int] = Field(..., description="Opportunities by stage")
    model_version: str = Field(..., description="Forecast model version")
    confidence_score: float = Field(..., ge=0, le=100, description="Confidence score (0-100%)")

class SalesForecastCreate(SalesForecastBase):
    pass

class SalesForecastUpdate(BaseModel):
    predicted_revenue: Optional[float] = Field(None, ge=0)
    weighted_revenue: Optional[float] = Field(None, ge=0)
    committed_revenue: Optional[float] = Field(None, ge=0)
    best_case_revenue: Optional[float] = Field(None, ge=0)
    worst_case_revenue: Optional[float] = Field(None, ge=0)
    total_opportunities: Optional[int] = Field(None, ge=0)
    opportunities_by_stage: Optional[Dict[str, int]] = None
    confidence_score: Optional[float] = Field(None, ge=0, le=100)

class SalesForecastInDB(SalesForecastBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    created_by_id: Optional[int] = None
    created_at: datetime

class SalesForecast(SalesForecastInDB):
    pass

# Conversion Schemas
class LeadConversionRequest(BaseModel):
    convert_to_customer: bool = Field(True, description="Convert lead to customer")
    convert_to_opportunity: bool = Field(True, description="Convert lead to opportunity")
    customer_data: Optional[Dict[str, Any]] = Field(None, description="Customer data for conversion")
    opportunity_data: Optional[Dict[str, Any]] = Field(None, description="Opportunity data for conversion")

class LeadConversionResponse(BaseModel):
    success: bool
    customer_id: Optional[int] = None
    opportunity_id: Optional[int] = None
    message: str

# Analytics Schemas
class CRMAnalytics(BaseModel):
    leads_total: int
    leads_by_status: Dict[str, int]
    leads_by_source: Dict[str, int]
    opportunities_total: int
    opportunities_by_stage: Dict[str, int]
    pipeline_value: float
    weighted_pipeline_value: float
    conversion_rate: float
    average_deal_size: float
    sales_cycle_days: float
    win_rate: float
    period_start: date
    period_end: date

class CustomerAnalytics(BaseModel):
    total_customers: int
    new_customers: int
    customer_lifetime_value: float
    churn_rate: float
    repeat_customers: int
    customer_satisfaction_score: float
    period_start: date
    period_end: date


# Commission Schemas
class CommissionBase(BaseModel):
    sales_person_id: int = Field(..., description="ID of the sales person")
    sales_person_name: str = Field(..., min_length=1, description="Name of the sales person")
    person_type: str = Field(..., pattern="^(internal|external)$", description="Type: internal or external")
    opportunity_id: Optional[int] = Field(None, description="Related opportunity ID")
    lead_id: Optional[int] = Field(None, description="Related lead ID")
    commission_type: str = Field(..., pattern="^(percentage|fixed_amount|tiered|bonus)$", description="Commission type: percentage, fixed_amount, tiered, bonus")
    commission_rate: Optional[float] = Field(None, ge=0, le=100, description="Commission rate (for percentage type, 0-100)")
    commission_amount: Optional[float] = Field(None, ge=0, description="Commission amount (for fixed_amount, bonus types)")
    base_amount: float = Field(..., ge=0, description="Base amount for commission calculation")
    commission_date: date = Field(..., description="Date of commission")
    payment_status: str = Field("pending", pattern="^(pending|paid|approved|rejected|on_hold)$", description="Payment status: pending, paid, approved, rejected, on_hold")
    payment_date: Optional[date] = Field(None, description="Date of payment")
    notes: Optional[str] = Field(None, description="Additional notes")

class CommissionCreate(CommissionBase):
    pass

class CommissionUpdate(BaseModel):
    sales_person_name: Optional[str] = Field(None, min_length=1)
    person_type: Optional[str] = Field(None, pattern="^(internal|external)$")
    opportunity_id: Optional[int] = None
    lead_id: Optional[int] = None
    commission_type: Optional[str] = Field(None, pattern="^(percentage|fixed_amount|tiered|bonus)$")
    commission_rate: Optional[float] = Field(None, ge=0, le=100)
    commission_amount: Optional[float] = Field(None, ge=0)
    base_amount: Optional[float] = Field(None, ge=0)
    commission_date: Optional[date] = None
    payment_status: Optional[str] = Field(None, pattern="^(pending|paid|approved|rejected|on_hold)$")
    payment_date: Optional[date] = None
    notes: Optional[str] = None

class Commission(CommissionBase):
    id: int
    organization_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by_id: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)
    