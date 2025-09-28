# app/api/vendors.py

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from typing import List, Optional
from app.core.database import get_db
from app.api.v1.auth import (
    get_current_active_user, get_current_admin_user
)
from app.core.tenant import TenantQueryFilter
from app.core.org_restrictions import require_current_organization_id, ensure_organization_context
from app.models import User, Vendor, VendorFile
from app.schemas.base import VendorCreate, VendorUpdate, VendorInDB, BulkImportResponse, VendorFileResponse
from app.services.excel_service import VendorExcelService, ExcelService
import logging
import os
import uuid
import shutil

logger = logging.getLogger(__name__)
router = APIRouter()

# --- Vendor CRUD Endpoints ---

@router.get("", response_model=List[VendorInDB])
async def get_vendors(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    active_only: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all vendors for the organization"""
    
    # Restrict app super admins from accessing organization data  
    target_org_id = ensure_organization_context(current_user)
    
    stmt = TenantQueryFilter.apply_organization_filter(
        select(Vendor), Vendor, target_org_id, current_user
    )

    if active_only:
        stmt = stmt.where(Vendor.is_active == True)
    if search:
        search_filter = or_(
            Vendor.name.contains(search),
            Vendor.contact_number.contains(search),
            Vendor.email.contains(search)
        )
        stmt = stmt.where(search_filter)
    result = await db.execute(stmt.offset(skip).limit(limit))
    vendors = result.scalars().all()
    return vendors

@router.post("", response_model=VendorInDB)
async def create_vendor(
    vendor: VendorCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create new vendor"""
    vendor_data = vendor.dict()
    vendor_data = TenantQueryFilter.validate_organization_data(vendor_data, current_user)
    # Check for duplicate vendor name in organization
    stmt = TenantQueryFilter.apply_organization_filter(
        select(Vendor), Vendor, vendor_data['organization_id'], current_user
    ).where(Vendor.name == vendor_data['name'])
    result = await db.execute(stmt)
    existing_vendor = result.scalar_one_or_none()
    if existing_vendor:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Vendor with name '{vendor_data['name']}' already exists in this organization"
        )
    db_vendor = Vendor(**vendor_data)
    db.add(db_vendor)
    await db.commit()
    await db.refresh(db_vendor)
    logger.info(f"Created vendor {db_vendor.name} (ID: {db_vendor.id}) in organization {db_vendor.organization_id}")
    return db_vendor

@router.get("/{vendor_id}", response_model=VendorInDB)
async def get_vendor(
    vendor_id: int,
    organization_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get vendor by ID with organization validation"""
    if organization_id and getattr(current_user, 'is_platform_user', False):
        validate_organization_access(organization_id, current_user, db)
        target_org_id = organization_id
    else:
        target_org_id = require_current_organization_id(current_user)
    
    stmt = TenantQueryFilter.apply_organization_filter(
        select(Vendor), Vendor, target_org_id, current_user
    ).where(Vendor.id == vendor_id)
    result = await db.execute(stmt)
    vendor = result.scalar_one_or_none()
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vendor {vendor_id} not found in organization {target_org_id}"
        )
    return vendor

@router.put("/{vendor_id}", response_model=VendorInDB)
async def update_vendor(
    vendor_id: int,
    vendor: VendorUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update vendor with organization validation"""
    target_org_id = require_current_organization_id(current_user)
    stmt = TenantQueryFilter.apply_organization_filter(
        select(Vendor), Vendor, target_org_id, current_user
    ).where(Vendor.id == vendor_id)
    result = await db.execute(stmt)
    db_vendor = result.scalar_one_or_none()
    if not db_vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vendor {vendor_id} not found in organization {target_org_id}"
        )
    update_data = vendor.dict(exclude_unset=True)
    if 'name' in update_data and update_data['name'] != db_vendor.name:
        stmt = TenantQueryFilter.apply_organization_filter(
            select(Vendor), Vendor, target_org_id, current_user
        ).where(
            Vendor.name == update_data['name'],
            Vendor.id != vendor_id
        )
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Vendor with name '{update_data['name']}' already exists in this organization"
            )
    for field, value in update_data.items():
        setattr(db_vendor, field, value)
    await db.commit()
    await db.refresh(db_vendor)
    logger.info(f"Updated vendor {db_vendor.name} (ID: {db_vendor.id}) in organization {db_vendor.organization_id}")
    return db_vendor

