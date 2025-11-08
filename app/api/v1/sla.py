# app/api/v1/sla.py

"""
SLA Management API endpoints for Service CRM.
Provides RBAC-protected endpoints for SLA policies and tracking.
"""

from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.enforcement import require_access
from app.models import User
from app.services.sla import SLAService, get_sla_service
from app.schemas.sla import (
    SLAPolicyCreate, SLAPolicyUpdate, SLAPolicyResponse, SLAPolicyInDB,
    SLATrackingResponse, SLATrackingUpdate, SLATrackingWithPolicy,
    SLAMetrics, SLADashboard, SLAPolicyAssignment, SLAPolicyAssignmentResponse,
    TicketWithSLA
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


# SLA Policy Management Endpoints
@router.get("/organizations/{organization_id}/policies", response_model=List[SLAPolicyResponse])
async def get_sla_policies(
    organization_id: int = Path(..., description="Organization ID"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    auth: tuple = Depends(require_access("sla", "read")),
    sla_service: SLAService = Depends(get_sla_service),
    db: Session = Depends(get_db)
):
    """Get all SLA policies for an organization"""
    logger.info(f"User {current_user.id} requesting SLA policies for organization {organization_id}")
    
    policies = sla_service.get_policies(organization_id, is_active=is_active)
    return policies


@router.post("/organizations/{organization_id}/policies", response_model=SLAPolicyResponse)
async def create_sla_policy(
    organization_id: int = Path(..., description="Organization ID"),
    policy: SLAPolicyCreate = ...,
    auth: tuple = Depends(require_access("sla", "create")),
    sla_service: SLAService = Depends(get_sla_service),
    db: Session = Depends(get_db)
):
    """Create a new SLA policy"""
    logger.info(f"User {current_user.id} creating SLA policy '{policy.name}' for organization {organization_id}")
    
    try:
        db_policy = sla_service.create_policy(
            policy_data=policy,
            organization_id=organization_id,
            created_by_id=current_user.id
        )
        return db_policy
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating SLA policy: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create SLA policy"
        )


@router.get("/organizations/{organization_id}/policies/{policy_id}", response_model=SLAPolicyResponse)
async def get_sla_policy(
    organization_id: int = Path(..., description="Organization ID"),
    policy_id: int = Path(..., description="SLA Policy ID"),
    sla_service: SLAService = Depends(get_sla_service),
    auth: tuple = Depends(require_access("sla", "read"))
):
    """Get a specific SLA policy"""
    logger.info(f"User {current_user.id} requesting SLA policy {policy_id}")
    
    policy = sla_service.get_policy(policy_id, organization_id)
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SLA policy not found"
        )
    
    return policy


@router.put("/organizations/{organization_id}/policies/{policy_id}", response_model=SLAPolicyResponse)
async def update_sla_policy(
    organization_id: int = Path(..., description="Organization ID"),
    policy_id: int = Path(..., description="SLA Policy ID"),
    policy_update: SLAPolicyUpdate = ...,
    sla_service: SLAService = Depends(get_sla_service),
    auth: tuple = Depends(require_access("sla", "update"))
):
    """Update an SLA policy"""
    logger.info(f"User {current_user.id} updating SLA policy {policy_id}")
    
    try:
        updated_policy = sla_service.update_policy(policy_id, organization_id, policy_update)
        if not updated_policy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="SLA policy not found"
            )
        
        return updated_policy
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating SLA policy: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update SLA policy"
        )


@router.delete("/organizations/{organization_id}/policies/{policy_id}")
async def delete_sla_policy(
    organization_id: int = Path(..., description="Organization ID"),
    policy_id: int = Path(..., description="SLA Policy ID"),
    sla_service: SLAService = Depends(get_sla_service),
    auth: tuple = Depends(require_access("sla", "delete"))
):
    """Delete an SLA policy"""
    logger.info(f"User {current_user.id} deleting SLA policy {policy_id}")
    
    try:
        success = sla_service.delete_policy(policy_id, organization_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="SLA policy not found"
            )
        
        return {"message": "SLA policy deleted successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error deleting SLA policy: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete SLA policy"
        )


