# app/api/v1/manufacturing/job_cards.py
"""Job Cards module"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.v1.auth import get_current_active_user

router = APIRouter()

@router.get("/job-card-vouchers")
async def get_job_card_vouchers(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    return []
