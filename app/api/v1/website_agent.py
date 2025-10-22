# app/api/v1/website_agent.py

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import datetime
import logging

from app.core.database import get_db
from app.core.security import get_current_user, get_current_active_user
from app.models.user_models import User
from app.models.website_agent import WebsiteProject, WebsitePage, WebsiteDeployment, WebsiteMaintenanceLog
from app.schemas import website_agent as schemas

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/website-agent", tags=["website-agent"])


# Helper function to check organization access
def check_project_access(project_id: int, organization_id: int, db: Session) -> WebsiteProject:
    """Check if user has access to the project"""
    project = db.query(WebsiteProject).filter(
        and_(
            WebsiteProject.id == project_id,
            WebsiteProject.organization_id == organization_id
        )
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Website project not found"
        )
    
    return project


# Website Project Endpoints

@router.get("/projects", response_model=List[schemas.WebsiteProject])
async def list_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[str] = None,
    project_type: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List all website projects for the organization.
    """
    try:
        query = db.query(WebsiteProject).filter(
            WebsiteProject.organization_id == current_user.organization_id
        )
        
        if status:
            query = query.filter(WebsiteProject.status == status)
        
        if project_type:
            query = query.filter(WebsiteProject.project_type == project_type)
        
        projects = query.order_by(WebsiteProject.created_at.desc()).offset(skip).limit(limit).all()
        
        logger.info(f"User {current_user.id} listed {len(projects)} website projects")
        return projects
    
    except Exception as e:
        logger.error(f"Error listing website projects: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing website projects: {str(e)}"
        )


@router.get("/projects/{project_id}", response_model=schemas.WebsiteProject)
async def get_project(
    project_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific website project by ID.
    """
    try:
        project = check_project_access(project_id, current_user.organization_id, db)
        logger.info(f"User {current_user.id} retrieved website project {project_id}")
        return project
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving website project {project_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving website project: {str(e)}"
        )


