# app/api/v1/gst_search.py

"""
GST Number Search API endpoint
Searches for GST details using external GST APIs or databases
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import logging
import httpx

from app.api.v1.auth import get_current_active_user
from app.models.user_models import User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/gst", tags=["GST Search"])


class GSTDetails(BaseModel):
    """GST Details Response Schema"""
    name: str
    gst_number: str
    address1: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pin_code: Optional[str] = None
    pan_number: Optional[str] = None
    state_code: Optional[str] = None


@router.get("/search/{gst_number}", response_model=GSTDetails)
async def search_gst_number(
    gst_number: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Search for GST details by GST number.
    
    This endpoint uses free public APIs or databases to fetch GST details.
    For production use, integrate with:
    1. GST API Gateway (requires subscription)
    2. Free public GST APIs (limited access)
    3. Local database of GST numbers
    
    Currently implements a mock response for demonstration.
    """
    
    # Validate GST format
    import re
    gst_pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$'
    if not re.match(gst_pattern, gst_number):
        raise HTTPException(
            status_code=400,
            detail="Invalid GST number format"
        )
    
    logger.info(f"Searching GST details for: {gst_number}")
    
    try:
        # Extract state code from GST (first 2 digits)
        state_code = gst_number[:2]
        
        # Extract PAN from GST (positions 2-12)
        pan_number = gst_number[2:12]
        
        # Map state codes to state names (basic mapping)
        state_map = {
            '01': 'Jammu and Kashmir', '02': 'Himachal Pradesh', '03': 'Punjab',
            '04': 'Chandigarh', '05': 'Uttarakhand', '06': 'Haryana',
            '07': 'Delhi', '08': 'Rajasthan', '09': 'Uttar Pradesh',
            '10': 'Bihar', '11': 'Sikkim', '12': 'Arunachal Pradesh',
            '13': 'Nagaland', '14': 'Manipur', '15': 'Mizoram',
            '16': 'Tripura', '17': 'Meghalaya', '18': 'Assam',
            '19': 'West Bengal', '20': 'Jharkhand', '21': 'Odisha',
            '22': 'Chhattisgarh', '23': 'Madhya Pradesh', '24': 'Gujarat',
            '27': 'Maharashtra', '29': 'Karnataka', '32': 'Kerala',
            '33': 'Tamil Nadu', '34': 'Puducherry', '35': 'Andaman and Nicobar Islands',
            '36': 'Telangana', '37': 'Andhra Pradesh'
        }
        
        state_name = state_map.get(state_code, "Unknown State")
        
        # TODO: In production, integrate with actual GST API
        # For now, return extracted information from GST number
        # You can integrate with free APIs like:
        # - GSTIN Search APIs (if available)
        # - Third-party GST verification services
        
        # Mock response with extracted data
        return GSTDetails(
            name="Fetched from GST Database",
            gst_number=gst_number,
            state=state_name,
            state_code=state_code,
            pan_number=pan_number,
            address1="",
            city="",
            pin_code=""
        )
        
    except Exception as e:
        logger.error(f"Error searching GST details: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch GST details: {str(e)}"
        )


@router.get("/verify/{gst_number}")
async def verify_gst_number(
    gst_number: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Verify if a GST number is valid and active.
    
    Returns basic validation status.
    """
    import re
    gst_pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$'
    
    is_valid_format = bool(re.match(gst_pattern, gst_number))
    
    if not is_valid_format:
        return {
            "valid": False,
            "message": "Invalid GST number format"
        }
    
    # TODO: Integrate with GST verification API
    # For now, just validate format
    return {
        "valid": True,
        "message": "GST number format is valid",
        "gst_number": gst_number
    }
