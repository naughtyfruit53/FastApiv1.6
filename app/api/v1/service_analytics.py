# app/api/v1/service_analytics.py

"""
Service Analytics API endpoints for Service CRM.
Provides RBAC-protected endpoints for analytics data and reporting.
"""

from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import User, InstallationJob, Customer
from app.services.service_analytics_service import ServiceAnalyticsService, get_service_analytics_service
from app.schemas.service_analytics import (
    AnalyticsRequest, ReportConfigurationRequest, ReportPeriod, MetricType,
    JobCompletionMetrics, TechnicianPerformanceMetrics, CustomerSatisfactionMetrics,
    JobVolumeMetrics, SLAComplianceMetrics, AnalyticsDashboard, ReportConfiguration,
    ExportRequest, AnalyticsErrorResponse
)
from app.core.rbac_dependencies import (
    require_same_organization, require_analytics_read, require_analytics_manage,
    require_analytics_export
)
from app.core.tenant import require_current_organization_id
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


# Analytics Metrics Endpoints
@router.get("/organizations/{organization_id}/analytics/dashboard", response_model=AnalyticsDashboard)
async def get_analytics_dashboard(
    organization_id: int = Path(..., description="Organization ID"),
    period: ReportPeriod = Query(ReportPeriod.MONTH, description="Report period"),
    start_date: Optional[date] = Query(None, description="Custom start date"),
    end_date: Optional[date] = Query(None, description="Custom end date"),
    technician_id: Optional[int] = Query(None, description="Filter by technician"),
    customer_id: Optional[int] = Query(None, description="Filter by customer"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analytics_read),
    _: int = Depends(require_same_organization)
):
    """Get complete analytics dashboard with all metrics"""
    logger.info(f"User {current_user.id} requesting analytics dashboard for organization {organization_id}")
    
    try:
        analytics_service = ServiceAnalyticsService(db, organization_id)
        dashboard = analytics_service.get_analytics_dashboard(
            period=period,
            start_date=start_date,
            end_date=end_date,
            technician_id=technician_id,
            customer_id=customer_id
        )
        return dashboard
    except Exception as e:
        logger.error(f"Error generating analytics dashboard: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate analytics dashboard: {str(e)}"
        )


@router.get("/organizations/{organization_id}/analytics/job-completion", response_model=JobCompletionMetrics)
async def get_job_completion_metrics(
    organization_id: int = Path(..., description="Organization ID"),
    period: ReportPeriod = Query(ReportPeriod.MONTH, description="Report period"),
    start_date: Optional[date] = Query(None, description="Custom start date"),
    end_date: Optional[date] = Query(None, description="Custom end date"),
    technician_id: Optional[int] = Query(None, description="Filter by technician"),
    customer_id: Optional[int] = Query(None, description="Filter by customer"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analytics_read),
    _: int = Depends(require_same_organization)
):
    """Get job completion metrics"""
    logger.info(f"User {current_user.id} requesting job completion metrics for organization {organization_id}")
    
    try:
        analytics_service = ServiceAnalyticsService(db, organization_id)
        date_start, date_end = analytics_service.get_date_range(period, start_date, end_date)
        
        metrics = analytics_service.get_job_completion_metrics(
            start_date=date_start,
            end_date=date_end,
            technician_id=technician_id,
            customer_id=customer_id
        )
        return metrics
    except Exception as e:
        logger.error(f"Error getting job completion metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get job completion metrics: {str(e)}"
        )


