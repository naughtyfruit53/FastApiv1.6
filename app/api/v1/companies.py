# app/api/v1/companies.py

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from datetime import datetime
from app.core.database import get_db
from app.core.enforcement import require_access
from app.models import User, Company, Organization
from app.models.user_models import UserCompany
from app.schemas.company import CompanyCreate, CompanyUpdate, CompanyInDB, CompanyResponse, CompanyErrorResponse, UserCompanyAssignmentCreate, UserCompanyAssignmentUpdate, UserCompanyAssignmentInDB
from app.schemas.base import BulkImportResponse
from app.services.excel_service import CompanyExcelService, ExcelService
import logging
import os
import uuid
import shutil
from app.api.v1.auth import get_current_active_user
from sqlalchemy.exc import IntegrityError

logger = logging.getLogger(__name__)
router = APIRouter()

# Logo upload directory
LOGO_UPLOAD_DIR = "uploads/company_logos"
os.makedirs(LOGO_UPLOAD_DIR, exist_ok=True)

@router.get("", response_model=List[CompanyInDB])
async def get_companies(
    auth: tuple = Depends(require_access("company", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get companies in current organization"""
    
    # Restrict app super admins from accessing organization data
    current_user, org_id = auth
    
    stmt = select(Company)
    stmt = stmt.where(Company.organization_id == org_id)
    
    result = await db.execute(stmt)
    companies = result.scalars().all()
    
    return companies

@router.get("/current", response_model=CompanyInDB)
async def get_current_company(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current organization's company details"""
    
    # Enhanced logging for debugging session issues
    logger.info(f"[/companies/current] Request from user: {current_user.id} ({current_user.email})")
    logger.info(f"[/companies/current] User context: role={current_user.role}, is_super_admin={current_user.is_super_admin}, org_id={current_user.organization_id}")
    
    org_id = current_user.organization_id
    
    try:
        # For super admins, return a placeholder empty company (no org context post-reset)
        if current_user.is_super_admin and org_id is None:
            logger.info(f"[/companies/current] Super admin access without organization context - returning placeholder")
            return CompanyInDB(
                id=0,
                name="Global Super Admin",
                organization_id=0,
                address1="Super Admin Address",
                address2=None,
                city="Global",
                state="Global",
                pin_code="123456",
                state_code="00",
                contact_number="0000000000",
                email=None,
                gst_number=None,
                pan_number=None,
                business_type=None,
                industry=None,
                website=None,
                logo_path=None,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        
        # For organization users, ensure organization context
        logger.info(f"[/companies/current] Organization context established: org_id={org_id}")
        
        stmt = select(Company).where(Company.organization_id == org_id)
        result = await db.execute(stmt)
        company = result.scalar_one_or_none()
        
        if not company:
            logger.warning(f"[/companies/current] Company not found for org_id={org_id}, user={current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Company details not found for organization {org_id}. Please set up company information."
            )
        
        logger.info(f"[/companies/current] Company found: id={company.id}, name={company.name}")
        return company
        
    except HTTPException as e:
        logger.error(f"[/companies/current] HTTP error for user {current_user.id}: {e.status_code} - {e.detail}")
        raise
    except Exception as e:
        logger.error(f"[/companies/current] Unexpected error for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while retrieving company information"
        )

@router.get("/{company_id}", response_model=CompanyInDB)
async def get_company(
    company_id: int,
    auth: tuple = Depends(require_access("company", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get company by ID"""
    
    stmt = select(Company).where(Company.id == company_id)
    result = await db.execute(stmt)
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    return company

@router.post("", response_model=CompanyResponse)
async def create_company(
    company: CompanyCreate,
    auth: tuple = Depends(require_access("company", "create")),
    db: AsyncSession = Depends(get_db)
):
    """Create company details for current organization with enhanced validation"""
    
    try:
        # Validate and set organization_id in data
        current_user, org_id = auth
        data = company.model_dump()
        data['organization_id'] = org_id
        
        # Get organization to check limits
        stmt = select(Organization).where(Organization.id == data['organization_id'])
        result = await db.execute(stmt)
        org = result.scalar_one_or_none()
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )
        
        # Check company count against max_companies limit
        stmt = select(func.count(Company.id)).where(Company.organization_id == data['organization_id'])
        result = await db.execute(stmt)
        existing_companies_count = result.scalar_one()
        if existing_companies_count >= org.max_companies:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Maximum number of companies ({org.max_companies}) already reached for this organization."
            )
        
        # Check if company name already exists for this organization
        stmt = select(Company).where(
            Company.organization_id == data['organization_id'],
            Company.name == data['name']
        )
        result = await db.execute(stmt)
        existing_company = result.scalar_one_or_none()
        if existing_company:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Company with this name already exists in your organization."
            )
        
        db_company = Company(**data)
        db.add(db_company)
        
        # Mark organization as having completed company details if first company
        if existing_companies_count == 0:
            org.company_details_completed = True
        
        await db.commit()
        await db.refresh(db_company)
        
        logger.info(f"Company {company.name} created for org {data['organization_id']} by {current_user.email}")
        return db_company
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating company: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create company. Please try again."
        )

@router.put("/{company_id}", response_model=CompanyResponse)
async def update_company(
    company_id: int,
    company_update: CompanyUpdate,
    auth: tuple = Depends(require_access("company", "update")),
    db: AsyncSession = Depends(get_db)
):
    """Update company details with enhanced validation"""
    
    current_user, org_id = auth  # Unpack auth to define current_user and org_id
    
    stmt = select(Company).where(Company.id == company_id)
    result = await db.execute(stmt)
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    try:
        for field, value in company_update.model_dump(exclude_unset=True).items():
            setattr(company, field, value)
        
        await db.commit()
        await db.refresh(company)
        
        logger.info(f"Company {company.name} updated by {current_user.email}")
        return company
        
    except IntegrityError as e:
        await db.rollback()
        logger.error(f"Integrity error updating company: {str(e.orig)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Required field cannot be empty or invalid data provided."
        )
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating company: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update company. Please try again."
        )

@router.delete("/{company_id}")
async def delete_company(
    company_id: int,
    auth: tuple = Depends(require_access("company", "delete")),
    db: AsyncSession = Depends(get_db)
):
    """Delete company (admin only)"""
    
    current_user, org_id = auth  # Unpack auth to define current_user and org_id
    
    stmt = select(Company).where(Company.id == company_id)
    result = await db.execute(stmt)
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    await db.delete(company)
    await db.commit()
    
    logger.info(f"Company {company.name} deleted by {current_user.email}")
    return {"message": "Company deleted successfully"}

# Excel Import/Export/Template endpoints

@router.get("/template/excel")
async def download_companies_template(
    auth: tuple = Depends(require_access("company", "read"))
):
    """Download Excel template for companies bulk import"""
    current_user, org_id = auth
    
    try:
        excel_data = CompanyExcelService.create_template()
        logger.info("Company template downloaded successfully")
        return ExcelService.create_streaming_response(excel_data, "companies_template.xlsx")
    except Exception as e:
        logger.error(f"Error generating company template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate company template. Please try again later."
        )

@router.get("/export/excel")
async def export_companies_excel(
    skip: int = 0,
    limit: int = 1000,
    auth: tuple = Depends(require_access("company", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Export companies to Excel"""
    current_user, org_id = auth
    
    skip = max(0, skip)  # Ensure non-negative skip
    limit = min(1000, max(1, limit))  # Limit between 1 and 1000
    
    # Get companies using the same logic as the list endpoint
    stmt = select(Company).offset(skip).limit(limit)
    stmt = stmt.where(Company.organization_id == org_id)
    
    result = await db.execute(stmt)
    companies = result.scalars().all()
    
    # Convert to dict format for Excel export
    companies_data = []
    for company in companies:
        companies_data.append({
            "name": company.name,
            "address1": company.address1,
            "address2": company.address2 or "",
            "city": company.city,
            "state": company.state,
            "pin_code": company.pin_code,
            "state_code": company.state_code,
            "contact_number": company.contact_number,
            "email": company.email or "",
            "gst_number": company.gst_number or "",
            "pan_number": company.pan_number or "",
            "business_type": company.business_type or "",
            "industry": company.industry or "",
            "website": company.website or "",
        })
    
    excel_data = CompanyExcelService.export_companies(companies_data)
    return ExcelService.create_streaming_response(excel_data, "companies_export.xlsx")

@router.post("/import/excel", response_model=BulkImportResponse)
async def import_companies_excel(
    file: UploadFile = File(...),
    auth: tuple = Depends(require_access("company", "create")),
    db: AsyncSession = Depends(get_db)
):
    """Import companies from Excel file"""
    current_user, org_id = auth
    
    # Validate file type
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only Excel files (.xlsx, .xls) are allowed"
        )
    
    try:
        # Parse Excel file
        records = await ExcelService.parse_excel_file(file, CompanyExcelService.REQUIRED_COLUMNS, "Company Import Template")
        
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
                company_data = {
                    "name": str(record.get("name", "")).strip(),
                    "address1": str(record.get("address_line_1", "")).strip(),
                    "address2": str(record.get("address_line_2", "")).strip() or None,
                    "city": str(record.get("city", "")).strip(),
                    "state": str(record.get("state", "")).strip(),
                    "pin_code": str(record.get("pin_code", "")).strip(),
                    "state_code": str(record.get("state_code", "")).strip(),
                    "contact_number": str(record.get("contact_number", "")).strip(),
                    "email": str(record.get("email", "")).strip() or None,
                    "gst_number": str(record.get("gst_number", "")).strip() or None,
                    "pan_number": str(record.get("pan_number", "")).strip() or None,
                    "registration_number": str(record.get("registration_number", "")).strip() or None,
                    "business_type": str(record.get("business_type", "")).strip() or None,
                    "industry": str(record.get("industry", "")).strip() or None,
                    "website": str(record.get("website", "")).strip() or None,
                }
                
                # Validate required fields
                required_fields = ["name", "address1", "city", "state", "pin_code", "state_code", "contact_number"]
                for field in required_fields:
                    if not company_data[field]:
                        errors.append(f"Row {i}: {field.replace('_', ' ').title()} is required")
                        continue
                
                if errors and errors[-1].startswith(f"Row {i}:"):
                    continue
                
                # Check if company already exists for this organization
                stmt = select(Company).where(
                    Company.name == company_data["name"],
                    Company.organization_id == org_id
                )
                result = await db.execute(stmt)
                existing_company = result.scalar_one_or_none()
                
                if existing_company:
                    # Update existing company
                    for field, value in company_data.items():
                        setattr(existing_company, field, value)
                    updated_count += 1
                    logger.info(f"Updated company: {company_data['name']}")
                else:
                    # Create new company
                    new_company = Company(
                        organization_id=org_id,
                        **company_data
                    )
                    db.add(new_company)
                    created_count += 1
                    logger.info(f"Created company: {company_data['name']}")
                    
                    # Mark organization as having completed company details if this is the first company
                    if created_count == 1:
                        stmt = select(Organization).where(Organization.id == org_id)
                        result = await db.execute(stmt)
                        org = result.scalar_one_or_none()
                        if org:
                            org.company_details_completed = True
                    
            except Exception as e:
                errors.append(f"Row {i}: Error processing record - {str(e)}")
                continue
        
        # Commit all changes
        await db.commit()
        
        logger.info(f"Companies import completed by {current_user.email}: "
                   f"{created_count} created, {updated_count} updated, {len(errors)} errors")
        
        return BulkImportResponse(
            message=f"Import completed successfully. {created_count} companies created, {updated_count} updated.",
            total_processed=len(records),
            created=created_count,
            updated=created_count,
            errors=errors
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error importing companies: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing import: {str(e)}"
        )

# User-Company Assignment Endpoints

@router.get("/{company_id}/users", response_model=List[UserCompanyAssignmentInDB])
async def get_company_users(
    company_id: int,
    auth: tuple = Depends(require_access("company", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get users assigned to a specific company"""
    current_user, org_id = auth
    
    # Check company exists and belongs to current user's org
    stmt = select(Company).where(
        Company.id == company_id,
        Company.organization_id == org_id
    )
    result = await db.execute(stmt)
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Get user assignments for this company
    stmt = select(UserCompany).where(
        UserCompany.company_id == company_id,
        UserCompany.is_active == True
    )
    result = await db.execute(stmt)
    assignments = result.scalars().all()
    
    # Enrich with user and company data
    result_list = []
    for assignment in assignments:
        stmt_user = select(User).where(User.id == assignment.user_id)
        result_user = await db.execute(stmt_user)
        user = result_user.scalar_one_or_none()
        assignment_dict = {
            "id": assignment.id,
            "user_id": assignment.user_id,
            "company_id": assignment.company_id,
            "organization_id": assignment.organization_id,
            "assigned_by_id": assignment.assigned_by_id,
            "is_active": assignment.is_active,
            "is_company_admin": assignment.is_company_admin,
            "assigned_at": assignment.assigned_at,
            "created_at": assignment.created_at,
            "updated_at": assignment.updated_at,
            "user_email": user.email if user else None,
            "user_full_name": user.full_name if user else None,
            "company_name": company.name
        }
        result_list.append(assignment_dict)
    
    return result_list

@router.post("/{company_id}/users", response_model=UserCompanyAssignmentInDB)
async def assign_user_to_company(
    company_id: int,
    assignment: UserCompanyAssignmentCreate,
    auth: tuple = Depends(require_access("company", "update")),
    db: AsyncSession = Depends(get_db)
):
    """Assign a user to a company (org admin only)"""
    current_user, org_id = auth
    
    # Check company exists and belongs to current user's org
    stmt = select(Company).where(
        Company.id == company_id,
        Company.organization_id == org_id
    )
    result = await db.execute(stmt)
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Check user exists and belongs to same organization
    stmt = select(User).where(User.id == assignment.user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.organization_id != company.organization_id:
        raise HTTPException(status_code=400, detail="User and company must be in the same organization")
    
    # Check if assignment already exists
    stmt = select(UserCompany).where(
        UserCompany.user_id == assignment.user_id,
        UserCompany.company_id == company_id
    )
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()
    
    if existing:
        if existing.is_active:
            raise HTTPException(status_code=400, detail="User is already assigned to this company")
        else:
            # Reactivate existing assignment
            existing.is_active = True
            existing.is_company_admin = assignment.is_company_admin
            existing.assigned_by_id = current_user.id
            existing.assigned_at = datetime.utcnow()
            await db.commit()
            await db.refresh(existing)
            return existing
    
    # Create new assignment
    new_assignment = UserCompany(
        user_id=assignment.user_id,
        company_id=company_id,
        organization_id=company.organization_id,
        assigned_by_id=current_user.id,
        is_company_admin=assignment.is_company_admin,
        is_active=True
    )
    
    db.add(new_assignment)
    await db.commit()
    await db.refresh(new_assignment)
    
    logger.info(f"User {user.email} assigned to company {company.name} by {current_user.email}")
    return new_assignment

@router.put("/{company_id}/users/{user_id}", response_model=UserCompanyAssignmentInDB)
async def update_user_company_assignment(
    company_id: int,
    user_id: int,
    update_data: UserCompanyAssignmentUpdate,
    auth: tuple = Depends(require_access("company", "update")),
    db: AsyncSession = Depends(get_db)
):
    """Update user-company assignment (org admin only)"""
    current_user, org_id = auth
    
    stmt = select(UserCompany).where(
        UserCompany.company_id == company_id,
        UserCompany.user_id == user_id,
        UserCompany.organization_id == org_id
    )
    result = await db.execute(stmt)
    assignment = result.scalar_one_or_none()
    
    if not assignment:
        raise HTTPException(status_code=404, detail="User-company assignment not found")
    
    # Update fields
    if update_data.is_active is not None:
        assignment.is_active = update_data.is_active
    if update_data.is_company_admin is not None:
        assignment.is_company_admin = update_data.is_company_admin
    
    await db.commit()
    await db.refresh(assignment)
    
    return assignment

@router.delete("/{company_id}/users/{user_id}")
async def remove_user_from_company(
    company_id: int,
    user_id: int,
    auth: tuple = Depends(require_access("company", "delete")),
    db: AsyncSession = Depends(get_db)
):
    """Remove user from company (org admin only)"""
    current_user, org_id = auth
    
    stmt = select(UserCompany).where(
        UserCompany.company_id == company_id,
        UserCompany.user_id == user_id,
        UserCompany.organization_id == org_id
    )
    result = await db.execute(stmt)
    assignment = result.scalar_one_or_none()
    
    if not assignment:
        raise HTTPException(status_code=404, detail="User-company assignment not found")
    
    # Soft delete - deactivate assignment
    assignment.is_active = False
    await db.commit()
    
    return {"message": "User removed from company successfully"}

@router.post("/{company_id}/logo")
async def upload_company_logo(
    company_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload or update company logo"""
    try:
        # First, get or create company
        stmt = select(Company).where(Company.id == company_id)
        result = await db.execute(stmt)
        company = result.scalar_one_or_none()
        
        if not company:
            # Create default company if not exists
            company = Company(
                id=company_id,
                organization_id=current_user.organization_id,
                name="Default Company",  # Placeholder, can be updated later
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(company)
            await db.commit()
            await db.refresh(company)
            logger.info(f"Created default company {company_id} for logo upload")
        
        # Validate file type
        file_extension = file.filename.split('.')[-1].lower()
        allowed_extensions = {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp', 'svg'}
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid image file type. Supported: {', '.join(allowed_extensions)}"
            )
        
        # Create upload directory if not exists
        upload_dir = "./uploads/company_logos"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        filename = f"logo_{company_id}_{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(upload_dir, filename)
        
        # Save file
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
        
        # Delete old logo if exists
        if company.logo_path:
            old_path = "." + company.logo_path
            if os.path.exists(old_path):
                os.remove(old_path)
                logger.info(f"Removed old logo: {old_path}")
        
        # Update company with new logo path
        company.logo_path = f"/uploads/company_logos/{filename}"
        company.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(company)
        
        logger.info(f"Logo uploaded successfully for company {company_id} by user {current_user.id}")
        
        return {"logo_path": company.logo_path}
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error uploading logo for company {company_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload logo. Please try again."
        )

logger.info("Companies router loaded")