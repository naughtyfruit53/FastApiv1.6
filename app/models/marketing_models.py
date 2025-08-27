# app/models/marketing_models.py

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON, Index, UniqueConstraint, Date, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.core.database import Base
from typing import List, Optional, Dict, Any
from datetime import datetime, date
import enum

class CampaignType(enum.Enum):
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

class CampaignStatus(enum.Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class PromotionType(enum.Enum):
    PERCENTAGE_DISCOUNT = "percentage_discount"
    FIXED_AMOUNT_DISCOUNT = "fixed_amount_discount"
    BUY_X_GET_Y = "buy_x_get_y"
    FREE_SHIPPING = "free_shipping"
    BUNDLE_OFFER = "bundle_offer"
    CASHBACK = "cashback"
    LOYALTY_POINTS = "loyalty_points"

class Campaign(Base):
    """
    Model for marketing campaigns.
    Supports various campaign types and comprehensive tracking.
    """
    __tablename__ = "campaigns"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_campaign_organization_id"), nullable=False, index=True)
    
    # Campaign identification
    campaign_number: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Campaign details
    campaign_type: Mapped[CampaignType] = mapped_column(Enum(CampaignType), nullable=False, index=True)
    status: Mapped[CampaignStatus] = mapped_column(Enum(CampaignStatus), default=CampaignStatus.DRAFT, index=True)
    
    # Timeline
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    scheduled_send_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Budget and objectives
    budget: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    target_audience_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    objective: Mapped[Optional[str]] = mapped_column(String, nullable=True) # brand_awareness, lead_generation, sales, etc.
    
    # Content and creative
    subject_line: Mapped[Optional[str]] = mapped_column(String, nullable=True) # For email campaigns
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True) # Campaign content/copy
    creative_assets: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True) # Images, videos, etc.
    
    # Targeting criteria (JSON for flexibility)
    target_criteria: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Performance tracking
    sent_count: Mapped[int] = mapped_column(Integer, default=0)
    delivered_count: Mapped[int] = mapped_column(Integer, default=0)
    opened_count: Mapped[int] = mapped_column(Integer, default=0)
    clicked_count: Mapped[int] = mapped_column(Integer, default=0)
    converted_count: Mapped[int] = mapped_column(Integer, default=0)
    unsubscribed_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Revenue tracking
    revenue_generated: Mapped[float] = mapped_column(Float, default=0.0)
    cost_per_acquisition: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    return_on_investment: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Assignment and ownership
    assigned_to_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_campaign_assigned_to_id"), nullable=True)
    created_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_campaign_created_by_id"), nullable=True)
    
    # Integration settings
    integration_settings: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True) # Platform-specific settings
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    launched_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    assigned_to: Mapped[Optional["User"]] = relationship("User", foreign_keys=[assigned_to_id])
    created_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[created_by_id])
    promotions: Mapped[List["Promotion"]] = relationship("Promotion", back_populates="campaign", cascade="all, delete-orphan")
    analytics: Mapped[List["CampaignAnalytics"]] = relationship("CampaignAnalytics", back_populates="campaign", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_campaign_org_type', 'organization_id', 'campaign_type'),
        Index('idx_campaign_org_status', 'organization_id', 'status'),
        Index('idx_campaign_dates', 'start_date', 'end_date'),
        UniqueConstraint('organization_id', 'campaign_number', name='uq_campaign_org_number'),
    )

    @property
    def open_rate(self) -> float:
        """Calculate email open rate as percentage"""
        if self.delivered_count == 0:
            return 0.0
        return (self.opened_count / self.delivered_count) * 100

    @property
    def click_rate(self) -> float:
        """Calculate click-through rate as percentage"""
        if self.delivered_count == 0:
            return 0.0
        return (self.clicked_count / self.delivered_count) * 100

    @property
    def conversion_rate(self) -> float:
        """Calculate conversion rate as percentage"""
        if self.delivered_count == 0:
            return 0.0
        return (self.converted_count / self.delivered_count) * 100

