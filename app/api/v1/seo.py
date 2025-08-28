# app/api/v1/seo.py

from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.core.org_restrictions import ensure_organization_context
from app.models.user_models import User
from app.schemas.seo import (
    SEOMetaTagCreate, SEOMetaTagUpdate, SEOMetaTagInDB,
    SitemapEntryCreate, SitemapEntryUpdate, SitemapEntryInDB,
    AnalyticsIntegrationCreate, AnalyticsIntegrationUpdate, AnalyticsIntegrationInDB,
    KeywordAnalysisCreate, KeywordAnalysisUpdate, KeywordAnalysisInDB,
    CompetitorAnalysisCreate, CompetitorAnalysisUpdate, CompetitorAnalysisInDB,
    SEODashboard, KeywordReport, CompetitorReport, SitemapGeneration, SEOAudit,
    BulkKeywordImport, BulkKeywordImportResponse
)
from app.services.seo_service import seo_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


# SEO Dashboard and Overview

@router.get("/dashboard", response_model=SEODashboard)
async def get_seo_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get SEO dashboard overview"""
    
    org_id = ensure_organization_context(current_user)
    dashboard = seo_service.get_seo_dashboard(db, org_id)
    return dashboard


@router.get("/audit", response_model=SEOAudit)
async def run_seo_audit(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Run comprehensive SEO audit"""
    
    org_id = ensure_organization_context(current_user)
    audit = seo_service.run_seo_audit(db, org_id)
    return audit


# Meta Tag Management

