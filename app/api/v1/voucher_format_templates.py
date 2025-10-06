# app/api/v1/voucher_format_templates.py

"""
API endpoints for voucher format templates (PDF/email formatting)
Requirement 7: Multiple voucher format templates with preview/select
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.core.database import get_db
from app.core.permissions import require_organization_permission, Permission
from app.core.security import get_current_user
from app.models.organization_settings import VoucherFormatTemplate
from app.schemas.organization_settings import (
    VoucherFormatTemplateCreate,
    VoucherFormatTemplateUpdate,
    VoucherFormatTemplateResponse
)

router = APIRouter(prefix="/voucher-format-templates", tags=["voucher-format-templates"])


@router.get("/", response_model=List[VoucherFormatTemplateResponse])
async def list_voucher_format_templates(
    include_system: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_organization_permission(Permission.VIEW_VOUCHERS))
):
    """List all available voucher format templates (system and custom)"""
    stmt = select(VoucherFormatTemplate).where(
        VoucherFormatTemplate.is_active == True
    )
    
    if not include_system:
        stmt = stmt.where(VoucherFormatTemplate.is_system_template == False)
    
    result = await db.execute(stmt)
    templates = result.scalars().all()
    return templates


@router.get("/{template_id}", response_model=VoucherFormatTemplateResponse)
async def get_voucher_format_template(
    template_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_organization_permission(Permission.VIEW_VOUCHERS))
):
    """Get a specific voucher format template"""
    stmt = select(VoucherFormatTemplate).where(
        VoucherFormatTemplate.id == template_id
    )
    result = await db.execute(stmt)
    template = result.scalar_one_or_none()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Voucher format template not found"
        )
    
    return template


@router.post("/", response_model=VoucherFormatTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_voucher_format_template(
    template_data: VoucherFormatTemplateCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_organization_permission(Permission.MANAGE_VOUCHERS))
):
    """Create a new voucher format template (custom template)"""
    template = VoucherFormatTemplate(**template_data.model_dump())
    db.add(template)
    await db.commit()
    await db.refresh(template)
    
    return template


@router.put("/{template_id}", response_model=VoucherFormatTemplateResponse)
async def update_voucher_format_template(
    template_id: int,
    template_data: VoucherFormatTemplateUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_organization_permission(Permission.MANAGE_VOUCHERS))
):
    """Update a voucher format template"""
    stmt = select(VoucherFormatTemplate).where(
        VoucherFormatTemplate.id == template_id
    )
    result = await db.execute(stmt)
    template = result.scalar_one_or_none()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Voucher format template not found"
        )
    
    # Prevent modification of system templates
    if template.is_system_template:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot modify system templates"
        )
    
    update_data = template_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(template, field, value)
    
    await db.commit()
    await db.refresh(template)
    
    return template


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_voucher_format_template(
    template_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_organization_permission(Permission.MANAGE_VOUCHERS))
):
    """Delete a voucher format template"""
    stmt = select(VoucherFormatTemplate).where(
        VoucherFormatTemplate.id == template_id
    )
    result = await db.execute(stmt)
    template = result.scalar_one_or_none()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Voucher format template not found"
        )
    
    # Prevent deletion of system templates
    if template.is_system_template:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete system templates"
        )
    
    await db.delete(template)
    await db.commit()
    
    return None


@router.get("/system/defaults", response_model=List[VoucherFormatTemplateResponse])
async def get_default_system_templates(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_organization_permission(Permission.VIEW_VOUCHERS))
):
    """Get default system voucher format templates"""
    stmt = select(VoucherFormatTemplate).where(
        VoucherFormatTemplate.is_system_template == True,
        VoucherFormatTemplate.is_active == True
    )
    result = await db.execute(stmt)
    templates = result.scalars().all()
    return templates


@router.get("/{template_id}/preview")
async def preview_voucher_format_template(
    template_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_organization_permission(Permission.VIEW_VOUCHERS))
):
    """
    Generate a preview image/PDF for a voucher format template
    Returns sample voucher rendered with the template configuration
    """
    from fastapi.responses import StreamingResponse
    from app.services.pdf_generation_service import pdf_generator
    import io
    
    stmt = select(VoucherFormatTemplate).where(
        VoucherFormatTemplate.id == template_id
    )
    result = await db.execute(stmt)
    template = result.scalar_one_or_none()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Voucher format template not found"
        )
    
    # Generate a sample voucher with dummy data
    sample_voucher_data = {
        'id': 1,
        'voucher_number': 'PO/2425/00001',
        'voucher_date': '2024-01-15',
        'due_date': '2024-02-15',
        'vendor_name': 'Sample Vendor Pvt Ltd',
        'vendor_address': '123 Sample Street, Sample City, Sample',
        'vendor_gst': '29ABCDE1234F1Z5',
        'total_amount': 11800.00,
        'items': [
            {
                'product_name': 'Sample Product A',
                'hsn_code': '1234',
                'quantity': 10,
                'unit': 'PCS',
                'unit_price': 1000.00,
                'gst_rate': 18.0
            }
        ]
    }
    
    try:
        # Generate PDF with the template
        pdf_bytes = await pdf_generator.generate_voucher_pdf(
            voucher_type='purchase-orders',
            voucher_data=sample_voucher_data,
            db=db,
            organization_id=current_user.organization_id,
            current_user=current_user
        )
        
        return StreamingResponse(
            pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"inline; filename=template_preview_{template_id}.pdf"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate preview: {str(e)}"
        )