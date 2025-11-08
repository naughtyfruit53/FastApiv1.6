# Revised: app/api/v1/customers.py

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from typing import List, Optional
from app.core.database import get_db
from app.core.enforcement import require_access
from app.models import User, Customer, CustomerFile
from app.schemas.base import CustomerCreate, CustomerUpdate, CustomerInDB, BulkImportResponse, CustomerFileResponse
from app.services.excel_service import CustomerExcelService, ExcelService
from app.services.rbac import RBACService

# NEW: Import for entitlement check
from app.api.deps.entitlements import require_permission_with_entitlement

import logging
import os
import uuid
import shutil

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("", response_model=List[CustomerInDB])
async def get_customers(
    skip: int = 0,
    limit: int = 1000000,
    search: Optional[str] = None,
    active_only: bool = True,
    company_id: Optional[int] = Query(None, description="Filter by specific company (if user has access)"),
    # CHANGED: Use entitlement with submodule
    auth: tuple = Depends(require_permission_with_entitlement("erp", "customers.read", "customers")),
    db: AsyncSession = Depends(get_db)
):
    """Get customers with company scoping"""
    
    current_user, org_id = auth
    rbac = RBACService(db)
    
    # Get user's accessible companies
    user_companies = await rbac.get_user_companies(current_user.id)
    
    # Build base query with company filtering
    if company_id is not None:
        # User requested specific company - verify access
        if company_id not in user_companies:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: User does not have access to the specified company"
            )
        # Filter by specific company
        stmt = select(Customer).where(
            and_(
                Customer.organization_id == org_id,
                Customer.company_id == company_id
            )
        )
    elif user_companies:
        # Filter by user's accessible companies (including org-level customers with company_id=None)
        stmt = select(Customer).where(
            and_(
                Customer.organization_id == org_id,
                or_(
                    Customer.company_id.in_(user_companies),
                    Customer.company_id.is_(None)  # Include org-level customers
                )
            )
        )
    else:
        # User has no company access, only show org-level customers
        stmt = select(Customer).where(
            and_(
                Customer.organization_id == org_id,
                Customer.company_id.is_(None)
            )
        )
    
    if active_only:
        stmt = stmt.where(Customer.is_active == True)
    
    if search:
        search_filter = or_(
            Customer.name.contains(search),
            Customer.contact_number.contains(search),
            Customer.email.contains(search)
        )
        stmt = stmt.where(search_filter)
    
    result = await db.execute(stmt.offset(skip).limit(limit))
    customers = result.scalars().all()
    return customers

@router.get("/{customer_id}", response_model=CustomerInDB)
async def get_customer(
    customer_id: int,
    # CHANGED: Use entitlement with submodule
    auth: tuple = Depends(require_permission_with_entitlement("erp", "customers.read", "customers")),
    db: AsyncSession = Depends(get_db)
):
    """Get customer by ID with organization validation"""
    current_user, org_id = auth
    
    stmt = select(Customer).where(
        Customer.id == customer_id,
        Customer.organization_id == org_id
    )
    result = await db.execute(stmt)
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    return customer

@router.post("", response_model=CustomerInDB)
async def create_customer(
    customer: CustomerCreate,
    # CHANGED: Use entitlement with submodule
    auth: tuple = Depends(require_permission_with_entitlement("erp", "customers.create", "customers")),
    db: AsyncSession = Depends(get_db)
):
    """Create new customer with company scoping"""
    
    current_user, org_id = auth
    rbac = RBACService(db)
    
    # If company_id is provided, verify user has access to it
    if customer.company_id:
        await rbac.enforce_company_access(current_user.id, customer.company_id, "customer_create")
    else:
        # If no company_id provided, auto-assign to user's first company if they have access to only one
        user_companies = await rbac.get_user_companies(current_user.id)
        if len(user_companies) == 1:
            customer.company_id = user_companies[0]
        elif len(user_companies) > 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="company_id is required when user has access to multiple companies"
            )
        # If user has no companies, allow creating organization-level customer (company_id=None)
    
    # Check if customer name already exists in organization/company scope
    stmt = select(Customer).where(
        Customer.name == customer.name,
        Customer.organization_id == org_id
    )
    if customer.company_id:
        stmt = stmt.where(Customer.company_id == customer.company_id)
    result = await db.execute(stmt)
    existing_customer = result.scalar_one_or_none()
    if existing_customer:
        scope_text = f"company {customer.company_id}" if customer.company_id else "organization"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Customer with this name already exists in {scope_text}"
        )
    
    # Create new customer
    customer_data = customer.dict()
    
    # Auto-assign default receivable account if not provided
    if not customer_data.get('receivable_account_id'):
        from app.models.erp_models import ChartOfAccounts
        default_receivable_stmt = select(ChartOfAccounts).where(
            and_(
                ChartOfAccounts.organization_id == org_id,
                ChartOfAccounts.account_code == '1120',  # Accounts Receivable
                ChartOfAccounts.is_active == True
            )
        )
        default_receivable_result = await db.execute(default_receivable_stmt)
        default_receivable = default_receivable_result.scalar_one_or_none()
        if default_receivable:
            customer_data['receivable_account_id'] = default_receivable.id
            logger.info(f"Auto-assigned receivable account {default_receivable.account_name} to customer")
    
    db_customer = Customer(
        organization_id=org_id,
        **customer_data
    )
    db.add(db_customer)
    await db.commit()
    await db.refresh(db_customer)
    
    company_text = f" in company {customer.company_id}" if customer.company_id else ""
    logger.info(f"Customer {customer.name} created in org {org_id}{company_text} by {current_user.email}")
    return db_customer

