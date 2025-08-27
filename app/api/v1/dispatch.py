# app/api/v1/dispatch.py

"""
Material Dispatch API endpoints for the Service CRM
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.models import User, DispatchOrder, DispatchItem, InstallationJob, InstallationTask, CompletionRecord
from app.schemas.dispatch import (
    DispatchOrderCreate, DispatchOrderUpdate, DispatchOrderInDB, DispatchOrderFilter,
    DispatchItemCreate, DispatchItemUpdate, DispatchItemInDB,
    InstallationJobCreate, InstallationJobUpdate, InstallationJobInDB, InstallationJobFilter,
    InstallationJobWithDetails, InstallationSchedulePromptResponse,
    InstallationTaskCreate, InstallationTaskUpdate, InstallationTaskInDB, InstallationTaskFilter,
    CompletionRecordCreate, CompletionRecordUpdate, CompletionRecordInDB, CompletionRecordFilter
)
from app.services.dispatch_service import DispatchService, InstallationJobService, InstallationTaskService, CompletionRecordService
from app.core.rbac_dependencies import (
    require_dispatch_create, require_dispatch_read, require_dispatch_update, require_dispatch_delete,
    require_installation_create, require_installation_read, require_installation_update, require_installation_delete,
    require_installation_task_create, require_installation_task_read, require_installation_task_update, require_installation_task_delete,
    require_completion_record_create, require_completion_record_read, require_completion_record_update,
    require_technician_completion, require_assigned_technician
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


# Dispatch Order Endpoints
@router.post("/orders", response_model=DispatchOrderInDB, status_code=status.HTTP_201_CREATED)
async def create_dispatch_order(
    order_data: DispatchOrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_dispatch_create)
):
    """Create a new dispatch order"""
    logger.info(f"User {current_user.id} creating dispatch order for customer {order_data.customer_id}")
    
    try:
        dispatch_service = DispatchService(db)
        
        # Extract items from order data
        items_data = [item.dict() for item in order_data.items]
        order_dict = order_data.dict(exclude={'items'})
        
        dispatch_order = dispatch_service.create_dispatch_order(
            organization_id=current_user.organization_id,
            created_by_id=current_user.id,
            items=items_data,
            **order_dict
        )
        
        return dispatch_order
        
    except Exception as e:
        logger.error(f"Error creating dispatch order: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create dispatch order"
        )


@router.get("/orders", response_model=List[DispatchOrderInDB])
async def get_dispatch_orders(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Number of records to return"),
    filter_params: DispatchOrderFilter = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_dispatch_read)
):
    """Get dispatch orders for the organization"""
    logger.info(f"User {current_user.id} requesting dispatch orders")
    
    query = db.query(DispatchOrder).filter(
        DispatchOrder.organization_id == current_user.organization_id
    )
    
    # Apply filters
    if filter_params.status:
        query = query.filter(DispatchOrder.status == filter_params.status)
    if filter_params.customer_id:
        query = query.filter(DispatchOrder.customer_id == filter_params.customer_id)
    if filter_params.ticket_id:
        query = query.filter(DispatchOrder.ticket_id == filter_params.ticket_id)
    if filter_params.from_date:
        query = query.filter(DispatchOrder.created_at >= filter_params.from_date)
    if filter_params.to_date:
        query = query.filter(DispatchOrder.created_at <= filter_params.to_date)
    
    # Order by creation date descending
    query = query.order_by(DispatchOrder.created_at.desc())
    
    # Apply pagination
    dispatch_orders = query.offset(skip).limit(limit).all()
    
    return dispatch_orders


@router.get("/orders/{order_id}", response_model=DispatchOrderInDB)
async def get_dispatch_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_dispatch_read)
):
    """Get a specific dispatch order"""
    dispatch_order = db.query(DispatchOrder).filter(
        DispatchOrder.id == order_id,
        DispatchOrder.organization_id == current_user.organization_id
    ).first()
    
    if not dispatch_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispatch order not found"
        )
    
    return dispatch_order


@router.put("/orders/{order_id}", response_model=DispatchOrderInDB)
async def update_dispatch_order(
    order_id: int,
    order_update: DispatchOrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_dispatch_update)
):
    """Update a dispatch order"""
    dispatch_order = db.query(DispatchOrder).filter(
        DispatchOrder.id == order_id,
        DispatchOrder.organization_id == current_user.organization_id
    ).first()
    
    if not dispatch_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispatch order not found"
        )
    
    try:
        dispatch_service = DispatchService(db)
        
        # Update dispatch order fields
        update_data = order_update.dict(exclude_unset=True)
        if update_data.get('status'):
            dispatch_order = dispatch_service.update_dispatch_status(
                dispatch_order_id=order_id,
                updated_by_id=current_user.id,
                **update_data
            )
        else:
            for key, value in update_data.items():
                setattr(dispatch_order, key, value)
            
            dispatch_order.updated_by_id = current_user.id
            db.commit()
            db.refresh(dispatch_order)
        
        logger.info(f"User {current_user.id} updated dispatch order {order_id}")
        return dispatch_order
        
    except Exception as e:
        logger.error(f"Error updating dispatch order {order_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update dispatch order"
        )


@router.delete("/orders/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dispatch_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_dispatch_delete)
):
    """Delete a dispatch order (only if in pending status)"""
    dispatch_order = db.query(DispatchOrder).filter(
        DispatchOrder.id == order_id,
        DispatchOrder.organization_id == current_user.organization_id
    ).first()
    
    if not dispatch_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispatch order not found"
        )
    
    if dispatch_order.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only delete dispatch orders in pending status"
        )
    
    try:
        db.delete(dispatch_order)
        db.commit()
        logger.info(f"User {current_user.id} deleted dispatch order {order_id}")
        
    except Exception as e:
        logger.error(f"Error deleting dispatch order {order_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete dispatch order"
        )


# Installation Job Endpoints
@router.post("/installation-jobs", response_model=InstallationJobInDB, status_code=status.HTTP_201_CREATED)
async def create_installation_job(
    job_data: InstallationJobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_installation_create)
):
    """Create a new installation job"""
    logger.info(f"User {current_user.id} creating installation job for dispatch order {job_data.dispatch_order_id}")
    
    # Verify dispatch order exists and belongs to organization
    dispatch_order = db.query(DispatchOrder).filter(
        DispatchOrder.id == job_data.dispatch_order_id,
        DispatchOrder.organization_id == current_user.organization_id
    ).first()
    
    if not dispatch_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispatch order not found"
        )
    
    try:
        installation_service = InstallationJobService(db)
        
        job_dict = job_data.dict(exclude={'dispatch_order_id'})
        installation_job = installation_service.create_installation_job(
            organization_id=current_user.organization_id,
            dispatch_order_id=job_data.dispatch_order_id,
            created_by_id=current_user.id,
            **job_dict
        )
        
        return installation_job
        
    except Exception as e:
        logger.error(f"Error creating installation job: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create installation job"
        )


@router.get("/installation-jobs", response_model=List[InstallationJobInDB])
async def get_installation_jobs(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Number of records to return"),
    filter_params: InstallationJobFilter = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_installation_read)
):
    """Get installation jobs for the organization"""
    logger.info(f"User {current_user.id} requesting installation jobs")
    
    query = db.query(InstallationJob).filter(
        InstallationJob.organization_id == current_user.organization_id
    )
    
    # Apply filters
    if filter_params.status:
        query = query.filter(InstallationJob.status == filter_params.status)
    if filter_params.priority:
        query = query.filter(InstallationJob.priority == filter_params.priority)
    if filter_params.customer_id:
        query = query.filter(InstallationJob.customer_id == filter_params.customer_id)
    if filter_params.assigned_technician_id:
        query = query.filter(InstallationJob.assigned_technician_id == filter_params.assigned_technician_id)
    if filter_params.dispatch_order_id:
        query = query.filter(InstallationJob.dispatch_order_id == filter_params.dispatch_order_id)
    if filter_params.from_date:
        query = query.filter(InstallationJob.created_at >= filter_params.from_date)
    if filter_params.to_date:
        query = query.filter(InstallationJob.created_at <= filter_params.to_date)
    
    # Order by creation date descending
    query = query.order_by(InstallationJob.created_at.desc())
    
    # Apply pagination
    installation_jobs = query.offset(skip).limit(limit).all()
    
    return installation_jobs


@router.get("/installation-jobs/{job_id}", response_model=InstallationJobInDB)
async def get_installation_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_installation_read)
):
    """Get a specific installation job"""
    installation_job = db.query(InstallationJob).filter(
        InstallationJob.id == job_id,
        InstallationJob.organization_id == current_user.organization_id
    ).first()
    
    if not installation_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Installation job not found"
        )
    
    return installation_job


@router.put("/installation-jobs/{job_id}", response_model=InstallationJobInDB)
async def update_installation_job(
    job_id: int,
    job_update: InstallationJobUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_installation_update)
):
    """Update an installation job"""
    installation_job = db.query(InstallationJob).filter(
        InstallationJob.id == job_id,
        InstallationJob.organization_id == current_user.organization_id
    ).first()
    
    if not installation_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Installation job not found"
        )
    
    try:
        installation_service = InstallationJobService(db)
        
        # Update installation job fields
        update_data = job_update.dict(exclude_unset=True)
        if update_data.get('status'):
            installation_job = installation_service.update_job_status(
                job_id=job_id,
                updated_by_id=current_user.id,
                **update_data
            )
        elif update_data.get('assigned_technician_id'):
            installation_job = installation_service.assign_technician(
                job_id=job_id,
                technician_id=update_data['assigned_technician_id'],
                updated_by_id=current_user.id
            )
            # Apply other updates
            other_updates = {k: v for k, v in update_data.items() if k != 'assigned_technician_id'}
            for key, value in other_updates.items():
                setattr(installation_job, key, value)
            db.commit()
            db.refresh(installation_job)
        else:
            for key, value in update_data.items():
                setattr(installation_job, key, value)
            
            installation_job.updated_by_id = current_user.id
            db.commit()
            db.refresh(installation_job)
        
        logger.info(f"User {current_user.id} updated installation job {job_id}")
        return installation_job
        
    except Exception as e:
        logger.error(f"Error updating installation job {job_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update installation job"
        )


@router.delete("/installation-jobs/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_installation_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_installation_delete)
):
    """Delete an installation job (only if in scheduled status)"""
    installation_job = db.query(InstallationJob).filter(
        InstallationJob.id == job_id,
        InstallationJob.organization_id == current_user.organization_id
    ).first()
    
    if not installation_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Installation job not found"
        )
    
    if installation_job.status not in ["scheduled", "cancelled"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only delete installation jobs in scheduled or cancelled status"
        )
    
    try:
        db.delete(installation_job)
        db.commit()
        logger.info(f"User {current_user.id} deleted installation job {job_id}")
        
    except Exception as e:
        logger.error(f"Error deleting installation job {job_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete installation job"
        )


# Installation Schedule Prompt Endpoint (for delivery challan/service voucher workflow)
@router.post("/installation-schedule-prompt", response_model=InstallationJobInDB)
async def handle_installation_schedule_prompt(
    response_data: InstallationSchedulePromptResponse,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_installation_create)
):
    """Handle the installation schedule prompt response after delivery challan/service voucher creation"""
    logger.info(f"User {current_user.id} responding to installation schedule prompt")
    
    if not response_data.create_installation_schedule:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Installation schedule creation not requested"
        )
    
    if not response_data.installation_job:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Installation job details required"
        )
    
    try:
        # Create the installation job
        installation_service = InstallationJobService(db)
        
        job_dict = response_data.installation_job.dict(exclude={'dispatch_order_id'})
        installation_job = installation_service.create_installation_job(
            organization_id=current_user.organization_id,
            dispatch_order_id=response_data.installation_job.dispatch_order_id,
            created_by_id=current_user.id,
            **job_dict
        )
        
        logger.info(f"Created installation job {installation_job.job_number} from prompt response")
        return installation_job
        
    except Exception as e:
        logger.error(f"Error creating installation job from prompt: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create installation job"
        )


# Enhanced Installation Job Endpoints with Tasks and Completion
@router.get("/installation-jobs/{job_id}/details", response_model=InstallationJobWithDetails)
async def get_installation_job_with_details(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_installation_read)
):
    """Get installation job with tasks and completion record"""
    installation_job = db.query(InstallationJob).filter(
        InstallationJob.id == job_id,
        InstallationJob.organization_id == current_user.organization_id
    ).first()
    
    if not installation_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Installation job not found"
        )
    
    return installation_job


# Installation Task Endpoints
@router.post("/installation-tasks", response_model=InstallationTaskInDB, status_code=status.HTTP_201_CREATED)
async def create_installation_task(
    task_data: InstallationTaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_installation_task_create)
):
    """Create a new installation task"""
    logger.info(f"User {current_user.id} creating installation task for job {task_data.installation_job_id}")
    
    # Verify installation job exists and belongs to organization
    installation_job = db.query(InstallationJob).filter(
        InstallationJob.id == task_data.installation_job_id,
        InstallationJob.organization_id == current_user.organization_id
    ).first()
    
    if not installation_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Installation job not found"
        )
    
    try:
        task_service = InstallationTaskService(db)
        
        task_dict = task_data.dict(exclude={'installation_job_id'})
        installation_task = task_service.create_installation_task(
            organization_id=current_user.organization_id,
            installation_job_id=task_data.installation_job_id,
            created_by_id=current_user.id,
            **task_dict
        )
        
        return installation_task
        
    except Exception as e:
        logger.error(f"Error creating installation task: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create installation task"
        )


@router.get("/installation-tasks", response_model=List[InstallationTaskInDB])
async def get_installation_tasks(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Number of records to return"),
    filter_params: InstallationTaskFilter = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_installation_task_read)
):
    """Get installation tasks for the organization"""
    logger.info(f"User {current_user.id} requesting installation tasks")
    
    query = db.query(InstallationTask).filter(
        InstallationTask.organization_id == current_user.organization_id
    )
    
    # Apply filters
    if filter_params.status:
        query = query.filter(InstallationTask.status == filter_params.status)
    if filter_params.priority:
        query = query.filter(InstallationTask.priority == filter_params.priority)
    if filter_params.installation_job_id:
        query = query.filter(InstallationTask.installation_job_id == filter_params.installation_job_id)
    if filter_params.assigned_technician_id:
        query = query.filter(InstallationTask.assigned_technician_id == filter_params.assigned_technician_id)
    
    # Order by sequence within job, then creation date
    query = query.order_by(InstallationTask.installation_job_id, InstallationTask.sequence_order, InstallationTask.created_at)
    
    # Apply pagination
    installation_tasks = query.offset(skip).limit(limit).all()
    
    return installation_tasks


@router.get("/installation-tasks/{task_id}", response_model=InstallationTaskInDB)
async def get_installation_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_installation_task_read)
):
    """Get a specific installation task"""
    installation_task = db.query(InstallationTask).filter(
        InstallationTask.id == task_id,
        InstallationTask.organization_id == current_user.organization_id
    ).first()
    
    if not installation_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Installation task not found"
        )
    
    return installation_task


@router.put("/installation-tasks/{task_id}", response_model=InstallationTaskInDB)
async def update_installation_task(
    task_id: int,
    task_update: InstallationTaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_installation_task_update)
):
    """Update an installation task"""
    installation_task = db.query(InstallationTask).filter(
        InstallationTask.id == task_id,
        InstallationTask.organization_id == current_user.organization_id
    ).first()
    
    if not installation_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Installation task not found"
        )
    
    try:
        task_service = InstallationTaskService(db)
        
        # Update task fields
        update_data = task_update.dict(exclude_unset=True)
        if update_data.get('status'):
            installation_task = task_service.update_task_status(
                task_id=task_id,
                updated_by_id=current_user.id,
                **update_data
            )
        elif update_data.get('assigned_technician_id'):
            installation_task = task_service.assign_technician(
                task_id=task_id,
                technician_id=update_data['assigned_technician_id'],
                updated_by_id=current_user.id
            )
            # Apply other updates
            other_updates = {k: v for k, v in update_data.items() if k != 'assigned_technician_id'}
            for key, value in other_updates.items():
                setattr(installation_task, key, value)
            db.commit()
            db.refresh(installation_task)
        else:
            for key, value in update_data.items():
                setattr(installation_task, key, value)
            
            installation_task.updated_by_id = current_user.id
            db.commit()
            db.refresh(installation_task)
        
        logger.info(f"User {current_user.id} updated installation task {task_id}")
        return installation_task
        
    except Exception as e:
        logger.error(f"Error updating installation task {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update installation task"
        )


@router.delete("/installation-tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_installation_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_installation_task_delete)
):
    """Delete an installation task"""
    installation_task = db.query(InstallationTask).filter(
        InstallationTask.id == task_id,
        InstallationTask.organization_id == current_user.organization_id
    ).first()
    
    if not installation_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Installation task not found"
        )
    
    if installation_task.status in ["in_progress", "completed"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete task that is in progress or completed"
        )
    
    try:
        db.delete(installation_task)
        db.commit()
        logger.info(f"User {current_user.id} deleted installation task {task_id}")
        
    except Exception as e:
        logger.error(f"Error deleting installation task {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete installation task"
        )


# Completion Record Endpoints
@router.post("/installation-jobs/{job_id}/complete", response_model=CompletionRecordInDB, status_code=status.HTTP_201_CREATED)
async def complete_installation_job(
    job_id: int,
    completion_data: CompletionRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_technician_completion)
):
    """Complete an installation job (technician only)"""
    logger.info(f"User {current_user.id} completing installation job {job_id}")
    
    # Override job_id from URL
    completion_data.installation_job_id = job_id
    
    try:
        completion_service = CompletionRecordService(db)
        
        completion_dict = completion_data.dict(exclude={'installation_job_id'})
        completion_record = completion_service.create_completion_record(
            organization_id=current_user.organization_id,
            installation_job_id=job_id,
            completed_by_id=current_user.id,
            **completion_dict
        )
        
        return completion_record
        
    except ValueError as e:
        logger.error(f"Validation error completing installation job {job_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error completing installation job {job_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to complete installation job"
        )


@router.get("/completion-records", response_model=List[CompletionRecordInDB])
async def get_completion_records(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Number of records to return"),
    filter_params: CompletionRecordFilter = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_completion_record_read)
):
    """Get completion records for the organization"""
    logger.info(f"User {current_user.id} requesting completion records")
    
    query = db.query(CompletionRecord).filter(
        CompletionRecord.organization_id == current_user.organization_id
    )
    
    # Apply filters
    if filter_params.completion_status:
        query = query.filter(CompletionRecord.completion_status == filter_params.completion_status)
    if filter_params.completed_by_id:
        query = query.filter(CompletionRecord.completed_by_id == filter_params.completed_by_id)
    if filter_params.customer_rating:
        query = query.filter(CompletionRecord.customer_rating == filter_params.customer_rating)
    if filter_params.follow_up_required is not None:
        query = query.filter(CompletionRecord.follow_up_required == filter_params.follow_up_required)
    if filter_params.from_date:
        query = query.filter(CompletionRecord.completion_date >= filter_params.from_date)
    if filter_params.to_date:
        query = query.filter(CompletionRecord.completion_date <= filter_params.to_date)
    
    # Order by completion date descending
    query = query.order_by(CompletionRecord.completion_date.desc())
    
    # Apply pagination
    completion_records = query.offset(skip).limit(limit).all()
    
    return completion_records


@router.get("/completion-records/{record_id}", response_model=CompletionRecordInDB)
async def get_completion_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_completion_record_read)
):
    """Get a specific completion record"""
    completion_record = db.query(CompletionRecord).filter(
        CompletionRecord.id == record_id,
        CompletionRecord.organization_id == current_user.organization_id
    ).first()
    
    if not completion_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Completion record not found"
        )
    
    return completion_record


@router.put("/completion-records/{record_id}", response_model=CompletionRecordInDB)
async def update_completion_record(
    record_id: int,
    completion_update: CompletionRecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_completion_record_update)
):
    """Update a completion record"""
    completion_record = db.query(CompletionRecord).filter(
        CompletionRecord.id == record_id,
        CompletionRecord.organization_id == current_user.organization_id
    ).first()
    
    if not completion_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Completion record not found"
        )
    
    try:
        completion_service = CompletionRecordService(db)
        
        # Update completion record fields
        update_data = completion_update.dict(exclude_unset=True)
        completion_record = completion_service.update_completion_record(
            completion_record_id=record_id,
            organization_id=current_user.organization_id,
            **update_data
        )
        
        logger.info(f"User {current_user.id} updated completion record {record_id}")
        return completion_record
        
    except Exception as e:
        logger.error(f"Error updating completion record {record_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update completion record"
        )