# SLA Tracking Endpoints
@router.post("/organizations/{organization_id}/tickets/{ticket_id}/sla", response_model=SLAPolicyAssignmentResponse)
async def assign_sla_to_ticket(
    organization_id: int = Path(..., description="Organization ID"),
    ticket_id: int = Path(..., description="Ticket ID"),
    assignment: Optional[SLAPolicyAssignment] = None,
    force_recreate: bool = Query(False, description="Force recreate SLA tracking if it exists"),
    sla_service: SLAService = Depends(get_sla_service),
    current_user: User = Depends(lambda: require_service_permission("sla_create"))
):
    """Assign SLA policy to a ticket (auto-detects if no policy specified)"""
    logger.info(f"User {current_user.id} assigning SLA to ticket {ticket_id}")
    
    try:
        tracking = sla_service.create_tracking(
            ticket_id=ticket_id,
            organization_id=organization_id,
            force_recreate=force_recreate
        )
        
        if not tracking:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not create SLA tracking - ticket not found or no matching policy"
            )
        
        return SLAPolicyAssignmentResponse(
            ticket_id=tracking.ticket_id,
            policy_id=tracking.policy_id,
            sla_tracking_id=tracking.id,
            message="SLA policy assigned successfully"
        )
    except Exception as e:
        logger.error(f"Error assigning SLA to ticket: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to assign SLA policy"
        )


@router.get("/organizations/{organization_id}/tickets/{ticket_id}/sla", response_model=SLATrackingWithPolicy)
async def get_ticket_sla(
    organization_id: int = Path(..., description="Organization ID"),
    ticket_id: int = Path(..., description="Ticket ID"),
    sla_service: SLAService = Depends(get_sla_service),
    auth: tuple = Depends(require_access("sla", "read"))
):
    """Get SLA tracking for a specific ticket"""
    logger.info(f"User {current_user.id} requesting SLA tracking for ticket {ticket_id}")
    
    tracking = sla_service.get_tracking(ticket_id, organization_id)
    if not tracking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SLA tracking not found for this ticket"
        )
    
    # Load the policy relationship
    policy = sla_service.get_policy(tracking.policy_id, organization_id)
    
    return SLATrackingWithPolicy(
        **tracking.__dict__,
        policy=policy
    )


@router.put("/organizations/{organization_id}/tracking/{tracking_id}", response_model=SLATrackingResponse)
async def update_sla_tracking(
    organization_id: int = Path(..., description="Organization ID"),
    tracking_id: int = Path(..., description="SLA Tracking ID"),
    tracking_update: SLATrackingUpdate = ...,
    sla_service: SLAService = Depends(get_sla_service),
    auth: tuple = Depends(require_access("sla", "update"))
):
    """Update SLA tracking (typically for system use)"""
    logger.info(f"User {current_user.id} updating SLA tracking {tracking_id}")
    
    try:
        updated_tracking = sla_service.update_tracking(tracking_id, organization_id, tracking_update)
        if not updated_tracking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="SLA tracking not found"
            )
        
        return updated_tracking
    except Exception as e:
        logger.error(f"Error updating SLA tracking: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update SLA tracking"
        )


# SLA Monitoring Endpoints
@router.get("/organizations/{organization_id}/sla/breached", response_model=List[SLATrackingResponse])
async def get_breached_slas(
    organization_id: int = Path(..., description="Organization ID"),
    limit: int = Query(50, description="Maximum number of results", le=200),
    sla_service: SLAService = Depends(get_sla_service),
    auth: tuple = Depends(require_access("sla", "read"))
):
    """Get tickets with breached SLAs"""
    logger.info(f"User {current_user.id} requesting breached SLAs for organization {organization_id}")
    
    breached_slas = sla_service.get_breached_slas(organization_id, limit=limit)
    return breached_slas


@router.get("/organizations/{organization_id}/sla/escalation-candidates", response_model=List[SLATrackingResponse])
async def get_escalation_candidates(
    organization_id: int = Path(..., description="Organization ID"),
    sla_service: SLAService = Depends(get_sla_service),
    auth: tuple = Depends(require_access("sla", "read"))
):
    """Get tickets that are candidates for escalation"""
    logger.info(f"User {current_user.id} requesting escalation candidates for organization {organization_id}")
    
    candidates = sla_service.get_escalation_candidates(organization_id)
    return candidates