@router.put("/{customer_id}", response_model=CustomerInDB)
async def update_customer(
    customer_id: int,
    customer_update: CustomerUpdate,
    # CHANGED: Use entitlement with submodule
    auth: tuple = Depends(require_permission_with_entitlement("erp", "customers.update", "customers")),
    db: AsyncSession = Depends(get_db)
):
    """Update customer"""
    
    current_user, org_id = auth
    
    stmt = select(Customer).where(
        Customer.id == customer_id,
        Customer.organization_id == org_id
    )
    result = await db.execute(stmt)
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    # Check name uniqueness if being updated
    if customer_update.name and customer_update.name != customer.name:
        stmt = select(Customer).where(
            Customer.name == customer_update.name,
            Customer.organization_id == customer.organization_id
        )
        result = await db.execute(stmt)
        existing_customer = result.scalar_one_or_none()
        if existing_customer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Customer with this name already exists in organization"
            )
    
    # Update customer
    for field, value in customer_update.dict(exclude_unset=True).items():
        setattr(customer, field, value)
    
    await db.commit()
    await db.refresh(customer)
    
    logger.info(f"Customer {customer.name} updated by {current_user.email}")
    return customer

@router.delete("/{customer_id}")
async def delete_customer(
    customer_id: int,
    # CHANGED: Use entitlement with submodule
    auth: tuple = Depends(require_permission_with_entitlement("erp", "customers.delete", "customers")),
    db: AsyncSession = Depends(get_db)
):
    """Delete customer"""
    
    current_user, org_id = auth
    
    stmt = select(Customer).where(
        Customer.id == customer_id,
        Customer.organization_id == org_id
    )
    result = await db.execute(stmt)
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    # TODO: Check if customer has any associated transactions/vouchers
    # before allowing deletion
    
    await db.delete(customer)
    await db.commit()
    
    logger.info(f"Customer {customer.name} deleted by {current_user.email}")
    return {"message": "Customer deleted successfully"}

# Excel Import/Export/Template endpoints

@router.get("/template/excel")
async def download_customers_template(
    # CHANGED: Use entitlement with submodule
    auth: tuple = Depends(require_permission_with_entitlement("erp", "customers.read", "customers"))
):
    """Download Excel template for customers bulk import"""
    current_user, org_id = auth
    excel_data = CustomerExcelService.create_template()
    return ExcelService.create_streaming_response(excel_data, "customers_template.xlsx")

