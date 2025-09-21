# app/api/v1/payroll_gl.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any
from decimal import Decimal
from datetime import datetime, date
import logging

from app.db.session import get_db
from app.api.v1.auth import get_current_active_user
from app.core.org_restrictions import require_current_organization_id
from app.models.user_models import User
from app.models.payroll_models import PayrollRun, PayrollComponent, PayrollLine
from app.models.erp_models import ChartOfAccounts
from app.schemas.payroll_schemas import (
    PayrollGLPreview,
    PayrollGLPosting,
    PayrollGLPostingResult,
    GLPreviewLine
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/payroll/runs/{run_id}/gl-preview", response_model=PayrollGLPreview)
async def get_payroll_gl_preview(
    run_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    organization_id: int = Depends(require_current_organization_id)
):
    """Generate GL preview for a payroll run"""
    try:
        # Get payroll run
        payroll_run = db.query(PayrollRun).filter(
            PayrollRun.id == run_id,
            PayrollRun.organization_id == organization_id
        ).first()
        
        if not payroll_run:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payroll run not found"
            )
        
        if payroll_run.status not in ["processed", "approved"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payroll run must be processed before GL preview"
            )
        
        # Get existing payroll lines if any
        existing_lines = db.query(PayrollLine).filter(
            PayrollLine.payroll_run_id == run_id,
            PayrollLine.organization_id == organization_id
        ).all()
        
        preview_lines = []
        total_debit = Decimal('0.00')
        total_credit = Decimal('0.00')
        
        if existing_lines:
            # Use existing lines for preview
            account_totals = {}
            
            for line in existing_lines:
                account_key = line.chart_account_id
                if account_key not in account_totals:
                    account = db.query(ChartOfAccounts).filter(
                        ChartOfAccounts.id == line.chart_account_id
                    ).first()
                    account_totals[account_key] = {
                        'account': account,
                        'debit': Decimal('0.00'),
                        'credit': Decimal('0.00'),
                        'description': line.description
                    }
                
                if line.posting_type == 'debit':
                    account_totals[account_key]['debit'] += line.amount
                    total_debit += line.amount
                else:
                    account_totals[account_key]['credit'] += line.amount
                    total_credit += line.amount
            
            for account_data in account_totals.values():
                preview_lines.append(GLPreviewLine(
                    account_code=account_data['account'].account_code,
                    account_name=account_data['account'].account_name,
                    account_type=account_data['account'].account_type.value,
                    debit_amount=account_data['debit'],
                    credit_amount=account_data['credit'],
                    description=account_data['description']
                ))
        
        else:
            # Generate preview from payroll run totals
            # This is a simplified preview - in real implementation, you'd calculate
            # from actual employee payslips
            
            # Expense entries (Debit)
            if payroll_run.total_expense_amount > 0:
                # Get default expense account or use first available expense account
                expense_account = db.query(ChartOfAccounts).filter(
                    ChartOfAccounts.organization_id == organization_id,
                    ChartOfAccounts.account_type == "expense",
                    ChartOfAccounts.is_active == True
                ).first()
                
                if expense_account:
                    preview_lines.append(GLPreviewLine(
                        account_code=expense_account.account_code,
                        account_name=expense_account.account_name,
                        account_type=expense_account.account_type.value,
                        debit_amount=payroll_run.total_expense_amount,
                        credit_amount=Decimal('0.00'),
                        description=f"Payroll expenses for {payroll_run.run_name}"
                    ))
                    total_debit += payroll_run.total_expense_amount
            
            # Payable entries (Credit)
            if payroll_run.total_payable_amount > 0:
                # Get default payable account
                payable_account = db.query(ChartOfAccounts).filter(
                    ChartOfAccounts.organization_id == organization_id,
                    ChartOfAccounts.account_type == "liability",
                    ChartOfAccounts.is_active == True
                ).first()
                
                if payable_account:
                    preview_lines.append(GLPreviewLine(
                        account_code=payable_account.account_code,
                        account_name=payable_account.account_name,
                        account_type=payable_account.account_type.value,
                        debit_amount=Decimal('0.00'),
                        credit_amount=payroll_run.total_payable_amount,
                        description=f"Payroll payables for {payroll_run.run_name}"
                    ))
                    total_credit += payroll_run.total_payable_amount
        
        is_balanced = abs(total_debit - total_credit) < Decimal('0.01')
        
        return PayrollGLPreview(
            payroll_run_id=run_id,
            total_debit=total_debit,
            total_credit=total_credit,
            lines=preview_lines,
            is_balanced=is_balanced
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating GL preview: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating GL preview"
        )


