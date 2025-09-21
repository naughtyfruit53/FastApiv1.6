# app/api/v1/payroll_migration.py
# Phase 2: Payroll Migration and Backfill System

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_, or_, text
from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime, date

from app.db.session import get_db
from app.api.v1.auth import get_current_active_user
from app.core.org_restrictions import require_current_organization_id
from app.models.user_models import User
from app.models.payroll_models import PayrollComponent, PayrollRun, PayrollLine
from app.models.erp_models import ChartOfAccounts
from app.schemas.payroll_schemas import (
    PayrollBackfillRequest,
    PayrollBackfillResult,
    PayrollMigrationStatus,
    PayrollValidationResult
)

import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/payroll/migration/status", response_model=PayrollMigrationStatus)
async def get_migration_status(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get current migration status for payroll components"""
    try:
        # Count total components
        total_components = db.query(func.count(PayrollComponent.id)).filter(
            PayrollComponent.organization_id == organization_id,
            PayrollComponent.is_active == True
        ).scalar()
        
        # Count mapped components (have at least one account)
        mapped_components = db.query(func.count(PayrollComponent.id)).filter(
            PayrollComponent.organization_id == organization_id,
            PayrollComponent.is_active == True,
            or_(
                PayrollComponent.expense_account_id.isnot(None),
                PayrollComponent.payable_account_id.isnot(None)
            )
        ).scalar()
        
        unmapped_components = total_components - mapped_components
        mapping_percentage = (mapped_components / total_components * 100) if total_components > 0 else 0
        
        # Get validation errors
        validation_errors = []
        migration_suggestions = []
        
        # Check for components without required mappings
        components = db.query(PayrollComponent).filter(
            PayrollComponent.organization_id == organization_id,
            PayrollComponent.is_active == True
        ).all()
        
        for component in components:
            if component.component_type in ['earning', 'deduction'] and not component.expense_account_id:
                validation_errors.append(f"Component '{component.component_name}' missing expense account")
                migration_suggestions.append(f"Map component '{component.component_name}' to an expense account")
            
            if component.component_type in ['deduction', 'employer_contribution'] and not component.payable_account_id:
                validation_errors.append(f"Component '{component.component_name}' missing payable account")
                migration_suggestions.append(f"Map component '{component.component_name}' to a liability account")
        
        # Check for inactive chart accounts
        inactive_accounts = db.query(ChartOfAccounts).filter(
            ChartOfAccounts.organization_id == organization_id,
            ChartOfAccounts.is_active == False,
            or_(
                ChartOfAccounts.id.in_(
                    db.query(PayrollComponent.expense_account_id).filter(
                        PayrollComponent.organization_id == organization_id,
                        PayrollComponent.expense_account_id.isnot(None)
                    )
                ),
                ChartOfAccounts.id.in_(
                    db.query(PayrollComponent.payable_account_id).filter(
                        PayrollComponent.organization_id == organization_id,
                        PayrollComponent.payable_account_id.isnot(None)
                    )
                )
            )
        ).all()
        
        for account in inactive_accounts:
            validation_errors.append(f"Chart account '{account.account_name}' is inactive but used in payroll")
            migration_suggestions.append(f"Activate account '{account.account_name}' or remap components using it")
        
        return PayrollMigrationStatus(
            total_components=total_components,
            mapped_components=mapped_components,
            unmapped_components=unmapped_components,
            mapping_percentage=round(mapping_percentage, 2),
            validation_errors=validation_errors,
            migration_suggestions=migration_suggestions
        )
        
    except Exception as e:
        logger.error(f"Error getting migration status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving migration status"
        )


@router.post("/payroll/migration/backfill", response_model=PayrollBackfillResult)
async def backfill_payroll_components(
    backfill_request: PayrollBackfillRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    organization_id: int = Depends(require_current_organization_id)
):
    """Backfill chart account mappings for payroll components"""
    try:
        # Get components to backfill
        query = db.query(PayrollComponent).filter(
            PayrollComponent.organization_id == organization_id,
            PayrollComponent.is_active == True
        )
        
        if backfill_request.target_components:
            query = query.filter(PayrollComponent.id.in_(backfill_request.target_components))
        
        components = query.all()
        
        # Get available accounts by type
        expense_accounts = db.query(ChartOfAccounts).filter(
            ChartOfAccounts.organization_id == organization_id,
            ChartOfAccounts.account_type.ilike('%expense%'),
            ChartOfAccounts.is_active == True
        ).all()
        
        liability_accounts = db.query(ChartOfAccounts).filter(
            ChartOfAccounts.organization_id == organization_id,
            ChartOfAccounts.account_type.ilike('%liability%'),
            ChartOfAccounts.is_active == True
        ).all()
        
        # Default account mappings
        default_expense_account = expense_accounts[0] if expense_accounts else None
        default_payable_account = liability_accounts[0] if liability_accounts else None
        
        # Find or create specific accounts for common components
        salary_expense_account = None
        payroll_payable_account = None
        
        for account in expense_accounts:
            if any(keyword in account.account_name.lower() for keyword in ['salary', 'wage', 'payroll']):
                salary_expense_account = account
                break
        
        for account in liability_accounts:
            if any(keyword in account.account_name.lower() for keyword in ['salary', 'wage', 'payroll', 'payable']):
                payroll_payable_account = account
                break
        
        updated_components = 0
        created_accounts = 0
        errors = []
        preview_data = []
        
        for component in components:
            component_updates = {}
            
            try:
                # Determine appropriate accounts
                expense_account = None
                payable_account = None
                
                if component.component_type in ['earning', 'deduction']:
                    if not component.expense_account_id:
                        expense_account = salary_expense_account or default_expense_account
                        if expense_account:
                            component_updates['expense_account_id'] = expense_account.id
                
                if component.component_type in ['deduction', 'employer_contribution']:
                    if not component.payable_account_id:
                        payable_account = payroll_payable_account or default_payable_account
                        if payable_account:
                            component_updates['payable_account_id'] = payable_account.id
                
                # Create missing accounts if requested
                if backfill_request.create_missing_accounts:
                    if component.component_type in ['earning', 'deduction'] and not expense_account:
                        # Create specific expense account for this component
                        new_account = ChartOfAccounts(
                            organization_id=organization_id,
                            account_code=f"EXP-{component.component_code}",
                            account_name=f"{component.component_name} Expense",
                            account_type="Expense",
                            is_active=True
                        )
                        db.add(new_account)
                        db.flush()
                        component_updates['expense_account_id'] = new_account.id
                        created_accounts += 1
                    
                    if component.component_type in ['deduction', 'employer_contribution'] and not payable_account:
                        # Create specific payable account for this component
                        new_account = ChartOfAccounts(
                            organization_id=organization_id,
                            account_code=f"PAY-{component.component_code}",
                            account_name=f"{component.component_name} Payable",
                            account_type="Liability",
                            is_active=True
                        )
                        db.add(new_account)
                        db.flush()
                        component_updates['payable_account_id'] = new_account.id
                        created_accounts += 1
                
                if component_updates:
                    if backfill_request.preview_mode:
                        preview_data.append({
                            "component_id": component.id,
                            "component_name": component.component_name,
                            "component_code": component.component_code,
                            "component_type": component.component_type,
                            "updates": component_updates
                        })
                    else:
                        # Apply updates
                        for field, value in component_updates.items():
                            setattr(component, field, value)
                        component.updated_at = datetime.utcnow()
                        updated_components += 1
                
            except Exception as e:
                errors.append(f"Error processing component {component.component_name}: {str(e)}")
        
        if not backfill_request.preview_mode:
            db.commit()
            
            # Schedule background validation
            background_tasks.add_task(
                validate_payroll_mappings_background,
                organization_id,
                current_user.id
            )
        
        return PayrollBackfillResult(
            total_components=len(components),
            updated_components=updated_components,
            created_accounts=created_accounts,
            errors=errors,
            preview_data=preview_data if backfill_request.preview_mode else None
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error in payroll backfill: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error during payroll backfill operation"
        )


@router.get("/payroll/migration/validation")
async def validate_payroll_mappings(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    organization_id: int = Depends(require_current_organization_id)
):
    """Validate all payroll component mappings"""
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
            validation_errors = []
            suggestions = []
            
            # Validate mapping requirements by component type
            if component.component_type == 'earning':
                if not component.expense_account_id:
                    validation_errors.append("Earning components require expense account mapping")
                    suggestions.append("Map to a salary or wage expense account")
            
            elif component.component_type == 'deduction':
                if not component.expense_account_id:
                    validation_errors.append("Deduction components require expense account mapping")
                    suggestions.append("Map to appropriate expense account")
                if not component.payable_account_id:
                    validation_errors.append("Deduction components require payable account mapping")
                    suggestions.append("Map to employee payable or statutory liability account")
            
            elif component.component_type == 'employer_contribution':
                if not component.expense_account_id:
                    validation_errors.append("Employer contribution components require expense account mapping")
                    suggestions.append("Map to employer contribution expense account")
                if not component.payable_account_id:
                    validation_errors.append("Employer contribution components require payable account mapping")
                    suggestions.append("Map to statutory liability account")
            
            # Validate account types
            if component.expense_account:
                if component.expense_account.account_type.lower() not in ['expense', 'expenses']:
                    validation_errors.append(f"Expense account has incorrect type: {component.expense_account.account_type}")
                    suggestions.append("Change to an Expense type account")
                
                if not component.expense_account.is_active:
                    validation_errors.append("Expense account is inactive")
                    suggestions.append("Activate the account or map to an active account")
            
            if component.payable_account:
                if component.payable_account.account_type.lower() not in ['liability', 'liabilities']:
                    validation_errors.append(f"Payable account has incorrect type: {component.payable_account.account_type}")
                    suggestions.append("Change to a Liability type account")
                
                if not component.payable_account.is_active:
                    validation_errors.append("Payable account is inactive")
                    suggestions.append("Activate the account or map to an active account")
            
            validation_results.append(PayrollValidationResult(
                component_id=component.id,
                component_name=component.component_name,
                is_valid=len(validation_errors) == 0,
                validation_errors=validation_errors,
                suggestions=suggestions
            ))
        
        return {
            "total_components": len(components),
            "valid_components": len([r for r in validation_results if r.is_valid]),
            "invalid_components": len([r for r in validation_results if not r.is_valid]),
            "validation_results": validation_results
        }
        
    except Exception as e:
        logger.error(f"Error validating payroll mappings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error validating payroll mappings"
        )


@router.post("/payroll/migration/fix-mappings")
async def auto_fix_mappings(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    organization_id: int = Depends(require_current_organization_id)
):
    """Automatically fix common mapping issues"""
    try:
        fixes_applied = 0
        errors = []
        
        # Get components with validation issues
        components = db.query(PayrollComponent).options(
            joinedload(PayrollComponent.expense_account),
            joinedload(PayrollComponent.payable_account)
        ).filter(
            PayrollComponent.organization_id == organization_id,
            PayrollComponent.is_active == True
        ).all()
        
        # Get available accounts
        expense_accounts = db.query(ChartOfAccounts).filter(
            ChartOfAccounts.organization_id == organization_id,
            ChartOfAccounts.account_type.ilike('%expense%'),
            ChartOfAccounts.is_active == True
        ).all()
        
        liability_accounts = db.query(ChartOfAccounts).filter(
            ChartOfAccounts.organization_id == organization_id,
            ChartOfAccounts.account_type.ilike('%liability%'),
            ChartOfAccounts.is_active == True
        ).all()
        
        for component in components:
            try:
                component_fixed = False
                
                # Fix expense account mapping
                if (component.component_type in ['earning', 'deduction', 'employer_contribution'] 
                    and not component.expense_account_id and expense_accounts):
                    component.expense_account_id = expense_accounts[0].id
                    component_fixed = True
                
                # Fix payable account mapping
                if (component.component_type in ['deduction', 'employer_contribution'] 
                    and not component.payable_account_id and liability_accounts):
                    component.payable_account_id = liability_accounts[0].id
                    component_fixed = True
                
                # Fix inactive account references
                if (component.expense_account and not component.expense_account.is_active 
                    and expense_accounts):
                    component.expense_account_id = expense_accounts[0].id
                    component_fixed = True
                
                if (component.payable_account and not component.payable_account.is_active 
                    and liability_accounts):
                    component.payable_account_id = liability_accounts[0].id
                    component_fixed = True
                
                if component_fixed:
                    component.updated_at = datetime.utcnow()
                    fixes_applied += 1
                
            except Exception as e:
                errors.append(f"Error fixing component {component.component_name}: {str(e)}")
        
        db.commit()
        
        # Schedule background validation
        background_tasks.add_task(
            validate_payroll_mappings_background,
            organization_id,
            current_user.id
        )
        
        return {
            "success": True,
            "fixes_applied": fixes_applied,
            "errors": errors,
            "message": f"Applied {fixes_applied} automatic fixes"
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error auto-fixing mappings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error applying automatic fixes"
        )


async def validate_payroll_mappings_background(organization_id: int, user_id: int):
    """Background task to validate payroll mappings"""
    try:
        # This would run comprehensive validation and generate reports
        # For now, just log the completion
        logger.info(f"Background validation completed for organization {organization_id} by user {user_id}")
    except Exception as e:
        logger.error(f"Error in background validation: {str(e)}")


@router.get("/payroll/migration/report")
async def get_migration_report(
    format: str = Query("json", description="Report format: json, csv"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get detailed migration report"""
    try:
        # Get comprehensive migration data
        components = db.query(PayrollComponent).options(
            joinedload(PayrollComponent.expense_account),
            joinedload(PayrollComponent.payable_account)
        ).filter(
            PayrollComponent.organization_id == organization_id
        ).all()
        
        report_data = {
            "organization_id": organization_id,
            "generated_at": datetime.utcnow().isoformat(),
            "generated_by": current_user.email,
            "summary": {
                "total_components": len(components),
                "active_components": len([c for c in components if c.is_active]),
                "fully_mapped": len([c for c in components if c.expense_account_id and c.payable_account_id]),
                "partially_mapped": len([c for c in components if (c.expense_account_id or c.payable_account_id) and not (c.expense_account_id and c.payable_account_id)]),
                "unmapped": len([c for c in components if not c.expense_account_id and not c.payable_account_id])
            },
            "components": []
        }
        
        for component in components:
            component_data = {
                "id": component.id,
                "name": component.component_name,
                "code": component.component_code,
                "type": component.component_type,
                "is_active": component.is_active,
                "expense_account": {
                    "id": component.expense_account_id,
                    "name": component.expense_account.account_name if component.expense_account else None,
                    "code": component.expense_account.account_code if component.expense_account else None,
                    "is_active": component.expense_account.is_active if component.expense_account else None
                } if component.expense_account_id else None,
                "payable_account": {
                    "id": component.payable_account_id,
                    "name": component.payable_account.account_name if component.payable_account else None,
                    "code": component.payable_account.account_code if component.payable_account else None,
                    "is_active": component.payable_account.is_active if component.payable_account else None
                } if component.payable_account_id else None,
                "created_at": component.created_at.isoformat(),
                "updated_at": component.updated_at.isoformat() if component.updated_at else None
            }
            report_data["components"].append(component_data)
        
        if format == "csv":
            # Convert to CSV format (simplified)
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write headers
            writer.writerow([
                "Component ID", "Component Name", "Component Code", "Component Type", "Is Active",
                "Expense Account ID", "Expense Account Name", "Expense Account Code",
                "Payable Account ID", "Payable Account Name", "Payable Account Code",
                "Created At", "Updated At"
            ])
            
            # Write data rows
            for component in report_data["components"]:
                writer.writerow([
                    component["id"],
                    component["name"],
                    component["code"],
                    component["type"],
                    component["is_active"],
                    component["expense_account"]["id"] if component["expense_account"] else "",
                    component["expense_account"]["name"] if component["expense_account"] else "",
                    component["expense_account"]["code"] if component["expense_account"] else "",
                    component["payable_account"]["id"] if component["payable_account"] else "",
                    component["payable_account"]["name"] if component["payable_account"] else "",
                    component["payable_account"]["code"] if component["payable_account"] else "",
                    component["created_at"],
                    component["updated_at"]
                ])
            
            from fastapi.responses import Response
            return Response(
                content=output.getvalue(),
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=payroll_migration_report.csv"}
            )
        
        return report_data
        
    except Exception as e:
        logger.error(f"Error generating migration report: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating migration report"
        )