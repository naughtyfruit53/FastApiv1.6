# app/api/v1/manufacturing/shop_floor.py
"""Shop Floor Operations and Barcode Scanning module"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.v1.auth import get_current_active_user

router = APIRouter()

@router.get("/shop-floor/active-orders")
async def get_active_shop_floor_orders(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    return []
