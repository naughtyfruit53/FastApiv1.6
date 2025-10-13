# app/api/v1/manufacturing/mrp.py
"""Material Requirements Planning module"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.v1.auth import get_current_active_user

router = APIRouter()

@router.post("/mrp/analyze")
async def analyze_mrp(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    return {"message": "MRP analysis - to be implemented"}
