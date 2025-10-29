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
from app.core.enforcement import require_access
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
    auth: tuple = Depends(require_access("voucher_format_template", "read")),
    db: AsyncSession = Depends(get_db)
):
    """List all available voucher format templates (system and custom)"""
    current_user, org_id = auth
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
    auth: tuple = Depends(require_access("voucher_format_template", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific voucher format template"""
    current_user, org_id = auth
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
    auth: tuple = Depends(require_access("voucher_format_template", "create")),
    db: AsyncSession = Depends(get_db)
):
    """Create a new voucher format template (custom template)"""
    current_user, org_id = auth
    template = VoucherFormatTemplate(**template_data.model_dump())
    db.add(template)
    await db.commit()
    await db.refresh(template)
    
    return template


@router.put("/{template_id}", response_model=VoucherFormatTemplateResponse)
async def update_voucher_format_template(
    template_id: int,
    template_data: VoucherFormatTemplateUpdate,
    auth: tuple = Depends(require_access("voucher_format_template", "update")),
    db: AsyncSession = Depends(get_db)
):
    """Update a voucher format template"""
    current_user, org_id = auth
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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Voucher format template not found"
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
    auth: tuple = Depends(require_access("voucher_format_template", "delete")),
    db: AsyncSession = Depends(get_db)
):
    """Delete a voucher format template"""
    current_user, org_id = auth
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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Voucher format template not found"
        )
    
    await db.delete(template)
    await db.commit()
    
    return None


@router.get("/system/defaults", response_model=List[VoucherFormatTemplateResponse])
async def get_default_system_templates(
    auth: tuple = Depends(require_access("voucher_format_template", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get default system voucher format templates"""
    current_user, org_id = auth
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
    auth: tuple = Depends(require_access("voucher_format_template", "read")),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate a preview image/PDF for a voucher format template
    Returns sample voucher rendered with the template configuration
    """
    current_user, org_id = auth
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
            organization_id=org_id,
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