class Promotion(Base):
    """
    Model for promotional offers and discounts.
    Can be linked to campaigns or standalone.
    """
    __tablename__ = "promotions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_promotion_organization_id"), nullable=False, index=True)
    
    # Promotion identification
    promotion_code: Mapped[str] = mapped_column(String, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Promotion details
    promotion_type: Mapped[PromotionType] = mapped_column(Enum(PromotionType), nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    
    # Validity period
    valid_from: Mapped[date] = mapped_column(Date, nullable=False)
    valid_until: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    
    # Discount configuration
    discount_percentage: Mapped[Optional[float]] = mapped_column(Float, nullable=True) # For percentage discounts
    discount_amount: Mapped[Optional[float]] = mapped_column(Float, nullable=True) # For fixed amount discounts
    minimum_purchase_amount: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    maximum_discount_amount: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Usage limitations
    usage_limit_total: Mapped[Optional[int]] = mapped_column(Integer, nullable=True) # Total usage limit
    usage_limit_per_customer: Mapped[Optional[int]] = mapped_column(Integer, nullable=True) # Per customer limit
    current_usage_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Buy X Get Y configuration
    buy_quantity: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    get_quantity: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    get_discount_percentage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Applicable products/categories (JSON for flexibility)
    applicable_products: Mapped[Optional[List[int]]] = mapped_column(JSON, nullable=True) # Product IDs
    applicable_categories: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True) # Category names
    exclude_products: Mapped[Optional[List[int]]] = mapped_column(JSON, nullable=True) # Excluded product IDs
    
    # Customer targeting
    target_customer_segments: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    new_customers_only: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Campaign linkage
    campaign_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("campaigns.id", name="fk_promotion_campaign_id"), nullable=True)
    
    # Performance tracking
    total_redemptions: Mapped[int] = mapped_column(Integer, default=0)
    total_discount_given: Mapped[float] = mapped_column(Float, default=0.0)
    total_revenue_impact: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Assignment
    created_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_promotion_created_by_id"), nullable=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    campaign: Mapped[Optional["Campaign"]] = relationship("Campaign", back_populates="promotions")
    created_by: Mapped[Optional["User"]] = relationship("User")
    redemptions: Mapped[List["PromotionRedemption"]] = relationship("PromotionRedemption", back_populates="promotion", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_promotion_org_type', 'organization_id', 'promotion_type'),
        Index('idx_promotion_org_active', 'organization_id', 'is_active'),
        Index('idx_promotion_validity', 'valid_from', 'valid_until'),
        UniqueConstraint('organization_id', 'promotion_code', name='uq_promotion_org_code'),
    )

class PromotionRedemption(Base):
    """
    Track individual promotion redemptions by customers.
    """
    __tablename__ = "promotion_redemptions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_promotion_redemption_organization_id"), nullable=False, index=True)
    
    # References
    promotion_id: Mapped[int] = mapped_column(Integer, ForeignKey("promotions.id", name="fk_promotion_redemption_promotion_id"), nullable=False)
    customer_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("customers.id", name="fk_promotion_redemption_customer_id"), nullable=True)
    
    # Order/voucher reference (if applicable)
    voucher_type: Mapped[Optional[str]] = mapped_column(String, nullable=True) # sales_voucher, sales_order, etc.
    voucher_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    voucher_number: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # Redemption details
    discount_amount: Mapped[float] = mapped_column(Float, nullable=False)
    order_amount: Mapped[float] = mapped_column(Float, nullable=False)
    final_amount: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Metadata
    redeemed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    promotion: Mapped["Promotion"] = relationship("Promotion", back_populates="redemptions")
    customer: Mapped[Optional["Customer"]] = relationship("Customer")
    
    __table_args__ = (
        Index('idx_promotion_redemption_org_promotion', 'organization_id', 'promotion_id'),
        Index('idx_promotion_redemption_customer', 'customer_id'),
        Index('idx_promotion_redemption_date', 'redeemed_at'),
    )

