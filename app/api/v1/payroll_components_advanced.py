# app/api/v1/payroll_components_advanced.py
from app.core.enforcement import require_access
# Phase 2: Advanced Payroll Component Management with Multi-Component Support

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_, or_
from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime, date

from app.db.session import get_db

from app.models.user_models import User
from app.models.payroll_models import PayrollComponent, PayrollRun, PayrollLine
from app.models.erp_models import ChartOfAccounts
from app.schemas.payroll_schemas import (
    PayrollComponentCreate,
    PayrollComponentUpdate,
    PayrollComponentResponse,
    PayrollComponentDetail,
    BulkPayrollComponentCreate,
    BulkPayrollComponentResult,
    PayrollComponentMapping,
    PayrollComponentMappingUpdate,
    AdvancedPayrollSettings,
    DepartmentAccountMapping,
    PayrollComponentFilter
)

import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/payroll/components/bulk", response_model=BulkPayrollComponentResult)
async def bulk_create_payroll_components(
    bulk_data: BulkPayrollComponentCreate,
    auth: tuple = Depends(require_access("payroll", "create")),
    db: Session = Depends(get_db),
):
    """Bulk create payroll components with chart account mappings"""
    try:
        created_components = []
        errors = []
        
        for component_data in bulk_data.components:
            try:
                # Validate chart accounts if provided
                if component_data.expense_account_id:
                    expense_account = db.query(ChartOfAccounts).filter(
                        ChartOfAccounts.id == component_data.expense_account_id,
                        ChartOfAccounts.organization_id == organization_id,
                        ChartOfAccounts.is_active == True
                    ).first()
                    
                    if not expense_account:
                        errors.append({
                            "component_code": component_data.component_code,
                            "error": "Invalid expense account ID"
                        })
                        continue
                
                if component_data.payable_account_id:
                    payable_account = db.query(ChartOfAccounts).filter(
                        ChartOfAccounts.id == component_data.payable_account_id,
                        ChartOfAccounts.organization_id == organization_id,
                        ChartOfAccounts.is_active == True
                    ).first()
                    
                    if not payable_account:
                        errors.append({
                            "component_code": component_data.component_code,
                            "error": "Invalid payable account ID"
                        })
                        continue
                
                # Check for duplicate component code
                existing_component = db.query(PayrollComponent).filter(
                    PayrollComponent.organization_id == organization_id,
                    PayrollComponent.component_code == component_data.component_code
                ).first()
                
                if existing_component:
                    errors.append({
                        "component_code": component_data.component_code,
                        "error": "Component code already exists"
                    })
                    continue
                
                # Create component
                new_component = PayrollComponent(
                    organization_id=organization_id,
                    component_name=component_data.component_name,
                    component_code=component_data.component_code,
                    component_type=component_data.component_type,
                    expense_account_id=component_data.expense_account_id,
                    payable_account_id=component_data.payable_account_id,
                    is_active=component_data.is_active,
                    is_taxable=component_data.is_taxable,
                    calculation_formula=component_data.calculation_formula,
                    default_amount=component_data.default_amount,
                    default_percentage=component_data.default_percentage,
                    created_by_id=current_user.id
                )
                
                db.add(new_component)
                db.flush()  # Get the ID
                
                created_components.append({
                    "id": new_component.id,
                    "component_code": new_component.component_code,
                    "component_name": new_component.component_name
                })
                
            except Exception as e:
                errors.append({
                    "component_code": component_data.component_code,
                    "error": str(e)
                })
        
        db.commit()
        
        return BulkPayrollComponentResult(
            total_components=len(bulk_data.components),
            created_count=len(created_components),
            error_count=len(errors),
            created_components=created_components,
            errors=errors
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error in bulk component creation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating bulk payroll components"
        )


