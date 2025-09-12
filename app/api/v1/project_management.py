# app/api/v1/project_management.py

"""
Project Management API endpoints for comprehensive project lifecycle management
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc, asc
from typing import List, Optional
from datetime import datetime, date

from app.core.database import get_db
from app.api.v1.auth import get_current_active_user as get_current_user
from app.models.user_models import User
from app.models.project_models import (
    Project, ProjectMilestone, ProjectResource, ProjectDocument, ProjectTimeLog
)
from app.schemas.project import (
    ProjectCreate, ProjectUpdate, ProjectResponse, ProjectWithDetails, ProjectList, 
    ProjectFilter, ProjectDashboardStats, BulkProjectUpdate, ProjectStatusBulkUpdate,
    MilestoneCreate, MilestoneUpdate, MilestoneResponse, MilestoneWithDetails,
    ResourceCreate, ResourceUpdate, ResourceResponse, ResourceWithDetails,
    DocumentCreate, DocumentUpdate, DocumentResponse, DocumentWithDetails,
    TimeLogCreate, TimeLogUpdate, TimeLogResponse, TimeLogWithDetails, TimeLogApproval
)
from app.services.rbac import RBACService
from app.core.rbac_dependencies import check_service_permission

router = APIRouter()

# Project Management Dashboard
@router.get("/dashboard", response_model=ProjectDashboardStats)
async def get_project_dashboard(
    company_id: Optional[int] = Query(None, description="Filter by specific company"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get project management dashboard statistics"""
    org_id = current_user.organization_id
    rbac = RBACService(db)
    
    # Get user's accessible companies
    user_companies = rbac.get_user_companies(current_user.id)
    
    # Build base query
    base_query = db.query(Project).filter(Project.organization_id == org_id)
    
    if company_id is not None:
        if company_id not in user_companies:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: User does not have access to the specified company"
            )
        base_query = base_query.filter(Project.company_id == company_id)
    else:
        base_query = base_query.filter(Project.company_id.in_(user_companies))
    
    # Calculate statistics
    total_projects = base_query.count()
    active_projects = base_query.filter(Project.status == 'active').count()
    completed_projects = base_query.filter(Project.status == 'completed').count()
    
    # Calculate overdue projects
    today = date.today()
    overdue_projects = base_query.filter(
        and_(
            Project.end_date < today,
            Project.status.in_(['planning', 'active'])
        )
    ).count()
    
    # Financial metrics
    budget_stats = base_query.with_entities(
        func.coalesce(func.sum(Project.budget), 0).label('total_budget'),
        func.coalesce(func.sum(Project.actual_cost), 0).label('total_actual_cost'),
        func.coalesce(func.avg(Project.progress_percentage), 0).label('avg_progress')
    ).first()
    
    total_budget = float(budget_stats.total_budget) if budget_stats.total_budget else 0.0
    actual_cost = float(budget_stats.total_actual_cost) if budget_stats.total_actual_cost else 0.0
    budget_utilization = (actual_cost / total_budget * 100) if total_budget > 0 else 0.0
    avg_progress = float(budget_stats.avg_progress) if budget_stats.avg_progress else 0.0
    
    # Projects by status
    status_counts = db.query(
        Project.status,
        func.count(Project.id).label('count')
    ).filter(
        Project.organization_id == org_id,
        Project.company_id.in_(user_companies) if not company_id else Project.company_id == company_id
    ).group_by(Project.status).all()
    
    projects_by_status = {str(status): count for status, count in status_counts}
    
    # Projects by type
    type_counts = db.query(
        Project.project_type,
        func.count(Project.id).label('count')
    ).filter(
        Project.organization_id == org_id,
        Project.company_id.in_(user_companies) if not company_id else Project.company_id == company_id
    ).group_by(Project.project_type).all()
    
    projects_by_type = {str(project_type): count for project_type, count in type_counts}
    
    # Upcoming milestones (next 30 days)
    upcoming_date = datetime.now().date()
    from datetime import timedelta
    upcoming_end = upcoming_date + timedelta(days=30)
    
    upcoming_milestones = db.query(ProjectMilestone).filter(
        ProjectMilestone.organization_id == org_id,
        ProjectMilestone.target_date.between(upcoming_date, upcoming_end),
        ProjectMilestone.status != 'completed'
    ).options(joinedload(ProjectMilestone.project)).limit(10).all()
    
    # Recent activities (simplified)
    recent_activities = []
    
    return ProjectDashboardStats(
        total_projects=total_projects,
        active_projects=active_projects,
        completed_projects=completed_projects,
        overdue_projects=overdue_projects,
        total_budget=total_budget,
        actual_cost=actual_cost,
        budget_utilization_percentage=budget_utilization,
        average_progress_percentage=avg_progress,
        projects_by_status=projects_by_status,
        projects_by_type=projects_by_type,
        upcoming_milestones=[MilestoneResponse.from_orm(m) for m in upcoming_milestones],
        recent_activities=recent_activities
    )

