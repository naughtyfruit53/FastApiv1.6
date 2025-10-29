# app/api/v1/workflow_approval.py

"""
Workflow and Approval Engine API endpoints for comprehensive business process automation
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status, BackgroundTasks
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc, asc
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.enforcement import require_access
from app.models.user_models import User
from app.models.workflow_models import (
    WorkflowTemplate, WorkflowStep, WorkflowInstance, WorkflowStepInstance,
    ApprovalRequest, ApprovalHistory, ApprovalAttachment
)
from app.schemas.workflow import (
    WorkflowTemplateCreate, WorkflowTemplateUpdate, WorkflowTemplateResponse, WorkflowTemplateWithDetails,
    WorkflowTemplateList, WorkflowTemplateFilter,
    WorkflowStepCreate, WorkflowStepUpdate, WorkflowStepResponse, WorkflowStepWithDetails,
    WorkflowInstanceCreate, WorkflowInstanceUpdate, WorkflowInstanceResponse, WorkflowInstanceWithDetails,
    WorkflowInstanceList, WorkflowInstanceFilter,
    ApprovalRequestCreate, ApprovalRequestUpdate, ApprovalRequestResponse, ApprovalRequestWithDetails,
    ApprovalRequestList, ApprovalRequestFilter, ApprovalDecision,
    ApprovalHistoryResponse, WorkflowDashboardStats, ApprovalDashboardStats,
    BulkApprovalDecision, BulkWorkflowAction
)
from app.services.rbac import RBACService
from app.core.rbac_dependencies import check_service_permission

router = APIRouter()

# Dashboard Endpoints
@router.get("/dashboard/workflow", response_model=WorkflowDashboardStats)
async def get_workflow_dashboard(
    company_id: Optional[int] = Query(None, description="Filter by specific company"),
    auth: tuple = Depends(require_access("workflow_approval", "read")),
    db: Session = Depends(get_db)
):
    """Get workflow management dashboard statistics"""
    org_id = org_id
    rbac = RBACService(db)
    
    # Get user's accessible companies
    user_companies = rbac.get_user_companies(current_user.id)
    
    # Build base queries
    template_query = db.query(WorkflowTemplate).filter(WorkflowTemplate.organization_id == org_id)
    approval_query = db.query(ApprovalRequest).filter(ApprovalRequest.organization_id == org_id)
    
    if company_id is not None:
        if company_id not in user_companies:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: User does not have access to the specified company"
            )
        template_query = template_query.filter(WorkflowTemplate.company_id == company_id)
        approval_query = approval_query.filter(ApprovalRequest.company_id == company_id)
    else:
        template_query = template_query.filter(
            or_(
                WorkflowTemplate.company_id.in_(user_companies),
                WorkflowTemplate.company_id.is_(None)
            )
        )
        approval_query = approval_query.filter(
            or_(
                ApprovalRequest.company_id.in_(user_companies),
                ApprovalRequest.company_id.is_(None)
            )
        )
    
    # Calculate statistics
    total_active_workflows = template_query.filter(WorkflowTemplate.status == 'active').count()
    pending_approvals = approval_query.filter(ApprovalRequest.status == 'pending').count()
    
    # Overdue approvals (past deadline)
    now = datetime.utcnow()
    overdue_approvals = approval_query.filter(
        ApprovalRequest.status == 'pending',
        ApprovalRequest.deadline < now
    ).count()
    
    # Completed today
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    completed_today = approval_query.filter(
        ApprovalRequest.status.in_(['approved', 'rejected']),
        ApprovalRequest.responded_at >= today_start
    ).count()
    
    # Average processing time
    avg_processing = db.query(
        func.avg(
            func.extract('epoch', ApprovalRequest.responded_at) - 
            func.extract('epoch', ApprovalRequest.requested_at)
        ).label('avg_seconds')
    ).filter(
        ApprovalRequest.organization_id == org_id,
        ApprovalRequest.responded_at.isnot(None)
    ).scalar()
    
    avg_processing_hours = (avg_processing / 3600) if avg_processing else 0.0
    
    # Approvals by status
    status_counts = db.query(
        ApprovalRequest.status,
        func.count(ApprovalRequest.id).label('count')
    ).filter(
        approval_query.whereclause
    ).group_by(ApprovalRequest.status).all()
    
    approvals_by_status = {str(status): count for status, count in status_counts}
    
    # Workflows by type
    type_counts = db.query(
        WorkflowTemplate.category,
        func.count(WorkflowTemplate.id).label('count')
    ).filter(
        template_query.whereclause
    ).group_by(WorkflowTemplate.category).all()
    
    workflows_by_type = {str(category or 'uncategorized'): count for category, count in type_counts}
    
    # Top pending approvals
    top_pending = approval_query.filter(
        ApprovalRequest.status == 'pending'
    ).options(
        joinedload(ApprovalRequest.requester),
        joinedload(ApprovalRequest.approver)
    ).order_by(ApprovalRequest.requested_at).limit(10).all()
    
    # Recent completions
    recent_completions = approval_query.filter(
        ApprovalRequest.status.in_(['approved', 'rejected'])
    ).options(
        joinedload(ApprovalRequest.requester),
        joinedload(ApprovalRequest.approver)
    ).order_by(desc(ApprovalRequest.responded_at)).limit(10).all()
    
    return WorkflowDashboardStats(
        total_active_workflows=total_active_workflows,
        pending_approvals=pending_approvals,
        overdue_approvals=overdue_approvals,
        completed_today=completed_today,
        average_processing_time_hours=avg_processing_hours,
        approvals_by_status=approvals_by_status,
        workflows_by_type=workflows_by_type,
        top_pending_approvals=[
            ApprovalRequestWithDetails.from_orm(a) for a in top_pending
        ],
        recent_completions=[
            ApprovalRequestResponse.from_orm(a) for a in recent_completions
        ]
    )

@router.get("/dashboard/approvals", response_model=ApprovalDashboardStats)
async def get_approval_dashboard(
    auth: tuple = Depends(require_access("workflow_approval", "read")),
    db: Session = Depends(get_db)
):
    """Get personal approval dashboard for current user"""
    org_id = org_id
    user_id = current_user.id
    
    # My pending approvals
    my_pending = db.query(ApprovalRequest).filter(
        ApprovalRequest.organization_id == org_id,
        ApprovalRequest.assigned_to == user_id,
        ApprovalRequest.status == 'pending'
    ).count()
    
    # My delegated approvals
    my_delegated = db.query(ApprovalRequest).filter(
        ApprovalRequest.organization_id == org_id,
        ApprovalRequest.delegated_to == user_id,
        ApprovalRequest.status == 'delegated'
    ).count()
    
    # My escalated approvals
    my_escalated = db.query(ApprovalRequest).filter(
        ApprovalRequest.organization_id == org_id,
        ApprovalRequest.escalated_to == user_id,
        ApprovalRequest.status == 'escalated'
    ).count()
    
    # Approvals processed today
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    processed_today = db.query(ApprovalRequest).filter(
        ApprovalRequest.organization_id == org_id,
        ApprovalRequest.assigned_to == user_id,
        ApprovalRequest.status.in_(['approved', 'rejected']),
        ApprovalRequest.responded_at >= today_start
    ).count()
    
    # My average response time
    my_avg_response = db.query(
        func.avg(
            func.extract('epoch', ApprovalRequest.responded_at) - 
            func.extract('epoch', ApprovalRequest.requested_at)
        ).label('avg_seconds')
    ).filter(
        ApprovalRequest.organization_id == org_id,
        ApprovalRequest.assigned_to == user_id,
        ApprovalRequest.responded_at.isnot(None)
    ).scalar()
    
    avg_response_hours = (my_avg_response / 3600) if my_avg_response else 0.0
    
    # Pending by priority
    priority_counts = db.query(
        ApprovalRequest.priority,
        func.count(ApprovalRequest.id).label('count')
    ).filter(
        ApprovalRequest.organization_id == org_id,
        ApprovalRequest.assigned_to == user_id,
        ApprovalRequest.status == 'pending'
    ).group_by(ApprovalRequest.priority).all()
    
    pending_by_priority = {str(priority): count for priority, count in priority_counts}
    
    # Overdue approvals assigned to me
    now = datetime.utcnow()
    overdue = db.query(ApprovalRequest).filter(
        ApprovalRequest.organization_id == org_id,
        ApprovalRequest.assigned_to == user_id,
        ApprovalRequest.status == 'pending',
        ApprovalRequest.deadline < now
    ).options(
        joinedload(ApprovalRequest.requester)
    ).order_by(ApprovalRequest.deadline).all()
    
    # Recent decisions by me
    recent_decisions = db.query(ApprovalRequest).filter(
        ApprovalRequest.organization_id == org_id,
        ApprovalRequest.assigned_to == user_id,
        ApprovalRequest.status.in_(['approved', 'rejected'])
    ).options(
        joinedload(ApprovalRequest.requester)
    ).order_by(desc(ApprovalRequest.responded_at)).limit(10).all()
    
    return ApprovalDashboardStats(
        my_pending_approvals=my_pending,
        my_delegated_approvals=my_delegated,
        my_escalated_approvals=my_escalated,
        approvals_processed_today=processed_today,
        average_response_time_hours=avg_response_hours,
        pending_by_priority=pending_by_priority,
        overdue_approvals=[
            ApprovalRequestWithDetails.from_orm(a) for a in overdue
        ],
        recent_decisions=[
            ApprovalRequestResponse.from_orm(a) for a in recent_decisions
        ]
    )

# Workflow Template Management
@router.post("/templates", response_model=WorkflowTemplateResponse)
async def create_workflow_template(
    template: WorkflowTemplateCreate,
    auth: tuple = Depends(require_access("workflow_approval", "create")),
    db: Session = Depends(get_db)
):
    """Create a new workflow template"""
    check_service_permission(current_user, "workflow", "create", db)
    org_id = org_id
    rbac = RBACService(db)
    
    # Validate company access
    if template.company_id:
        user_companies = rbac.get_user_companies(current_user.id)
        if template.company_id not in user_companies:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: User does not have access to the specified company"
            )
    
    # Check for duplicate name
    existing = db.query(WorkflowTemplate).filter(
        WorkflowTemplate.organization_id == org_id,
        WorkflowTemplate.name == template.name,
        WorkflowTemplate.version == template.version
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Workflow template with this name and version already exists"
        )
    
    # Create template
    db_template = WorkflowTemplate(
        organization_id=org_id,
        company_id=template.company_id,
        name=template.name,
        description=template.description,
        category=template.category,
        trigger_type=template.trigger_type,
        version=template.version,
        is_default=template.is_default,
        allow_parallel_execution=template.allow_parallel_execution,
        auto_complete=template.auto_complete,
        entity_type=template.entity_type,
        entity_conditions=template.entity_conditions,
        created_by=current_user.id
    )
    
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    
    return WorkflowTemplateResponse.from_orm(db_template)

@router.get("/templates", response_model=WorkflowTemplateList)
async def list_workflow_templates(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(50, ge=1, le=100, description="Items per page"),
    company_id: Optional[int] = Query(None, description="Filter by company"),
    filters: WorkflowTemplateFilter = Depends(),
    auth: tuple = Depends(require_access("workflow_approval", "read")),
    db: Session = Depends(get_db)
):
    """List workflow templates with filtering and pagination"""
    org_id = org_id
    rbac = RBACService(db)
    
    # Get user's accessible companies
    user_companies = rbac.get_user_companies(current_user.id)
    
    # Build query
    query = db.query(WorkflowTemplate).filter(WorkflowTemplate.organization_id == org_id)
    
    # Company filtering
    if company_id is not None:
        if company_id not in user_companies:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: User does not have access to the specified company"
            )
        query = query.filter(WorkflowTemplate.company_id == company_id)
    else:
        query = query.filter(
            or_(
                WorkflowTemplate.company_id.in_(user_companies),
                WorkflowTemplate.company_id.is_(None)
            )
        )
    
    # Apply filters
    if filters.status:
        query = query.filter(WorkflowTemplate.status == filters.status)
    if filters.category:
        query = query.filter(WorkflowTemplate.category == filters.category)
    if filters.trigger_type:
        query = query.filter(WorkflowTemplate.trigger_type == filters.trigger_type)
    if filters.entity_type:
        query = query.filter(WorkflowTemplate.entity_type == filters.entity_type)
    if filters.created_by:
        query = query.filter(WorkflowTemplate.created_by == filters.created_by)
    if filters.search:
        search_term = f"%{filters.search}%"
        query = query.filter(
            or_(
                WorkflowTemplate.name.ilike(search_term),
                WorkflowTemplate.description.ilike(search_term)
            )
        )
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * per_page
    templates = query.options(
        joinedload(WorkflowTemplate.creator)
    ).offset(offset).limit(per_page).all()
    
    # Build response with details
    template_details = []
    for template in templates:
        # Get step count
        step_count = db.query(WorkflowStep).filter(
            WorkflowStep.template_id == template.id
        ).count()
        
        # Get instance count
        instance_count = db.query(WorkflowInstance).filter(
            WorkflowInstance.template_id == template.id
        ).count()
        
        # Get active instances
        active_instances = db.query(WorkflowInstance).filter(
            WorkflowInstance.template_id == template.id,
            WorkflowInstance.status == 'in_progress'
        ).count()
        
        template_detail = WorkflowTemplateWithDetails(
            **template.__dict__,
            creator_name=template.creator.full_name if template.creator else None,
            step_count=step_count,
            instance_count=instance_count,
            active_instances=active_instances
        )
        template_details.append(template_detail)
    
    total_pages = (total + per_page - 1) // per_page
    
    return WorkflowTemplateList(
        templates=template_details,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages
    )

# Approval Request Management
@router.post("/approvals", response_model=ApprovalRequestResponse)
async def create_approval_request(
    approval: ApprovalRequestCreate,
    auth: tuple = Depends(require_access("workflow_approval", "create")),
    db: Session = Depends(get_db)
):
    """Create a new approval request"""
    check_service_permission(current_user, "approval", "create", db)
    org_id = org_id
    rbac = RBACService(db)
    
    # Validate company access
    if approval.company_id:
        user_companies = rbac.get_user_companies(current_user.id)
        if approval.company_id not in user_companies:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: User does not have access to the specified company"
            )
    
    # Generate approval code
    import uuid
    approval_code = f"APP-{uuid.uuid4().hex[:8].upper()}"
    
    # Create approval request
    db_approval = ApprovalRequest(
        organization_id=org_id,
        company_id=approval.company_id,
        approval_code=approval_code,
        title=approval.title,
        description=approval.description,
        entity_type=approval.entity_type,
        entity_id=approval.entity_id,
        entity_data=approval.entity_data,
        priority=approval.priority,
        assigned_to=approval.assigned_to,
        deadline=approval.deadline,
        workflow_instance_id=approval.workflow_instance_id,
        step_instance_id=approval.step_instance_id,
        requested_by=current_user.id
    )
    
    db.add(db_approval)
    db.commit()
    db.refresh(db_approval)
    
    # Log the approval creation
    history = ApprovalHistory(
        organization_id=org_id,
        approval_id=db_approval.id,
        action="created",
        previous_status=None,
        new_status='pending',
        performed_by=current_user.id,
        comments="Approval request created"
    )
    db.add(history)
    db.commit()
    
    return ApprovalRequestResponse.from_orm(db_approval)

@router.get("/approvals", response_model=ApprovalRequestList)
async def list_approval_requests(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(50, ge=1, le=100, description="Items per page"),
    company_id: Optional[int] = Query(None, description="Filter by company"),
    filters: ApprovalRequestFilter = Depends(),
    auth: tuple = Depends(require_access("workflow_approval", "read")),
    db: Session = Depends(get_db)
):
    """List approval requests with filtering and pagination"""
    org_id = org_id
    rbac = RBACService(db)
    
    # Get user's accessible companies
    user_companies = rbac.get_user_companies(current_user.id)
    
    # Build query
    query = db.query(ApprovalRequest).filter(ApprovalRequest.organization_id == org_id)
    
    # Company filtering
    if company_id is not None:
        if company_id not in user_companies:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: User does not have access to the specified company"
            )
        query = query.filter(ApprovalRequest.company_id == company_id)
    else:
        query = query.filter(
            or_(
                ApprovalRequest.company_id.in_(user_companies),
                ApprovalRequest.company_id.is_(None)
            )
        )
    
    # Apply filters
    if filters.status:
        query = query.filter(ApprovalRequest.status == filters.status)
    if filters.entity_type:
        query = query.filter(ApprovalRequest.entity_type == filters.entity_type)
    if filters.assigned_to:
        query = query.filter(ApprovalRequest.assigned_to == filters.assigned_to)
    if filters.requested_by:
        query = query.filter(ApprovalRequest.requested_by == filters.requested_by)
    if filters.priority:
        query = query.filter(ApprovalRequest.priority == filters.priority)
    if filters.requested_from:
        query = query.filter(ApprovalRequest.requested_at >= filters.requested_from)
    if filters.requested_to:
        query = query.filter(ApprovalRequest.requested_at <= filters.requested_to)
    if filters.deadline_from:
        query = query.filter(ApprovalRequest.deadline >= filters.deadline_from)
    if filters.deadline_to:
        query = query.filter(ApprovalRequest.deadline <= filters.deadline_to)
    if filters.search:
        search_term = f"%{filters.search}%"
        query = query.filter(
            or_(
                ApprovalRequest.title.ilike(search_term),
                ApprovalRequest.description.ilike(search_term),
                ApprovalRequest.approval_code.ilike(search_term)
            )
        )
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * per_page
    approvals = query.options(
        joinedload(ApprovalRequest.requester),
        joinedload(ApprovalRequest.approver),
        joinedload(ApprovalRequest.delegate),
        joinedload(ApprovalRequest.escalated_user)
    ).offset(offset).limit(per_page).all()
    
    # Build response with details
    approval_details = []
    for approval in approvals:
        # Calculate time pending
        time_pending = None
        if approval.status == 'pending' and approval.requested_at:
            time_pending = (datetime.utcnow() - approval.requested_at).total_seconds() / 3600
        
        # Get attachment count
        attachment_count = db.query(ApprovalAttachment).filter(
            ApprovalAttachment.approval_id == approval.id
        ).count()
        
        approval_detail = ApprovalRequestWithDetails(
            **approval.__dict__,
            requester_name=approval.requester.full_name if approval.requester else None,
            approver_name=approval.approver.full_name if approval.approver else None,
            delegate_name=approval.delegate.full_name if approval.delegate else None,
            escalated_user_name=approval.escalated_user.full_name if approval.escalated_user else None,
            entity_description=f"{approval.entity_type}#{approval.entity_id}",
            time_pending_hours=time_pending,
            attachment_count=attachment_count
        )
        approval_details.append(approval_detail)
    
    total_pages = (total + per_page - 1) // per_page
    
    return ApprovalRequestList(
        approvals=approval_details,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages
    )

@router.put("/approvals/{approval_id}/decision", response_model=ApprovalRequestResponse)
async def make_approval_decision(
    approval_id: int,
    decision: ApprovalDecision,
    auth: tuple = Depends(require_access("workflow_approval", "update")),
    db: Session = Depends(get_db)
):
    """Make a decision on an approval request"""
    check_service_permission(current_user, "approval", "respond", db)
    org_id = org_id
    rbac = RBACService(db)
    
    # Get the approval request
    approval = db.query(ApprovalRequest).filter(
        ApprovalRequest.id == approval_id,
        ApprovalRequest.organization_id == org_id
    ).first()
    
    if not approval:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval request not found"
        )
    
    # Check company access
    user_companies = rbac.get_user_companies(current_user.id)
    if approval.company_id and approval.company_id not in user_companies:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: User does not have access to this approval's company"
        )
    
    # Check if user can respond to this approval
    if approval.assigned_to != current_user.id:
        # Check if user is delegated or escalated to
        if not (approval.delegated_to == current_user.id or approval.escalated_to == current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to respond to this approval request"
            )
    
    # Check if approval is still pending
    if approval.status != 'pending':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This approval request has already been processed"
        )
    
    # Record previous status
    previous_status = approval.status
    
    # Update approval
    approval.decision = decision.decision
    approval.decision_comments = decision.decision_comments
    approval.decision_data = decision.decision_data
    approval.status = decision.decision
    approval.responded_at = datetime.utcnow()
    
    # Handle delegation
    if decision.decision == 'delegated':
        if not decision.delegated_to:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Delegated_to user must be specified for delegation"
            )
        approval.delegated_to = decision.delegated_to
        approval.delegation_reason = decision.delegation_reason
        approval.assigned_to = decision.delegated_to  # Transfer assignment
        approval.status = 'pending'  # Reset to pending for new assignee
        approval.responded_at = None  # Clear response time
    
    approval.updated_at = datetime.utcnow()
    
    # Create approval history
    history = ApprovalHistory(
        organization_id=org_id,
        approval_id=approval.id,
        action=decision.decision.value,
        previous_status=previous_status,
        new_status=approval.status,
        performed_by=current_user.id,
        comments=decision.decision_comments
    )
    db.add(history)
    
    db.commit()
    db.refresh(approval)
    
    return ApprovalRequestResponse.from_orm(approval)

# Bulk Operations
@router.put("/approvals/bulk-decision")
async def bulk_approval_decision(
    bulk_decision: BulkApprovalDecision,
    auth: tuple = Depends(require_access("workflow_approval", "update")),
    db: Session = Depends(get_db)
):
    """Make bulk approval decisions"""
    check_service_permission(current_user, "approval", "respond", db)
    org_id = org_id
    rbac = RBACService(db)
    user_companies = rbac.get_user_companies(current_user.id)
    
    # Get approvals to process
    approvals = db.query(ApprovalRequest).filter(
        ApprovalRequest.id.in_(bulk_decision.approval_ids),
        ApprovalRequest.organization_id == org_id,
        or_(
            ApprovalRequest.company_id.in_(user_companies),
            ApprovalRequest.company_id.is_(None)
        ),
        ApprovalRequest.assigned_to == current_user.id,
        ApprovalRequest.status == 'pending'
    ).all()
    
    if not approvals:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid approval requests found"
        )
    
    # Process each approval
    processed_count = 0
    now = datetime.utcnow()
    
    for approval in approvals:
        previous_status = approval.status
        
        approval.decision = bulk_decision.decision
        approval.decision_comments = bulk_decision.decision_comments
        approval.status = bulk_decision.decision
        approval.responded_at = now
        approval.updated_at = now
        
        # Create history
        history = ApprovalHistory(
            organization_id=org_id,
            approval_id=approval.id,
            action=bulk_decision.decision.value,
            previous_status=previous_status,
            new_status=bulk_decision.decision,
            performed_by=current_user.id,
            comments=bulk_decision.decision_comments
        )
        db.add(history)
        
        processed_count += 1
    
    db.commit()
    
    return {"message": f"Processed {processed_count} approval requests"}

@router.get("/approvals/{approval_id}/history", response_model=List[ApprovalHistoryResponse])
async def get_approval_history(
    approval_id: int,
    auth: tuple = Depends(require_access("workflow_approval", "read")),
    db: Session = Depends(get_db)
):
    """Get approval request history"""
    org_id = org_id
    rbac = RBACService(db)
    
    # Check approval exists and user has access
    approval = db.query(ApprovalRequest).filter(
        ApprovalRequest.id == approval_id,
        ApprovalRequest.organization_id == org_id
    ).first()
    
    if not approval:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval request not found"
        )
    
    user_companies = rbac.get_user_companies(current_user.id)
    if approval.company_id and approval.company_id not in user_companies:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: User does not have access to this approval's company"
        )
    
    # Get history
    history = db.query(ApprovalHistory).filter(
        ApprovalHistory.approval_id == approval_id,
        ApprovalHistory.organization_id == org_id
    ).options(
        joinedload(ApprovalHistory.performer)
    ).order_by(ApprovalHistory.created_at).all()
    
    # Build response
    history_response = []
    for h in history:
        history_item = ApprovalHistoryResponse(
            **h.__dict__,
            performer_name=h.performer.full_name if h.performer else None
        )
        history_response.append(history_item)
    
    return history_response