class CampaignAnalytics(Base):
    """
    Detailed analytics data for campaigns.
    Stores time-series data for performance tracking.
    """
    __tablename__ = "campaign_analytics"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_campaign_analytics_organization_id"), nullable=False, index=True)
    
    # References
    campaign_id: Mapped[int] = mapped_column(Integer, ForeignKey("campaigns.id", name="fk_campaign_analytics_campaign_id"), nullable=False)
    
    # Time dimension
    analytics_date: Mapped[date] = mapped_column(Date, nullable=False)
    hour: Mapped[Optional[int]] = mapped_column(Integer, nullable=True) # For hourly data
    
    # Metrics
    impressions: Mapped[int] = mapped_column(Integer, default=0)
    clicks: Mapped[int] = mapped_column(Integer, default=0)
    conversions: Mapped[int] = mapped_column(Integer, default=0)
    spend: Mapped[float] = mapped_column(Float, default=0.0)
    revenue: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Email-specific metrics
    emails_sent: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    emails_delivered: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    emails_opened: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    emails_clicked: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    unsubscribes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    bounces: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Social media metrics
    likes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    shares: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    comments: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    followers_gained: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Additional metrics (JSON for flexibility)
    custom_metrics: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    campaign: Mapped["Campaign"] = relationship("Campaign", back_populates="analytics")
    
    __table_args__ = (
        Index('idx_campaign_analytics_org_campaign', 'organization_id', 'campaign_id'),
        Index('idx_campaign_analytics_date', 'analytics_date'),
        UniqueConstraint('campaign_id', 'analytics_date', 'hour', name='uq_campaign_analytics_date_hour'),
    )

class MarketingList(Base):
    """
    Marketing lists for targeting campaigns.
    Contains customer segments and contact lists.
    """
    __tablename__ = "marketing_lists"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_marketing_list_organization_id"), nullable=False, index=True)
    
    # List details
    name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    list_type: Mapped[str] = mapped_column(String, nullable=False, default="custom") # custom, dynamic, imported
    
    # Segmentation criteria (for dynamic lists)
    segmentation_criteria: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # List statistics
    total_contacts: Mapped[int] = mapped_column(Integer, default=0)
    active_contacts: Mapped[int] = mapped_column(Integer, default=0)
    opted_out_contacts: Mapped[int] = mapped_column(Integer, default=0)
    
    # List management
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_updated: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Assignment
    created_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_marketing_list_created_by_id"), nullable=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    created_by: Mapped[Optional["User"]] = relationship("User")
    contacts: Mapped[List["MarketingListContact"]] = relationship("MarketingListContact", back_populates="marketing_list", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_marketing_list_org_type', 'organization_id', 'list_type'),
        Index('idx_marketing_list_active', 'is_active'),
        UniqueConstraint('organization_id', 'name', name='uq_marketing_list_org_name'),
    )

class MarketingListContact(Base):
    """
    Contacts within marketing lists.
    Links customers to marketing lists with subscription status.
    """
    __tablename__ = "marketing_list_contacts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_marketing_list_contact_organization_id"), nullable=False, index=True)
    
    # References
    marketing_list_id: Mapped[int] = mapped_column(Integer, ForeignKey("marketing_lists.id", name="fk_marketing_list_contact_list_id"), nullable=False)
    customer_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("customers.id", name="fk_marketing_list_contact_customer_id"), nullable=True)
    
    # Contact details (for external contacts not in customer base)
    email: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)
    phone: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    first_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # Subscription status
    is_subscribed: Mapped[bool] = mapped_column(Boolean, default=True)
    subscribed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    unsubscribed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    opt_in_source: Mapped[Optional[str]] = mapped_column(String, nullable=True) # website, import, manual, etc.
    
    # Custom attributes
    custom_attributes: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    marketing_list: Mapped["MarketingList"] = relationship("MarketingList", back_populates="contacts")
    customer: Mapped[Optional["Customer"]] = relationship("Customer")
    
    __table_args__ = (
        Index('idx_marketing_list_contact_org_list', 'organization_id', 'marketing_list_id'),
        Index('idx_marketing_list_contact_subscribed', 'is_subscribed'),
        Index('idx_marketing_list_contact_email', 'email'),
        UniqueConstraint('marketing_list_id', 'customer_id', name='uq_marketing_list_contact_customer'),
        UniqueConstraint('marketing_list_id', 'email', name='uq_marketing_list_contact_email'),
    )