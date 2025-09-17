from fastapi import APIRouter, HTTPException
from typing import Dict
import requests
import logging
import traceback  # For detailed error logging
import ssl  # For TLS adapter
from requests.adapters import HTTPAdapter  # For TLS adapter
from urllib3.poolmanager import PoolManager  # For TLS adapter

logger = logging.getLogger(__name__)
router = APIRouter()

# Custom TLS adapter to enforce minimum TLS version (helps with SSL issues)
class TLSAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False):
        """Create and initialize the urllib3 PoolManager."""
        context = ssl.create_default_context()
        context.check_hostname = False  # Added to allow verify=False without conflict (resolves ValueError)
        context.minimum_version = ssl.TLSVersion.TLSv1_2  # Enforce TLS 1.2 or higher
        self.poolmanager = PoolManager(
            num_pools=connections,
            maxsize=maxsize,
            block=block,
            ssl_context=context,
        )

# Create a session with the TLS adapter mounted for HTTPS
session = requests.Session()
session.mount('https://', TLSAdapter())

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
        # Fetch from alternative external API (switched to pinlookup.in as postalpincode.in seems unreliable/unavailable)
        # This API is free, no key needed, up to 5K requests/day
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        # Use the session with TLS adapter
        response = session.get(
            f"https://pinlookup.in/api/pincode?pincode={pin_code}",
            headers=headers,
            timeout=15,  # 15 seconds for slower networks
            verify=False  # Kept as fallback for any remaining SSL issues (use cautiously in production)
        )
        response.raise_for_status()  # Raise error for bad status codes
        data = response.json()
        
        # Check if data exists (API returns {'data': {...}} on success)
        if not data.get('data'):
            raise HTTPException(
                status_code=404,
                detail=f"PIN code {pin_code} not found. Please enter city and state manually."
            )
        
        # Extract from data entry
        pin_data = data['data']
        city = pin_data['district_name'].title()  # e.g., "South Goa"
        state = pin_data['state_name'].title()   # e.g., "Goa"
        state_code = STATE_CODE_MAP.get(state, "00")  # Default to "00" if not found in map
        
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