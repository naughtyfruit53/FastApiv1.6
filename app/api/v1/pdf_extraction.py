"""
PDF Extraction API endpoints
"""

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
from app.core.database import get_db
from app.core.enforcement import require_access
from app.models import User
from app.services.pdf_extraction import pdf_extraction_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/extract/{voucher_type}")
async def extract_pdf_data(
    voucher_type: str,
    file: UploadFile = File(...),
    auth: tuple = Depends(require_access("pdf_extraction", "create")),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Extract structured data from uploaded PDF based on voucher type
    
    Supported voucher types:
    - purchase_voucher
    - sales_order
    - vendor
    - customer
    """
    current_user, org_id = auth
    
    logger.info(f"PDF extraction requested for voucher type: {voucher_type} by user: {current_user.id}")
    
    try:
        # Extract data using the PDF extraction service
        extracted_data = await pdf_extraction_service.extract_voucher_data(file, voucher_type)
        
        logger.info(f"PDF extraction successful for voucher type: {voucher_type}")
        
        return {
            "success": True,
            "voucher_type": voucher_type,
            "extracted_data": extracted_data,
            "filename": file.filename
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error during PDF extraction: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"PDF extraction failed: {str(e)}"
        )

@router.get("/health")
async def pdf_extraction_health():
    """Health check for PDF extraction service"""
    return {
        "status": "healthy",
        "service": "pdf_extraction",
        "max_file_size_mb": pdf_extraction_service.MAX_FILE_SIZE / (1024 * 1024)
    }