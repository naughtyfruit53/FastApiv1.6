# app/services/seo_service.py

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func
from datetime import datetime, timezone
import xml.etree.ElementTree as ET
from xml.dom import minidom

from app.models.seo_models import (
    SEOMetaTag, SitemapEntry, AnalyticsIntegration, 
    KeywordAnalysis, CompetitorAnalysis
)
from app.schemas.seo import (
    SEOMetaTagCreate, SEOMetaTagUpdate, SEOMetaTagInDB,
    SitemapEntryCreate, SitemapEntryUpdate, SitemapEntryInDB,
    AnalyticsIntegrationCreate, AnalyticsIntegrationUpdate, AnalyticsIntegrationInDB,
    KeywordAnalysisCreate, KeywordAnalysisUpdate, KeywordAnalysisInDB,
    CompetitorAnalysisCreate, CompetitorAnalysisUpdate, CompetitorAnalysisInDB,
    SEODashboard, KeywordReport, CompetitorReport, SitemapGeneration, SEOAudit
)
import logging

logger = logging.getLogger(__name__)


class SEOService:
    """Service for managing SEO, meta tags, sitemaps, and analytics"""
    
    def __init__(self):
        pass
    
    # SEO Meta Tag Management
    
    def create_meta_tag(
        self, 
        db: Session, 
        tag_data: SEOMetaTagCreate, 
        organization_id: int, 
        created_by_id: int
    ) -> SEOMetaTag:
        """Create a new SEO meta tag"""
        
        db_tag = SEOMetaTag(
            organization_id=organization_id,
            created_by_id=created_by_id,
            **tag_data.dict()
        )
        
        db.add(db_tag)
        db.commit()
        db.refresh(db_tag)
        
        logger.info(f"Created SEO meta tag for {tag_data.page_path} in organization {organization_id}")
        return db_tag
    
    def get_meta_tags(
        self, 
        db: Session, 
        organization_id: int,
        page_path: Optional[str] = None,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[SEOMetaTag]:
        """Get SEO meta tags for an organization"""
        
        query = db.query(SEOMetaTag).filter(SEOMetaTag.organization_id == organization_id)
        
        if page_path:
            query = query.filter(SEOMetaTag.page_path == page_path)
        if is_active is not None:
            query = query.filter(SEOMetaTag.is_active == is_active)
        
        return query.order_by(SEOMetaTag.priority.desc(), SEOMetaTag.created_at.desc()).offset(skip).limit(limit).all()
    
    def get_meta_tag_for_page(self, db: Session, organization_id: int, page_path: str) -> Optional[SEOMetaTag]:
        """Get the active meta tag for a specific page"""
        
        return db.query(SEOMetaTag).filter(
            and_(
                SEOMetaTag.organization_id == organization_id,
                SEOMetaTag.page_path == page_path,
                SEOMetaTag.is_active == True
            )
        ).order_by(SEOMetaTag.priority.desc()).first()
    
    def update_meta_tag(
        self, 
        db: Session, 
        tag_id: int, 
        organization_id: int, 
        tag_data: SEOMetaTagUpdate
    ) -> Optional[SEOMetaTag]:
        """Update an SEO meta tag"""
        
        db_tag = db.query(SEOMetaTag).filter(
            and_(SEOMetaTag.id == tag_id, SEOMetaTag.organization_id == organization_id)
        ).first()
        
        if not db_tag:
            return None
        
        update_data = tag_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_tag, field, value)
        
        db.commit()
        db.refresh(db_tag)
        
        logger.info(f"Updated SEO meta tag {tag_id}")
        return db_tag
    
    def delete_meta_tag(self, db: Session, tag_id: int, organization_id: int) -> bool:
        """Delete an SEO meta tag"""
        
        db_tag = db.query(SEOMetaTag).filter(
            and_(SEOMetaTag.id == tag_id, SEOMetaTag.organization_id == organization_id)
        ).first()
        
        if not db_tag:
            return False
        
        db.delete(db_tag)
        db.commit()
        
        logger.info(f"Deleted SEO meta tag {tag_id}")
        return True
    
    # Sitemap Management
    
    def create_sitemap_entry(
        self, 
        db: Session, 
        entry_data: SitemapEntryCreate, 
        organization_id: int
    ) -> SitemapEntry:
        """Create a new sitemap entry"""
        
        db_entry = SitemapEntry(
            organization_id=organization_id,
            **entry_data.dict()
        )
        
        db.add(db_entry)
        db.commit()
        db.refresh(db_entry)
        
        logger.info(f"Created sitemap entry for {entry_data.url} in organization {organization_id}")
        return db_entry
    
    def get_sitemap_entries(
        self, 
        db: Session, 
        organization_id: int,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 1000
    ) -> List[SitemapEntry]:
        """Get sitemap entries for an organization"""
        
        query = db.query(SitemapEntry).filter(SitemapEntry.organization_id == organization_id)
        
        if is_active is not None:
            query = query.filter(SitemapEntry.is_active == is_active)
        
        return query.order_by(SitemapEntry.priority.desc(), SitemapEntry.url).offset(skip).limit(limit).all()
    
    def generate_sitemap_xml(self, db: Session, organization_id: int, base_url: str) -> str:
        """Generate XML sitemap for an organization"""
        
        entries = self.get_sitemap_entries(db, organization_id, is_active=True)
        
        # Create XML structure
        urlset = ET.Element("urlset")
        urlset.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")
        
        for entry in entries:
            url_elem = ET.SubElement(urlset, "url")
            
            # Location (required)
            loc = ET.SubElement(url_elem, "loc")
            loc.text = f"{base_url.rstrip('/')}{entry.url}"
            
            # Last modified
            if entry.last_modified:
                lastmod = ET.SubElement(url_elem, "lastmod")
                lastmod.text = entry.last_modified.strftime("%Y-%m-%d")
            
            # Change frequency
            changefreq = ET.SubElement(url_elem, "changefreq")
            changefreq.text = entry.change_frequency
            
            # Priority
            priority = ET.SubElement(url_elem, "priority")
            priority.text = str(entry.priority)
        
        # Convert to pretty XML string
        rough_string = ET.tostring(urlset, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        
        logger.info(f"Generated sitemap XML with {len(entries)} entries for organization {organization_id}")
        return reparsed.toprettyxml(indent="  ")
    
    def auto_generate_sitemap_entries(self, db: Session, organization_id: int, urls: List[str]) -> int:
        """Auto-generate sitemap entries from a list of URLs"""
        
        created_count = 0
        
        for url in urls:
            # Check if entry already exists
            existing = db.query(SitemapEntry).filter(
                and_(
                    SitemapEntry.organization_id == organization_id,
                    SitemapEntry.url == url
                )
            ).first()
            
            if not existing:
                entry_data = SitemapEntryCreate(
                    url=url,
                    priority=0.5,
                    change_frequency="monthly",
                    auto_generated=True
                )
                
                self.create_sitemap_entry(db, entry_data, organization_id)
                created_count += 1
        
        logger.info(f"Auto-generated {created_count} sitemap entries for organization {organization_id}")
        return created_count
    
    # Analytics Integration Management
    
    def create_analytics_integration(
        self, 
        db: Session, 
        integration_data: AnalyticsIntegrationCreate, 
        organization_id: int, 
        created_by_id: int
    ) -> AnalyticsIntegration:
        """Create a new analytics integration"""
        
        db_integration = AnalyticsIntegration(
            organization_id=organization_id,
            created_by_id=created_by_id,
            **integration_data.dict()
        )
        
        db.add(db_integration)
        db.commit()
        db.refresh(db_integration)
        
        logger.info(f"Created analytics integration {integration_data.provider} for organization {organization_id}")
        return db_integration
    
    def get_analytics_integrations(
        self, 
        db: Session, 
        organization_id: int,
        provider: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> List[AnalyticsIntegration]:
        """Get analytics integrations for an organization"""
        
        query = db.query(AnalyticsIntegration).filter(AnalyticsIntegration.organization_id == organization_id)
        
        if provider:
            query = query.filter(AnalyticsIntegration.provider == provider)
        if is_active is not None:
            query = query.filter(AnalyticsIntegration.is_active == is_active)
        
        return query.order_by(AnalyticsIntegration.created_at.desc()).all()
    
    # Keyword Analysis
    
    def create_keyword_analysis(
        self, 
        db: Session, 
        keyword_data: KeywordAnalysisCreate, 
        organization_id: int, 
        created_by_id: int
    ) -> KeywordAnalysis:
        """Create a new keyword analysis"""
        
        db_keyword = KeywordAnalysis(
            organization_id=organization_id,
            created_by_id=created_by_id,
            **keyword_data.dict()
        )
        
        db.add(db_keyword)
        db.commit()
        db.refresh(db_keyword)
        
        logger.info(f"Created keyword analysis for '{keyword_data.keyword}' in organization {organization_id}")
        return db_keyword
    
    def get_keyword_analysis(
        self, 
        db: Session, 
        organization_id: int,
        is_target_keyword: Optional[bool] = None,
        priority: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[KeywordAnalysis]:
        """Get keyword analysis for an organization"""
        
        query = db.query(KeywordAnalysis).filter(KeywordAnalysis.organization_id == organization_id)
        
        if is_target_keyword is not None:
            query = query.filter(KeywordAnalysis.is_target_keyword == is_target_keyword)
        if priority:
            query = query.filter(KeywordAnalysis.priority == priority)
        
        return query.order_by(KeywordAnalysis.analysis_date.desc()).offset(skip).limit(limit).all()
    
    def get_keyword_report(self, db: Session, organization_id: int) -> KeywordReport:
        """Generate keyword analysis report"""
        
        # Get basic counts
        total_keywords = db.query(func.count(KeywordAnalysis.id)).filter(
            KeywordAnalysis.organization_id == organization_id
        ).scalar()
        
        target_keywords = db.query(func.count(KeywordAnalysis.id)).filter(
            and_(
                KeywordAnalysis.organization_id == organization_id,
                KeywordAnalysis.is_target_keyword == True
            )
        ).scalar()
        
        # Get averages
        avg_search_volume = db.query(func.avg(KeywordAnalysis.search_volume)).filter(
            and_(
                KeywordAnalysis.organization_id == organization_id,
                KeywordAnalysis.search_volume.isnot(None)
            )
        ).scalar()
        
        avg_difficulty = db.query(func.avg(KeywordAnalysis.difficulty)).filter(
            and_(
                KeywordAnalysis.organization_id == organization_id,
                KeywordAnalysis.difficulty.isnot(None)
            )
        ).scalar()
        
        avg_ranking = db.query(func.avg(KeywordAnalysis.current_ranking)).filter(
            and_(
                KeywordAnalysis.organization_id == organization_id,
                KeywordAnalysis.current_ranking.isnot(None)
            )
        ).scalar()
        
        # Get keyword distribution by priority
        priority_distribution = db.query(
            KeywordAnalysis.priority,
            func.count(KeywordAnalysis.id)
        ).filter(
            KeywordAnalysis.organization_id == organization_id
        ).group_by(KeywordAnalysis.priority).all()
        
        # Get top opportunities (high search volume, low difficulty, not ranking well)
        top_opportunities = db.query(KeywordAnalysis).filter(
            and_(
                KeywordAnalysis.organization_id == organization_id,
                KeywordAnalysis.search_volume > 1000,
                KeywordAnalysis.difficulty < 50,
                KeywordAnalysis.current_ranking > 10
            )
        ).order_by(KeywordAnalysis.search_volume.desc()).limit(10).all()
        
        return KeywordReport(
            total_keywords=total_keywords or 0,
            target_keywords=target_keywords or 0,
            avg_search_volume=float(avg_search_volume) if avg_search_volume else None,
            avg_difficulty=float(avg_difficulty) if avg_difficulty else None,
            avg_ranking=float(avg_ranking) if avg_ranking else None,
            keyword_distribution={priority: count for priority, count in priority_distribution},
            top_opportunities=top_opportunities,
            ranking_improvements=[]  # TODO: Implement ranking change tracking
        )
    
    # Competitor Analysis
    
    def create_competitor_analysis(
        self, 
        db: Session, 
        competitor_data: CompetitorAnalysisCreate, 
        organization_id: int, 
        created_by_id: int
    ) -> CompetitorAnalysis:
        """Create a new competitor analysis"""
        
        db_competitor = CompetitorAnalysis(
            organization_id=organization_id,
            created_by_id=created_by_id,
            **competitor_data.dict()
        )
        
        db.add(db_competitor)
        db.commit()
        db.refresh(db_competitor)
        
        logger.info(f"Created competitor analysis for {competitor_data.competitor_domain} in organization {organization_id}")
        return db_competitor
    
    def get_competitor_analysis(
        self, 
        db: Session, 
        organization_id: int,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[CompetitorAnalysis]:
        """Get competitor analysis for an organization"""
        
        query = db.query(CompetitorAnalysis).filter(CompetitorAnalysis.organization_id == organization_id)
        
        if is_active is not None:
            query = query.filter(CompetitorAnalysis.is_active_competitor == is_active)
        
        return query.order_by(CompetitorAnalysis.analysis_date.desc()).offset(skip).limit(limit).all()
    
    # Dashboard and Reporting
    
    def get_seo_dashboard(self, db: Session, organization_id: int) -> SEODashboard:
        """Get SEO dashboard overview"""
        
        # Get counts
        total_pages = db.query(func.count(SEOMetaTag.id.distinct())).filter(
            SEOMetaTag.organization_id == organization_id
        ).scalar()
        
        meta_tags_configured = db.query(func.count(SEOMetaTag.id)).filter(
            and_(
                SEOMetaTag.organization_id == organization_id,
                SEOMetaTag.is_active == True
            )
        ).scalar()
        
        sitemap_entries = db.query(func.count(SitemapEntry.id)).filter(
            and_(
                SitemapEntry.organization_id == organization_id,
                SitemapEntry.is_active == True
            )
        ).scalar()
        
        analytics_integrations = db.query(func.count(AnalyticsIntegration.id)).filter(
            and_(
                AnalyticsIntegration.organization_id == organization_id,
                AnalyticsIntegration.is_active == True
            )
        ).scalar()
        
        tracked_keywords = db.query(func.count(KeywordAnalysis.id)).filter(
            KeywordAnalysis.organization_id == organization_id
        ).scalar()
        
        target_keywords = db.query(func.count(KeywordAnalysis.id)).filter(
            and_(
                KeywordAnalysis.organization_id == organization_id,
                KeywordAnalysis.is_target_keyword == True
            )
        ).scalar()
        
        competitors_monitored = db.query(func.count(CompetitorAnalysis.id)).filter(
            and_(
                CompetitorAnalysis.organization_id == organization_id,
                CompetitorAnalysis.is_active_competitor == True
            )
        ).scalar()
        
        # Get average keyword ranking
        avg_keyword_ranking = db.query(func.avg(KeywordAnalysis.current_ranking)).filter(
            and_(
                KeywordAnalysis.organization_id == organization_id,
                KeywordAnalysis.current_ranking.isnot(None)
            )
        ).scalar()
        
        return SEODashboard(
            total_pages=total_pages or 0,
            meta_tags_configured=meta_tags_configured or 0,
            sitemap_entries=sitemap_entries or 0,
            analytics_integrations=analytics_integrations or 0,
            tracked_keywords=tracked_keywords or 0,
            target_keywords=target_keywords or 0,
            competitors_monitored=competitors_monitored or 0,
            avg_keyword_ranking=float(avg_keyword_ranking) if avg_keyword_ranking else None,
            recent_keyword_changes=[]  # TODO: Implement keyword change tracking
        )
    
    def run_seo_audit(self, db: Session, organization_id: int) -> SEOAudit:
        """Run comprehensive SEO audit"""
        
        issues = []
        recommendations = []
        meta_tag_issues = []
        score = 100.0
        
        # Check meta tag coverage
        total_pages = db.query(func.count(SEOMetaTag.page_path.distinct())).filter(
            SEOMetaTag.organization_id == organization_id
        ).scalar()
        
        pages_with_meta = db.query(func.count(SEOMetaTag.id.distinct())).filter(
            and_(
                SEOMetaTag.organization_id == organization_id,
                SEOMetaTag.is_active == True,
                SEOMetaTag.title.isnot(None),
                SEOMetaTag.meta_description.isnot(None)
            )
        ).scalar()
        
        if total_pages and pages_with_meta:
            meta_coverage = (pages_with_meta / total_pages) * 100
            if meta_coverage < 80:
                score -= 20
                issues.append({
                    "type": "meta_tags",
                    "severity": "high",
                    "message": f"Only {meta_coverage:.1f}% of pages have complete meta tags"
                })
                recommendations.append("Add title and meta description tags to all pages")
        
        # Check for analytics integration
        analytics_count = db.query(func.count(AnalyticsIntegration.id)).filter(
            and_(
                AnalyticsIntegration.organization_id == organization_id,
                AnalyticsIntegration.is_active == True
            )
        ).scalar()
        
        if not analytics_count:
            score -= 15
            issues.append({
                "type": "analytics",
                "severity": "medium",
                "message": "No analytics integration configured"
            })
            recommendations.append("Set up Google Analytics or similar tracking")
        
        # Check sitemap
        sitemap_count = db.query(func.count(SitemapEntry.id)).filter(
            and_(
                SitemapEntry.organization_id == organization_id,
                SitemapEntry.is_active == True
            )
        ).scalar()
        
        if not sitemap_count:
            score -= 10
            issues.append({
                "type": "sitemap",
                "severity": "medium",
                "message": "No sitemap entries found"
            })
            recommendations.append("Generate and submit a sitemap to search engines")
        
        return SEOAudit(
            audit_date=datetime.now(timezone.utc),
            score=max(score, 0.0),
            issues=issues,
            recommendations=recommendations,
            meta_tag_issues=meta_tag_issues,
            sitemap_status={"entries": sitemap_count or 0},
            analytics_status={"integrations": analytics_count or 0}
        )


# Global service instance
seo_service = SEOService()