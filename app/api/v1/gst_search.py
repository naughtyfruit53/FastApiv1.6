"""
GST Number Search API endpoint
Searches for GST details using external GST APIs or databases
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import logging
import httpx
from app.core.config import settings

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


def validate_gstin_checksum(gstin: str) -> bool:
    """Validate GSTIN checksum."""
    if len(gstin) != 15:
        return False
    
    def char_to_num(c: str) -> int:
        if c.isdigit():
            return int(c)
        else:
            return 10 + ord(c.upper()) - ord('A')
    
    total = 0
    for i in range(14):
        num = char_to_num(gstin[i])
        factor = 1 if (i % 2 == 0) else 2  # Corrected: Start with 1 for first position (i=0)
        product = num * factor
        total += (product // 36) + (product % 36)  # Corrected: Use base 36 instead of 10
    
    checksum = (36 - (total % 36)) % 36
    check_char = str(checksum) if checksum < 10 else chr(checksum - 10 + ord('A'))
    
    return gstin[14] == check_char


@router.get("/search/{gst_number}", response_model=GSTDetails)
async def search_gst_number(
    gst_number: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Search for GST details by GST number.
    
    This endpoint uses the GST Insights API via RapidAPI to fetch GST details.
    Requires RAPIDAPI_KEY in .env (sign up at https://rapidapi.com/amiteshgupta/api/gst-insights-api).
    Validates checksum before API call. Handles 400 as invalid GSTIN without retry. Retries other errors up to 3 times.
    Falls back to basic extracted info if API fails or key is missing.
    """
    
    # Validate GST format
    import re
    gst_pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$'
    if not re.match(gst_pattern, gst_number):
        raise HTTPException(
            status_code=400,
            detail="Invalid GST number format"
        )
    
    # Validate checksum
    if not validate_gstin_checksum(gst_number):
        raise HTTPException(
            status_code=400,
            detail="Invalid GSTIN checksum. Please verify the number."
        )
    
    logger.info(f"Searching GST details for: {gst_number}")
    
    if not settings.RAPIDAPI_KEY:
        logger.warning("RAPIDAPI_KEY not set, using mock response")
        # Fall back to mock if no key
        state_code = gst_number[:2]
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
        return GSTDetails(
            name="Fetched from GST Database (Mock)",
            gst_number=gst_number,
            state=state_name,
            state_code=state_code,
            pan_number=gst_number[2:12],
            address1="",
            city="",
            pin_code=""
        )
    
    try:
        url = f"https://gst-insights-api.p.rapidapi.com/getGSTDetailsUsingGST/{gst_number}"
        headers = {
            "X-RapidAPI-Key": settings.RAPIDAPI_KEY,
            "X-RapidAPI-Host": "gst-insights-api.p.rapidapi.com"
        }
        
        async with httpx.AsyncClient() as client:
            for attempt in range(1, 4):  # 3 attempts max
                response = await client.get(url, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    if not data.get('success', False):
                        raise Exception(data.get('message', 'API success false'))
                    result = data.get('data', {})
                    address = result.get('pradr', {})  # Assuming 'pradr' for principal address
                    name = result.get('lgnm', result.get('tradeNam', 'Unknown'))  # Use 'lgnm' for legal name, fallback to 'tradeNam'
                    return GSTDetails(
                        name=name,
                        gst_number=result.get('gstin', gst_number),
                        address1=address.get('addr', {}).get('bno', "") + " " + address.get('addr', {}).get('st', ""),  # Combine building no and street
                        city=address.get('addr', {}).get('city', ""),
                        state=address.get('addr', {}).get('stcd', ""),
                        pin_code=address.get('addr', {}).get('pncd', ""),
                        pan_number=result.get('pan', ""),
                        state_code=result.get('stjCd', gst_number[:2])
                    )
                elif response.status_code == 400:
                    logger.warning(f"RapidAPI returned 400 for GSTIN {gst_number}: {response.text}")
                    raise HTTPException(
                        status_code=400,
                        detail="Invalid GSTIN. Please check the number and try again."
                    )
                else:
                    logger.warning(f"RapidAPI attempt {attempt} failed: {response.status_code} - {response.text}")
        
        raise Exception("Failed after 3 attempts")
    
    except HTTPException as he:
        raise he  # Re-raise if already handled
    except Exception as e:
        logger.error(f"Error searching GST details: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"GST search failed after retries: {str(e)}. Please try again later."
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
    
    # Add checksum validation
    is_valid_checksum = validate_gstin_checksum(gst_number)
    
    if not is_valid_checksum:
        return {
            "valid": False,
            "message": "Invalid GSTIN checksum"
        }
    
    # TODO: Integrate with GST verification API
    # For now, just validate format and checksum
    return {
        "valid": True,
        "message": "GST number format and checksum are valid",
        "gst_number": gst_number
    }