# app/api/v1/manufacturing/material_receipt.py
"""
Material Receipt module - Handles material receipt vouchers
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.core.enforcement import require_access

router = APIRouter()

@router.get("/material-receipt-vouchers")
async def get_material_receipt_vouchers(
    auth: tuple = Depends(require_access("manufacturing", "read")),

    db: AsyncSession = Depends(get_db)
):
    return []
