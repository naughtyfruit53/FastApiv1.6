"""
GST Number Search API endpoint
Searches for GST details using external GST APIs or databases
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import logging
import httpx
import time  # For delay between retries
from app.core.config import settings
from app.core.enforcement import require_access
from app.core.database import Base, get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.audit_log import AuditLog

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/gst", tags=["GST Search"])

# Simple in-memory cache for GST results (dict: gst_number -> GSTDetails)
gst_cache = {}


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


def create_mock_gst_result(gstin: str, reason: str = "Format valid - Not found in public database") -> GSTDetails:
    """Helper to create mock GST result with informative name"""
    state_code = gstin[:2]
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
        name=f"Company Name Not Found ({reason})",
        gst_number=gstin,
        state=state_name,
        state_code=state_code,
        pan_number=gstin[2:12],
        address1="",
        city="",
        pin_code=""
    )


@router.get("/search/{gst_number}", response_model=GSTDetails)
async def search_gst_number(
    gst_number: str,
    auth: tuple = Depends(require_access("gst", "read")),
    db: AsyncSession = Depends(get_db)
):
    """
    Search for GST details by GST number.
    
    This endpoint uses the GST Insights API via RapidAPI to fetch GST details.
    Requires RAPIDAPI_KEY in .env (sign up at https://rapidapi.com/amiteshgupta/api/gst-insights-api).
    Validates checksum before API call. Handles 400 as invalid GSTIN without retry. Retries other errors up to 3 times.
    Falls back to basic extracted info if API fails, key is missing, or GSTIN not found in API database.
    """
    current_user, org_id = auth
    
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
    
    # Helper function to log audit
    async def log_gst_search(success: bool, details: str = ""):
        """Log GST search to audit log"""
        try:
            audit_log = AuditLog(
                organization_id=org_id,
                entity_type="gst_lookup",
                entity_id=None,
                entity_name=gst_number,
                action="read",
                action_description=f"GST number lookup: {gst_number} - {details}",
                user_id=current_user.id,
                changes={
                    "gst_number": gst_number,
                    "user_role": current_user.role,
                    "details": details
                },
                success=success
            )
            db.add(audit_log)
            await db.commit()
        except Exception as e:
            logger.error(f"Failed to log audit: {e}")
    
    # Check cache first
    if gst_number in gst_cache:
        logger.info(f"Cache hit for GSTIN: {gst_number}")
        await log_gst_search(True, "Retrieved from cache")
        return gst_cache[gst_number]
    
    if not settings.RAPIDAPI_KEY:
        logger.warning("RAPIDAPI_KEY not set, using mock response")
        mock_result = create_mock_gst_result(gst_number, "API key not configured")
        gst_cache[gst_number] = mock_result
        return mock_result
    
    try:
        url = f"https://powerful-gstin-tool.p.rapidapi.com/v1/gstin/{gst_number}/details"
        headers = {
            "X-RapidAPI-Key": settings.RAPIDAPI_KEY,
            "X-RapidAPI-Host": "powerful-gstin-tool.p.rapidapi.com"
        }
        
        async with httpx.AsyncClient() as client:
            for attempt in range(1, 4):  # 3 attempts max
                response = await client.get(url, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    logger.debug(f"API response data type: {type(data)}")
                    logger.debug(f"API response content: {data}")
                    # Handle if data is list
                    if isinstance(data, list):
                        logger.info("API returned list, attempting to use first item if dict")
                        if data and isinstance(data[0], dict):
                            data = data[0]
                        else:
                            logger.warning("Empty list response - falling back to mock")
                            mock_result = create_mock_gst_result(gst_number)
                            gst_cache[gst_number] = mock_result
                            return mock_result
                    # Additional check if data is now dict
                    if not isinstance(data, dict):
                        logger.warning(f"Unexpected response type after handling: {type(data)} - falling back to mock")
                        mock_result = create_mock_gst_result(gst_number)
                        gst_cache[gst_number] = mock_result
                        return mock_result
                    result = data.get('data', {})
                    # Handle if result ('data' field) is a list
                    if isinstance(result, list):
                        logger.info("API 'data' field is list, attempting to use first item if dict")
                        if result and isinstance(result[0], dict):
                            result = result[0]
                        else:
                            logger.warning("Empty 'data' list - falling back to mock")
                            mock_result = create_mock_gst_result(gst_number)
                            gst_cache[gst_number] = mock_result
                            return mock_result
                    # Additional check if result is now dict
                    if not isinstance(result, dict):
                        logger.warning(f"Unexpected 'data' type after handling: {type(result)} - falling back to mock")
                        mock_result = create_mock_gst_result(gst_number)
                        gst_cache[gst_number] = mock_result
                        return mock_result
                    # Removed the !result.get('gstin') raise - return even if partial
                    address = result.get('place_of_business_principal', {}).get('address', {})  # Updated path based on test result
                    name = result.get('legal_name', result.get('trade_name', 'Company Name Not Found in Database'))
                    pan_number = result.get('pan_number') or gst_number[2:12]
                    gst_result = GSTDetails(
                        name=name,
                        gst_number=result.get('gstin', gst_number),
                        address1=address.get('building_name', "") + " " + address.get('street', ""),  # Combine building_name and street
                        city=address.get('city', ""),
                        state=address.get('state', ""),
                        pin_code=address.get('pin_code', ""),
                        pan_number=pan_number,
                        state_code=result.get('state_code', gst_number[:2])
                    )
                    gst_cache[gst_number] = gst_result  # Cache successful result
                    await log_gst_search(True, f"Retrieved from API: {name}")
                    return gst_result
                elif response.status_code == 400:
                    logger.warning(f"RapidAPI returned 400 for GSTIN {gst_number}: {response.text}")
                    raise HTTPException(
                        status_code=400,
                        detail="Invalid GSTIN. Please check the number and try again."
                    )
                elif response.status_code == 429:  # Handle rate limit
                    logger.warning(f"RapidAPI rate limit hit (429) for GSTIN {gst_number}: {response.text}")
                    # Fallback to mock on rate limit, no retry
                    mock_result = create_mock_gst_result(gst_number, "API rate limit exceeded")
                    gst_cache[gst_number] = mock_result
                    return mock_result
                else:
                    logger.warning(f"RapidAPI attempt {attempt} failed: {response.status_code} - {response.text}")
                    if attempt < 3:  # Exponential backoff delay before next retry
                        delay = 2 ** attempt  # 2, 4 seconds
                        logger.info(f"Waiting {delay} seconds before retry {attempt + 1}")
                        time.sleep(delay)
        
        logger.warning("Failed after 3 attempts - falling back to mock")
        mock_result = create_mock_gst_result(gst_number, "API failed after retries")
        gst_cache[gst_number] = mock_result
        await log_gst_search(False, "API failed after retries, using fallback")
        return mock_result
    
    except HTTPException as he:
        await log_gst_search(False, f"Validation error: {he.detail}")
        raise he  # Re-raise if already handled
    except Exception as e:
        logger.error(f"Error searching GST details: {str(e)} - falling back to mock")
        mock_result = create_mock_gst_result(gst_number, "API error")
        gst_cache[gst_number] = mock_result
        await log_gst_search(False, f"Exception: {str(e)}")
        return mock_result


@router.get("/verify/{gst_number}")
async def verify_gst_number(
    gst_number: str,
    auth: tuple = Depends(require_access("gst", "read"))
):
    """
    Verify if a GST number is valid and active.
    
    Returns basic validation status.
    """
    current_user, org_id = auth
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
            "message": "Invalid GSTIN checksum. Please verify the number."
        }
    
    # TODO: Integrate with GST verification API
    # For now, just validate format and checksum
    return {
        "valid": True,
        "message": "GST number format and checksum are valid",
        "gst_number": gst_number
    }