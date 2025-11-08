# app/api/v1/manufacturing/stock_journals.py
"""Stock Journals module"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.core.enforcement import require_access

router = APIRouter()

@router.get("/stock-journals")
async def get_stock_journals(
    auth: tuple = Depends(require_access("manufacturing", "read")),

    db: AsyncSession = Depends(get_db)
):
    return []