@router.get("/organizations/{organization_id}/analytics/technician-performance", response_model=List[TechnicianPerformanceMetrics])
async def get_technician_performance_metrics(
    organization_id: int = Path(..., description="Organization ID"),
    period: ReportPeriod = Query(ReportPeriod.MONTH, description="Report period"),
    start_date: Optional[date] = Query(None, description="Custom start date"),
    end_date: Optional[date] = Query(None, description="Custom end date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analytics_manage),  # Managers only
    _: int = Depends(require_same_organization)
):
    """Get technician performance metrics - Managers only"""
    logger.info(f"User {current_user.id} requesting technician performance metrics for organization {organization_id}")
    
    try:
        analytics_service = ServiceAnalyticsService(db, organization_id)
        date_start, date_end = analytics_service.get_date_range(period, start_date, end_date)
        
        metrics = analytics_service.get_technician_performance_metrics(
            start_date=date_start,
            end_date=date_end
        )
        return metrics
    except Exception as e:
        logger.error(f"Error getting technician performance metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get technician performance metrics: {str(e)}"
        )


@router.get("/organizations/{organization_id}/analytics/customer-satisfaction", response_model=CustomerSatisfactionMetrics)
async def get_customer_satisfaction_metrics(
    organization_id: int = Path(..., description="Organization ID"),
    period: ReportPeriod = Query(ReportPeriod.MONTH, description="Report period"),
    start_date: Optional[date] = Query(None, description="Custom start date"),
    end_date: Optional[date] = Query(None, description="Custom end date"),
    technician_id: Optional[int] = Query(None, description="Filter by technician"),
    customer_id: Optional[int] = Query(None, description="Filter by customer"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analytics_read),
    _: int = Depends(require_same_organization)
):
    """Get customer satisfaction metrics"""
    logger.info(f"User {current_user.id} requesting customer satisfaction metrics for organization {organization_id}")
    
    try:
        analytics_service = ServiceAnalyticsService(db, organization_id)
        date_start, date_end = analytics_service.get_date_range(period, start_date, end_date)
        
        metrics = analytics_service.get_customer_satisfaction_metrics(
            start_date=date_start,
            end_date=date_end,
            technician_id=technician_id,
            customer_id=customer_id
        )
        return metrics
    except Exception as e:
        logger.error(f"Error getting customer satisfaction metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get customer satisfaction metrics: {str(e)}"
        )


@router.get("/organizations/{organization_id}/analytics/job-volume", response_model=JobVolumeMetrics)
async def get_job_volume_metrics(
    organization_id: int = Path(..., description="Organization ID"),
    period: ReportPeriod = Query(ReportPeriod.MONTH, description="Report period"),
    start_date: Optional[date] = Query(None, description="Custom start date"),
    end_date: Optional[date] = Query(None, description="Custom end date"),
    technician_id: Optional[int] = Query(None, description="Filter by technician"),
    customer_id: Optional[int] = Query(None, description="Filter by customer"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analytics_read),
    _: int = Depends(require_same_organization)
):
    """Get job volume metrics"""
    logger.info(f"User {current_user.id} requesting job volume metrics for organization {organization_id}")
    
    try:
        analytics_service = ServiceAnalyticsService(db, organization_id)
        date_start, date_end = analytics_service.get_date_range(period, start_date, end_date)
        
        metrics = analytics_service.get_job_volume_metrics(
            start_date=date_start,
            end_date=date_end,
            technician_id=technician_id,
            customer_id=customer_id
        )
        return metrics
    except Exception as e:
        logger.error(f"Error getting job volume metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get job volume metrics: {str(e)}"
        )


@router.get("/organizations/{organization_id}/analytics/sla-compliance", response_model=SLAComplianceMetrics)
async def get_sla_compliance_metrics(
    organization_id: int = Path(..., description="Organization ID"),
    period: ReportPeriod = Query(ReportPeriod.MONTH, description="Report period"),
    start_date: Optional[date] = Query(None, description="Custom start date"),
    end_date: Optional[date] = Query(None, description="Custom end date"),
    technician_id: Optional[int] = Query(None, description="Filter by technician"),
    customer_id: Optional[int] = Query(None, description="Filter by customer"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analytics_manage),  # Managers only
    _: int = Depends(require_same_organization)
):
    """Get SLA compliance metrics - Managers only"""
    logger.info(f"User {current_user.id} requesting SLA compliance metrics for organization {organization_id}")
    
    try:
        analytics_service = ServiceAnalyticsService(db, organization_id)
        date_start, date_end = analytics_service.get_date_range(period, start_date, end_date)
        
        metrics = analytics_service.get_sla_compliance_metrics(
            start_date=date_start,
            end_date=date_end,
            technician_id=technician_id,
            customer_id=customer_id
        )
        return metrics
    except Exception as e:
        logger.error(f"Error getting SLA compliance metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get SLA compliance metrics: {str(e)}"
        )


# Report Configuration Endpoints
@router.get("/organizations/{organization_id}/analytics/report-configurations", response_model=List[ReportConfiguration])
async def get_report_configurations(
    organization_id: int = Path(..., description="Organization ID"),
    active_only: bool = Query(True, description="Filter by active configurations"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analytics_read),
    _: int = Depends(require_same_organization)
):
    """Get all report configurations for the organization"""
    logger.info(f"User {current_user.id} requesting report configurations for organization {organization_id}")
    
    try:
        # This would be implemented when report configurations are fully developed
        return []
    except Exception as e:
        logger.error(f"Error getting report configurations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get report configurations: {str(e)}"
        )


@router.post("/organizations/{organization_id}/analytics/report-configurations", response_model=ReportConfiguration)
async def create_report_configuration(
    organization_id: int = Path(..., description="Organization ID"),
    config_request: ReportConfigurationRequest = ...,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analytics_manage),  # Managers only
    _: int = Depends(require_same_organization)
):
    """Create a new report configuration - Managers only"""
    logger.info(f"User {current_user.id} creating report configuration for organization {organization_id}")
    
    try:
        # This would be implemented when report configurations are fully developed
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Report configuration creation not yet implemented"
        )
    except Exception as e:
        logger.error(f"Error creating report configuration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create report configuration: {str(e)}"
        )


