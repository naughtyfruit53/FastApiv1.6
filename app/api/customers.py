from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.api.v1.auth import get_current_active_user, get_current_admin_user
from app.core.tenant import TenantQueryMixin
from app.core.org_restrictions import ensure_organization_context
from app.models import User, Customer, CustomerFile
from app.schemas.base import CustomerCreate, CustomerUpdate, CustomerInDB, BulkImportResponse, CustomerFileResponse
from app.services.excel_service import CustomerExcelService, ExcelService
import logging
import os
import uuid
import shutil

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("", response_model=List[CustomerInDB])
async def get_customers(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get customers in current organization"""
    
    # Restrict app super admins from accessing organization data  
    org_id = ensure_organization_context(current_user)
    
    query = db.query(Customer)
    query = TenantQueryMixin.filter_by_tenant(query, Customer, org_id)
    
    if active_only:
        query = query.filter(Customer.is_active == True)
    
    if search:
        search_filter = (
            Customer.name.contains(search) |
            Customer.contact_number.contains(search) |
            Customer.email.contains(search)
        )
        query = query.filter(search_filter)
    
    customers = query.offset(skip).limit(limit).all()
    return customers

@router.get("/{customer_id}", response_model=CustomerInDB)
async def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get customer by ID"""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    # Ensure tenant access for non-super-admin users
    if not bool(current_user.is_super_admin):
        TenantQueryMixin.ensure_tenant_access(customer, getattr(customer, "organization_id", None))
    
    return customer

@router.post("", response_model=CustomerInDB)
async def create_customer(
    customer: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create new customer"""
    
    org_id = current_user.organization_id
    if org_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User must belong to an organization to create customers")
    
    # Check if customer name already exists in organization
    existing_customer = db.query(Customer).filter(
        Customer.name == customer.name,
        Customer.organization_id == org_id
    ).first()
    if existing_customer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Customer with this name already exists in organization"
        )
    
    # Create new customer
    db_customer = Customer(
        organization_id=org_id,
        **customer.dict()
    )
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    
    logger.info(f"Customer {customer.name} created in org {org_id} by {current_user.email}")
    return db_customer

@router.put("/{customer_id}", response_model=CustomerInDB)
async def update_customer(
    customer_id: int,
    customer_update: CustomerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update customer"""
    
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    # Ensure tenant access for non-super-admin users
    if not bool(current_user.is_super_admin):
        TenantQueryMixin.ensure_tenant_access(customer, getattr(customer, "organization_id", None))
    
    # Check name uniqueness if being updated
    if customer_update.name and customer_update.name != customer.name:
        existing_customer = db.query(Customer).filter(
            Customer.name == customer_update.name,
            Customer.organization_id == customer.organization_id
        ).first()
        if existing_customer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Customer with this name already exists in organization"
            )
    
    # Update customer
    for field, value in customer_update.dict(exclude_unset=True).items():
        setattr(customer, field, value)
    
    db.commit()
    db.refresh(customer)
    
    logger.info(f"Customer {customer.name} updated by {current_user.email}")
    return customer

@router.delete("/{customer_id}")
async def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Delete customer (admin only)"""
    
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    # Ensure tenant access for non-super-admin users
    if not bool(current_user.is_super_admin):
        TenantQueryMixin.ensure_tenant_access(customer, getattr(customer, "organization_id", None))
    
    # TODO: Check if customer has any associated transactions/vouchers
    # before allowing deletion
    
    db.delete(customer)
    db.commit()
    
    logger.info(f"Customer {customer.name} deleted by {current_user.email}")
    return {"message": "Customer deleted successfully"}

# Excel Import/Export/Template endpoints

@router.get("/template/excel")
async def download_customers_template(
    current_user: User = Depends(get_current_active_user)
):
    """Download Excel template for customers bulk import"""
    excel_data = CustomerExcelService.create_template()
    return ExcelService.create_streaming_response(excel_data, "customers_template.xlsx")

@router.get("/export/excel")
async def export_customers_excel(
    skip: int = 0,
    limit: int = 1000,
    search: Optional[str] = None,
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Export customers to Excel"""
    
    # Get customers using the same logic as the list endpoint
    query = db.query(Customer)
    
    # Apply tenant filtering for non-super-admin users
    if not bool(current_user.is_super_admin):
        org_id = current_user.organization_id
        if org_id is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User must belong to an organization")
        query = TenantQueryMixin.filter_by_tenant(query, org_id)
    
    if active_only:
        query = query.filter(Customer.is_active == True)
    
    if search:
        search_filter = (
            Customer.name.contains(search) |
            Customer.contact_number.contains(search) |
            Customer.email.contains(search)
        )
        query = query.filter(search_filter)
    
    customers = query.offset(skip).limit(limit).all()
    
    # Convert to dict format for Excel export
    customers_data = []
    for customer in customers:
        customers_data.append({
            "name": customer.name,
            "contact_number": customer.contact_number,
            "email": customer.email or "",
            "address1": customer.address1,
            "address2": customer.address2 or "",
            "city": customer.city,
            "state": customer.state,
            "pin_code": customer.pin_code,
            "state_code": customer.state_code,
            "gst_number": customer.gst_number or "",
            "pan_number": customer.pan_number or "",
        })
    
    excel_data = CustomerExcelService.export_customers(customers_data)
    return ExcelService.create_streaming_response(excel_data, "customers_export.xlsx")

@router.post("/import/excel", response_model=BulkImportResponse)
async def import_customers_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Import customers from Excel file"""
    
    org_id = current_user.organization_id
    if org_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User must belong to an organization to import customers")
    
    # Validate file type
    if not file.filename or not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only Excel files (.xlsx, .xls) are allowed"
        )
    
    try:
        # Parse Excel file
        records = await ExcelService.parse_excel_file(file, CustomerExcelService.REQUIRED_COLUMNS, "Customer Import Template")
        
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
                # Map Excel columns to model fields (using normalized column names)
                customer_data = {
                    "name": str(record.get("name", "")).strip(),
                    "contact_number": str(record.get("contact_number", "")).strip(),
                    "email": str(record.get("email", "")).strip() or None,
                    "address1": str(record.get("address_line_1", "")).strip(),
                    "address2": str(record.get("address_line_2", "")).strip() or None,
                    "city": str(record.get("city", "")).strip(),
                    "state": str(record.get("state", "")).strip(),
                    "pin_code": str(record.get("pin_code", "")).strip(),
                    "state_code": str(record.get("state_code", "")).strip(),
                    "gst_number": str(record.get("gst_number", "")).strip() or None,
                    "pan_number": str(record.get("pan_number", "")).strip() or None,
                }
                
                # Validate required fields
                required_fields = ["name", "contact_number", "address1", "city", "state", "pin_code", "state_code"]
                for field in required_fields:
                    if not customer_data[field]:
                        errors.append(f"Row {i}: {field.replace('_', ' ').title()} is required")
                        continue
                
                if errors and errors[-1].startswith(f"Row {i}:"):
                    continue
                
                # Check if customer already exists
                existing_customer = db.query(Customer).filter(
                    Customer.name == customer_data["name"],
                    Customer.organization_id == org_id
                ).first()
                
                if existing_customer:
                    # Update existing customer
                    for field, value in customer_data.items():
                        setattr(existing_customer, field, value)
                    updated_count += 1
                    logger.info(f"Updated customer: {customer_data['name']}")
                else:
                    # Create new customer
                    new_customer = Customer(
                        organization_id=org_id,
                        **customer_data
                    )
                    db.add(new_customer)
                    created_count += 1
                    logger.info(f"Created customer: {customer_data['name']}")
                    
            except Exception as e:
                errors.append(f"Row {i}: Error processing record - {str(e)}")
                continue
        
        # Commit all changes
        db.commit()
        
        logger.info(f"Customers import completed by {current_user.email}: "
                   f"{created_count} created, {updated_count} updated, {len(errors)} errors")
        
        return BulkImportResponse(
            message=f"Import completed successfully. {created_count} customers created, {updated_count} updated.",
            total_processed=len(records),
            created=created_count,
            updated=updated_count,
            errors=errors
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error importing customers: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing import: {str(e)}"
        )

# File upload directory
UPLOAD_DIR = "uploads/customers"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/{customer_id}/files", response_model=CustomerFileResponse)
async def upload_customer_file(
    customer_id: int,
    file: UploadFile = File(...),
    file_type: str = "general",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Upload a file for a customer (GST certificate, PAN card, etc.)"""
    
    from app.core.org_restrictions import ensure_organization_context
    org_id = ensure_organization_context(current_user)
    
    # Verify customer exists and belongs to current organization
    customer = db.query(Customer).filter(
        Customer.id == customer_id,
        Customer.organization_id == org_id
    ).first()
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    # Check file count limit (max 10 files per customer)
    existing_files_count = db.query(CustomerFile).filter(
        CustomerFile.customer_id == customer_id,
        CustomerFile.organization_id == org_id
    ).count()
    
    if existing_files_count >= 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 10 files allowed per customer"
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
    
    try:
        # Save file to disk
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Create database record
        db_file = CustomerFile(
            customer_id=customer_id,
            organization_id=org_id,
            filename=unique_filename,
            original_filename=file.filename or "unknown",
            file_path=file_path,
            file_size=file.size or 0,
            content_type=file.content_type or "application/octet-stream",
            file_type=file_type
        )
        db.add(db_file)
        db.commit()
        db.refresh(db_file)
        
        logger.info(f"Customer file uploaded: {db_file.original_filename} for customer {customer_id}")
        
        return CustomerFileResponse(
            id=db_file.id,
            filename=db_file.filename,
            original_filename=db_file.original_filename,
            file_size=db_file.file_size,
            content_type=db_file.content_type,
            file_type=db_file.file_type,
            customer_id=db_file.customer_id,
            created_at=db_file.created_at
        )
        
    except Exception as e:
        # Clean up file if database operation fails
        if os.path.exists(file_path):
            os.remove(file_path)
        logger.error(f"Error uploading customer file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error uploading file"
        )

@router.get("/{customer_id}/files", response_model=List[CustomerFileResponse])
async def get_customer_files(
    customer_id: int,
    file_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all files for a customer, optionally filtered by file type"""
    
    from app.core.org_restrictions import ensure_organization_context
    org_id = ensure_organization_context(current_user)
    
    # Verify customer exists and belongs to current organization
    customer = db.query(Customer).filter(
        Customer.id == customer_id,
        Customer.organization_id == org_id
    ).first()
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    query = db.query(CustomerFile).filter(
        CustomerFile.customer_id == customer_id,
        CustomerFile.organization_id == org_id
    )
    
    if file_type:
        query = query.filter(CustomerFile.file_type == file_type)
    
    files = query.all()
    
    return [
        CustomerFileResponse(
            id=f.id,
            filename=f.filename,
            original_filename=f.original_filename,
            file_size=f.file_size,
            content_type=f.content_type,
            file_type=f.file_type,
            customer_id=f.customer_id,
            created_at=f.created_at
        ) for f in files
    ]

@router.get("/{customer_id}/files/{file_id}/download")
async def download_customer_file(
    customer_id: int,
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Download a customer file"""
    
    from app.core.org_restrictions import ensure_organization_context
    org_id = ensure_organization_context(current_user)
    
    # Get file record
    file_record = db.query(CustomerFile).filter(
        CustomerFile.id == file_id,
        CustomerFile.customer_id == customer_id,
        CustomerFile.organization_id == org_id
    ).first()
    
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

@router.delete("/{customer_id}/files/{file_id}")
async def delete_customer_file(
    customer_id: int,
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a customer file"""
    
    from app.core.org_restrictions import ensure_organization_context
    org_id = ensure_organization_context(current_user)
    
    # Get file record
    file_record = db.query(CustomerFile).filter(
        CustomerFile.id == file_id,
        CustomerFile.customer_id == customer_id,
        CustomerFile.organization_id == org_id
    ).first()
    
    if not file_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    try:
        # Remove file from disk
        if os.path.exists(file_record.file_path):
            os.remove(file_record.file_path)
        
        # Remove database record
        db.delete(file_record)
        db.commit()
        
        return {"message": "File deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting customer file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting file"
        )