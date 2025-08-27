# app/api/v1/gst.py

from fastapi import APIRouter, Depends, HTTPException
from app.services.pdf_extraction import pdf_extraction_service
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/search/{gstin}")
async def search_gst_details(gstin: str) -> Dict[str, Any]:
    """
    Search GST details using extracted GSTIN
    """
    try:
        # Use the service to fetch from RapidAPI
        details = await pdf_extraction_service.fetch_gst_details(gstin)
        return details
    except Exception as e:
        logger.error(f"GST search failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch GST details: {str(e)}"
        )