@router.post("/projects", response_model=schemas.WebsiteProject, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: schemas.WebsiteProjectCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new website project.
    """
    try:
        # Check for duplicate project name
        existing = db.query(WebsiteProject).filter(
            and_(
                WebsiteProject.organization_id == current_user.organization_id,
                WebsiteProject.project_name == project_data.project_name
            )
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Project with this name already exists"
            )
        
        # Create new project
        new_project = WebsiteProject(
            **project_data.model_dump(),
            organization_id=current_user.organization_id,
            created_by_id=current_user.id,
            updated_by_id=current_user.id
        )
        
        db.add(new_project)
        db.commit()
        db.refresh(new_project)
        
        logger.info(f"User {current_user.id} created website project {new_project.id}")
        return new_project
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating website project: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating website project: {str(e)}"
        )


@router.put("/projects/{project_id}", response_model=schemas.WebsiteProject)
async def update_project(
    project_id: int,
    project_data: schemas.WebsiteProjectUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing website project.
    """
    try:
        project = check_project_access(project_id, current_user.organization_id, db)
        
        # Update fields
        update_data = project_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(project, field, value)
        
        project.updated_by_id = current_user.id
        
        db.commit()
        db.refresh(project)
        
        logger.info(f"User {current_user.id} updated website project {project_id}")
        return project
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating website project {project_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating website project: {str(e)}"
        )


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a website project.
    """
    try:
        project = check_project_access(project_id, current_user.organization_id, db)
        
        db.delete(project)
        db.commit()
        
        logger.info(f"User {current_user.id} deleted website project {project_id}")
        return None
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting website project {project_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting website project: {str(e)}"
        )


# Website Page Endpoints

@router.get("/projects/{project_id}/pages", response_model=List[schemas.WebsitePage])
async def list_pages(
    project_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List all pages for a website project.
    """
    try:
        # Check project access
        check_project_access(project_id, current_user.organization_id, db)
        
        pages = db.query(WebsitePage).filter(
            and_(
                WebsitePage.project_id == project_id,
                WebsitePage.organization_id == current_user.organization_id
            )
        ).order_by(WebsitePage.order_index).all()
        
        logger.info(f"User {current_user.id} listed {len(pages)} pages for project {project_id}")
        return pages
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing pages for project {project_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing pages: {str(e)}"
        )


@router.post("/projects/{project_id}/pages", response_model=schemas.WebsitePage, status_code=status.HTTP_201_CREATED)
async def create_page(
    project_id: int,
    page_data: schemas.WebsitePageCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new page for a website project.
    """
    try:
        # Check project access
        check_project_access(project_id, current_user.organization_id, db)
        
        # Check for duplicate page slug
        existing = db.query(WebsitePage).filter(
            and_(
                WebsitePage.project_id == project_id,
                WebsitePage.page_slug == page_data.page_slug
            )
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Page with this slug already exists in the project"
            )
        
        # Create new page
        new_page = WebsitePage(
            **page_data.model_dump(),
            organization_id=current_user.organization_id
        )
        
        db.add(new_page)
        db.commit()
        db.refresh(new_page)
        
        logger.info(f"User {current_user.id} created page {new_page.id} for project {project_id}")
        return new_page
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating page for project {project_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating page: {str(e)}"
        )


@router.put("/pages/{page_id}", response_model=schemas.WebsitePage)
async def update_page(
    page_id: int,
    page_data: schemas.WebsitePageUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing website page.
    """
    try:
        page = db.query(WebsitePage).filter(
            and_(
                WebsitePage.id == page_id,
                WebsitePage.organization_id == current_user.organization_id
            )
        ).first()
        
        if not page:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Page not found"
            )
        
        # Update fields
        update_data = page_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(page, field, value)
        
        db.commit()
        db.refresh(page)
        
        logger.info(f"User {current_user.id} updated page {page_id}")
        return page
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating page {page_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating page: {str(e)}"
        )


@router.delete("/pages/{page_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_page(
    page_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a website page.
    """
    try:
        page = db.query(WebsitePage).filter(
            and_(
                WebsitePage.id == page_id,
                WebsitePage.organization_id == current_user.organization_id
            )
        ).first()
        
        if not page:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Page not found"
            )
        
        db.delete(page)
        db.commit()
        
        logger.info(f"User {current_user.id} deleted page {page_id}")
        return None
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting page {page_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting page: {str(e)}"
        )


# Deployment Endpoints

@router.post("/projects/{project_id}/deploy", response_model=schemas.WebsiteDeployment, status_code=status.HTTP_201_CREATED)
async def deploy_project(
    project_id: int,
    deployment_data: schemas.WebsiteDeploymentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Deploy a website project.
    """
    try:
        project = check_project_access(project_id, current_user.organization_id, db)
        
        # Create deployment record
        new_deployment = WebsiteDeployment(
            **deployment_data.model_dump(),
            organization_id=current_user.organization_id,
            deployment_status="pending",
            deployed_by_id=current_user.id,
            started_at=datetime.now()
        )
        
        db.add(new_deployment)
        db.commit()
        db.refresh(new_deployment)
        
        # TODO: Trigger actual deployment process here
        # For now, just mark as success
        new_deployment.deployment_status = "success"
        new_deployment.completed_at = datetime.now()
        project.last_deployed_at = datetime.now()
        project.deployment_url = new_deployment.deployment_url
        project.deployment_provider = new_deployment.deployment_provider
        
        db.commit()
        db.refresh(new_deployment)
        
        logger.info(f"User {current_user.id} deployed website project {project_id}")
        return new_deployment
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deploying project {project_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deploying project: {str(e)}"
        )


@router.get("/projects/{project_id}/deployments", response_model=List[schemas.WebsiteDeployment])
async def list_deployments(
    project_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List all deployments for a website project.
    """
    try:
        # Check project access
        check_project_access(project_id, current_user.organization_id, db)
        
        deployments = db.query(WebsiteDeployment).filter(
            and_(
                WebsiteDeployment.project_id == project_id,
                WebsiteDeployment.organization_id == current_user.organization_id
            )
        ).order_by(WebsiteDeployment.created_at.desc()).all()
        
        logger.info(f"User {current_user.id} listed {len(deployments)} deployments for project {project_id}")
        return deployments
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing deployments for project {project_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing deployments: {str(e)}"
        )


# Maintenance Log Endpoints

@router.post("/projects/{project_id}/maintenance", response_model=schemas.WebsiteMaintenanceLog, status_code=status.HTTP_201_CREATED)
async def create_maintenance_log(
    project_id: int,
    log_data: schemas.WebsiteMaintenanceLogCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a maintenance log entry for a website project.
    """
    try:
        # Check project access
        check_project_access(project_id, current_user.organization_id, db)
        
        # Create maintenance log
        new_log = WebsiteMaintenanceLog(
            **log_data.model_dump(),
            organization_id=current_user.organization_id,
            performed_by_id=current_user.id,
            completed_at=datetime.now() if log_data.status == "completed" else None
        )
        
        db.add(new_log)
        db.commit()
        db.refresh(new_log)
        
        logger.info(f"User {current_user.id} created maintenance log {new_log.id} for project {project_id}")
        return new_log
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating maintenance log for project {project_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating maintenance log: {str(e)}"
        )


@router.get("/projects/{project_id}/maintenance", response_model=List[schemas.WebsiteMaintenanceLog])
async def list_maintenance_logs(
    project_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List all maintenance logs for a website project.
    """
    try:
        # Check project access
        check_project_access(project_id, current_user.organization_id, db)
        
        logs = db.query(WebsiteMaintenanceLog).filter(
            and_(
                WebsiteMaintenanceLog.project_id == project_id,
                WebsiteMaintenanceLog.organization_id == current_user.organization_id
            )
        ).order_by(WebsiteMaintenanceLog.created_at.desc()).all()
        
        logger.info(f"User {current_user.id} listed {len(logs)} maintenance logs for project {project_id}")
        return logs
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing maintenance logs for project {project_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing maintenance logs: {str(e)}"
        )
