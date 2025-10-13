# app/api/v1/manufacturing/manufacturing_journals.py
"""
Manufacturing Journals module - Handles manufacturing journal vouchers
Extracted from monolithic manufacturing.py
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.v1.auth import get_current_active_user

router = APIRouter()

@router.get("/manufacturing-journal-vouchers")
async def get_manufacturing_journal_vouchers(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get manufacturing journal vouchers - to be implemented"""
    return []
