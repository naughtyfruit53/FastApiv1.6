from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Response
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.system_models import Company
from app.models.user_models import User
from app.schemas.company import CompanyCreate, CompanyUpdate, CompanyInDB
from app.core.tenant import TenantQueryFilter
import logging
import os
import uuid

router = APIRouter(prefix="/companies", tags=["companies"])
logger = logging.getLogger(__name__)

@router.get("/current", response_model=CompanyInDB)
async def get_current_company(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        company = TenantQueryFilter.apply_organization_filter(
            db.query(Company), Company, current_user.organization_id
        ).first()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        return company
    except Exception as e:
        logger.error(f"Error fetching current company: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch company details")

@router.post("/", response_model=CompanyInDB)
async def create_company(
    company_data: CompanyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        existing_company = db.query(Company).filter(Company.organization_id == current_user.organization_id).first()
        if existing_company:
            raise HTTPException(status_code=400, detail="Company already exists for this organization")

        db_company = Company(**company_data.dict(), organization_id=current_user.organization_id)
        db.add(db_company)
        db.commit()
        db.refresh(db_company)
        return db_company
    except Exception as e:
        logger.error(f"Error creating company: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create company")

@router.put("/{company_id}", response_model=CompanyInDB)
async def update_company(
    company_id: int,
    update_data: CompanyUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        company = db.query(Company).filter(
            Company.id == company_id,
            Company.organization_id == current_user.organization_id
        ).first()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")

        update_dict = update_data.dict(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(company, key, value)

        db.commit()
        db.refresh(company)
        return company
    except Exception as e:
        logger.error(f"Error updating company: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update company")

@router.post("/{company_id}/logo")
async def upload_company_logo(
    company_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        company = db.query(Company).filter(
            Company.id == company_id,
            Company.organization_id == current_user.organization_id
        ).first()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")

        file_extension = file.filename.split('.')[-1].lower()
        allowed_extensions = {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp', 'svg'}
        if file_extension not in allowed_extensions:
            raise HTTPException(status_code=400, detail="Invalid image file type. Supported: jpg, jpeg, png, gif, bmp, tiff, webp, svg")

        upload_dir = "./uploads/company_logos"
        os.makedirs(upload_dir, exist_ok=True)

        filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(upload_dir, filename)

        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)

        # Delete old logo if exists
        if company.logo_path:
            old_path = "." + company.logo_path
            if os.path.exists(old_path):
                os.remove(old_path)

        company.logo_path = f"/uploads/company_logos/{filename}"
        db.commit()
        db.refresh(company)

        return {"logo_path": company.logo_path}
    except Exception as e:
        logger.error(f"Error uploading logo: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to upload logo")

@router.get("/{company_id}/logo")
async def get_company_logo(
    company_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        company = db.query(Company).filter(
            Company.id == company_id,
            Company.organization_id == current_user.organization_id
        ).first()
        if not company or not company.logo_path:
            raise HTTPException(status_code=404, detail="Logo not found")

        file_path = "." + company.logo_path
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Logo file not found")

        media_type = "image/" + company.logo_path.split('.')[-1].lower()
        return FileResponse(file_path, media_type=media_type)
    except Exception as e:
        logger.error(f"Error fetching logo: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch logo")

@router.delete("/{company_id}/logo")
async def delete_company_logo(
    company_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        company = db.query(Company).filter(
            Company.id == company_id,
            Company.organization_id == current_user.organization_id
        ).first()
        if not company or not company.logo_path:
            raise HTTPException(status_code=404, detail="Logo not found")

        file_path = "." + company.logo_path
        if os.path.exists(file_path):
            os.remove(file_path)

        company.logo_path = None
        db.commit()
        return {"message": "Logo deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting logo: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete logo")

@router.get("/branding")
async def get_company_branding(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get company branding information for PDF generation
    """
    try:
        # Get the user's company
        company = TenantQueryFilter.apply_organization_filter(
            db.query(Company), Company, current_user.organization_id
        ).first()

        if not company:
            # Return default branding if no company configured
            return {
                "name": "Your Company Name",
                "address": "Company Address",
                "contact_number": "Contact Number",
                "email": "company@email.com",
                "website": "www.yourcompany.com",
                "logo_path": None,
                "gstin": None
            }

        return {
            "name": company.name,
            "address": company.address or "Company Address",
            "contact_number": company.contact_number,
            "email": company.email or "company@email.com",
            "website": company.website,
            "logo_path": company.logo_path,
            "gstin": getattr(company, 'gstin', None),
            "business_type": company.business_type,
            "industry": company.industry
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve company branding: {str(e)}"
        )

@router.post("/audit/pdf-generation")
async def log_pdf_generation(
    audit_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Log PDF generation for audit purposes
    """
    try:
        logger.info(
            f"PDF Generated - User: {getattr(current_user, 'username', getattr(current_user, 'email', 'unknown'))}, "
            f"Organization: {getattr(current_user, 'organization_id', 'unknown')}, "
            f"Voucher Type: {audit_data.get('voucher_type')}, "
            f"Voucher Number: {audit_data.get('voucher_number')}, "
            f"Timestamp: {audit_data.get('timestamp')}"
        )
        return {"status": "logged"}

    except Exception as e:
        logger.warning(f"Failed to log PDF generation: {str(e)}")
        return {"status": "warning", "message": "Audit logging failed but PDF generation succeeded"}