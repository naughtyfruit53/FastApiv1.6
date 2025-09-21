# app/api/v1/payroll_components.py

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.db.session import get_db
from app.api.v1.auth import get_current_active_user
from app.core.org_restrictions import require_current_organization_id
from app.models.user_models import User
from app.models.payroll_models import PayrollComponent
from app.models.erp_models import ChartOfAccounts
from app.schemas.payroll_schemas import (
    PayrollComponentCreate, 
    PayrollComponentUpdate, 
    PayrollComponentResponse,
    PayrollComponentList
)

logger = logging.getLogger(__name__)
router = APIRouter()


def validate_chart_account(db: Session, chart_account_id: int, organization_id: int, account_types: List[str] = None) -> ChartOfAccounts:
    """Validate that chart_account_id exists, belongs to organization, and has correct account type"""
    query = db.query(ChartOfAccounts).filter(
        ChartOfAccounts.id == chart_account_id,
        ChartOfAccounts.organization_id == organization_id,
        ChartOfAccounts.is_active == True
    )
    
    if account_types:
        query = query.filter(ChartOfAccounts.account_type.in_(account_types))
    
    chart_account = query.first()
    
    if not chart_account:
        if account_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid chart account ID or account not found for this organization. Account must be of type: {', '.join(account_types)}"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid chart account ID or account not found for this organization"
            )
    
    return chart_account


@router.post("/payroll/components", response_model=PayrollComponentResponse)
async def create_payroll_component(
    component: PayrollComponentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    organization_id: int = Depends(require_current_organization_id)
):
    """Create a new payroll component with chart account mapping"""
    try:
        # Validate expense account if provided
        if component.expense_account_id:
            validate_chart_account(
                db, 
                component.expense_account_id, 
                organization_id, 
                ["expense"]
            )
        
        # Validate payable account if provided
        if component.payable_account_id:
            validate_chart_account(
                db, 
                component.payable_account_id, 
                organization_id, 
                ["liability"]
            )
        
        # Check for duplicate component code
        existing = db.query(PayrollComponent).filter(
            PayrollComponent.organization_id == organization_id,
            PayrollComponent.component_code == component.component_code
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Component code already exists for this organization"
            )
        
        # Create new payroll component
        db_component = PayrollComponent(
            organization_id=organization_id,
            created_by_id=current_user.id,
            **component.dict()
        )
        
        db.add(db_component)
        db.commit()
        db.refresh(db_component)
        
        logger.info(f"Created payroll component {db_component.id} for organization {organization_id}")
        return db_component
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating payroll component: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating payroll component"
        )


@router.get("/payroll/components", response_model=PayrollComponentList)
async def get_payroll_components(
    page: int = Query(1, ge=1),
    per_page: int = Query(100, ge=1, le=1000),
    component_type: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get payroll components with filtering and pagination"""
    try:
        query = db.query(PayrollComponent).filter(
            PayrollComponent.organization_id == organization_id
        )
        
        # Apply filters
        if component_type:
            query = query.filter(PayrollComponent.component_type == component_type)
        
        if is_active is not None:
            query = query.filter(PayrollComponent.is_active == is_active)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        components = query.offset((page - 1) * per_page).limit(per_page).all()
        
        return PayrollComponentList(
            components=components,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=(total + per_page - 1) // per_page
        )
        
    except Exception as e:
        logger.error(f"Error fetching payroll components: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching payroll components"
        )


@router.get("/payroll/components/{component_id}", response_model=PayrollComponentResponse)
async def get_payroll_component(
    component_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get a specific payroll component"""
    component = db.query(PayrollComponent).filter(
        PayrollComponent.id == component_id,
        PayrollComponent.organization_id == organization_id
    ).first()
    
    if not component:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payroll component not found"
        )
    
    return component


@router.put("/payroll/components/{component_id}", response_model=PayrollComponentResponse)
async def update_payroll_component(
    component_id: int,
    component_update: PayrollComponentUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    organization_id: int = Depends(require_current_organization_id)
):
    """Update a payroll component"""
    try:
        # Get existing component
        db_component = db.query(PayrollComponent).filter(
            PayrollComponent.id == component_id,
            PayrollComponent.organization_id == organization_id
        ).first()
        
        if not db_component:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payroll component not found"
            )
        
        # Validate expense account if provided
        if component_update.expense_account_id:
            validate_chart_account(
                db, 
                component_update.expense_account_id, 
                organization_id, 
                ["expense"]
            )
        
        # Validate payable account if provided
        if component_update.payable_account_id:
            validate_chart_account(
                db, 
                component_update.payable_account_id, 
                organization_id, 
                ["liability"]
            )
        
        # Check for duplicate component code if code is being changed
        if component_update.component_code and component_update.component_code != db_component.component_code:
            existing = db.query(PayrollComponent).filter(
                PayrollComponent.organization_id == organization_id,
                PayrollComponent.component_code == component_update.component_code,
                PayrollComponent.id != component_id
            ).first()
            
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Component code already exists for this organization"
                )
        
        # Update component
        update_data = component_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_component, field, value)
        
        db.commit()
        db.refresh(db_component)
        
        logger.info(f"Updated payroll component {component_id} for organization {organization_id}")
        return db_component
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating payroll component: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating payroll component"
        )


@router.delete("/payroll/components/{component_id}")
async def delete_payroll_component(
    component_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    organization_id: int = Depends(require_current_organization_id)
):
    """Delete a payroll component (soft delete by setting inactive)"""
    try:
        component = db.query(PayrollComponent).filter(
            PayrollComponent.id == component_id,
            PayrollComponent.organization_id == organization_id
        ).first()
        
        if not component:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payroll component not found"
            )
        
        # Soft delete by setting inactive
        component.is_active = False
        db.commit()
        
        logger.info(f"Deleted payroll component {component_id} for organization {organization_id}")
        return {"message": "Payroll component deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting payroll component: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting payroll component"
        )


@router.post("/payroll/components/{component_id}/chart-account-mapping")
async def update_component_chart_account_mapping(
    component_id: int,
    expense_account_id: Optional[int] = None,
    payable_account_id: Optional[int] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    organization_id: int = Depends(require_current_organization_id)
):
    """Update chart account mapping for a payroll component"""
    try:
        component = db.query(PayrollComponent).filter(
            PayrollComponent.id == component_id,
            PayrollComponent.organization_id == organization_id
        ).first()
        
        if not component:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payroll component not found"
            )
        
        # Validate accounts if provided
        if expense_account_id:
            validate_chart_account(db, expense_account_id, organization_id, ["expense"])
            component.expense_account_id = expense_account_id
        
        if payable_account_id:
            validate_chart_account(db, payable_account_id, organization_id, ["liability"])
            component.payable_account_id = payable_account_id
        
        db.commit()
        db.refresh(component)
        
        logger.info(f"Updated chart account mapping for payroll component {component_id}")
        return component
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating chart account mapping: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating chart account mapping"
        )