@router.get("/payroll/components/advanced", response_model=List[PayrollComponentDetail])
async def get_advanced_payroll_components(
    filter_params: PayrollComponentFilter = Depends(),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    auth: tuple = Depends(require_access("payroll", "read")),
    db: Session = Depends(get_db),
):
    """Get payroll components with advanced filtering and account details"""
    try:
        query = db.query(PayrollComponent).options(
            joinedload(PayrollComponent.expense_account),
            joinedload(PayrollComponent.payable_account)
        ).filter(
            PayrollComponent.organization_id == organization_id
        )
        
        # Apply filters
        if filter_params.component_types:
            query = query.filter(PayrollComponent.component_type.in_(filter_params.component_types))
        
        if filter_params.is_active is not None:
            query = query.filter(PayrollComponent.is_active == filter_params.is_active)
        
        if filter_params.is_taxable is not None:
            query = query.filter(PayrollComponent.is_taxable == filter_params.is_taxable)
        
        if filter_params.has_expense_account is not None:
            if filter_params.has_expense_account:
                query = query.filter(PayrollComponent.expense_account_id.isnot(None))
            else:
                query = query.filter(PayrollComponent.expense_account_id.is_(None))
        
        if filter_params.has_payable_account is not None:
            if filter_params.has_payable_account:
                query = query.filter(PayrollComponent.payable_account_id.isnot(None))
            else:
                query = query.filter(PayrollComponent.payable_account_id.is_(None))
        
        if filter_params.search:
            search_term = f"%{filter_params.search}%"
            query = query.filter(
                or_(
                    PayrollComponent.component_name.ilike(search_term),
                    PayrollComponent.component_code.ilike(search_term)
                )
            )
        
        # Order by component type and name
        query = query.order_by(
            PayrollComponent.component_type,
            PayrollComponent.component_name
        )
        
        components = query.offset(skip).limit(limit).all()
        
        # Convert to detailed response
        result = []
        for component in components:
            component_detail = PayrollComponentDetail(
                id=component.id,
                organization_id=component.organization_id,
                component_name=component.component_name,
                component_code=component.component_code,
                component_type=component.component_type,
                expense_account_id=component.expense_account_id,
                payable_account_id=component.payable_account_id,
                is_active=component.is_active,
                is_taxable=component.is_taxable,
                calculation_formula=component.calculation_formula,
                default_amount=component.default_amount,
                default_percentage=component.default_percentage,
                created_at=component.created_at,
                updated_at=component.updated_at,
                expense_account=component.expense_account,
                payable_account=component.payable_account
            )
            result.append(component_detail)
        
        return result
        
    except Exception as e:
        logger.error(f"Error fetching advanced payroll components: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching payroll components"
        )


@router.post("/payroll/components/{component_id}/mapping", response_model=PayrollComponentMapping)
async def update_component_chart_mapping(
    component_id: int,
    mapping_data: PayrollComponentMappingUpdate,
    auth: tuple = Depends(require_access("payroll", "create")),
    db: Session = Depends(get_db),
):
    """Update chart account mapping for a payroll component"""
    try:
        # Get component
        component = db.query(PayrollComponent).filter(
            PayrollComponent.id == component_id,
            PayrollComponent.organization_id == organization_id
        ).first()
        
        if not component:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payroll component not found"
            )
        
        # Validate expense account
        if mapping_data.expense_account_id:
            expense_account = db.query(ChartOfAccounts).filter(
                ChartOfAccounts.id == mapping_data.expense_account_id,
                ChartOfAccounts.organization_id == organization_id,
                ChartOfAccounts.is_active == True
            ).first()
            
            if not expense_account:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid expense account ID"
                )
            
            # Validate account type for payroll expenses
            if expense_account.account_type.lower() not in ['expense', 'expenses']:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Expense account must be of type 'Expense'"
                )
        
        # Validate payable account
        if mapping_data.payable_account_id:
            payable_account = db.query(ChartOfAccounts).filter(
                ChartOfAccounts.id == mapping_data.payable_account_id,
                ChartOfAccounts.organization_id == organization_id,
                ChartOfAccounts.is_active == True
            ).first()
            
            if not payable_account:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid payable account ID"
                )
            
            # Validate account type for payroll payables
            if payable_account.account_type.lower() not in ['liability', 'liabilities']:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Payable account must be of type 'Liability'"
                )
        
        # Update component
        component.expense_account_id = mapping_data.expense_account_id
        component.payable_account_id = mapping_data.payable_account_id
        component.updated_at = datetime.utcnow()
        
        db.commit()
        
        # Reload with relationships
        db.refresh(component)
        
        return PayrollComponentMapping(
            component_id=component.id,
            component_name=component.component_name,
            component_code=component.component_code,
            component_type=component.component_type,
            expense_account_id=component.expense_account_id,
            payable_account_id=component.payable_account_id,
            expense_account=component.expense_account,
            payable_account=component.payable_account
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating component mapping: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating chart account mapping"
        )


