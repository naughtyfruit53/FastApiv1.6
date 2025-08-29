# app/api/v1/tasks.py

"""
Task Management API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc, asc
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models import User, Organization, Task, TaskProject, TaskProjectMember, TaskComment, TaskAttachment, TaskTimeLog, TaskReminder
from app.schemas.task_schemas import (
    TaskCreate, TaskUpdate, TaskResponse, TaskWithDetails, TaskList, TaskFilter, TaskDashboardStats,
    TaskProjectCreate, TaskProjectUpdate, TaskProjectResponse, TaskProjectWithDetails,
    TaskProjectMemberCreate, TaskProjectMemberUpdate, TaskProjectMemberResponse, TaskProjectMemberWithDetails,
    TaskCommentCreate, TaskCommentUpdate, TaskCommentResponse, TaskCommentWithDetails,
    TaskTimeLogCreate, TaskTimeLogUpdate, TaskTimeLogResponse, TaskTimeLogWithDetails,
    TaskReminderCreate, TaskReminderUpdate, TaskReminderResponse, TaskReminderWithDetails
)
from app.services.rbac_service import require_permission

router = APIRouter()

# Task endpoints
@router.get("/dashboard", response_model=TaskDashboardStats)
async def get_task_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get task dashboard statistics for current user's organization"""
    org_id = current_user.organization_id
    
    # Base query for user's organization
    base_query = db.query(Task).filter(Task.organization_id == org_id)
    
    # Total tasks
    total_tasks = base_query.count()
    
    # Tasks by status
    todo_tasks = base_query.filter(Task.status == "todo").count()
    in_progress_tasks = base_query.filter(Task.status == "in_progress").count()
    review_tasks = base_query.filter(Task.status == "review").count()
    done_tasks = base_query.filter(Task.status == "done").count()
    cancelled_tasks = base_query.filter(Task.status == "cancelled").count()
    
    # Overdue tasks (due date passed and not completed)
    overdue_tasks = base_query.filter(
        and_(
            Task.due_date < datetime.utcnow(),
            Task.status.notin_(["done", "cancelled"])
        )
    ).count()
    
    # Due today
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    due_today_tasks = base_query.filter(
        and_(
            Task.due_date >= today_start,
            Task.due_date < today_end,
            Task.status.notin_(["done", "cancelled"])
        )
    ).count()
    
    # Due this week
    week_end = today_start + timedelta(days=7)
    due_this_week_tasks = base_query.filter(
        and_(
            Task.due_date >= today_start,
            Task.due_date < week_end,
            Task.status.notin_(["done", "cancelled"])
        )
    ).count()
    
    # Assigned to me and created by me
    assigned_to_me = base_query.filter(Task.assigned_to == current_user.id).count()
    created_by_me = base_query.filter(Task.created_by == current_user.id).count()
    
    return TaskDashboardStats(
        total_tasks=total_tasks,
        todo_tasks=todo_tasks,
        in_progress_tasks=in_progress_tasks,
        review_tasks=review_tasks,
        done_tasks=done_tasks,
        cancelled_tasks=cancelled_tasks,
        overdue_tasks=overdue_tasks,
        due_today_tasks=due_today_tasks,
        due_this_week_tasks=due_this_week_tasks,
        assigned_to_me=assigned_to_me,
        created_by_me=created_by_me
    )

