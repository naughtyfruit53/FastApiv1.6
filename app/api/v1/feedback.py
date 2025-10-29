# app/api/v1/feedback.py

"""
FastAPI routes for customer feedback and service closure workflow
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.core.rbac_dependencies import check_service_permission
from app.models import User
from app.schemas.feedback import (
    CustomerFeedbackCreate, CustomerFeedbackUpdate, CustomerFeedbackInDB, CustomerFeedbackFilter,
    ServiceClosureCreate, ServiceClosureUpdate, ServiceClosureInDB, ServiceClosureFilter,
    FeedbackStatus, ClosureStatus
)
from app.services.feedback_service import CustomerFeedbackService, ServiceClosureService


router = APIRouter()


# Customer Feedback Endpoints

@router.post("/feedback", response_model=CustomerFeedbackInDB, status_code=status.HTTP_201_CREATED)
async def submit_customer_feedback(
    feedback_data: CustomerFeedbackCreate,
    db: Session = Depends(get_db),
    auth: tuple = Depends(require_access("feedback", "update"))
):
    """
    Submit customer feedback for a completed service.
    Requires customer_feedback_submit permission.
    """
    # Check permission - customers can submit feedback, managers can create on behalf
    check_service_permission(
        user=current_user, 
        module="customer_feedback", 
        action="submit",
        db=db
    )
    
    feedback_service = CustomerFeedbackService(db)
    return feedback_service.create_feedback(feedback_data, org_id)


@router.get("/feedback", response_model=List[CustomerFeedbackInDB])
async def get_feedback_list(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    feedback_status: Optional[FeedbackStatus] = None,
    overall_rating: Optional[int] = Query(None, ge=1, le=5),
    customer_id: Optional[int] = None,
    installation_job_id: Optional[int] = None,
    db: Session = Depends(get_db),
    auth: tuple = Depends(require_access("feedback", "read"))
):
    """
    Get list of customer feedback records with filtering.
    Requires customer_feedback_read permission.
    """
    check_service_permission(
        user=current_user, 
        module="customer_feedback", 
        action="read",
        db=db
    )
    
    filter_params = CustomerFeedbackFilter(
        feedback_status=feedback_status,
        overall_rating=overall_rating,
        customer_id=customer_id,
        installation_job_id=installation_job_id
    )
    
    feedback_service = CustomerFeedbackService(db)
    return feedback_service.get_feedback_list(
        organization_id=org_id,
        filter_params=filter_params,
        skip=skip,
        limit=limit
    )


@router.get("/feedback/{feedback_id}", response_model=CustomerFeedbackInDB)
async def get_feedback_by_id(
    feedback_id: int,
    db: Session = Depends(get_db),
    auth: tuple = Depends(require_access("feedback", "read"))
):
    """
    Get specific customer feedback by ID.
    Requires customer_feedback_read permission.
    """
    check_service_permission(
        user=current_user, 
        module="customer_feedback", 
        action="read",
        db=db
    )
    
    feedback_service = CustomerFeedbackService(db)
    feedback = feedback_service.get_feedback_by_id(feedback_id, org_id)
    
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found"
        )
    
    return feedback


@router.put("/feedback/{feedback_id}", response_model=CustomerFeedbackInDB)
async def update_feedback(
    feedback_id: int,
    feedback_update: CustomerFeedbackUpdate,
    db: Session = Depends(get_db),
    auth: tuple = Depends(require_access("feedback", "update"))
):
    """
    Update customer feedback record.
    Requires customer_feedback_update permission.
    """
    check_service_permission(
        user=current_user, 
        module="customer_feedback", 
        action="update",
        db=db
    )
    
    feedback_service = CustomerFeedbackService(db)
    return feedback_service.update_feedback(
        feedback_id=feedback_id,
        feedback_update=feedback_update,
        organization_id=org_id,
        updated_by_id=current_user.id
    )


@router.post("/feedback/{feedback_id}/review", response_model=CustomerFeedbackInDB)
async def review_feedback(
    feedback_id: int,
    response_notes: str,
    db: Session = Depends(get_db),
    auth: tuple = Depends(require_access("feedback", "update"))
):
    """
    Review and respond to customer feedback.
    Requires customer_feedback_update permission.
    """
    check_service_permission(
        user=current_user, 
        module="customer_feedback", 
        action="update",
        db=db
    )
    
    feedback_update = CustomerFeedbackUpdate(
        feedback_status=FeedbackStatus.REVIEWED,
        response_notes=response_notes
    )
    
    feedback_service = CustomerFeedbackService(db)
    return feedback_service.update_feedback(
        feedback_id=feedback_id,
        feedback_update=feedback_update,
        organization_id=org_id,
        updated_by_id=current_user.id
    )


# Service Closure Endpoints

@router.post("/service-closure", response_model=ServiceClosureInDB, status_code=status.HTTP_201_CREATED)
async def create_service_closure(
    closure_data: ServiceClosureCreate,
    db: Session = Depends(get_db),
    auth: tuple = Depends(require_access("feedback", "update"))
):
    """
    Create a service closure request.
    Requires service_closure_create permission.
    """
    check_service_permission(
        user=current_user, 
        module="service_closure", 
        action="create",
        db=db
    )
    
    closure_service = ServiceClosureService(db)
    return closure_service.create_closure(
        closure_data=closure_data,
        organization_id=org_id,
        created_by_id=current_user.id
    )


@router.get("/service-closure", response_model=List[ServiceClosureInDB])
async def get_service_closures(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    closure_status: Optional[ClosureStatus] = None,
    requires_manager_approval: Optional[bool] = None,
    feedback_received: Optional[bool] = None,
    escalation_required: Optional[bool] = None,
    db: Session = Depends(get_db),
    auth: tuple = Depends(require_access("feedback", "read"))
):
    """
    Get list of service closures with filtering.
    Requires service_closure_read permission.
    """
    check_service_permission(
        user=current_user, 
        module="service_closure", 
        action="read",
        db=db
    )
    
    filter_params = ServiceClosureFilter(
        closure_status=closure_status,
        requires_manager_approval=requires_manager_approval,
        feedback_received=feedback_received,
        escalation_required=escalation_required
    )
    
    closure_service = ServiceClosureService(db)
    return closure_service.get_closure_list(
        organization_id=org_id,
        filter_params=filter_params,
        skip=skip,
        limit=limit
    )


@router.get("/service-closure/{closure_id}", response_model=ServiceClosureInDB)
async def get_service_closure_by_id(
    closure_id: int,
    db: Session = Depends(get_db),
    auth: tuple = Depends(require_access("feedback", "read"))
):
    """
    Get specific service closure by ID.
    Requires service_closure_read permission.
    """
    check_service_permission(
        user=current_user, 
        module="service_closure", 
        action="read",
        db=db
    )
    
    closure_service = ServiceClosureService(db)
    closure = closure_service.get_closure_by_id(closure_id, org_id)
    
    if not closure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service closure not found"
        )
    
    return closure


@router.post("/service-closure/{closure_id}/approve", response_model=ServiceClosureInDB)
async def approve_service_closure(
    closure_id: int,
    approval_notes: Optional[str] = None,
    db: Session = Depends(get_db),
    auth: tuple = Depends(require_access("feedback", "update"))
):
    """
    Approve a service closure request.
    Requires service_closure_approve permission (manager only).
    """
    check_service_permission(
        user=current_user, 
        module="service_closure", 
        action="approve",
        db=db
    )
    
    closure_service = ServiceClosureService(db)
    return closure_service.approve_closure(
        closure_id=closure_id,
        organization_id=org_id,
        approved_by_id=current_user.id,
        approval_notes=approval_notes
    )


@router.post("/service-closure/{closure_id}/close", response_model=ServiceClosureInDB)
async def close_service_ticket(
    closure_id: int,
    final_closure_notes: Optional[str] = None,
    db: Session = Depends(get_db),
    auth: tuple = Depends(require_access("feedback", "update"))
):
    """
    Close a service ticket (final closure).
    Requires service_closure_close permission (manager only).
    """
    check_service_permission(
        user=current_user, 
        module="service_closure", 
        action="close",
        db=db
    )
    
    closure_service = ServiceClosureService(db)
    return closure_service.close_service(
        closure_id=closure_id,
        organization_id=org_id,
        closed_by_id=current_user.id,
        final_closure_notes=final_closure_notes
    )


@router.post("/service-closure/{closure_id}/reopen", response_model=ServiceClosureInDB)
async def reopen_service_ticket(
    closure_id: int,
    reopening_reason: str,
    db: Session = Depends(get_db),
    auth: tuple = Depends(require_access("feedback", "update"))
):
    """
    Reopen a closed service ticket.
    Requires service_closure_create permission.
    """
    check_service_permission(
        user=current_user, 
        module="service_closure", 
        action="create",
        db=db
    )
    
    closure_service = ServiceClosureService(db)
    return closure_service.reopen_service(
        closure_id=closure_id,
        organization_id=org_id,
        reopened_by_id=current_user.id,
        reopening_reason=reopening_reason
    )


# Analytics Endpoints

@router.get("/feedback/analytics/summary")
async def get_feedback_analytics(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    auth: tuple = Depends(require_access("feedback", "update"))
):
    """
    Get feedback analytics summary.
    Requires service_reports_read permission.
    """
    check_service_permission(
        user=current_user, 
        module="service_reports", 
        action="read",
        db=db
    )
    
    from datetime import datetime, timedelta
    from sqlalchemy import func
    from app.models.base import CustomerFeedback
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Basic analytics query
    analytics = db.query(
        func.count(CustomerFeedback.id).label('total_feedback'),
        func.avg(CustomerFeedback.overall_rating).label('avg_rating'),
        func.count(CustomerFeedback.id).filter(CustomerFeedback.overall_rating >= 4).label('positive_feedback'),
        func.count(CustomerFeedback.id).filter(CustomerFeedback.overall_rating <= 2).label('negative_feedback')
    ).filter(
        CustomerFeedback.organization_id == org_id,
        CustomerFeedback.submitted_at >= start_date,
        CustomerFeedback.submitted_at <= end_date
    ).first()
    
    return {
        "period_days": days,
        "total_feedback": analytics.total_feedback or 0,
        "average_rating": round(analytics.avg_rating or 0, 2),
        "positive_feedback": analytics.positive_feedback or 0,
        "negative_feedback": analytics.negative_feedback or 0,
        "satisfaction_rate": round((analytics.positive_feedback or 0) / max(analytics.total_feedback or 1, 1) * 100, 2)
    }


@router.get("/service-closure/analytics/summary")
async def get_closure_analytics(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    auth: tuple = Depends(require_access("feedback", "read"))
):
    """
    Get service closure analytics summary.
    Requires service_reports_read permission.
    """
    check_service_permission(
        user=current_user, 
        module="service_reports", 
        action="read",
        db=db
    )
    
    from datetime import datetime, timedelta
    from sqlalchemy import func
    from app.models.base import ServiceClosure
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Basic analytics query
    analytics = db.query(
        func.count(ServiceClosure.id).label('total_closures'),
        func.count(ServiceClosure.id).filter(ServiceClosure.closure_status == 'closed').label('completed_closures'),
        func.count(ServiceClosure.id).filter(ServiceClosure.escalation_required == True).label('escalated_closures'),
        func.avg(ServiceClosure.reopened_count).label('avg_reopens')
    ).filter(
        ServiceClosure.organization_id == org_id,
        ServiceClosure.created_at >= start_date,
        ServiceClosure.created_at <= end_date
    ).first()
    
    return {
        "period_days": days,
        "total_closures": analytics.total_closures or 0,
        "completed_closures": analytics.completed_closures or 0,
        "escalated_closures": analytics.escalated_closures or 0,
        "average_reopens": round(analytics.avg_reopens or 0, 2),
        "completion_rate": round((analytics.completed_closures or 0) / max(analytics.total_closures or 1, 1) * 100, 2)
    }