from fastapi import APIRouter, HTTPException
from typing import Dict
import requests
import logging
import traceback  # For detailed error logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Mapping of Indian state names to GST state codes (unchanged)
STATE_CODE_MAP = {
    "Andaman & Nicobar Islands": "35",
    "Andhra Pradesh": "37",
    "Arunachal Pradesh": "12",
    "Assam": "18",
    "Bihar": "10",
    "Chandigarh": "04",
    "Chhattisgarh": "22",
    "Dadra & Nagar Haveli & Daman & Diu": "26",
    "Delhi": "07",
    "Goa": "30",
    "Gujarat": "24",
    "Haryana": "06",
    "Himachal Pradesh": "02",
    "Jammu & Kashmir": "01",
    "Jharkhand": "20",
    "Karnataka": "29",
    "Kerala": "32",
    "Ladakh": "38",
    "Lakshadweep": "31",
    "Madhya Pradesh": "23",
    "Maharashtra": "27",
    "Manipur": "14",
    "Meghalaya": "17",
    "Mizoram": "15",
    "Nagaland": "13",
    "Odisha": "21",
    "Puducherry": "34",
    "Punjab": "03",
    "Rajasthan": "08",
    "Sikkim": "11",
    "Tamil Nadu": "33",
    "Telangana": "36",
    "Tripura": "16",
    "Uttar Pradesh": "09",
    "Uttarakhand": "05",
    "West Bengal": "19",
    "Other Territory": "97",
    "Other Country": "99"
}

@router.get("/lookup/{pin_code}")
async def lookup_pincode(pin_code: str) -> Dict[str, str]:
    """
    Lookup city, state, and state_code by PIN code using external API
    """
    # Validate pin code format
    if not pin_code.isdigit() or len(pin_code) != 6:
        raise HTTPException(
            status_code=400,
            detail="Invalid PIN code format. PIN code must be 6 digits."
        )
    
    try:
        # Fetch from external API with timeout, User-Agent header to mimic browser (prevents bot blocking)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(
            f"https://api.postalpincode.in/pincode/{pin_code}",
            headers=headers,
            timeout=15  # Increased to 15 seconds for slower networks
        )
        response.raise_for_status()  # Raise error for bad status codes
        data = response.json()
        
        if not data or data[0]['Status'] != "Success":
            raise HTTPException(
                status_code=404,
                detail=f"PIN code {pin_code} not found. Please enter city and state manually."
            )
        
        # Extract from first PostOffice entry
        post_office = data[0]['PostOffice'][0]
        city = post_office['District']
        state = post_office['State']
        state_code = STATE_CODE_MAP.get(state, "00")  # Default to "00" if not found
        
        # Log successful lookup for debugging
        logger.info(f"Successful PIN code lookup for {pin_code}: {city}, {state}, {state_code}")
        
        return {
            "city": city,
            "state": state,
            "state_code": state_code
        }
    
    except requests.Timeout as e:
        logger.error(f"Timeout fetching PIN code data for {pin_code}: {str(e)} - Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=503,
            detail="PIN code lookup timed out. Please try again later or enter details manually."
        )
    except requests.ConnectionError as e:
        logger.error(f"Connection error fetching PIN code data for {pin_code}: {str(e)} - Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=503,
            detail="Unable to connect to PIN code service. Check your network or try again later."
        )
    except requests.RequestException as e:
        logger.error(f"Error fetching PIN code data for {pin_code}: {str(e)} - Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=503,
            detail="PIN code lookup service is currently unavailable. Please try again later or enter details manually."
        )
    except Exception as e:
        logger.error(f"Unexpected error in PIN code lookup for {pin_code}: {str(e)} - Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred during PIN code lookup."
        )