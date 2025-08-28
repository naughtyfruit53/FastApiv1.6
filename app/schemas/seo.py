# app/schemas/seo.py

from pydantic import BaseModel, HttpUrl, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum


class ChangeFrequency(str, Enum):
    ALWAYS = "always"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"
    NEVER = "never"


class AnalyticsProvider(str, Enum):
    GOOGLE_ANALYTICS = "google_analytics"
    GOOGLE_TAG_MANAGER = "google_tag_manager"
    FACEBOOK_PIXEL = "facebook_pixel"
    HOTJAR = "hotjar"
    MIXPANEL = "mixpanel"
    AMPLITUDE = "amplitude"


class Competition(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class MonitoringFrequency(str, Enum):
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"


# SEO Meta Tag schemas
class SEOMetaTagBase(BaseModel):
    page_path: str
    page_title: str
    title: str
    meta_description: Optional[str] = None
    meta_keywords: Optional[str] = None
    og_title: Optional[str] = None
    og_description: Optional[str] = None
    og_image: Optional[str] = None
    og_type: Optional[str] = "website"
    og_url: Optional[str] = None
    twitter_card: Optional[str] = "summary"
    twitter_title: Optional[str] = None
    twitter_description: Optional[str] = None
    twitter_image: Optional[str] = None
    twitter_site: Optional[str] = None
    canonical_url: Optional[str] = None
    robots: Optional[str] = "index,follow"
    lang: str = "en"
    additional_meta: Optional[Dict[str, Any]] = None
    is_active: bool = True
    priority: int = 1


class SEOMetaTagCreate(SEOMetaTagBase):
    @validator('page_path')
    def validate_page_path(cls, v):
        if not v.startswith('/'):
            raise ValueError('Page path must start with /')
        return v


class SEOMetaTagUpdate(BaseModel):
    page_title: Optional[str] = None
    title: Optional[str] = None
    meta_description: Optional[str] = None
    meta_keywords: Optional[str] = None
    og_title: Optional[str] = None
    og_description: Optional[str] = None
    og_image: Optional[str] = None
    og_type: Optional[str] = None
    og_url: Optional[str] = None
    twitter_card: Optional[str] = None
    twitter_title: Optional[str] = None
    twitter_description: Optional[str] = None
    twitter_image: Optional[str] = None
    twitter_site: Optional[str] = None
    canonical_url: Optional[str] = None
    robots: Optional[str] = None
    lang: Optional[str] = None
    additional_meta: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    priority: Optional[int] = None


class SEOMetaTagInDB(SEOMetaTagBase):
    id: int
    organization_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by_id: int
    
    class Config:
        from_attributes = True


# Sitemap schemas
class SitemapEntryBase(BaseModel):
    url: str
    priority: float = 0.5
    change_frequency: ChangeFrequency = ChangeFrequency.MONTHLY
    last_modified: Optional[datetime] = None
    is_active: bool = True
    auto_generated: bool = True

    @validator('priority')
    def validate_priority(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError('Priority must be between 0.0 and 1.0')
        return v


class SitemapEntryCreate(SitemapEntryBase):
    pass


class SitemapEntryUpdate(BaseModel):
    priority: Optional[float] = None
    change_frequency: Optional[ChangeFrequency] = None
    last_modified: Optional[datetime] = None
    is_active: Optional[bool] = None


class SitemapEntryInDB(SitemapEntryBase):
    id: int
    organization_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Analytics Integration schemas
class AnalyticsIntegrationBase(BaseModel):
    provider: AnalyticsProvider
    tracking_id: str
    configuration: Optional[Dict[str, Any]] = None
    is_active: bool = True


class AnalyticsIntegrationCreate(AnalyticsIntegrationBase):
    pass


class AnalyticsIntegrationUpdate(BaseModel):
    tracking_id: Optional[str] = None
    configuration: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class AnalyticsIntegrationInDB(AnalyticsIntegrationBase):
    id: int
    organization_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by_id: int
    
    class Config:
        from_attributes = True


# Keyword Analysis schemas
class KeywordAnalysisBase(BaseModel):
    keyword: str
    search_volume: Optional[int] = None
    competition: Optional[Competition] = None
    difficulty: Optional[float] = None
    cpc: Optional[float] = None
    commercial_intent: Optional[Competition] = None
    current_ranking: Optional[int] = None
    target_ranking: Optional[int] = None
    target_page: Optional[str] = None
    content_gaps: Optional[Dict[str, Any]] = None
    data_source: Optional[str] = None
    is_target_keyword: bool = False
    priority: Priority = Priority.MEDIUM

    @validator('difficulty')
    def validate_difficulty(cls, v):
        if v is not None and not 0 <= v <= 100:
            raise ValueError('Difficulty must be between 0 and 100')
        return v

    @validator('current_ranking', 'target_ranking')
    def validate_ranking(cls, v):
        if v is not None and v < 1:
            raise ValueError('Ranking must be 1 or higher')
        return v


class KeywordAnalysisCreate(KeywordAnalysisBase):
    pass


class KeywordAnalysisUpdate(BaseModel):
    search_volume: Optional[int] = None
    competition: Optional[Competition] = None
    difficulty: Optional[float] = None
    cpc: Optional[float] = None
    commercial_intent: Optional[Competition] = None
    current_ranking: Optional[int] = None
    target_ranking: Optional[int] = None
    target_page: Optional[str] = None
    content_gaps: Optional[Dict[str, Any]] = None
    data_source: Optional[str] = None
    is_target_keyword: Optional[bool] = None
    priority: Optional[Priority] = None


class KeywordAnalysisInDB(KeywordAnalysisBase):
    id: int
    organization_id: int
    analysis_date: datetime
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by_id: int
    
    class Config:
        from_attributes = True


# Competitor Analysis schemas
class CompetitorAnalysisBase(BaseModel):
    competitor_name: str
    competitor_domain: str
    domain_authority: Optional[float] = None
    organic_traffic: Optional[int] = None
    organic_keywords: Optional[int] = None
    backlinks: Optional[int] = None
    content_gaps: Optional[Dict[str, Any]] = None
    top_keywords: Optional[Dict[str, Any]] = None
    content_strategy: Optional[Dict[str, Any]] = None
    site_speed: Optional[float] = None
    mobile_friendly: Optional[bool] = None
    technical_issues: Optional[Dict[str, Any]] = None
    data_source: Optional[str] = None
    is_active_competitor: bool = True
    monitoring_frequency: MonitoringFrequency = MonitoringFrequency.MONTHLY

    @validator('domain_authority')
    def validate_domain_authority(cls, v):
        if v is not None and not 0 <= v <= 100:
            raise ValueError('Domain Authority must be between 0 and 100')
        return v

    @validator('site_speed')
    def validate_site_speed(cls, v):
        if v is not None and v < 0:
            raise ValueError('Site speed must be positive')
        return v


class CompetitorAnalysisCreate(CompetitorAnalysisBase):
    pass


class CompetitorAnalysisUpdate(BaseModel):
    competitor_name: Optional[str] = None
    domain_authority: Optional[float] = None
    organic_traffic: Optional[int] = None
    organic_keywords: Optional[int] = None
    backlinks: Optional[int] = None
    content_gaps: Optional[Dict[str, Any]] = None
    top_keywords: Optional[Dict[str, Any]] = None
    content_strategy: Optional[Dict[str, Any]] = None
    site_speed: Optional[float] = None
    mobile_friendly: Optional[bool] = None
    technical_issues: Optional[Dict[str, Any]] = None
    data_source: Optional[str] = None
    is_active_competitor: Optional[bool] = None
    monitoring_frequency: Optional[MonitoringFrequency] = None


class CompetitorAnalysisInDB(CompetitorAnalysisBase):
    id: int
    organization_id: int
    analysis_date: datetime
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by_id: int
    
    class Config:
        from_attributes = True


# Combined response schemas
class SEODashboard(BaseModel):
    """Dashboard overview of SEO metrics"""
    total_pages: int
    meta_tags_configured: int
    sitemap_entries: int
    analytics_integrations: int
    tracked_keywords: int
    target_keywords: int
    competitors_monitored: int
    avg_keyword_ranking: Optional[float]
    recent_keyword_changes: List[Dict[str, Any]] = []


class KeywordReport(BaseModel):
    """Keyword analysis report"""
    total_keywords: int
    target_keywords: int
    avg_search_volume: Optional[float]
    avg_difficulty: Optional[float]
    avg_ranking: Optional[float]
    keyword_distribution: Dict[str, int]
    top_opportunities: List[KeywordAnalysisInDB] = []
    ranking_improvements: List[Dict[str, Any]] = []


class CompetitorReport(BaseModel):
    """Competitor analysis report"""
    total_competitors: int
    avg_domain_authority: Optional[float]
    content_gap_opportunities: List[Dict[str, Any]] = []
    keyword_overlap: Dict[str, Any] = {}
    technical_comparison: Dict[str, Any] = {}


class SitemapGeneration(BaseModel):
    """Sitemap generation response"""
    total_urls: int
    generated_at: datetime
    sitemap_url: str
    last_modified: Optional[datetime] = None


class SEOAudit(BaseModel):
    """SEO audit results"""
    audit_date: datetime
    score: float  # Overall SEO score 0-100
    issues: List[Dict[str, Any]] = []
    recommendations: List[Dict[str, Any]] = []
    meta_tag_issues: List[Dict[str, Any]] = []
    sitemap_status: Dict[str, Any] = {}
    analytics_status: Dict[str, Any] = {}


# Bulk operation schemas
class BulkKeywordImport(BaseModel):
    """Schema for bulk keyword import"""
    keywords: List[KeywordAnalysisCreate]
    overwrite_existing: bool = False


class BulkKeywordImportResponse(BaseModel):
    """Response for bulk keyword import"""
    imported_count: int
    updated_count: int
    failed_count: int
    errors: List[str] = []


# Marketing report schemas
class MarketingReport(BaseModel):
    """Comprehensive marketing report"""
    report_id: str
    organization_id: int
    report_type: str  # seo, keyword, competitor, comprehensive
    generated_at: datetime
    data: Dict[str, Any]
    charts: List[Dict[str, Any]] = []
    insights: List[str] = []
    recommendations: List[str] = []
    export_formats: List[str] = ["pdf", "excel", "csv"]