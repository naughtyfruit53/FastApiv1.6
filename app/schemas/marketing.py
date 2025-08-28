# app/schemas/marketing.py

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from enum import Enum

# Enums
class CampaignTypeEnum(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    SOCIAL_MEDIA = "social_media"
    DIGITAL_ADS = "digital_ads"
    PRINT = "print"
    EVENT = "event"
    WEBINAR = "webinar"
    CONTENT_MARKETING = "content_marketing"
    REFERRAL = "referral"
    OTHER = "other"

class CampaignStatusEnum(str, Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class PromotionTypeEnum(str, Enum):
    PERCENTAGE_DISCOUNT = "percentage_discount"
    FIXED_AMOUNT_DISCOUNT = "fixed_amount_discount"
    BUY_X_GET_Y = "buy_x_get_y"
    FREE_SHIPPING = "free_shipping"
    BUNDLE_OFFER = "bundle_offer"
    CASHBACK = "cashback"
    LOYALTY_POINTS = "loyalty_points"

# Campaign Schemas
class CampaignBase(BaseModel):
    name: str = Field(..., description="Campaign name")
    description: Optional[str] = Field(None, description="Campaign description")
    campaign_type: CampaignTypeEnum = Field(..., description="Campaign type")
    status: CampaignStatusEnum = Field(CampaignStatusEnum.DRAFT, description="Campaign status")
    start_date: date = Field(..., description="Campaign start date")
    end_date: Optional[date] = Field(None, description="Campaign end date")
    scheduled_send_time: Optional[datetime] = Field(None, description="Scheduled send time")
    budget: Optional[float] = Field(None, ge=0, description="Campaign budget")
    target_audience_size: Optional[int] = Field(None, ge=0, description="Target audience size")
    objective: Optional[str] = Field(None, description="Campaign objective")
    subject_line: Optional[str] = Field(None, description="Email subject line")
    content: Optional[str] = Field(None, description="Campaign content")
    creative_assets: Optional[Dict[str, Any]] = Field(None, description="Creative assets")
    target_criteria: Optional[Dict[str, Any]] = Field(None, description="Target criteria")
    assigned_to_id: Optional[int] = Field(None, description="Assigned user ID")
    integration_settings: Optional[Dict[str, Any]] = Field(None, description="Integration settings")

class CampaignCreate(CampaignBase):
    pass

class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    campaign_type: Optional[CampaignTypeEnum] = None
    status: Optional[CampaignStatusEnum] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    scheduled_send_time: Optional[datetime] = None
    budget: Optional[float] = Field(None, ge=0)
    target_audience_size: Optional[int] = Field(None, ge=0)
    objective: Optional[str] = None
    subject_line: Optional[str] = None
    content: Optional[str] = None
    creative_assets: Optional[Dict[str, Any]] = None
    target_criteria: Optional[Dict[str, Any]] = None
    assigned_to_id: Optional[int] = None
    integration_settings: Optional[Dict[str, Any]] = None

class CampaignInDB(CampaignBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    campaign_number: str
    sent_count: int = 0
    delivered_count: int = 0
    opened_count: int = 0
    clicked_count: int = 0
    converted_count: int = 0
    unsubscribed_count: int = 0
    revenue_generated: float = 0.0
    cost_per_acquisition: Optional[float] = None
    return_on_investment: Optional[float] = None
    created_by_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    launched_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class Campaign(CampaignInDB):
    @property
    def open_rate(self) -> float:
        if self.delivered_count == 0:
            return 0.0
        return (self.opened_count / self.delivered_count) * 100

    @property
    def click_rate(self) -> float:
        if self.delivered_count == 0:
            return 0.0
        return (self.clicked_count / self.delivered_count) * 100

    @property
    def conversion_rate(self) -> float:
        if self.delivered_count == 0:
            return 0.0
        return (self.converted_count / self.delivered_count) * 100

# Promotion Schemas
class PromotionBase(BaseModel):
    promotion_code: str = Field(..., description="Promotion code")
    name: str = Field(..., description="Promotion name")
    description: Optional[str] = Field(None, description="Promotion description")
    promotion_type: PromotionTypeEnum = Field(..., description="Promotion type")
    is_active: bool = Field(True, description="Is promotion active")
    valid_from: date = Field(..., description="Valid from date")
    valid_until: Optional[date] = Field(None, description="Valid until date")
    discount_percentage: Optional[float] = Field(None, ge=0, le=100, description="Discount percentage")
    discount_amount: Optional[float] = Field(None, ge=0, description="Discount amount")
    minimum_purchase_amount: Optional[float] = Field(None, ge=0, description="Minimum purchase amount")
    maximum_discount_amount: Optional[float] = Field(None, ge=0, description="Maximum discount amount")
    usage_limit_total: Optional[int] = Field(None, ge=0, description="Total usage limit")
    usage_limit_per_customer: Optional[int] = Field(None, ge=0, description="Per customer usage limit")
    buy_quantity: Optional[int] = Field(None, ge=0, description="Buy quantity for BOGO")
    get_quantity: Optional[int] = Field(None, ge=0, description="Get quantity for BOGO")
    get_discount_percentage: Optional[float] = Field(None, ge=0, le=100, description="Get discount percentage for BOGO")
    applicable_products: Optional[List[int]] = Field(None, description="Applicable product IDs")
    applicable_categories: Optional[List[str]] = Field(None, description="Applicable categories")
    exclude_products: Optional[List[int]] = Field(None, description="Excluded product IDs")
    target_customer_segments: Optional[List[str]] = Field(None, description="Target customer segments")
    new_customers_only: bool = Field(False, description="New customers only")
    campaign_id: Optional[int] = Field(None, description="Campaign ID")

class PromotionCreate(PromotionBase):
    pass

class PromotionUpdate(BaseModel):
    promotion_code: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    promotion_type: Optional[PromotionTypeEnum] = None
    is_active: Optional[bool] = None
    valid_from: Optional[date] = None
    valid_until: Optional[date] = None
    discount_percentage: Optional[float] = Field(None, ge=0, le=100)
    discount_amount: Optional[float] = Field(None, ge=0)
    minimum_purchase_amount: Optional[float] = Field(None, ge=0)
    maximum_discount_amount: Optional[float] = Field(None, ge=0)
    usage_limit_total: Optional[int] = Field(None, ge=0)
    usage_limit_per_customer: Optional[int] = Field(None, ge=0)
    buy_quantity: Optional[int] = Field(None, ge=0)
    get_quantity: Optional[int] = Field(None, ge=0)
    get_discount_percentage: Optional[float] = Field(None, ge=0, le=100)
    applicable_products: Optional[List[int]] = None
    applicable_categories: Optional[List[str]] = None
    exclude_products: Optional[List[int]] = None
    target_customer_segments: Optional[List[str]] = None
    new_customers_only: Optional[bool] = None
    campaign_id: Optional[int] = None

class PromotionInDB(PromotionBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    current_usage_count: int = 0
    total_redemptions: int = 0
    total_discount_given: float = 0.0
    total_revenue_impact: float = 0.0
    created_by_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

class Promotion(PromotionInDB):
    pass

# Promotion Redemption Schemas
class PromotionRedemptionBase(BaseModel):
    promotion_id: int = Field(..., description="Promotion ID")
    customer_id: Optional[int] = Field(None, description="Customer ID")
    voucher_type: Optional[str] = Field(None, description="Voucher type")
    voucher_id: Optional[int] = Field(None, description="Voucher ID")
    voucher_number: Optional[str] = Field(None, description="Voucher number")
    discount_amount: float = Field(..., ge=0, description="Discount amount")
    order_amount: float = Field(..., ge=0, description="Order amount")
    final_amount: float = Field(..., ge=0, description="Final amount")

class PromotionRedemptionCreate(PromotionRedemptionBase):
    pass

class PromotionRedemptionInDB(PromotionRedemptionBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    redeemed_at: datetime

class PromotionRedemption(PromotionRedemptionInDB):
    pass

# Campaign Analytics Schemas
class CampaignAnalyticsBase(BaseModel):
    campaign_id: int = Field(..., description="Campaign ID")
    analytics_date: date = Field(..., description="Analytics date")
    hour: Optional[int] = Field(None, ge=0, le=23, description="Hour for hourly data")
    impressions: int = Field(0, ge=0, description="Impressions")
    clicks: int = Field(0, ge=0, description="Clicks")
    conversions: int = Field(0, ge=0, description="Conversions")
    spend: float = Field(0.0, ge=0, description="Spend")
    revenue: float = Field(0.0, ge=0, description="Revenue")
    emails_sent: Optional[int] = Field(None, ge=0, description="Emails sent")
    emails_delivered: Optional[int] = Field(None, ge=0, description="Emails delivered")
    emails_opened: Optional[int] = Field(None, ge=0, description="Emails opened")
    emails_clicked: Optional[int] = Field(None, ge=0, description="Emails clicked")
    unsubscribes: Optional[int] = Field(None, ge=0, description="Unsubscribes")
    bounces: Optional[int] = Field(None, ge=0, description="Bounces")
    likes: Optional[int] = Field(None, ge=0, description="Likes")
    shares: Optional[int] = Field(None, ge=0, description="Shares")
    comments: Optional[int] = Field(None, ge=0, description="Comments")
    followers_gained: Optional[int] = Field(None, description="Followers gained")
    custom_metrics: Optional[Dict[str, Any]] = Field(None, description="Custom metrics")

class CampaignAnalyticsCreate(CampaignAnalyticsBase):
    pass

class CampaignAnalyticsUpdate(BaseModel):
    impressions: Optional[int] = Field(None, ge=0)
    clicks: Optional[int] = Field(None, ge=0)
    conversions: Optional[int] = Field(None, ge=0)
    spend: Optional[float] = Field(None, ge=0)
    revenue: Optional[float] = Field(None, ge=0)
    emails_sent: Optional[int] = Field(None, ge=0)
    emails_delivered: Optional[int] = Field(None, ge=0)
    emails_opened: Optional[int] = Field(None, ge=0)
    emails_clicked: Optional[int] = Field(None, ge=0)
    unsubscribes: Optional[int] = Field(None, ge=0)
    bounces: Optional[int] = Field(None, ge=0)
    likes: Optional[int] = Field(None, ge=0)
    shares: Optional[int] = Field(None, ge=0)
    comments: Optional[int] = Field(None, ge=0)
    followers_gained: Optional[int] = None
    custom_metrics: Optional[Dict[str, Any]] = None

class CampaignAnalyticsInDB(CampaignAnalyticsBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    created_at: datetime

class CampaignAnalytics(CampaignAnalyticsInDB):
    pass

# Marketing List Schemas
class MarketingListBase(BaseModel):
    name: str = Field(..., description="Marketing list name")
    description: Optional[str] = Field(None, description="Marketing list description")
    list_type: str = Field("custom", description="List type")
    segmentation_criteria: Optional[Dict[str, Any]] = Field(None, description="Segmentation criteria")
    is_active: bool = Field(True, description="Is list active")

class MarketingListCreate(MarketingListBase):
    pass

class MarketingListUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    list_type: Optional[str] = None
    segmentation_criteria: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class MarketingListInDB(MarketingListBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    total_contacts: int = 0
    active_contacts: int = 0
    opted_out_contacts: int = 0
    last_updated: Optional[datetime] = None
    created_by_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

class MarketingList(MarketingListInDB):
    pass

# Marketing List Contact Schemas
class MarketingListContactBase(BaseModel):
    marketing_list_id: int = Field(..., description="Marketing list ID")
    customer_id: Optional[int] = Field(None, description="Customer ID")
    email: Optional[str] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    first_name: Optional[str] = Field(None, description="First name")
    last_name: Optional[str] = Field(None, description="Last name")
    is_subscribed: bool = Field(True, description="Is subscribed")
    opt_in_source: Optional[str] = Field(None, description="Opt-in source")
    custom_attributes: Optional[Dict[str, Any]] = Field(None, description="Custom attributes")

class MarketingListContactCreate(MarketingListContactBase):
    pass

class MarketingListContactUpdate(BaseModel):
    customer_id: Optional[int] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_subscribed: Optional[bool] = None
    opt_in_source: Optional[str] = None
    custom_attributes: Optional[Dict[str, Any]] = None

class MarketingListContactInDB(MarketingListContactBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    subscribed_at: Optional[datetime] = None
    unsubscribed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

class MarketingListContact(MarketingListContactInDB):
    pass

# Campaign Performance Schemas
class CampaignPerformanceReport(BaseModel):
    campaign_id: int
    campaign_name: str
    campaign_type: str
    status: str
    start_date: date
    end_date: Optional[date]
    total_sent: int
    total_delivered: int
    total_opened: int
    total_clicked: int
    total_converted: int
    total_unsubscribed: int
    open_rate: float
    click_rate: float
    conversion_rate: float
    unsubscribe_rate: float
    total_spend: float
    total_revenue: float
    roi: float
    cost_per_acquisition: float

# Marketing Analytics Schemas
class MarketingAnalytics(BaseModel):
    total_campaigns: int
    active_campaigns: int
    completed_campaigns: int
    total_contacts: int
    total_subscribers: int
    total_unsubscribes: int
    average_open_rate: float
    average_click_rate: float
    average_conversion_rate: float
    total_marketing_spend: float
    total_marketing_revenue: float
    marketing_roi: float
    top_performing_campaigns: List[Dict[str, Any]]
    period_start: date
    period_end: date

# Promotion Analytics Schemas
class PromotionAnalytics(BaseModel):
    total_promotions: int
    active_promotions: int
    total_redemptions: int
    total_discount_given: float
    total_revenue_impact: float
    average_discount_per_redemption: float
    most_popular_promotions: List[Dict[str, Any]]
    promotion_types_performance: Dict[str, Any]
    period_start: date
    period_end: date

# Bulk Import/Export Schemas
class CampaignImportData(BaseModel):
    campaigns: List[Dict[str, Any]]
    validate_only: bool = Field(False, description="Validate only, don't import")

class CampaignImportResponse(BaseModel):
    success: bool
    imported_count: int
    failed_count: int
    errors: List[str]
    warnings: List[str]

class ContactImportData(BaseModel):
    marketing_list_id: int
    contacts: List[Dict[str, Any]]
    validate_only: bool = Field(False, description="Validate only, don't import")

class ContactImportResponse(BaseModel):
    success: bool
    imported_count: int
    failed_count: int
    errors: List[str]
    warnings: List[str]