# Project CRUD Operations
@router.post("/projects", response_model=ProjectResponse)
async def create_project(
    project: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new project"""
    check_service_permission(current_user, "project", "create", db)
    org_id = current_user.organization_id
    rbac = RBACService(db)
    
    # Validate company access
    if project.company_id:
        user_companies = rbac.get_user_companies(current_user.id)
        if project.company_id not in user_companies:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: User does not have access to the specified company"
            )
    
    # Check for duplicate project code
    existing = db.query(Project).filter(
        Project.organization_id == org_id,
        Project.project_code == project.project_code
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project code already exists"
        )
    
    # Create project
    db_project = Project(
        organization_id=org_id,
        company_id=project.company_id,
        project_code=project.project_code,
        name=project.name,
        description=project.description,
        project_type=project.project_type,
        priority=project.priority,
        start_date=project.start_date,
        end_date=project.end_date,
        planned_start_date=project.planned_start_date,
        planned_end_date=project.planned_end_date,
        budget=project.budget,
        client_id=project.client_id,
        project_manager_id=project.project_manager_id,
        is_billable=project.is_billable,
        tags=project.tags,
        custom_fields=project.custom_fields,
        created_by=current_user.id
    )
    
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    
    return ProjectResponse.from_orm(db_project)

@router.get("/projects", response_model=ProjectList)
async def list_projects(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(50, ge=1, le=100, description="Items per page"),
    company_id: Optional[int] = Query(None, description="Filter by company"),
    filters: ProjectFilter = Depends(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List projects with filtering and pagination"""
    org_id = current_user.organization_id
    rbac = RBACService(db)
    
    # Get user's accessible companies
    user_companies = rbac.get_user_companies(current_user.id)
    
    # Build query
    query = db.query(Project).filter(Project.organization_id == org_id)
    
    # Company filtering
    if company_id is not None:
        if company_id not in user_companies:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: User does not have access to the specified company"
            )
        query = query.filter(Project.company_id == company_id)
    else:
        query = query.filter(Project.company_id.in_(user_companies))
    
    # Apply filters
    if filters.status:
        query = query.filter(Project.status == filters.status)
    if filters.project_type:
        query = query.filter(Project.project_type == filters.project_type)
    if filters.priority:
        query = query.filter(Project.priority == filters.priority)
    if filters.project_manager_id:
        query = query.filter(Project.project_manager_id == filters.project_manager_id)
    if filters.client_id:
        query = query.filter(Project.client_id == filters.client_id)
    if filters.start_date_from:
        query = query.filter(Project.start_date >= filters.start_date_from)
    if filters.start_date_to:
        query = query.filter(Project.start_date <= filters.start_date_to)
    if filters.end_date_from:
        query = query.filter(Project.end_date >= filters.end_date_from)
    if filters.end_date_to:
        query = query.filter(Project.end_date <= filters.end_date_to)
    if filters.is_billable is not None:
        query = query.filter(Project.is_billable == filters.is_billable)
    if filters.search:
        search_term = f"%{filters.search}%"
        query = query.filter(
            or_(
                Project.name.ilike(search_term),
                Project.project_code.ilike(search_term),
                Project.description.ilike(search_term)
            )
        )
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * per_page
    projects = query.options(
        joinedload(Project.project_manager),
        joinedload(Project.client),
        joinedload(Project.creator)
    ).offset(offset).limit(per_page).all()
    
    # Build response with details
    project_details = []
    for project in projects:
        # Calculate additional stats
        milestone_stats = db.query(
            func.count(ProjectMilestone.id).label('total'),
            func.count(ProjectMilestone.id).filter(
                ProjectMilestone.status == 'completed'
            ).label('completed')
        ).filter(
            ProjectMilestone.project_id == project.id
        ).first()
        
        task_stats = db.query(
            func.count().label('total'),
            func.count().filter(
                func.lower(func.cast(func.json_extract(
                    project.custom_fields, '$.status'
                ), str)) == 'completed'
            ).label('completed')
        ).first() if project.custom_fields else (0, 0)
        
        time_logged = db.query(
            func.coalesce(
                func.sum(ProjectTimeLog.duration_minutes), 0
            ).label('total_minutes')
        ).filter(
            ProjectTimeLog.project_id == project.id
        ).scalar() or 0
        
        project_detail = ProjectWithDetails(
            **project.__dict__,
            client_name=project.client.company_name if project.client else None,
            project_manager_name=project.project_manager.full_name if project.project_manager else None,
            creator_name=project.creator.full_name if project.creator else None,
            total_milestones=milestone_stats.total if milestone_stats else 0,
            completed_milestones=milestone_stats.completed if milestone_stats else 0,
            total_tasks=task_stats[0] if task_stats else 0,
            completed_tasks=task_stats[1] if task_stats else 0,
            total_time_logged=round(time_logged / 60, 2) if time_logged else 0.0
        )
        project_details.append(project_detail)
    
    total_pages = (total + per_page - 1) // per_page
    
    return ProjectList(
        projects=project_details,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages
    )