@router.post("/payroll/runs/{run_id}/post-to-gl", response_model=PayrollGLPostingResult)
async def post_payroll_to_gl(
    run_id: int,
    posting_data: PayrollGLPosting,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    organization_id: int = Depends(require_current_organization_id)
):
    """Post payroll run to General Ledger"""
    try:
        # Get payroll run
        payroll_run = db.query(PayrollRun).filter(
            PayrollRun.id == run_id,
            PayrollRun.organization_id == organization_id
        ).first()
        
        if not payroll_run:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payroll run not found"
            )
        
        if payroll_run.gl_posted:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payroll run already posted to GL"
            )
        
        if payroll_run.status not in ["processed", "approved"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payroll run must be processed and approved before GL posting"
            )
        
        # Check if payroll lines exist
        existing_lines = db.query(PayrollLine).filter(
            PayrollLine.payroll_run_id == run_id,
            PayrollLine.organization_id == organization_id
        ).count()
        
        if existing_lines == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No payroll lines found. Generate payroll lines first."
            )
        
        # TODO: Create journal voucher entries
        # This would integrate with your journal voucher system
        journal_voucher_id = None  # Would be created here
        
        # Update payroll run status
        payroll_run.gl_posted = True
        payroll_run.gl_posted_at = datetime.utcnow()
        payroll_run.status = "posted"
        
        # Update payroll lines with journal voucher reference
        db.query(PayrollLine).filter(
            PayrollLine.payroll_run_id == run_id
        ).update({
            "journal_voucher_id": journal_voucher_id
        })
        
        db.commit()
        
        logger.info(f"Posted payroll run {run_id} to GL for organization {organization_id}")
        
        return PayrollGLPostingResult(
            success=True,
            message="Payroll successfully posted to General Ledger",
            journal_voucher_id=journal_voucher_id,
            gl_entries_created=existing_lines,
            total_amount=payroll_run.total_gross_amount
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error posting payroll to GL: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error posting payroll to General Ledger"
        )


@router.post("/payroll/runs/{run_id}/reverse-gl-posting")
async def reverse_payroll_gl_posting(
    run_id: int,
    reversal_reason: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    organization_id: int = Depends(require_current_organization_id)
):
    """Reverse GL posting for a payroll run"""
    try:
        # Get payroll run
        payroll_run = db.query(PayrollRun).filter(
            PayrollRun.id == run_id,
            PayrollRun.organization_id == organization_id
        ).first()
        
        if not payroll_run:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payroll run not found"
            )
        
        if not payroll_run.gl_posted:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payroll run is not posted to GL"
            )
        
        # TODO: Create reversal journal voucher
        # This would create opposite entries to reverse the original posting
        reversal_voucher_id = None  # Would be created here
        
        # Update payroll run
        payroll_run.gl_posted = False
        payroll_run.gl_posted_at = None
        payroll_run.gl_reversal_voucher_id = reversal_voucher_id
        payroll_run.status = "processed"  # Revert to processed status
        
        # Clear journal voucher references from payroll lines
        db.query(PayrollLine).filter(
            PayrollLine.payroll_run_id == run_id
        ).update({
            "journal_voucher_id": None
        })
        
        db.commit()
        
        logger.info(f"Reversed GL posting for payroll run {run_id}, reason: {reversal_reason}")
        
        return {
            "success": True,
            "message": "GL posting reversed successfully",
            "reversal_voucher_id": reversal_voucher_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error reversing GL posting: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error reversing GL posting"
        )


@router.post("/payroll/runs/{run_id}/generate-payment-vouchers")
async def generate_payment_vouchers(
    run_id: int,
    payment_date: date,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    organization_id: int = Depends(require_current_organization_id)
):
    """Generate payment vouchers for payroll run"""
    try:
        # Get payroll run
        payroll_run = db.query(PayrollRun).filter(
            PayrollRun.id == run_id,
            PayrollRun.organization_id == organization_id
        ).first()
        
        if not payroll_run:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payroll run not found"
            )
        
        if not payroll_run.gl_posted:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payroll run must be posted to GL before generating payment vouchers"
            )
        
        if payroll_run.payment_vouchers_generated:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment vouchers already generated for this payroll run"
            )
        
        # TODO: Generate actual payment vouchers
        # This would create payment vouchers for each employee's net pay
        vouchers_created = 0  # Would be calculated based on actual vouchers created
        
        # Update payroll run
        payroll_run.payment_vouchers_generated = True
        payroll_run.payment_date = payment_date
        payroll_run.status = "paid"
        
        db.commit()
        
        logger.info(f"Generated payment vouchers for payroll run {run_id}")
        
        return {
            "success": True,
            "message": f"Generated {vouchers_created} payment vouchers",
            "vouchers_created": vouchers_created,
            "payment_date": payment_date
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error generating payment vouchers: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating payment vouchers"
        )