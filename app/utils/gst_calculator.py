# app/utils/gst_calculator.py

"""
Smart GST Calculator with Strict State Code Enforcement
Implements intelligent GST calculation based on company and customer state codes.
Version 1.6+: NO FALLBACK - state codes are strictly required.
"""

from typing import Tuple, Dict, Optional
import logging

logger = logging.getLogger(__name__)

# Strict enforcement flag - NO FALLBACK allowed
STRICT_STATE_CODE_ENFORCEMENT = True


def calculate_gst_amounts(
    taxable_amount: float,
    gst_rate: float,
    company_state_code: str,
    customer_state_code: str,
    organization_id: Optional[int] = None,
    entity_id: Optional[int] = None,
    entity_type: Optional[str] = None
) -> Dict[str, float]:
    """
    Calculate GST amounts (CGST, SGST, or IGST) based on state codes.
    
    STRICT ENFORCEMENT (v1.6+): NO FALLBACK - Both state codes are REQUIRED.
    
    GST Rules:
    - If customer_state_code is same as company_state_code: Intra-state transaction
      → Apply CGST (half of GST rate) + SGST (half of GST rate)
    - If customer_state_code differs from company_state_code: Inter-state transaction
      → Apply IGST (full GST rate)
    
    Args:
        taxable_amount: The taxable amount (after discounts)
        gst_rate: GST rate as a percentage (e.g., 18 for 18%)
        company_state_code: State code of the company/seller (REQUIRED - NO FALLBACK)
        customer_state_code: State code of the customer/buyer (REQUIRED - NO FALLBACK)
        organization_id: Optional organization ID for audit logging
        entity_id: Optional entity ID (customer/vendor) for audit logging
        entity_type: Optional entity type (customer/vendor) for audit logging
    
    Returns:
        Dictionary with cgst_amount, sgst_amount, igst_amount, and is_inter_state flag
        
    Raises:
        ValueError: If company_state_code or customer_state_code is missing or invalid
    """
    def _validate_state_code(code: str, field_name: str) -> None:
        """Helper to validate state code - STRICT ENFORCEMENT"""
        if not code or not code.strip():
            error_msg = f"{field_name} is required for GST calculation (NO FALLBACK allowed)"
            logger.error(f"GST VALIDATION FAILED: {error_msg} - org_id={organization_id}, entity_id={entity_id}, entity_type={entity_type}")
            raise ValueError(error_msg)
    
    # Validate required state codes
    _validate_state_code(company_state_code, "company_state_code")
    _validate_state_code(customer_state_code, "customer_state_code")
    
    # Normalize state codes to uppercase for comparison
    company_state = company_state_code.strip().upper()
    customer_state = customer_state_code.strip().upper()
    
    # Audit log the GST calculation attempt
    audit_context = {
        "organization_id": organization_id,
        "entity_id": entity_id,
        "entity_type": entity_type,
        "taxable_amount": taxable_amount,
        "gst_rate": gst_rate,
        "company_state_code": company_state,
        "customer_state_code": customer_state
    }
    logger.info(f"GST CALCULATION: {audit_context}")
    
    # Determine if intra-state or inter-state transaction
    if customer_state == company_state:
        # Intra-state transaction: CGST + SGST
        half_rate = (gst_rate / 2) / 100
        cgst_amount = round(taxable_amount * half_rate, 2)
        sgst_amount = round(taxable_amount * half_rate, 2)
        igst_amount = 0.0
        is_inter_state = False
        
        logger.info(f"GST RESULT [INTRA-STATE]: Company={company_state}, Customer={customer_state}, "
                    f"CGST={cgst_amount}, SGST={sgst_amount}, org_id={organization_id}")
    else:
        # Inter-state transaction: IGST
        full_rate = gst_rate / 100
        cgst_amount = 0.0
        sgst_amount = 0.0
        igst_amount = round(taxable_amount * full_rate, 2)
        is_inter_state = True
        
        logger.info(f"GST RESULT [INTER-STATE]: Company={company_state}, Customer={customer_state}, "
                    f"IGST={igst_amount}, org_id={organization_id}")
    
    return {
        "cgst_amount": cgst_amount,
        "sgst_amount": sgst_amount,
        "igst_amount": igst_amount,
        "is_inter_state": is_inter_state
    }