@router.get("/export/excel")
async def export_customers_excel(
    skip: int = 0,
    limit: int = 1000,
    search: Optional[str] = None,
    active_only: bool = True,
    # CHANGED: Use entitlement with submodule
    auth: tuple = Depends(require_permission_with_entitlement("erp", "customers.read", "customers")),
    db: AsyncSession = Depends(get_db)
):
    """Export customers to Excel"""
    
    current_user, org_id = auth
    
    # Get customers using the same logic as the list endpoint
    stmt = select(Customer).where(Customer.organization_id == org_id)
    
    if active_only:
        stmt = stmt.where(Customer.is_active == True)
    
    if search:
        search_filter = or_(
            Customer.name.contains(search),
            Customer.contact_number.contains(search),
            Customer.email.contains(search)
        )
        stmt = stmt.where(search_filter)
    
    result = await db.execute(stmt.offset(skip).limit(limit))
    customers = result.scalars().all()
    
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
    # CHANGED: Use entitlement with submodule
    auth: tuple = Depends(require_permission_with_entitlement("erp", "customers.create", "customers")),
    db: AsyncSession = Depends(get_db)
):
    """Import customers from Excel file"""
    
    current_user, org_id = auth
    
    # Validate file type
    if not file.filename or not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only Excel files (.xlsx, .xls) are allowed"
        )
    
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
                    break
            
            if errors and errors[-1].startswith(f"Row {i}:"):
                continue
            
            # Check if customer already exists
            stmt = select(Customer).where(
                Customer.name == customer_data["name"],
                Customer.organization_id == org_id
            )
            result = await db.execute(stmt)
            existing_customer = result.scalar_one_or_none()
            
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
    
    await db.commit()
    
    logger.info(f"Customers import completed by {current_user.email}: "
               f"{created_count} created, {updated_count} updated, {len(errors)} errors")
    
    return BulkImportResponse(
        message=f"Import completed successfully. {created_count} customers created, {updated_count} updated.",
        total_processed=len(records),
        created=created_count,
        updated=updated_count,
        errors=errors
    )

# File upload directory
UPLOAD_DIR = "uploads/customers"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/{customer_id}/files", response_model=CustomerFileResponse)
async def upload_customer_file(
    customer_id: int,
    file: UploadFile = File(...),
    file_type: str = "general",
    # CHANGED: Use entitlement with submodule
    auth: tuple = Depends(require_permission_with_entitlement("erp", "customers.update", "customers")),
    db: AsyncSession = Depends(get_db)
):
    """Upload a file for a customer (GST certificate, PAN card, etc.)"""
    
    current_user, org_id = auth
    
    # Verify customer exists and belongs to current organization
    stmt = select(Customer).where(
        Customer.id == customer_id,
        Customer.organization_id == org_id
    )
    result = await db.execute(stmt)
    customer = result.scalar_one_or_none()
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    # Check file count limit (max 10 files per customer)
    stmt = select(CustomerFile).where(
        CustomerFile.customer_id == customer_id,
        CustomerFile.organization_id == org_id
    )
    result = await db.execute(stmt)
    existing_files_count = len(result.scalars().all())
    
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
    await db.commit()
    await db.refresh(db_file)
    
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

@router.get("/{customer_id}/files", response_model=List[CustomerFileResponse])
async def get_customer_files(
    customer_id: int,
    file_type: Optional[str] = None,
    # CHANGED: Use entitlement with submodule
    auth: tuple = Depends(require_permission_with_entitlement("erp", "customers.read", "customers")),
    db: AsyncSession = Depends(get_db)
):
    """Get all files for a customer, optionally filtered by file type"""
    
    current_user, org_id = auth
    
    # Verify customer exists and belongs to current organization
    stmt = select(Customer).where(
        Customer.id == customer_id,
        Customer.organization_id == org_id
    )
    result = await db.execute(stmt)
    customer = result.scalar_one_or_none()
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    stmt = select(CustomerFile).where(
        CustomerFile.customer_id == customer_id,
        CustomerFile.organization_id == org_id
    )
    
    if file_type:
        stmt = stmt.where(CustomerFile.file_type == file_type)
    
    result = await db.execute(stmt)
    files = result.scalars().all()
    
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
    # CHANGED: Use entitlement with submodule
    auth: tuple = Depends(require_permission_with_entitlement("erp", "customers.read", "customers")),
    db: AsyncSession = Depends(get_db)
):
    """Download a customer file"""
    
    current_user, org_id = auth
    
    # Get file record
    stmt = select(CustomerFile).where(
        CustomerFile.id == file_id,
        CustomerFile.customer_id == customer_id,
        CustomerFile.organization_id == org_id
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

@router.delete("/{customer_id}/files/{file_id}")
async def delete_customer_file(
    customer_id: int,
    file_id: int,
    # CHANGED: Use entitlement with submodule
    auth: tuple = Depends(require_permission_with_entitlement("erp", "customers.delete", "customers")),
    db: AsyncSession = Depends(get_db)
):
    """Delete a customer file"""
    
    current_user, org_id = auth
    
    # Get file record
    stmt = select(CustomerFile).where(
        CustomerFile.id == file_id,
        CustomerFile.customer_id == customer_id,
        CustomerFile.organization_id == org_id
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