@router.post("/organizations/{organization_id}/tracking/{tracking_id}/escalate")
async def trigger_escalation(
    organization_id: int = Path(..., description="Organization ID"),
    tracking_id: int = Path(..., description="SLA Tracking ID"),
    sla_service: SLAService = Depends(get_sla_service),
    auth: tuple = Depends(require_access("sla", "update"))
):
    """Trigger escalation for an SLA tracking record"""
    logger.info(f"User {current_user.id} triggering escalation for SLA tracking {tracking_id}")
    
    try:
        tracking = sla_service.trigger_escalation(tracking_id, organization_id)
        if not tracking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="SLA tracking not found"
            )
        
        return {
            "message": "Escalation triggered successfully",
            "tracking_id": tracking.id,
            "escalation_level": tracking.escalation_level,
            "escalated_at": tracking.escalation_triggered_at
        }
    except Exception as e:
        logger.error(f"Error triggering escalation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to trigger escalation"
        )


# SLA Analytics Endpoints
@router.get("/organizations/{organization_id}/sla/metrics", response_model=SLAMetrics)
async def get_sla_metrics(
    organization_id: int = Path(..., description="Organization ID"),
    start_date: Optional[datetime] = Query(None, description="Start date for metrics (ISO format)"),
    end_date: Optional[datetime] = Query(None, description="End date for metrics (ISO format)"),
    days: int = Query(30, description="Number of days to look back if dates not specified", ge=1, le=365),
    sla_service: SLAService = Depends(get_sla_service),
    auth: tuple = Depends(require_access("sla", "read"))
):
    """Get SLA performance metrics for a date range"""
    logger.info(f"User {current_user.id} requesting SLA metrics for organization {organization_id}")
    
    # Set default date range if not provided
    if not end_date:
        end_date = datetime.utcnow()
    if not start_date:
        start_date = end_date - timedelta(days=days)
    
    try:
        metrics = sla_service.get_sla_metrics(organization_id, start_date, end_date)
        return metrics
    except Exception as e:
        logger.error(f"Error getting SLA metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get SLA metrics"
        )


# Ticket Response/Resolution Processing (for system integration)
@router.post("/organizations/{organization_id}/tickets/{ticket_id}/response")
async def process_ticket_response(
    organization_id: int = Path(..., description="Organization ID"),
    ticket_id: int = Path(..., description="Ticket ID"),
    response_time: Optional[datetime] = Query(None, description="Response time (defaults to now)"),
    sla_service: SLAService = Depends(get_sla_service),
    auth: tuple = Depends(require_access("sla", "update"))
):
    """Process first response for a ticket and update SLA tracking"""
    logger.info(f"User {current_user.id} processing response for ticket {ticket_id}")
    
    if not response_time:
        response_time = datetime.utcnow()
    
    try:
        tracking = sla_service.process_ticket_response(ticket_id, organization_id, response_time)
        if not tracking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket or SLA tracking not found"
            )
        
        return {
            "message": "Ticket response processed successfully",
            "tracking_id": tracking.id,
            "response_status": tracking.response_status,
            "response_breach_hours": tracking.response_breach_hours
        }
    except Exception as e:
        logger.error(f"Error processing ticket response: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process ticket response"
        )


@router.post("/organizations/{organization_id}/tickets/{ticket_id}/resolution")
async def process_ticket_resolution(
    organization_id: int = Path(..., description="Organization ID"),
    ticket_id: int = Path(..., description="Ticket ID"),
    resolution_time: Optional[datetime] = Query(None, description="Resolution time (defaults to now)"),
    sla_service: SLAService = Depends(get_sla_service),
    auth: tuple = Depends(require_access("sla", "update"))
):
    """Process ticket resolution and update SLA tracking"""
    logger.info(f"User {current_user.id} processing resolution for ticket {ticket_id}")
    
    if not resolution_time:
        resolution_time = datetime.utcnow()
    
    try:
        tracking = sla_service.process_ticket_resolution(ticket_id, organization_id, resolution_time)
        if not tracking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket or SLA tracking not found"
            )
        
        return {
            "message": "Ticket resolution processed successfully",
            "tracking_id": tracking.id,
            "resolution_status": tracking.resolution_status,
            "resolution_breach_hours": tracking.resolution_breach_hours
        }
    except Exception as e:
        logger.error(f"Error processing ticket resolution: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process ticket resolution"
        )