def get_gst_summary(items: list, company_state_code: str) -> Dict[str, any]:
    """
    Calculate GST summary for a list of voucher items.
    
    Args:
        items: List of items with taxable_amount, gst_rate, and customer_state_code
        company_state_code: Company's state code
    
    Returns:
        Dictionary with total CGST, SGST, IGST, and mixed transaction flag
    """
    total_cgst = 0.0
    total_sgst = 0.0
    total_igst = 0.0
    has_intra_state = False
    has_inter_state = False
    
    for item in items:
        gst_amounts = calculate_gst_amounts(
            taxable_amount=item.get('taxable_amount', 0.0),
            gst_rate=item.get('gst_rate', 18.0),
            company_state_code=company_state_code,
            customer_state_code=item.get('customer_state_code')
        )
        
        total_cgst += gst_amounts['cgst_amount']
        total_sgst += gst_amounts['sgst_amount']
        total_igst += gst_amounts['igst_amount']
        
        if gst_amounts['is_inter_state']:
            has_inter_state = True
        else:
            has_intra_state = True
    
    return {
        "total_cgst": round(total_cgst, 2),
        "total_sgst": round(total_sgst, 2),
        "total_igst": round(total_igst, 2),
        "has_mixed_transactions": has_intra_state and has_inter_state
    }


def validate_state_code(state_code: str) -> bool:
    """
    Validate if a state code is valid for Indian states/UTs.
    
    Args:
        state_code: Two-digit state code
    
    Returns:
        True if valid, False otherwise
    """
    # Indian state codes range from 01 to 38 (with some gaps)
    valid_codes = {
        "01",  # Jammu and Kashmir
        "02",  # Himachal Pradesh
        "03",  # Punjab
        "04",  # Chandigarh
        "05",  # Uttarakhand
        "06",  # Haryana
        "07",  # Delhi
        "08",  # Rajasthan
        "09",  # Uttar Pradesh
        "10",  # Bihar
        "11",  # Sikkim
        "12",  # Arunachal Pradesh
        "13",  # Nagaland
        "14",  # Manipur
        "15",  # Mizoram
        "16",  # Tripura
        "17",  # Meghalaya
        "18",  # Assam
        "19",  # West Bengal
        "20",  # Jharkhand
        "21",  # Odisha
        "22",  # Chhattisgarh
        "23",  # Madhya Pradesh
        "24",  # Gujarat
        "26",  # Dadra and Nagar Haveli and Daman and Diu
        "27",  # Maharashtra
        "28",  # Andhra Pradesh (before bifurcation)
        "29",  # Karnataka
        "30",  # Goa
        "31",  # Lakshadweep
        "32",  # Kerala
        "33",  # Tamil Nadu
        "34",  # Puducherry
        "35",  # Andaman and Nicobar Islands
        "36",  # Telangana
        "37",  # Andhra Pradesh (after bifurcation)
        "38",  # Ladakh
        "97",  # Other Territory
    }
    
    return state_code.strip() in valid_codes


def get_state_name_from_code(state_code: str) -> Optional[str]:
    """
    Get state name from state code.
    
    Args:
        state_code: Two-digit state code
    
    Returns:
        State name or None if not found
    """
    state_mapping = {
        "01": "Jammu and Kashmir",
        "02": "Himachal Pradesh",
        "03": "Punjab",
        "04": "Chandigarh",
        "05": "Uttarakhand",
        "06": "Haryana",
        "07": "Delhi",
        "08": "Rajasthan",
        "09": "Uttar Pradesh",
        "10": "Bihar",
        "11": "Sikkim",
        "12": "Arunachal Pradesh",
        "13": "Nagaland",
        "14": "Manipur",
        "15": "Mizoram",
        "16": "Tripura",
        "17": "Meghalaya",
        "18": "Assam",
        "19": "West Bengal",
        "20": "Jharkhand",
        "21": "Odisha",
        "22": "Chhattisgarh",
        "23": "Madhya Pradesh",
        "24": "Gujarat",
        "26": "Dadra and Nagar Haveli and Daman and Diu",
        "27": "Maharashtra",
        "29": "Karnataka",
        "30": "Goa",
        "31": "Lakshadweep",
        "32": "Kerala",
        "33": "Tamil Nadu",
        "34": "Puducherry",
        "35": "Andaman and Nicobar Islands",
        "36": "Telangana",
        "37": "Andhra Pradesh",
        "38": "Ladakh",
        "97": "Other Territory",
    }
    
    return state_mapping.get(state_code.strip())