# Export Endpoints
@router.post("/organizations/{organization_id}/analytics/export")
async def export_analytics_data(
    organization_id: int = Path(..., description="Organization ID"),
    export_request: ExportRequest = ...,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analytics_export),  # Export permission required
    _: int = Depends(require_same_organization)
):
    """Export analytics data in specified format"""
    logger.info(f"User {current_user.id} requesting analytics data export for organization {organization_id}")
    
    try:
        # This would be implemented with the export service
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Analytics data export not yet implemented"
        )
    except Exception as e:
        logger.error(f"Error exporting analytics data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export analytics data: {str(e)}"
        )


# Utility Endpoints
@router.get("/organizations/{organization_id}/analytics/technicians")
async def get_available_technicians(
    organization_id: int = Path(..., description="Organization ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analytics_read),
    _: int = Depends(require_same_organization)
):
    """Get list of technicians available for filtering"""
    logger.info(f"User {current_user.id} requesting technician list for organization {organization_id}")
    
    try:
        # Get technicians who have been assigned to jobs
        technicians = db.query(User).join(
            InstallationJob, User.id == InstallationJob.assigned_technician_id
        ).filter(
            InstallationJob.organization_id == organization_id
        ).distinct().all()
        
        return [
            {
                "id": tech.id,
                "name": tech.full_name or f"Technician {tech.id}",
                "email": tech.email
            }
            for tech in technicians
        ]
    except Exception as e:
        logger.error(f"Error getting technician list: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get technician list: {str(e)}"
        )


@router.get("/organizations/{organization_id}/analytics/customers")
async def get_available_customers(
    organization_id: int = Path(..., description="Organization ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analytics_read),
    _: int = Depends(require_same_organization)
):
    """Get list of customers available for filtering"""
    logger.info(f"User {current_user.id} requesting customer list for organization {organization_id}")
    
    try:
        # Get customers who have had jobs
        customers = db.query(Customer).join(
            InstallationJob, Customer.id == InstallationJob.customer_id
        ).filter(
            InstallationJob.organization_id == organization_id
        ).distinct().all()
        
        return [
            {
                "id": customer.id,
                "name": customer.name,
                "email": customer.email
            }
            for customer in customers
        ]
    except Exception as e:
        logger.error(f"Error getting customer list: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get customer list: {str(e)}"
        )