@router.get("/projects/{project_id}", response_model=ProjectWithDetails)
async def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific project by ID"""
    org_id = current_user.organization_id
    rbac = RBACService(db)
    
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.organization_id == org_id
    ).options(
        joinedload(Project.project_manager),
        joinedload(Project.client),
        joinedload(Project.creator)
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check company access
    user_companies = rbac.get_user_companies(current_user.id)
    if project.company_id and project.company_id not in user_companies:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: User does not have access to this project's company"
        )
    
    # Get additional stats (similar to list_projects)
    milestone_stats = db.query(
        func.count(ProjectMilestone.id).label('total'),
        func.count(ProjectMilestone.id).filter(
            ProjectMilestone.status == 'completed'
        ).label('completed')
    ).filter(
        ProjectMilestone.project_id == project.id
    ).first()
    
    time_logged = db.query(
        func.coalesce(
            func.sum(ProjectTimeLog.duration_minutes), 0
        ).label('total_minutes')
    ).filter(
        ProjectTimeLog.project_id == project.id
    ).scalar() or 0
    
    return ProjectWithDetails(
        **project.__dict__,
        client_name=project.client.company_name if project.client else None,
        project_manager_name=project.project_manager.full_name if project.project_manager else None,
        creator_name=project.creator.full_name if project.creator else None,
        total_milestones=milestone_stats.total if milestone_stats else 0,
        completed_milestones=milestone_stats.completed if milestone_stats else 0,
        total_tasks=0,  # Simplified for now
        completed_tasks=0,  # Simplified for now
        total_time_logged=round(time_logged / 60, 2) if time_logged else 0.0
    )

@router.put("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_update: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a project"""
    check_service_permission(current_user, "project", "update", db)
    org_id = current_user.organization_id
    rbac = RBACService(db)
    
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.organization_id == org_id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check company access
    user_companies = rbac.get_user_companies(current_user.id)
    if project.company_id and project.company_id not in user_companies:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: User does not have access to this project's company"
        )
    
    # Update fields
    update_data = project_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)
    
    project.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(project)
    
    return ProjectResponse.from_orm(project)

