# app/api/v1/voucher_email_templates.py

"""
API endpoints for voucher email templates
Requirement 2: Auto-fill email templates for different voucher types
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.core.database import get_db
from app.core.permissions import require_organization_permission, Permission
from app.core.security import get_current_user
from app.models.email import VoucherEmailTemplate
from app.schemas.organization_settings import (
    VoucherEmailTemplateCreate,
    VoucherEmailTemplateUpdate,
    VoucherEmailTemplateResponse
)

router = APIRouter(prefix="/voucher-email-templates", tags=["voucher-email-templates"])


@router.get("/", response_model=List[VoucherEmailTemplateResponse])
async def list_voucher_email_templates(
    voucher_type: str = None,
    entity_type: str = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_organization_permission(Permission.VIEW_VOUCHERS))
):
    """List all voucher email templates for the organization"""
    stmt = select(VoucherEmailTemplate).where(
        VoucherEmailTemplate.organization_id == current_user.organization_id
    )
    
    if voucher_type:
        stmt = stmt.where(VoucherEmailTemplate.voucher_type == voucher_type)
    if entity_type:
        stmt = stmt.where(VoucherEmailTemplate.entity_type == entity_type)
    
    result = await db.execute(stmt)
    templates = result.scalars().all()
    return templates


@router.get("/{template_id}", response_model=VoucherEmailTemplateResponse)
async def get_voucher_email_template(
    template_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_organization_permission(Permission.VIEW_VOUCHERS))
):
    """Get a specific voucher email template"""
    stmt = select(VoucherEmailTemplate).where(
        VoucherEmailTemplate.id == template_id,
        VoucherEmailTemplate.organization_id == current_user.organization_id
    )
    result = await db.execute(stmt)
    template = result.scalar_one_or_none()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Voucher email template not found"
        )
    
    return template


@router.post("/", response_model=VoucherEmailTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_voucher_email_template(
    template_data: VoucherEmailTemplateCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_organization_permission(Permission.MANAGE_VOUCHERS))
):
    """Create a new voucher email template"""
    # Ensure template is for current user's organization
    if template_data.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create template for another organization"
        )
    
    # Check for duplicate
    stmt = select(VoucherEmailTemplate).where(
        VoucherEmailTemplate.organization_id == current_user.organization_id,
        VoucherEmailTemplate.voucher_type == template_data.voucher_type,
        VoucherEmailTemplate.entity_type == template_data.entity_type
    )
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Template already exists for {template_data.voucher_type} and {template_data.entity_type}"
        )
    
    template = VoucherEmailTemplate(**template_data.model_dump())
    db.add(template)
    await db.commit()
    await db.refresh(template)
    
    return template


@router.put("/{template_id}", response_model=VoucherEmailTemplateResponse)
async def update_voucher_email_template(
    template_id: int,
    template_data: VoucherEmailTemplateUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_organization_permission(Permission.MANAGE_VOUCHERS))
):
    """Update a voucher email template"""
    stmt = select(VoucherEmailTemplate).where(
        VoucherEmailTemplate.id == template_id,
        VoucherEmailTemplate.organization_id == current_user.organization_id
    )
    result = await db.execute(stmt)
    template = result.scalar_one_or_none()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Voucher email template not found"
        )
    
    update_data = template_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(template, field, value)
    
    await db.commit()
    await db.refresh(template)
    
    return template


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_voucher_email_template(
    template_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_organization_permission(Permission.MANAGE_VOUCHERS))
):
    """Delete a voucher email template"""
    stmt = select(VoucherEmailTemplate).where(
        VoucherEmailTemplate.id == template_id,
        VoucherEmailTemplate.organization_id == current_user.organization_id
    )
    result = await db.execute(stmt)
    template = result.scalar_one_or_none()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Voucher email template not found"
        )
    
    await db.delete(template)
    await db.commit()
    
    return None


@router.get("/default/{voucher_type}/{entity_type}", response_model=VoucherEmailTemplateResponse)
async def get_default_template(
    voucher_type: str,
    entity_type: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_organization_permission(Permission.VIEW_VOUCHERS))
):
    """
    Get default email template for a voucher type and entity type.
    Returns org-specific template if exists, otherwise returns a generated default.
    """
    # Try to get org-specific template
    stmt = select(VoucherEmailTemplate).where(
        VoucherEmailTemplate.organization_id == current_user.organization_id,
        VoucherEmailTemplate.voucher_type == voucher_type,
        VoucherEmailTemplate.entity_type == entity_type,
        VoucherEmailTemplate.is_active == True
    )
    result = await db.execute(stmt)
    template = result.scalar_one_or_none()
    
    if template:
        return template
    
    # Return a default template structure
    default_templates = {
        ("purchase_order", "vendor"): {
            "subject_template": "Purchase Order {voucher_number} - {organization_name}",
            "body_template": "Dear {vendor_name},\n\nPlease find the attached Purchase Order {voucher_number} dated {voucher_date}.\n\nTotal Amount: {total_amount}\n\nThank you for your business.\n\nBest regards,\n{organization_name}"
        },
        ("sales_order", "customer"): {
            "subject_template": "Sales Order {voucher_number} - {organization_name}",
            "body_template": "Dear {customer_name},\n\nThank you for your order! Please find the attached Sales Order {voucher_number} dated {voucher_date}.\n\nTotal Amount: {total_amount}\n\nWe will process your order shortly.\n\nBest regards,\n{organization_name}"
        },
        ("purchase_voucher", "vendor"): {
            "subject_template": "Purchase Invoice {voucher_number} - {organization_name}",
            "body_template": "Dear {vendor_name},\n\nPlease find the attached Purchase Invoice {voucher_number} dated {voucher_date}.\n\nTotal Amount: {total_amount}\n\nThank you.\n\nBest regards,\n{organization_name}"
        },
        ("sales_voucher", "customer"): {
            "subject_template": "Invoice {voucher_number} - {organization_name}",
            "body_template": "Dear {customer_name},\n\nPlease find the attached Invoice {voucher_number} dated {voucher_date}.\n\nTotal Amount: {total_amount}\n\nPayment is due as per the terms mentioned in the invoice.\n\nThank you for your business.\n\nBest regards,\n{organization_name}"
        },
        ("quotation", "customer"): {
            "subject_template": "Quotation {voucher_number} - {organization_name}",
            "body_template": "Dear {customer_name},\n\nThank you for your interest! Please find the attached Quotation {voucher_number} dated {voucher_date}.\n\nTotal Amount: {total_amount}\n\nThis quotation is valid for 30 days from the date mentioned.\n\nWe look forward to your confirmation.\n\nBest regards,\n{organization_name}"
        },
    }
    
    key = (voucher_type, entity_type)
    if key not in default_templates:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No default template found for {voucher_type} and {entity_type}"
        )
    
    # Return as a response-like object
    return VoucherEmailTemplateResponse(
        id=0,  # Special ID to indicate it's a default template
        organization_id=current_user.organization_id,
        voucher_type=voucher_type,
        entity_type=entity_type,
        subject_template=default_templates[key]["subject_template"],
        body_template=default_templates[key]["body_template"],
        is_active=True,
        created_at=None,
        updated_at=None
    )