@router.post("/meta-tags", response_model=SEOMetaTagInDB, status_code=status.HTTP_201_CREATED)
async def create_meta_tag(
    tag_data: SEOMetaTagCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new SEO meta tag for a page"""
    
    org_id = ensure_organization_context(current_user)
    
    # Check if meta tag already exists for this page
    existing = seo_service.get_meta_tag_for_page(db, org_id, tag_data.page_path)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Meta tag already exists for page {tag_data.page_path}"
        )
    
    tag = seo_service.create_meta_tag(db, tag_data, org_id, current_user.id)
    return tag


@router.get("/meta-tags", response_model=List[SEOMetaTagInDB])
async def get_meta_tags(
    page_path: Optional[str] = Query(None, description="Filter by page path"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    skip: int = Query(0, ge=0, description="Number of tags to skip"),
    limit: int = Query(100, ge=1, le=100, description="Number of tags to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get SEO meta tags for the organization"""
    
    org_id = ensure_organization_context(current_user)
    tags = seo_service.get_meta_tags(db, org_id, page_path, is_active, skip, limit)
    return tags


@router.get("/meta-tags/page/{page_path:path}", response_model=SEOMetaTagInDB)
async def get_meta_tag_for_page(
    page_path: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get meta tag for a specific page"""
    
    org_id = ensure_organization_context(current_user)
    
    # Ensure page path starts with /
    if not page_path.startswith('/'):
        page_path = '/' + page_path
    
    tag = seo_service.get_meta_tag_for_page(db, org_id, page_path)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No meta tag found for page {page_path}"
        )
    
    return tag


@router.put("/meta-tags/{tag_id}", response_model=SEOMetaTagInDB)
async def update_meta_tag(
    tag_id: int,
    tag_data: SEOMetaTagUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update an SEO meta tag"""
    
    org_id = ensure_organization_context(current_user)
    
    tag = seo_service.update_meta_tag(db, tag_id, org_id, tag_data)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meta tag not found"
        )
    
    return tag


@router.delete("/meta-tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_meta_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete an SEO meta tag"""
    
    org_id = ensure_organization_context(current_user)
    
    success = seo_service.delete_meta_tag(db, tag_id, org_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meta tag not found"
        )


# Sitemap Management

@router.post("/sitemap/entries", response_model=SitemapEntryInDB, status_code=status.HTTP_201_CREATED)
async def create_sitemap_entry(
    entry_data: SitemapEntryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new sitemap entry"""
    
    org_id = ensure_organization_context(current_user)
    entry = seo_service.create_sitemap_entry(db, entry_data, org_id)
    return entry


@router.get("/sitemap/entries", response_model=List[SitemapEntryInDB])
async def get_sitemap_entries(
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    skip: int = Query(0, ge=0, description="Number of entries to skip"),
    limit: int = Query(1000, ge=1, le=1000, description="Number of entries to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get sitemap entries for the organization"""
    
    org_id = ensure_organization_context(current_user)
    entries = seo_service.get_sitemap_entries(db, org_id, is_active, skip, limit)
    return entries


@router.get("/sitemap.xml", response_class=PlainTextResponse)
async def get_sitemap_xml(
    base_url: str = Query(..., description="Base URL for the sitemap"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Generate and return sitemap XML"""
    
    org_id = ensure_organization_context(current_user)
    
    xml_content = seo_service.generate_sitemap_xml(db, org_id, base_url)
    
    return Response(
        content=xml_content,
        media_type="application/xml",
        headers={"Content-Disposition": "attachment; filename=sitemap.xml"}
    )


@router.post("/sitemap/auto-generate", response_model=SitemapGeneration)
async def auto_generate_sitemap(
    urls: List[str],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Auto-generate sitemap entries from a list of URLs"""
    
    org_id = ensure_organization_context(current_user)
    
    created_count = seo_service.auto_generate_sitemap_entries(db, org_id, urls)
    
    return SitemapGeneration(
        total_urls=created_count,
        generated_at=datetime.utcnow(),
        sitemap_url="/api/v1/seo/sitemap.xml",
        last_modified=datetime.utcnow()
    )


# Analytics Integration Management

@router.post("/analytics", response_model=AnalyticsIntegrationInDB, status_code=status.HTTP_201_CREATED)
async def create_analytics_integration(
    integration_data: AnalyticsIntegrationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new analytics integration"""
    
    org_id = ensure_organization_context(current_user)
    
    integration = seo_service.create_analytics_integration(
        db, integration_data, org_id, current_user.id
    )
    return integration


@router.get("/analytics", response_model=List[AnalyticsIntegrationInDB])
async def get_analytics_integrations(
    provider: Optional[str] = Query(None, description="Filter by provider"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get analytics integrations for the organization"""
    
    org_id = ensure_organization_context(current_user)
    integrations = seo_service.get_analytics_integrations(db, org_id, provider, is_active)
    return integrations


# Keyword Analysis

@router.post("/keywords", response_model=KeywordAnalysisInDB, status_code=status.HTTP_201_CREATED)
async def create_keyword_analysis(
    keyword_data: KeywordAnalysisCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new keyword analysis"""
    
    org_id = ensure_organization_context(current_user)
    
    keyword = seo_service.create_keyword_analysis(
        db, keyword_data, org_id, current_user.id
    )
    return keyword


@router.get("/keywords", response_model=List[KeywordAnalysisInDB])
async def get_keyword_analysis(
    is_target_keyword: Optional[bool] = Query(None, description="Filter by target keyword status"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    skip: int = Query(0, ge=0, description="Number of keywords to skip"),
    limit: int = Query(100, ge=1, le=100, description="Number of keywords to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get keyword analysis for the organization"""
    
    org_id = ensure_organization_context(current_user)
    keywords = seo_service.get_keyword_analysis(db, org_id, is_target_keyword, priority, skip, limit)
    return keywords


@router.get("/keywords/report", response_model=KeywordReport)
async def get_keyword_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get comprehensive keyword analysis report"""
    
    org_id = ensure_organization_context(current_user)
    report = seo_service.get_keyword_report(db, org_id)
    return report


@router.post("/keywords/bulk-import", response_model=BulkKeywordImportResponse)
async def bulk_import_keywords(
    import_data: BulkKeywordImport,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Bulk import keyword analysis data"""
    
    org_id = ensure_organization_context(current_user)
    
    results = {
        "imported_count": 0,
        "updated_count": 0,
        "failed_count": 0,
        "errors": []
    }
    
    for keyword_data in import_data.keywords:
        try:
            # Check if keyword already exists
            existing = db.query(KeywordAnalysis).filter(
                and_(
                    KeywordAnalysis.organization_id == org_id,
                    KeywordAnalysis.keyword == keyword_data.keyword
                )
            ).first()
            
            if existing and import_data.overwrite_existing:
                # Update existing
                for field, value in keyword_data.dict(exclude_unset=True).items():
                    setattr(existing, field, value)
                db.commit()
                results["updated_count"] += 1
            elif not existing:
                # Create new
                seo_service.create_keyword_analysis(db, keyword_data, org_id, current_user.id)
                results["imported_count"] += 1
            else:
                results["failed_count"] += 1
                results["errors"].append(f"Keyword '{keyword_data.keyword}' already exists")
                
        except Exception as e:
            results["failed_count"] += 1
            results["errors"].append(f"Failed to import '{keyword_data.keyword}': {str(e)}")
            logger.error(f"Keyword import error: {str(e)}")
    
    return results


# Competitor Analysis

@router.post("/competitors", response_model=CompetitorAnalysisInDB, status_code=status.HTTP_201_CREATED)
async def create_competitor_analysis(
    competitor_data: CompetitorAnalysisCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new competitor analysis"""
    
    org_id = ensure_organization_context(current_user)
    
    competitor = seo_service.create_competitor_analysis(
        db, competitor_data, org_id, current_user.id
    )
    return competitor


@router.get("/competitors", response_model=List[CompetitorAnalysisInDB])
async def get_competitor_analysis(
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    skip: int = Query(0, ge=0, description="Number of competitors to skip"),
    limit: int = Query(100, ge=1, le=100, description="Number of competitors to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get competitor analysis for the organization"""
    
    org_id = ensure_organization_context(current_user)
    competitors = seo_service.get_competitor_analysis(db, org_id, is_active, skip, limit)
    return competitors


# Utility Endpoints

@router.get("/meta-tags/generate-suggestions")
async def generate_meta_tag_suggestions(
    page_path: str = Query(..., description="Page path to generate suggestions for"),
    content: Optional[str] = Query(None, description="Page content for analysis"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Generate SEO meta tag suggestions for a page"""
    
    org_id = ensure_organization_context(current_user)
    
    # TODO: Implement AI-powered meta tag suggestions based on content
    # This could use NLP to analyze page content and suggest optimal titles/descriptions
    
    suggestions = {
        "title_suggestions": [
            f"Page Title for {page_path}",
            f"Optimized {page_path} - Your Business",
            f"Best {page_path} Solutions"
        ],
        "description_suggestions": [
            f"Discover our comprehensive {page_path} solutions designed to help your business grow.",
            f"Expert {page_path} services tailored to your needs. Get started today.",
            f"Professional {page_path} with proven results. Contact us for more information."
        ],
        "keyword_suggestions": [
            page_path.strip('/').replace('-', ' ').replace('/', ' '),
            f"{page_path} services",
            f"best {page_path}"
        ]
    }
    
    return suggestions


@router.post("/test-meta-tags")
async def test_meta_tags(
    url: str = Query(..., description="URL to test meta tags"),
    current_user: User = Depends(get_current_active_user)
):
    """Test and analyze meta tags for a given URL"""
    
    # TODO: Implement URL meta tag scraping and analysis
    # This would fetch the URL and analyze existing meta tags
    
    return {
        "url": url,
        "message": "Meta tag testing functionality is not yet implemented",
        "suggestions": [
            "Implement URL scraping",
            "Analyze existing meta tags",
            "Compare with SEO best practices",
            "Provide improvement recommendations"
        ]
    }


from datetime import datetime