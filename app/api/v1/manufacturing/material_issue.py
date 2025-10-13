# app/api/v1/manufacturing/material_issue.py
"""
Material Issue module - Handles material issue vouchers
Extracted from monolithic manufacturing.py
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.api.v1.auth import get_current_active_user

router = APIRouter()

# Material issue endpoints will be migrated here from original manufacturing.py
# For now, keeping as stub to maintain imports

@router.get("/material-issues")
async def get_material_issues(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get material issues - to be implemented"""
    return []


@router.get("/material-issues/next-number")
async def get_next_material_issue_number(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get next material issue number - to be implemented"""
    return "MI-001"
