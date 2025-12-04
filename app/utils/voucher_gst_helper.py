# app/utils/voucher_gst_helper.py

"""
Voucher GST Helper Utilities
Provides reusable functions for strict GST state code enforcement across all voucher endpoints.
Version 1.6+: NO FALLBACK - state codes are strictly required.
"""

from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)


async def get_company_state_code_strict(
    db: AsyncSession,
    org_id: int,
    voucher_type: str = "voucher"
) -> str:
    """
    Get organization's state code with STRICT enforcement.
    
    Args:
        db: Database session
        org_id: Organization ID
        voucher_type: Type of voucher being created (for error message)
    
    Returns:
        State code string
        
    Raises:
        HTTPException: If state_code is missing (HTTP 400)
    """
    from app.models.user_models import Organization
    
    org_result = await db.execute(
        select(Organization.state_code).where(Organization.id == org_id)
    )
    company_state_code = org_result.scalars().first()
    
    if not company_state_code:
        error_msg = (
            f"Organization state code is required for GST calculation on {voucher_type}. "
            "Please update your organization profile with a valid state code before creating vouchers."
        )
        logger.error(f"MISSING COMPANY STATE CODE: org_id={org_id}, voucher_type={voucher_type}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    
    logger.info(f"Company state code retrieved: {company_state_code} for org_id={org_id}")
    return company_state_code


async def get_customer_state_code_strict(
    db: AsyncSession,
    customer_id: Optional[int],
    org_id: int,
    voucher_type: str = "voucher"
) -> Optional[str]:
    """
    Get customer's state code with STRICT enforcement.
    
    Args:
        db: Database session
        customer_id: Customer ID (can be None for some vouchers)
        org_id: Organization ID (for logging)
        voucher_type: Type of voucher being created (for error message)
    
    Returns:
        State code string or None if customer_id is None
        
    Raises:
        HTTPException: If customer_id is provided but state_code is missing (HTTP 400)
    """
    from app.models.customer_models import Customer
    
    if not customer_id:
        return None
    
    customer_result = await db.execute(
        select(Customer.state_code).where(Customer.id == customer_id)
    )
    customer_state_code = customer_result.scalars().first()
    
    if not customer_state_code:
        error_msg = (
            f"Customer state code is required for GST calculation on {voucher_type}. "
            "Please update the customer profile with a valid state code before creating vouchers."
        )
        logger.error(f"MISSING CUSTOMER STATE CODE: customer_id={customer_id}, org_id={org_id}, voucher_type={voucher_type}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    
    logger.info(f"Customer state code retrieved: {customer_state_code} for customer_id={customer_id}")
    return customer_state_code


async def get_vendor_state_code_strict(
    db: AsyncSession,
    vendor_id: Optional[int],
    org_id: int,
    voucher_type: str = "voucher"
) -> Optional[str]:
    """
    Get vendor's state code with STRICT enforcement.
    
    Args:
        db: Database session
        vendor_id: Vendor ID (can be None for some vouchers)
        org_id: Organization ID (for logging)
        voucher_type: Type of voucher being created (for error message)
    
    Returns:
        State code string or None if vendor_id is None
        
    Raises:
        HTTPException: If vendor_id is provided but state_code is missing (HTTP 400)
    """
    from app.models.customer_models import Vendor
    
    if not vendor_id:
        return None
    
    vendor_result = await db.execute(
        select(Vendor.state_code).where(Vendor.id == vendor_id)
    )
    vendor_state_code = vendor_result.scalars().first()
    
    if not vendor_state_code:
        error_msg = (
            f"Vendor state code is required for GST calculation on {voucher_type}. "
            "Please update the vendor profile with a valid state code before creating vouchers."
        )
        logger.error(f"MISSING VENDOR STATE CODE: vendor_id={vendor_id}, org_id={org_id}, voucher_type={voucher_type}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    
    logger.info(f"Vendor state code retrieved: {vendor_state_code} for vendor_id={vendor_id}")
    return vendor_state_code


async def get_state_codes_for_sales(
    db: AsyncSession,
    org_id: int,
    customer_id: Optional[int],
    voucher_type: str = "sales voucher"
) -> Tuple[str, Optional[str]]:
    """
    Get both company and customer state codes for sales-type vouchers.
    
    Args:
        db: Database session
        org_id: Organization ID
        customer_id: Customer ID
        voucher_type: Type of voucher (for error messages)
    
    Returns:
        Tuple of (company_state_code, customer_state_code)
    """
    company_state_code = await get_company_state_code_strict(db, org_id, voucher_type)
    customer_state_code = await get_customer_state_code_strict(db, customer_id, org_id, voucher_type)
    
    return company_state_code, customer_state_code


async def get_state_codes_for_purchase(
    db: AsyncSession,
    org_id: int,
    vendor_id: Optional[int],
    voucher_type: str = "purchase voucher"
) -> Tuple[str, Optional[str]]:
    """
    Get both company and vendor state codes for purchase-type vouchers.
    
    Args:
        db: Database session
        org_id: Organization ID
        vendor_id: Vendor ID
        voucher_type: Type of voucher (for error messages)
    
    Returns:
        Tuple of (company_state_code, vendor_state_code)
    """
    company_state_code = await get_company_state_code_strict(db, org_id, voucher_type)
    vendor_state_code = await get_vendor_state_code_strict(db, vendor_id, org_id, voucher_type)
    
    return company_state_code, vendor_state_code
