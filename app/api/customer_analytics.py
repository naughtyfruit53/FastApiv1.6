# app/api/customer_analytics.py

"""
Customer Analytics API endpoints

Provides REST API endpoints for customer analytics and insights including:
- Individual customer analytics
- Segment-wide analytics
- Organization dashboard metrics
- Multi-tenant isolation
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.core.org_restrictions import ensure_organization_context
from app.models import User, Customer, CustomerSegment
from app.services.customer_analytics_service import CustomerAnalyticsService
from app.schemas.customer_analytics import (
    CustomerAnalyticsResponse,
    SegmentAnalyticsResponse,
    OrganizationAnalyticsSummary,
    DashboardMetrics,
    CustomerAnalyticsRequest,
    SegmentAnalyticsRequest,
    AnalyticsErrorResponse,
    ValidationErrorResponse
)
from app.core.tenant import TenantQueryMixin
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/customers/{customer_id}/analytics", response_model=CustomerAnalyticsResponse)
async def get_customer_analytics(
    customer_id: int,
    include_recent_interactions: bool = Query(True, description="Include recent interactions in response"),
    recent_interactions_limit: int = Query(5, ge=1, le=20, description="Number of recent interactions to include"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get comprehensive analytics for a specific customer.
    
    Returns metrics including:
    - Total interactions count
    - Last interaction date
    - Interaction breakdown by type and status
    - Current segment memberships
    - Recent interactions summary
    
    **Required permissions**: Standard user or above
    **Multi-tenant**: Data is automatically scoped to user's organization
    """
    try:
        # Ensure organization context
        org_id = ensure_organization_context(current_user)
        
        # Verify customer exists and belongs to organization
        customer = TenantQueryMixin.filter_by_tenant(
            db.query(Customer), Customer, org_id
        ).filter(Customer.id == customer_id).first()
        
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer with ID {customer_id} not found"
            )
        
        # Initialize analytics service
        analytics_service = CustomerAnalyticsService(db, org_id)
        
        # Get customer analytics
        analytics_data = analytics_service.get_customer_metrics(customer_id)
        
        if not analytics_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Analytics data not available for customer {customer_id}"
            )
        
        # Limit recent interactions if requested
        if include_recent_interactions and 'recent_interactions' in analytics_data:
            analytics_data['recent_interactions'] = analytics_data['recent_interactions'][:recent_interactions_limit]
        elif not include_recent_interactions:
            analytics_data['recent_interactions'] = []
        
        logger.info(f"Retrieved analytics for customer {customer_id} in organization {org_id}")
        return CustomerAnalyticsResponse(**analytics_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving customer analytics for customer {customer_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while retrieving customer analytics"
        )


@router.get("/segments/{segment_name}/analytics", response_model=SegmentAnalyticsResponse)
async def get_segment_analytics(
    segment_name: str,
    include_timeline: bool = Query(True, description="Include activity timeline"),
    timeline_days: int = Query(30, ge=7, le=365, description="Number of days for timeline"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get comprehensive analytics for a customer segment.
    
    Returns metrics including:
    - Total customers in segment
    - Total and average interactions
    - Interaction distribution by type
    - Activity timeline over specified period
    
    **Required permissions**: Standard user or above
    **Multi-tenant**: Data is automatically scoped to user's organization
    """
    try:
        # Ensure organization context
        org_id = ensure_organization_context(current_user)
        
        # Validate segment exists in organization
        segment_exists = TenantQueryMixin.filter_by_tenant(
            db.query(CustomerSegment), CustomerSegment, org_id
        ).filter(
            CustomerSegment.segment_name == segment_name,
            CustomerSegment.is_active == True
        ).first()
        
        if not segment_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Segment '{segment_name}' not found or has no active customers"
            )
        
        # Initialize analytics service
        analytics_service = CustomerAnalyticsService(db, org_id)
        
        # Get segment analytics
        analytics_data = analytics_service.get_segment_analytics(segment_name)
        
        # Filter timeline if not requested
        if not include_timeline:
            analytics_data['activity_timeline'] = []
        
        logger.info(f"Retrieved analytics for segment '{segment_name}' in organization {org_id}")
        return SegmentAnalyticsResponse(**analytics_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving segment analytics for segment '{segment_name}': {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while retrieving segment analytics"
        )


@router.get("/organization/summary", response_model=OrganizationAnalyticsSummary)
async def get_organization_analytics_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get high-level analytics summary for the entire organization.
    
    Returns metrics including:
    - Total customers and interactions
    - Customer distribution by segment
    - Interaction trends over time
    
    **Required permissions**: Standard user or above
    **Multi-tenant**: Data is automatically scoped to user's organization
    """
    try:
        # Ensure organization context
        org_id = ensure_organization_context(current_user)
        
        # Initialize analytics service
        analytics_service = CustomerAnalyticsService(db, org_id)
        
        # Get organization summary
        summary_data = analytics_service.get_organization_analytics_summary()
        
        logger.info(f"Retrieved organization analytics summary for organization {org_id}")
        return OrganizationAnalyticsSummary(**summary_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving organization analytics summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while retrieving organization analytics"
        )


@router.get("/dashboard/metrics", response_model=DashboardMetrics)
async def get_dashboard_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get key metrics for analytics dashboard.
    
    Returns quick metrics including:
    - Customer counts
    - Interaction counts (today, week, month)
    - Top segments
    - Recent activity
    
    **Required permissions**: Standard user or above
    **Multi-tenant**: Data is automatically scoped to user's organization
    """
    try:
        # Ensure organization context
        org_id = ensure_organization_context(current_user)
        
        # Initialize analytics service
        analytics_service = CustomerAnalyticsService(db, org_id)
        
        # Get organization summary for base metrics
        summary_data = analytics_service.get_organization_analytics_summary()
        
        # Calculate additional dashboard-specific metrics
        from datetime import datetime, timedelta
        from sqlalchemy import and_
        from app.models.base import CustomerInteraction
        
        today = datetime.utcnow().date()
        week_start = today - timedelta(days=7)
        month_start = today - timedelta(days=30)
        
        # Interactions today
        interactions_today = TenantQueryMixin.filter_by_tenant(
            db.query(CustomerInteraction), CustomerInteraction, org_id
        ).filter(
            CustomerInteraction.interaction_date >= datetime.combine(today, datetime.min.time())
        ).count()
        
        # Interactions this week
        interactions_week = TenantQueryMixin.filter_by_tenant(
            db.query(CustomerInteraction), CustomerInteraction, org_id
        ).filter(
            CustomerInteraction.interaction_date >= datetime.combine(week_start, datetime.min.time())
        ).count()
        
        # Interactions this month
        interactions_month = TenantQueryMixin.filter_by_tenant(
            db.query(CustomerInteraction), CustomerInteraction, org_id
        ).filter(
            CustomerInteraction.interaction_date >= datetime.combine(month_start, datetime.min.time())
        ).count()
        
        # Top segments (by customer count)
        top_segments = [
            {"segment_name": segment, "customer_count": count}
            for segment, count in sorted(
                summary_data["segment_distribution"].items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
        ]
        
        # Recent activity (last 5 days from trends)
        recent_activity = summary_data["interaction_trends"][-5:] if summary_data["interaction_trends"] else []
        
        dashboard_data = {
            "total_customers": summary_data["total_customers"],
            "total_interactions_today": interactions_today,
            "total_interactions_week": interactions_week,
            "total_interactions_month": interactions_month,
            "top_segments": top_segments,
            "recent_activity": recent_activity,
            "calculated_at": datetime.utcnow()
        }
        
        logger.info(f"Retrieved dashboard metrics for organization {org_id}")
        return DashboardMetrics(**dashboard_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving dashboard metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while retrieving dashboard metrics"
        )


@router.get("/segments", response_model=List[str])
async def list_available_segments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get list of available customer segments in the organization.
    
    **Required permissions**: Standard user or above
    **Multi-tenant**: Data is automatically scoped to user's organization
    """
    try:
        # Ensure organization context
        org_id = ensure_organization_context(current_user)
        
        # Get distinct segment names
        segments = TenantQueryMixin.filter_by_tenant(
            db.query(CustomerSegment), CustomerSegment, org_id
        ).filter(CustomerSegment.is_active == True).with_entities(
            CustomerSegment.segment_name
        ).distinct().all()
        
        segment_names = [segment[0] for segment in segments]
        
        logger.info(f"Retrieved {len(segment_names)} segments for organization {org_id}")
        return segment_names
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving segments list: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while retrieving segments"
        )