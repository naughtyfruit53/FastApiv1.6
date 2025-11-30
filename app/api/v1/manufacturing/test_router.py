# app/api/v1/manufacturing/test_router.py
"""
Minimal test router to verify FastAPI router inclusion
"""

from fastapi import APIRouter
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("")
async def test_route():
    """Test endpoint to verify router inclusion"""
    logger.info("Test router endpoint accessed")
    return {"message": "Test router is registered"}