@router.delete("/projects/{project_id}")
async def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a project"""
    check_service_permission(current_user, "project", "delete", db)
    org_id = current_user.organization_id
    rbac = RBACService(db)
    
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.organization_id == org_id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check company access
    user_companies = rbac.get_user_companies(current_user.id)
    if project.company_id and project.company_id not in user_companies:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: User does not have access to this project's company"
        )
    
    db.delete(project)
    db.commit()
    
    return {"message": "Project deleted successfully"}

# Bulk Operations
@router.put("/projects/bulk-update")
async def bulk_update_projects(
    bulk_update: BulkProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Bulk update multiple projects"""
    check_service_permission(current_user, "project", "update", db)
    org_id = current_user.organization_id
    rbac = RBACService(db)
    user_companies = rbac.get_user_companies(current_user.id)
    
    # Get projects to update
    projects = db.query(Project).filter(
        Project.id.in_(bulk_update.project_ids),
        Project.organization_id == org_id,
        Project.company_id.in_(user_companies)
    ).all()
    
    if len(projects) != len(bulk_update.project_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Some projects not found or access denied"
        )
    
    # Update all projects
    update_data = bulk_update.updates.dict(exclude_unset=True)
    for project in projects:
        for field, value in update_data.items():
            setattr(project, field, value)
        project.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": f"Updated {len(projects)} projects successfully"}

@router.put("/projects/bulk-status")
async def bulk_update_project_status(
    status_update: ProjectStatusBulkUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Bulk update project status"""
    check_service_permission(current_user, "project", "update", db)
    org_id = current_user.organization_id
    rbac = RBACService(db)
    user_companies = rbac.get_user_companies(current_user.id)
    
    # Update projects
    updated_count = db.query(Project).filter(
        Project.id.in_(status_update.project_ids),
        Project.organization_id == org_id,
        Project.company_id.in_(user_companies)
    ).update(
        {"status": status_update.status, "updated_at": datetime.utcnow()},
        synchronize_session=False
    )
    
    db.commit()
    
    if updated_count != len(status_update.project_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Some projects not found or access denied"
        )
    
    return {"message": f"Updated status for {updated_count} projects"}

# Additional endpoints for milestones, resources, documents, and time logs would follow similar patterns
# For brevity, I'll include just the milestone endpoints as examples

# Milestone Management
@router.post("/projects/{project_id}/milestones", response_model=MilestoneResponse)
async def create_milestone(
    project_id: int,
    milestone: MilestoneCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new project milestone"""
    check_service_permission(current_user, "project", "update", db)
    org_id = current_user.organization_id
    rbac = RBACService(db)
    
    # Verify project exists and user has access
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.organization_id == org_id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    user_companies = rbac.get_user_companies(current_user.id)
    if project.company_id and project.company_id not in user_companies:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: User does not have access to this project's company"
        )
    
    # Create milestone
    db_milestone = ProjectMilestone(
        organization_id=org_id,
        project_id=project_id,
        name=milestone.name,
        description=milestone.description,
        target_date=milestone.target_date,
        assigned_to=milestone.assigned_to,
        dependencies=milestone.dependencies,
        created_by=current_user.id
    )
    
    db.add(db_milestone)
    db.commit()
    db.refresh(db_milestone)
    
    return MilestoneResponse.from_orm(db_milestone)

@router.get("/projects/{project_id}/milestones", response_model=List[MilestoneWithDetails])
async def list_project_milestones(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List milestones for a specific project"""
    org_id = current_user.organization_id
    rbac = RBACService(db)
    
    # Verify project access
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.organization_id == org_id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    user_companies = rbac.get_user_companies(current_user.id)
    if project.company_id and project.company_id not in user_companies:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: User does not have access to this project's company"
        )
    
    # Get milestones
    milestones = db.query(ProjectMilestone).filter(
        ProjectMilestone.project_id == project_id,
        ProjectMilestone.organization_id == org_id
    ).options(
        joinedload(ProjectMilestone.assignee),
        joinedload(ProjectMilestone.creator),
        joinedload(ProjectMilestone.project)
    ).order_by(ProjectMilestone.target_date).all()
    
    # Build detailed response
    milestone_details = []
    for milestone in milestones:
        milestone_detail = MilestoneWithDetails(
            **milestone.__dict__,
            project_name=milestone.project.name,
            assignee_name=milestone.assignee.full_name if milestone.assignee else None,
            creator_name=milestone.creator.full_name if milestone.creator else None
        )
        milestone_details.append(milestone_detail)
    
    return milestone_details