@router.delete("/{vendor_id}")
async def delete_vendor(
    vendor_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Delete vendor with organization validation (admin only)"""
    target_org_id = require_current_organization_id(current_user)
    stmt = TenantQueryFilter.apply_organization_filter(
        select(Vendor), Vendor, target_org_id, current_user
    ).where(Vendor.id == vendor_id)
    result = await db.execute(stmt)
    db_vendor = result.scalar_one_or_none()
    if not db_vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vendor {vendor_id} not found in organization {target_org_id}"
        )
    # Soft delete (recommended): mark as inactive
    db_vendor.is_active = False
    await db.commit()
    logger.info(f"Deleted vendor {db_vendor.name} (ID: {db_vendor.id}) in organization {db_vendor.organization_id}")
    return {"message": f"Vendor {vendor_id} deleted successfully"}

# --- Search for Dropdown/Autocomplete ---

@router.post("/search", response_model=List[VendorInDB])
async def search_vendors_for_dropdown(
    search_term: str,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Search vendors for dropdown/autocomplete with organization filtering"""
    target_org_id = require_current_organization_id(current_user)
    stmt = TenantQueryFilter.apply_organization_filter(
        select(Vendor), Vendor, target_org_id, current_user
    ).where(
        Vendor.is_active == True,
        Vendor.name.contains(search_term)
    ).limit(limit)
    result = await db.execute(stmt)
    vendors = result.scalars().all()
    return vendors

# --- Excel Import/Export/Template endpoints ---

@router.get("/template/excel")
async def download_vendors_template(
    current_user: User = Depends(get_current_active_user)
):
    """Download Excel template for vendors bulk import"""
    excel_data = VendorExcelService.create_template()
    return ExcelService.create_streaming_response(excel_data, "vendors_template.xlsx")

@router.get("/export/excel")
async def export_vendors_excel(
    skip: int = 0,
    limit: int = 1000,
    search: Optional[str] = None,
    active_only: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Export vendors to Excel"""
    target_org_id = require_current_organization_id(current_user)
    stmt = TenantQueryFilter.apply_organization_filter(
        select(Vendor), Vendor, target_org_id, current_user
    )
    if active_only:
        stmt = stmt.where(Vendor.is_active == True)
    if search:
        search_filter = or_(
            Vendor.name.contains(search),
            Vendor.contact_number.contains(search),
            Vendor.email.contains(search)
        )
        stmt = stmt.where(search_filter)
    result = await db.execute(stmt.offset(skip).limit(limit))
    vendors = result.scalars().all()
    
    vendors_data = []
    for vendor in vendors:
        vendors_data.append({
            "name": vendor.name,
            "contact_number": vendor.contact_number,
            "email": vendor.email or "",
            "address1": vendor.address1,
            "address2": vendor.address2 or "",
            "city": vendor.city,
            "state": vendor.state,
            "pin_code": vendor.pin_code,
            "state_code": vendor.state_code,
            "gst_number": vendor.gst_number or "",
            "pan_number": vendor.pan_number or "",
        })
    excel_data = VendorExcelService.export_vendors(vendors_data)
    return ExcelService.create_streaming_response(excel_data, "vendors_export.xlsx")

@router.post("/import/excel", response_model=BulkImportResponse)
async def import_vendors_excel(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Import vendors from Excel file"""
    org_id = require_current_organization_id(current_user)
    # Validate file type
    if not file.filename or not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only Excel files (.xlsx, .xls) are allowed"
        )
    # Parse Excel file
    records = await ExcelService.parse_excel_file(file, VendorExcelService.REQUIRED_COLUMNS, "Vendor Import Template")
    
    if not records:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data found in Excel file"
        )
    
    created_count = 0
    updated_count = 0
    errors = []
    
    for i, record in enumerate(records, 1):
        try:
            vendor_data = {
                "name": record.get("name", "").strip(),
                "contact_number": record.get("contact_number", "").strip(),
                "email": record.get("email", "").strip() or None,
                "address1": record.get("address_line_1", "").strip(),
                "address2": record.get("address_line_2", "").strip() or None,
                "city": record.get("city", "").strip(),
                "state": record.get("state", "").strip(),
                "pin_code": record.get("pin_code", "").strip(),
                "state_code": record.get("state_code", "").strip(),
                "gst_number": record.get("gst_number", "").strip() or None,
                "pan_number": record.get("pan_number", "").strip() or None,
            }
            # Validate required fields
            required_fields = ["name", "contact_number", "address1", "city", "state", "pin_code", "state_code"]
            for field in required_fields:
                if not vendor_data[field]:
                    errors.append(f"Row {i}: {field.replace('_', ' ').title()} is required")
                    break
            if errors and errors[-1].startswith(f"Row {i}:"):
                continue
            # Check if vendor already exists
            stmt = select(Vendor).where(
                Vendor.name == vendor_data["name"],
                Vendor.organization_id == org_id
            )
            result = await db.execute(stmt)
            existing_vendor = result.scalar_one_or_none()
            
            if existing_vendor:
                for field, value in vendor_data.items():
                    setattr(existing_vendor, field, value)
                updated_count += 1
                logger.info(f"Updated vendor: {vendor_data['name']}")
            else:
                new_vendor = Vendor(
                    organization_id=org_id,
                    **vendor_data
                )
                db.add(new_vendor)
                created_count += 1
                logger.info(f"Created vendor: {vendor_data['name']}")
        except Exception as e:
            errors.append(f"Row {i}: Error processing record - {str(e)}")
            continue
    await db.commit()
    logger.info(f"Vendors import completed by {current_user.email}: "
               f"{created_count} created, {updated_count} updated, {len(errors)} errors")
    return BulkImportResponse(
        message=f"Import completed successfully. {created_count} vendors created, {updated_count} updated.",
        total_processed=len(records),
        created=created_count,
        updated=updated_count,
        errors=errors
    )

