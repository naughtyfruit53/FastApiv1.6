# app/api/v1/manufacturing/shop_floor.py
"""Shop Floor Operations and Barcode Scanning module"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.core.enforcement import require_access

router = APIRouter()

@router.get("/shop-floor/active-orders")
async def get_active_shop_floor_orders(
    auth: tuple = Depends(require_access("manufacturing", "read")),

    db: AsyncSession = Depends(get_db)
):
    return []