@router.get("/", response_model=TaskList)
async def get_tasks(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: Optional[List[str]] = Query(None),
    priority: Optional[List[str]] = Query(None),
    assigned_to: Optional[List[int]] = Query(None),
    created_by: Optional[List[int]] = Query(None),
    project_id: Optional[List[int]] = Query(None),
    due_date_from: Optional[datetime] = Query(None),
    due_date_to: Optional[datetime] = Query(None),
    tags: Optional[List[str]] = Query(None),
    search: Optional[str] = Query(None),
    sort_by: str = Query("created_at", regex=r"^(created_at|updated_at|due_date|priority|title)$"),
    sort_order: str = Query("desc", regex=r"^(asc|desc)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get paginated list of tasks with filtering and sorting"""
    org_id = current_user.organization_id
    
    # Base query with eager loading
    query = db.query(Task).filter(Task.organization_id == org_id).options(
        joinedload(Task.creator),
        joinedload(Task.assignee),
        joinedload(Task.project)
    )
    
    # Apply filters
    if status:
        query = query.filter(Task.status.in_(status))
    
    if priority:
        query = query.filter(Task.priority.in_(priority))
    
    if assigned_to:
        query = query.filter(Task.assigned_to.in_(assigned_to))
    
    if created_by:
        query = query.filter(Task.created_by.in_(created_by))
    
    if project_id:
        query = query.filter(Task.project_id.in_(project_id))
    
    if due_date_from:
        query = query.filter(Task.due_date >= due_date_from)
    
    if due_date_to:
        query = query.filter(Task.due_date <= due_date_to)
    
    if tags:
        # Search for any of the provided tags in the JSON array
        tag_filters = [Task.tags.contains([tag]) for tag in tags]
        query = query.filter(or_(*tag_filters))
    
    if search:
        search_filter = or_(
            Task.title.contains(search),
            Task.description.contains(search)
        )
        query = query.filter(search_filter)
    
    # Apply sorting
    sort_column = getattr(Task, sort_by)
    if sort_order == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(asc(sort_column))
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * per_page
    tasks = query.offset(offset).limit(per_page).all()
    
    # Calculate total pages
    total_pages = (total + per_page - 1) // per_page
    
    # Convert to response models with details
    task_details = []
    for task in tasks:
        task_dict = {
            **task.__dict__,
            "creator": {"id": task.creator.id, "full_name": task.creator.full_name} if task.creator else None,
            "assignee": {"id": task.assignee.id, "full_name": task.assignee.full_name} if task.assignee else None,
            "project": {"id": task.project.id, "name": task.project.name} if task.project else None,
            "comments_count": len(task.comments) if task.comments else 0,
            "attachments_count": len(task.attachments) if task.attachments else 0,
            "time_logs_count": len(task.time_logs) if task.time_logs else 0
        }
        task_details.append(TaskWithDetails(**task_dict))
    
    return TaskList(
        tasks=task_details,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages
    )

@router.post("/", response_model=TaskResponse)
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new task"""
    # Verify assignee exists in same organization if provided
    if task_data.assigned_to:
        assignee = db.query(User).filter(
            and_(
                User.id == task_data.assigned_to,
                User.organization_id == current_user.organization_id
            )
        ).first()
        if not assignee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assignee not found in your organization"
            )
    
    # Verify project exists in same organization if provided
    if task_data.project_id:
        project = db.query(TaskProject).filter(
            and_(
                TaskProject.id == task_data.project_id,
                TaskProject.organization_id == current_user.organization_id
            )
        ).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found in your organization"
            )
    
    # Create task
    task = Task(
        **task_data.model_dump(),
        organization_id=current_user.organization_id,
        created_by=current_user.id
    )
    
    db.add(task)
    db.commit()
    db.refresh(task)
    
    return TaskResponse.model_validate(task)

@router.get("/{task_id}", response_model=TaskWithDetails)
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific task by ID"""
    task = db.query(Task).filter(
        and_(
            Task.id == task_id,
            Task.organization_id == current_user.organization_id
        )
    ).options(
        joinedload(Task.creator),
        joinedload(Task.assignee),
        joinedload(Task.project),
        joinedload(Task.comments),
        joinedload(Task.attachments),
        joinedload(Task.time_logs)
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Convert to response model with details
    task_dict = {
        **task.__dict__,
        "creator": {"id": task.creator.id, "full_name": task.creator.full_name} if task.creator else None,
        "assignee": {"id": task.assignee.id, "full_name": task.assignee.full_name} if task.assignee else None,
        "project": {"id": task.project.id, "name": task.project.name} if task.project else None,
        "comments_count": len(task.comments) if task.comments else 0,
        "attachments_count": len(task.attachments) if task.attachments else 0,
        "time_logs_count": len(task.time_logs) if task.time_logs else 0
    }
    
    return TaskWithDetails(**task_dict)

@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a task"""
    task = db.query(Task).filter(
        and_(
            Task.id == task_id,
            Task.organization_id == current_user.organization_id
        )
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Verify assignee exists in same organization if provided
    if task_data.assigned_to is not None:
        if task_data.assigned_to:
            assignee = db.query(User).filter(
                and_(
                    User.id == task_data.assigned_to,
                    User.organization_id == current_user.organization_id
                )
            ).first()
            if not assignee:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Assignee not found in your organization"
                )
    
    # Verify project exists in same organization if provided
    if task_data.project_id is not None:
        if task_data.project_id:
            project = db.query(TaskProject).filter(
                and_(
                    TaskProject.id == task_data.project_id,
                    TaskProject.organization_id == current_user.organization_id
                )
            ).first()
            if not project:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found in your organization"
                )
    
    # Update task fields
    update_data = task_data.model_dump(exclude_unset=True)
    
    # Handle status change to "done"
    if update_data.get("status") == "done" and task.status != "done":
        update_data["completed_at"] = datetime.utcnow()
    elif update_data.get("status") != "done" and task.status == "done":
        update_data["completed_at"] = None
    
    for field, value in update_data.items():
        setattr(task, field, value)
    
    db.commit()
    db.refresh(task)
    
    return TaskResponse.model_validate(task)

@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a task"""
    task = db.query(Task).filter(
        and_(
            Task.id == task_id,
            Task.organization_id == current_user.organization_id
        )
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check if user can delete (creator or assigned user or admin)
    if (task.created_by != current_user.id and 
        task.assigned_to != current_user.id and 
        current_user.role not in ["org_admin", "admin"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this task"
        )
    
    db.delete(task)
    db.commit()
    
    return {"message": "Task deleted successfully"}

# Task Projects endpoints
@router.get("/projects/", response_model=List[TaskProjectWithDetails])
async def get_task_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all task projects for current user's organization"""
    projects = db.query(TaskProject).filter(
        TaskProject.organization_id == current_user.organization_id
    ).options(
        joinedload(TaskProject.creator),
        joinedload(TaskProject.tasks),
        joinedload(TaskProject.members)
    ).all()
    
    project_details = []
    for project in projects:
        project_dict = {
            **project.__dict__,
            "creator": {"id": project.creator.id, "full_name": project.creator.full_name} if project.creator else None,
            "tasks_count": len(project.tasks) if project.tasks else 0,
            "members_count": len(project.members) if project.members else 0
        }
        project_details.append(TaskProjectWithDetails(**project_dict))
    
    return project_details

@router.post("/projects/", response_model=TaskProjectResponse)
async def create_task_project(
    project_data: TaskProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new task project"""
    project = TaskProject(
        **project_data.model_dump(),
        organization_id=current_user.organization_id,
        created_by=current_user.id
    )
    
    db.add(project)
    db.commit()
    db.refresh(project)
    
    # Add creator as admin member
    member = TaskProjectMember(
        project_id=project.id,
        user_id=current_user.id,
        role="admin"
    )
    db.add(member)
    db.commit()
    
    return TaskProjectResponse.model_validate(project)

@router.get("/projects/{project_id}", response_model=TaskProjectWithDetails)
async def get_task_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific task project by ID"""
    project = db.query(TaskProject).filter(
        and_(
            TaskProject.id == project_id,
            TaskProject.organization_id == current_user.organization_id
        )
    ).options(
        joinedload(TaskProject.creator),
        joinedload(TaskProject.tasks),
        joinedload(TaskProject.members).joinedload(TaskProjectMember.user)
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Convert to response model with details
    project_dict = {
        **project.__dict__,
        "creator": {"id": project.creator.id, "full_name": project.creator.full_name} if project.creator else None,
        "tasks_count": len(project.tasks) if project.tasks else 0,
        "members_count": len(project.members) if project.members else 0,
        "tasks": [TaskResponse.model_validate(task) for task in project.tasks] if project.tasks else [],
        "members": [
            {
                "id": member.id,
                "user_id": member.user_id,
                "role": member.role,
                "user": {"id": member.user.id, "full_name": member.user.full_name} if member.user else None
            }
            for member in project.members
        ] if project.members else []
    }
    
    return TaskProjectWithDetails(**project_dict)

# Time logging endpoints
@router.post("/{task_id}/time-logs", response_model=TaskTimeLogResponse)
async def create_time_log(
    task_id: int,
    time_log_data: TaskTimeLogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a time log entry for a task"""
    # Verify task exists and user has access
    task = db.query(Task).filter(
        and_(
            Task.id == task_id,
            Task.organization_id == current_user.organization_id
        )
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Create time log
    time_log = TaskTimeLog(
        **time_log_data.model_dump(),
        task_id=task_id,
        user_id=current_user.id
    )
    
    db.add(time_log)
    db.commit()
    db.refresh(time_log)
    
    return TaskTimeLogResponse.model_validate(time_log)

@router.get("/{task_id}/time-logs", response_model=List[TaskTimeLogWithDetails])
async def get_task_time_logs(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all time logs for a task"""
    # Verify task exists and user has access
    task = db.query(Task).filter(
        and_(
            Task.id == task_id,
            Task.organization_id == current_user.organization_id
        )
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    time_logs = db.query(TaskTimeLog).filter(
        TaskTimeLog.task_id == task_id
    ).options(
        joinedload(TaskTimeLog.user)
    ).order_by(desc(TaskTimeLog.logged_at)).all()
    
    time_log_details = []
    for log in time_logs:
        log_dict = {
            **log.__dict__,
            "user": {"id": log.user.id, "full_name": log.user.full_name} if log.user else None,
            "task": {"id": task.id, "title": task.title}
        }
        time_log_details.append(TaskTimeLogWithDetails(**log_dict))
    
    return time_log_details