# File upload directory
UPLOAD_DIR = "uploads/vendors"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/{vendor_id}/files", response_model=VendorFileResponse)
async def upload_vendor_file(
    vendor_id: int,
    file: UploadFile = File(...),
    file_type: str = "general",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Upload a file for a vendor (GST certificate, PAN card, etc.)"""
    
    org_id = ensure_organization_context(current_user)
    
    # Verify vendor exists and belongs to current organization
    stmt = select(Vendor).where(
        Vendor.id == vendor_id,
        Vendor.organization_id == org_id
    )
    result = await db.execute(stmt)
    vendor = result.scalar_one_or_none()
    
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor not found"
        )
    
    # Check file count limit (max 10 files per vendor)
    stmt = select(VendorFile).where(
        VendorFile.vendor_id == vendor_id,
        VendorFile.organization_id == org_id
    )
    result = await db.execute(stmt)
    existing_files_count = len(result.scalars().all())
    
    if existing_files_count >= 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 10 files allowed per vendor"
        )
    
    # Validate file size (max 10MB)
    if file.size and file.size > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size must be less than 10MB"
        )
    
    # For GST certificates, validate PDF format
    if file_type == "gst_certificate":
        if not file.filename or not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="GST certificate must be a PDF file"
            )
    
    # Generate unique filename
    file_extension = os.path.splitext(file.filename or "")[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    # Save file to disk
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Create database record
    db_file = VendorFile(
        vendor_id=vendor_id,
        organization_id=org_id,
        filename=unique_filename,
        original_filename=file.filename or "unknown",
        file_path=file_path,
        file_size=file.size or 0,
        content_type=file.content_type or "application/octet-stream",
        file_type=file_type
    )
    db.add(db_file)
    await db.commit()
    await db.refresh(db_file)
    
    logger.info(f"Vendor file uploaded: {db_file.original_filename} for vendor {vendor_id}")
    
    return VendorFileResponse(
        id=db_file.id,
        filename=db_file.filename,
        original_filename=db_file.original_filename,
        file_size=db_file.file_size,
        content_type=db_file.content_type,
        file_type=db_file.file_type,
        vendor_id=db_file.vendor_id,
        created_at=db_file.created_at
    )

@router.get("/{vendor_id}/files", response_model=List[VendorFileResponse])
async def get_vendor_files(
    vendor_id: int,
    file_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all files for a vendor, optionally filtered by file type"""
    
    org_id = ensure_organization_context(current_user)
    
    # Verify vendor exists and belongs to current organization
    stmt = select(Vendor).where(
        Vendor.id == vendor_id,
        Vendor.organization_id == org_id
    )
    result = await db.execute(stmt)
    vendor = result.scalar_one_or_none()
    
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor not found"
        )
    
    stmt = select(VendorFile).where(
        VendorFile.vendor_id == vendor_id,
        VendorFile.organization_id == org_id
    )
    
    if file_type:
        stmt = stmt.where(VendorFile.file_type == file_type)
    
    result = await db.execute(stmt)
    files = result.scalars().all()
    
    return [
        VendorFileResponse(
            id=f.id,
            filename=f.filename,
            original_filename=f.original_filename,
            file_size=f.file_size,
            content_type=f.content_type,
            file_type=f.file_type,
            vendor_id=f.vendor_id,
            created_at=f.created_at
        ) for f in files
    ]

@router.get("/{vendor_id}/files/{file_id}/download")
async def download_vendor_file(
    vendor_id: int,
    file_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Download a vendor file"""
    
    org_id = ensure_organization_context(current_user)
    
    # Get file record
    stmt = select(VendorFile).where(
        VendorFile.id == file_id,
        VendorFile.vendor_id == vendor_id,
        VendorFile.organization_id == org_id
    )
    result = await db.execute(stmt)
    file_record = result.scalar_one_or_none()
    
    if not file_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Check if file exists on disk
    if not os.path.exists(file_record.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found on disk"
        )
    
    return StreamingResponse(
        open(file_record.file_path, "rb"),
        media_type=file_record.content_type,
        headers={"Content-Disposition": f"attachment; filename={file_record.original_filename}"}
    )

@router.delete("/{vendor_id}/files/{file_id}")
async def delete_vendor_file(
    vendor_id: int,
    file_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a vendor file"""
    
    org_id = ensure_organization_context(current_user)
    
    # Get file record
    stmt = select(VendorFile).where(
        VendorFile.id == file_id,
        VendorFile.vendor_id == vendor_id,
        VendorFile.organization_id == org_id
    )
    result = await db.execute(stmt)
    file_record = result.scalar_one_or_none()
    
    if not file_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Remove file from disk
    if os.path.exists(file_record.file_path):
        os.remove(file_record.file_path)
    
    # Remove database record
    await db.delete(file_record)
    await db.commit()
    
    return {"message": "File deleted successfully"}