@router.get("/payroll/components/mapping-status")
async def get_component_mapping_status(
    auth: tuple = Depends(require_access("payroll", "read")),
    db: Session = Depends(get_db),
):
    """Get mapping status for all payroll components"""
    try:
        # Get counts by mapping status
        total_components = db.query(func.count(PayrollComponent.id)).filter(
            PayrollComponent.organization_id == organization_id,
            PayrollComponent.is_active == True
        ).scalar()
        
        fully_mapped = db.query(func.count(PayrollComponent.id)).filter(
            PayrollComponent.organization_id == organization_id,
            PayrollComponent.is_active == True,
            PayrollComponent.expense_account_id.isnot(None),
            PayrollComponent.payable_account_id.isnot(None)
        ).scalar()
        
        partially_mapped = db.query(func.count(PayrollComponent.id)).filter(
            PayrollComponent.organization_id == organization_id,
            PayrollComponent.is_active == True,
            or_(
                and_(PayrollComponent.expense_account_id.isnot(None), PayrollComponent.payable_account_id.is_(None)),
                and_(PayrollComponent.expense_account_id.is_(None), PayrollComponent.payable_account_id.isnot(None))
            )
        ).scalar()
        
        unmapped = db.query(func.count(PayrollComponent.id)).filter(
            PayrollComponent.organization_id == organization_id,
            PayrollComponent.is_active == True,
            PayrollComponent.expense_account_id.is_(None),
            PayrollComponent.payable_account_id.is_(None)
        ).scalar()
        
        # Get unmapped components list
        unmapped_components = db.query(PayrollComponent).filter(
            PayrollComponent.organization_id == organization_id,
            PayrollComponent.is_active == True,
            PayrollComponent.expense_account_id.is_(None),
            PayrollComponent.payable_account_id.is_(None)
        ).all()
        
        return {
            "total_components": total_components,
            "fully_mapped": fully_mapped,
            "partially_mapped": partially_mapped,
            "unmapped": unmapped,
            "mapping_percentage": round((fully_mapped / total_components * 100) if total_components > 0 else 0, 2),
            "unmapped_components": [
                {
                    "id": comp.id,
                    "component_name": comp.component_name,
                    "component_code": comp.component_code,
                    "component_type": comp.component_type
                }
                for comp in unmapped_components
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting mapping status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving mapping status"
        )


@router.post("/payroll/settings/advanced", response_model=AdvancedPayrollSettings)
async def update_advanced_payroll_settings(
    settings: AdvancedPayrollSettings,
    auth: tuple = Depends(require_access("payroll", "create")),
    db: Session = Depends(get_db),
):
    """Update advanced payroll settings with default account mappings"""
    try:
        # This would integrate with a PayrollSettings model to store advanced configurations
        # For now, we'll return the received settings as confirmation
        
        # TODO: Implement storage of advanced settings
        # This could include:
        # - Default account mappings per department
        # - Category-specific account defaults
        # - Approval workflow settings
        # - Multi-component calculation rules
        
        logger.info(f"Advanced payroll settings updated for organization {organization_id}")
        
        return settings
        
    except Exception as e:
        logger.error(f"Error updating advanced settings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating advanced payroll settings"
        )


@router.get("/payroll/components/validation")
async def validate_all_components(
    auth: tuple = Depends(require_access("payroll", "read")),
    db: Session = Depends(get_db),
):
    """Validate all payroll components for chart account mappings"""
    try:
        components = db.query(PayrollComponent).options(
            joinedload(PayrollComponent.expense_account),
            joinedload(PayrollComponent.payable_account)
        ).filter(
            PayrollComponent.organization_id == organization_id,
            PayrollComponent.is_active == True
        ).all()
        
        validation_results = []
        
        for component in components:
            issues = []
            
            # Check if expense account is mapped for earnings/deductions
            if component.component_type in ['earning', 'deduction'] and not component.expense_account_id:
                issues.append("Missing expense account mapping")
            
            # Check if payable account is mapped for deductions/contributions
            if component.component_type in ['deduction', 'employer_contribution'] and not component.payable_account_id:
                issues.append("Missing payable account mapping")
            
            # Check if mapped accounts are active
            if component.expense_account and not component.expense_account.is_active:
                issues.append("Expense account is inactive")
            
            if component.payable_account and not component.payable_account.is_active:
                issues.append("Payable account is inactive")
            
            # Check account types
            if component.expense_account and component.expense_account.account_type.lower() not in ['expense', 'expenses']:
                issues.append("Expense account has incorrect type")
            
            if component.payable_account and component.payable_account.account_type.lower() not in ['liability', 'liabilities']:
                issues.append("Payable account has incorrect type")
            
            validation_results.append({
                "component_id": component.id,
                "component_name": component.component_name,
                "component_code": component.component_code,
                "component_type": component.component_type,
                "is_valid": len(issues) == 0,
                "issues": issues,
                "expense_account_mapped": component.expense_account_id is not None,
                "payable_account_mapped": component.payable_account_id is not None
            })
        
        total_components = len(components)
        valid_components = len([r for r in validation_results if r["is_valid"]])
        
        return {
            "total_components": total_components,
            "valid_components": valid_components,
            "invalid_components": total_components - valid_components,
            "validation_percentage": round((valid_components / total_components * 100) if total_components > 0 else 0, 2),
            "validation_results": validation_results
        }
        
    except Exception as e:
        logger.error(f"Error validating components: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error validating payroll components"
        )