# app/models/seo_models.py

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.core.database import Base
from typing import List, Optional, Dict, Any
from datetime import datetime


class SEOMetaTag(Base):
    """Model for managing SEO meta tags for different pages"""
    __tablename__ = "seo_meta_tags"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Page identification
    page_path: Mapped[str] = mapped_column(String, nullable=False, index=True)  # e.g., "/", "/about", "/products"
    page_title: Mapped[str] = mapped_column(String, nullable=False)  # Internal title for management
    
    # Basic SEO meta tags
    title: Mapped[str] = mapped_column(String, nullable=False)  # <title> tag
    meta_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # meta description
    meta_keywords: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # meta keywords (legacy)
    
    # Open Graph meta tags
    og_title: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    og_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    og_image: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # URL to image
    og_type: Mapped[Optional[str]] = mapped_column(String, nullable=True, default="website")
    og_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # Twitter Card meta tags
    twitter_card: Mapped[Optional[str]] = mapped_column(String, nullable=True, default="summary")
    twitter_title: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    twitter_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    twitter_image: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    twitter_site: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # @username
    
    # Technical SEO
    canonical_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    robots: Mapped[Optional[str]] = mapped_column(String, nullable=True, default="index,follow")
    lang: Mapped[str] = mapped_column(String, nullable=False, default="en")
    
    # Additional meta tags (JSON storage for flexibility)
    additional_meta: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Status and management
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    priority: Mapped[int] = mapped_column(Integer, default=1)  # For ordering when multiple tags exist
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    
    # Relationships
    organization: Mapped["app.models.user_models.Organization"] = relationship(
        "app.models.user_models.Organization"
    )
    created_by: Mapped["app.models.user_models.User"] = relationship(
        "app.models.user_models.User"
    )
    
    __table_args__ = (
        Index('idx_seo_meta_org_path', 'organization_id', 'page_path'),
        Index('idx_seo_meta_active', 'is_active'),
        {'extend_existing': True}
    )


class SitemapEntry(Base):
    """Model for managing sitemap entries"""
    __tablename__ = "sitemap_entries"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), nullable=False, index=True)
    
    # URL information
    url: Mapped[str] = mapped_column(String, nullable=False, index=True)
    priority: Mapped[float] = mapped_column(nullable=False, default=0.5)  # 0.0 to 1.0
    change_frequency: Mapped[str] = mapped_column(String, nullable=False, default="monthly")  # always, hourly, daily, weekly, monthly, yearly, never
    
    # Timestamps
    last_modified: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Management
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    auto_generated: Mapped[bool] = mapped_column(Boolean, default=True)  # Whether this was auto-generated or manually added
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization: Mapped["app.models.user_models.Organization"] = relationship(
        "app.models.user_models.Organization"
    )
    
    __table_args__ = (
        Index('idx_sitemap_org_url', 'organization_id', 'url'),
        Index('idx_sitemap_active', 'is_active'),
        {'extend_existing': True}
    )


class AnalyticsIntegration(Base):
    """Model for managing analytics integration settings"""
    __tablename__ = "analytics_integrations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Analytics provider
    provider: Mapped[str] = mapped_column(String, nullable=False)  # google_analytics, google_tag_manager, facebook_pixel, etc.
    
    # Configuration
    tracking_id: Mapped[str] = mapped_column(String, nullable=False)  # GA tracking ID, GTM container ID, etc.
    configuration: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)  # Additional config
    
    # Settings
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    
    # Relationships
    organization: Mapped["app.models.user_models.Organization"] = relationship(
        "app.models.user_models.Organization"
    )
    created_by: Mapped["app.models.user_models.User"] = relationship(
        "app.models.user_models.User"
    )
    
    __table_args__ = (
        Index('idx_analytics_org_provider', 'organization_id', 'provider'),
        Index('idx_analytics_active', 'is_active'),
        {'extend_existing': True}
    )


class KeywordAnalysis(Base):
    """Model for storing keyword analysis data"""
    __tablename__ = "keyword_analysis"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Keyword information
    keyword: Mapped[str] = mapped_column(String, nullable=False, index=True)
    search_volume: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    competition: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # low, medium, high
    difficulty: Mapped[Optional[float]] = mapped_column(nullable=True)  # 0-100 difficulty score
    
    # Cost and value
    cpc: Mapped[Optional[float]] = mapped_column(nullable=True)  # Cost per click
    commercial_intent: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # low, medium, high
    
    # Rankings and performance
    current_ranking: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    target_ranking: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Associated content
    target_page: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    content_gaps: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Analysis metadata
    analysis_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    data_source: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # manual, google_ads, semrush, etc.
    
    # Status
    is_target_keyword: Mapped[bool] = mapped_column(Boolean, default=False)
    priority: Mapped[str] = mapped_column(String, default="medium")  # low, medium, high
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    
    # Relationships
    organization: Mapped["app.models.user_models.Organization"] = relationship(
        "app.models.user_models.Organization"
    )
    created_by: Mapped["app.models.user_models.User"] = relationship(
        "app.models.user_models.User"
    )
    
    __table_args__ = (
        Index('idx_keyword_org_keyword', 'organization_id', 'keyword'),
        Index('idx_keyword_target', 'is_target_keyword'),
        Index('idx_keyword_priority', 'priority'),
        {'extend_existing': True}
    )


class CompetitorAnalysis(Base):
    """Model for storing competitor analysis data"""
    __tablename__ = "competitor_analysis"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Competitor information
    competitor_name: Mapped[str] = mapped_column(String, nullable=False)
    competitor_domain: Mapped[str] = mapped_column(String, nullable=False, index=True)
    
    # SEO metrics
    domain_authority: Mapped[Optional[float]] = mapped_column(nullable=True)
    organic_traffic: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    organic_keywords: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    backlinks: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Content analysis
    content_gaps: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    top_keywords: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    content_strategy: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Technical analysis
    site_speed: Mapped[Optional[float]] = mapped_column(nullable=True)
    mobile_friendly: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    technical_issues: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Analysis metadata
    analysis_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    data_source: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # Status
    is_active_competitor: Mapped[bool] = mapped_column(Boolean, default=True)
    monitoring_frequency: Mapped[str] = mapped_column(String, default="monthly")  # weekly, monthly, quarterly
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    
    # Relationships
    organization: Mapped["app.models.user_models.Organization"] = relationship(
        "app.models.user_models.Organization"
    )
    created_by: Mapped["app.models.user_models.User"] = relationship(
        "app.models.user_models.User"
    )
    
    __table_args__ = (
        Index('idx_competitor_org_domain', 'organization_id', 'competitor_domain'),
        Index('idx_competitor_active', 'is_active_competitor'),
        {'extend_existing': True}
    )