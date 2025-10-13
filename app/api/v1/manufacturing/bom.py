# app/api/v1/manufacturing/bom.py
"""Bill of Materials module"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.v1.auth import get_current_active_user

router = APIRouter()

@router.post("/bom/{bom_id}/clone")
async def clone_bom(
    bom_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Clone BOM - to be implemented"""
    return {"message": "To be implemented"}
