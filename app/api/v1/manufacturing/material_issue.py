# app/api/v1/manufacturing/material_issues.py
"""
Material Issue module - Handles material issue vouchers
Extracted from monolithic manufacturing.py
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime
import logging

from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.core.enforcement import require_access
from app.models.vouchers import MaterialIssue, MaterialIssueItem
from app.services.voucher_service import VoucherNumberService
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter()

# Material Issue Schemas
class MaterialIssueItemCreate(BaseModel):
    product_id: int
    quantity: float
    unit: str
    unit_price: float
    notes: Optional[str] = None

class MaterialIssueCreate(BaseModel):
    manufacturing_order_id: Optional[int] = None
    issued_to_department: Optional[str] = None
    issued_to_employee: Optional[str] = None
    purpose: str = "production"
    notes: Optional[str] = None
    items: List[MaterialIssueItemCreate] = []

class MaterialIssueResponse(BaseModel):
    id: int
    voucher_number: str
    date: datetime
    manufacturing_order_id: Optional[int]
    issued_to_department: Optional[str]
    issued_to_employee: Optional[str]
    purpose: str
    notes: Optional[str]
    total_amount: float
    created_by: int

    class Config:
        from_attributes = True

@router.get("", response_model=List[MaterialIssueResponse])
async def get_material_issues(
    skip: int = 0,
    limit: int = 100,
    auth: tuple = Depends(require_access("manufacturing", "read")),

    db: AsyncSession = Depends(get_db)
):
    """Get list of material issues at /api/v1/material-issues"""
    try:
        stmt = select(MaterialIssue).where(
            MaterialIssue.organization_id == org_id
        ).offset(skip).limit(limit)
        result = await db.execute(stmt)
        issues = result.scalars().all()
        logger.info(f"Fetched {len(issues)} material issues for organization {org_id}")
        return issues
    except Exception as e:
        logger.error(f"Error fetching material issues: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch material issues")

@router.get("/next-number")
async def get_next_material_issue_number(
    auth: tuple = Depends(require_access("manufacturing", "read")),

    db: AsyncSession = Depends(get_db)
):
    """Get next material issue number at /api/v1/material-issues/next-number"""
    try:
        next_number = await VoucherNumberService.generate_voucher_number_async(
            db, "MI", org_id, MaterialIssue
        )
        logger.info(f"Generated next material issue number: {next_number} for organization {org_id}")
        return next_number
    except Exception as e:
        logger.error(f"Error generating material issue number: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate material issue number")

@router.post("")
async def create_material_issue(
    issue_data: MaterialIssueCreate,
    auth: tuple = Depends(require_access("manufacturing", "read")),

    db: AsyncSession = Depends(get_db)
):
    """Create new material issue at /api/v1/material-issues"""
    try:
        # Generate voucher number
        voucher_number = await VoucherNumberService.generate_voucher_number_async(
            db, "MI", org_id, MaterialIssue
        )

        # Calculate total amount
        total_amount = sum(item.quantity * item.unit_price for item in issue_data.items)

        db_issue = MaterialIssue(
            organization_id=org_id,
            voucher_number=voucher_number,
            date=datetime.now(),
            manufacturing_order_id=issue_data.manufacturing_order_id,
            issued_to_department=issue_data.issued_to_department,
            issued_to_employee=issue_data.issued_to_employee,
            purpose=issue_data.purpose,
            notes=issue_data.notes,
            total_amount=total_amount,
            created_by=current_user.id
        )

        db.add(db_issue)
        await db.flush()

        # Add items
        for item_data in issue_data.items:
            item = MaterialIssueItem(
                organization_id=org_id,
                material_issue_id=db_issue.id,
                product_id=item_data.product_id,
                quantity=item_data.quantity,
                unit=item_data.unit,
                unit_price=item_data.unit_price,
                taxable_amount=item_data.quantity * item_data.unit_price,
                total_amount=item_data.quantity * item_data.unit_price,
                notes=item_data.notes
            )
            db.add(item)

        await db.commit()
        await db.refresh(db_issue)
        logger.info(f"Created material issue {voucher_number} for organization {org_id}")
        return db_issue
    except Exception as e:
        logger.error(f"Error creating material issue: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create material issue")