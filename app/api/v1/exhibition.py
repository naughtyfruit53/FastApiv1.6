# Revised: app/api/v1/exhibition.py

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.core.org_restrictions import require_current_organization_id
from app.models.user_models import User
from app.schemas.exhibition import (
    ExhibitionEventCreate, ExhibitionEventUpdate, ExhibitionEventInDB,
    BusinessCardScanCreate, BusinessCardScanUpdate, BusinessCardScanInDB,
    ExhibitionProspectCreate, ExhibitionProspectUpdate, ExhibitionProspectInDB,
    OCRExtractionResult, ExhibitionAnalytics, ExhibitionEventMetrics,
    CardScanWithProspect, BulkCardScanResponse
)
from app.services.exhibition_service import exhibition_service
from app.services.rbac import RBACService
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


# Exhibition Event Endpoints

@router.post("/events", response_model=ExhibitionEventInDB, status_code=status.HTTP_201_CREATED)
async def create_exhibition_event(
    event_data: ExhibitionEventCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new exhibition event"""
    
    # Check RBAC permissions
    rbac = RBACService(db)
    user_permissions = await rbac.get_user_service_permissions(current_user.id)
    if "exhibition_event_create" not in user_permissions and not current_user.is_company_admin:
        logger.error(f"User {current_user.email} lacks 'exhibition_event_create' permission")
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions to create exhibition events"
        )
    
    org_id = require_current_organization_id(current_user)
    
    event = await exhibition_service.create_exhibition_event(
        db=db,
        event_data=event_data,
        organization_id=org_id,
        created_by_id=current_user.id
    )
    
    return event


@router.get("/events", response_model=List[ExhibitionEventInDB])
async def get_exhibition_events(
    status: Optional[str] = Query(None, description="Filter by event status"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    skip: int = Query(0, ge=0, description="Number of events to skip"),
    limit: int = Query(100, ge=1, le=100, description="Number of events to return"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get exhibition events for the current organization"""
    
    # Check RBAC permissions
    rbac = RBACService(db)
    user_permissions = await rbac.get_user_service_permissions(current_user.id)
    if "exhibition_event_read" not in user_permissions and not current_user.is_company_admin:
        logger.error(f"User {current_user.email} lacks 'exhibition_event_read' permission")
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions to view exhibition events"
        )
    
    org_id = require_current_organization_id(current_user)
    
    events = await exhibition_service.get_exhibition_events(
        db=db,
        organization_id=org_id,
        status=status,
        is_active=is_active,
        skip=skip,
        limit=limit
    )
    
    return events


@router.get("/events/{event_id}", response_model=ExhibitionEventInDB)
async def get_exhibition_event(
    event_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific exhibition event"""
    
    org_id = require_current_organization_id(current_user)
    
    event = await exhibition_service.get_exhibition_event(db, event_id, org_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exhibition event not found"
        )
    
    return event


@router.put("/events/{event_id}", response_model=ExhibitionEventInDB)
async def update_exhibition_event(
    event_id: int,
    event_data: ExhibitionEventUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update an exhibition event"""
    
    org_id = require_current_organization_id(current_user)
    
    event = await exhibition_service.update_exhibition_event(
        db=db,
        event_id=event_id,
        organization_id=org_id,
        event_data=event_data
    )
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exhibition event not found"
        )
    
    return event


@router.delete("/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_exhibition_event(
    event_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete an exhibition event"""
    
    org_id = require_current_organization_id(current_user)
    
    success = await exhibition_service.delete_exhibition_event(db, event_id, org_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exhibition event not found"
        )


# Business Card Scanning Endpoints

@router.post("/events/{event_id}/scan-card", response_model=BusinessCardScanInDB)
async def scan_business_card(
    event_id: int,
    file: UploadFile = File(..., description="Business card image file"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Scan a business card for an exhibition event"""
    
    org_id = require_current_organization_id(current_user)
    
    try:
        scan = await exhibition_service.scan_business_card(
            db=db,
            file=file,
            exhibition_event_id=event_id,
            organization_id=org_id,
            scanned_by_id=current_user.id
        )
        
        return scan
        
    except Exception as e:
        logger.error(f"Error scanning business card: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process business card: {str(e)}"
        )


@router.get("/card-scans", response_model=List[BusinessCardScanInDB])
async def get_card_scans(
    event_id: Optional[int] = Query(None, description="Filter by exhibition event"),
    validation_status: Optional[str] = Query(None, description="Filter by validation status"),
    processing_status: Optional[str] = Query(None, description="Filter by processing status"),
    skip: int = Query(0, ge=0, description="Number of scans to skip"),
    limit: int = Query(100, ge=1, le=100, description="Number of scans to return"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get business card scans for the current organization"""
    
    org_id = require_current_organization_id(current_user)
    
    scans = await exhibition_service.get_card_scans(
        db=db,
        organization_id=org_id,
        exhibition_event_id=event_id,
        validation_status=validation_status,
        processing_status=processing_status,
        skip=skip,
        limit=limit
    )
    
    return scans


@router.get("/card-scans/{scan_id}", response_model=BusinessCardScanInDB)
async def get_card_scan(
    scan_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific business card scan"""
    
    org_id = require_current_organization_id(current_user)
    
    scan = await exhibition_service.get_card_scan(db, scan_id, org_id)
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business card scan not found"
        )
    
    return scan


@router.put("/card-scans/{scan_id}", response_model=BusinessCardScanInDB)
async def update_card_scan(
    scan_id: int,
    scan_data: BusinessCardScanUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a business card scan (validation, correction)"""
    
    org_id = require_current_organization_id(current_user)
    
    scan = await exhibition_service.update_card_scan(
        db=db,
        scan_id=scan_id,
        organization_id=org_id,
        scan_data=scan_data,
        validated_by_id=current_user.id
    )
    
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business card scan not found"
        )
    
    return scan


# Exhibition Prospect Endpoints

@router.post("/prospects", response_model=ExhibitionProspectInDB, status_code=status.HTTP_201_CREATED)
async def create_prospect(
    prospect_data: ExhibitionProspectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new exhibition prospect"""
    
    org_id = require_current_organization_id(current_user)
    
    prospect = await exhibition_service.create_prospect(
        db=db,
        prospect_data=prospect_data,
        organization_id=org_id,
        created_by_id=current_user.id
    )
    
    return prospect


@router.get("/prospects", response_model=List[ExhibitionProspectInDB])
async def get_prospects(
    event_id: Optional[int] = Query(None, description="Filter by exhibition event"),
    status: Optional[str] = Query(None, description="Filter by prospect status"),
    qualification_status: Optional[str] = Query(None, description="Filter by qualification status"),
    assigned_to_id: Optional[int] = Query(None, description="Filter by assigned user"),
    skip: int = Query(0, ge=0, description="Number of prospects to skip"),
    limit: int = Query(100, ge=1, le=100, description="Number of prospects to return"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get exhibition prospects for the current organization"""
    
    org_id = require_current_organization_id(current_user)
    
    prospects = await exhibition_service.get_prospects(
        db=db,
        organization_id=org_id,
        exhibition_event_id=event_id,
        status=status,
        qualification_status=qualification_status,
        assigned_to_id=assigned_to_id,
        skip=skip,
        limit=limit
    )
    
    return prospects


@router.get("/prospects/{prospect_id}", response_model=ExhibitionProspectInDB)
async def get_prospect(
    prospect_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific exhibition prospect"""
    
    org_id = require_current_organization_id(current_user)
    
    prospect = await exhibition_service.get_prospect(db, prospect_id, org_id)
    if not prospect:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exhibition prospect not found"
        )
    
    return prospect


@router.put("/prospects/{prospect_id}", response_model=ExhibitionProspectInDB)
async def update_prospect(
    prospect_id: int,
    prospect_data: ExhibitionProspectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update an exhibition prospect"""
    
    org_id = require_current_organization_id(current_user)
    
    prospect = await exhibition_service.update_prospect(
        db=db,
        prospect_id=prospect_id,
        organization_id=org_id,
        prospect_data=prospect_data
    )
    
    if not prospect:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exhibition prospect not found"
        )
    
    return prospect


@router.post("/prospects/{prospect_id}/convert-to-customer")
async def convert_prospect_to_customer(
    prospect_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Convert an exhibition prospect to a CRM customer"""
    
    org_id = require_current_organization_id(current_user)
    
    customer = await exhibition_service.convert_prospect_to_customer(
        db=db,
        prospect_id=prospect_id,
        organization_id=org_id
    )
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exhibition prospect not found"
        )
    
    return {
        "message": "Prospect successfully converted to customer",
        "customer_id": customer.id,
        "customer_name": customer.name
    }


# Analytics and Reporting Endpoints

@router.get("/analytics", response_model=ExhibitionAnalytics)
async def get_exhibition_analytics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get overall exhibition analytics for the organization"""
    
    org_id = require_current_organization_id(current_user)
    
    analytics = await exhibition_service.get_exhibition_analytics(db, org_id)
    return analytics


@router.get("/events/{event_id}/metrics", response_model=ExhibitionEventMetrics)
async def get_event_metrics(
    event_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get detailed metrics for a specific exhibition event"""
    
    org_id = require_current_organization_id(current_user)
    
    metrics = await exhibition_service.get_event_metrics(db, event_id, org_id)
    if not metrics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exhibition event not found"
        )
    
    return metrics


# Bulk Operations

@router.post("/events/{event_id}/bulk-scan", response_model=BulkCardScanResponse)
async def bulk_scan_cards(
    event_id: int,
    files: List[UploadFile] = File(..., description="Multiple business card images"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Bulk scan multiple business cards for an exhibition event"""
    
    org_id = require_current_organization_id(current_user)
    
    results = {
        "successful_scans": 0,
        "failed_scans": 0,
        "created_prospects": 0,
        "emails_sent": 0,
        "errors": []
    }
    
    for file in files:
        try:
            scan = await exhibition_service.scan_business_card(
                db=db,
                file=file,
                exhibition_event_id=event_id,
                organization_id=org_id,
                scanned_by_id=current_user.id
            )
            
            results["successful_scans"] += 1
            
            if scan.prospect_created:
                results["created_prospects"] += 1
            if scan.intro_email_sent:
                results["emails_sent"] += 1
                
        except Exception as e:
            results["failed_scans"] += 1
            results["errors"].append(f"Failed to process {file.filename}: {str(e)}")
            logger.error(f"Failed to process file {file.filename}: {str(e)}")
    
    return results


# Utility Endpoints

@router.get("/events/{event_id}/export")
async def export_event_data(
    event_id: int,
    format: str = Query("csv", description="Export format: csv, excel, json"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Export exhibition event data"""
    
    org_id = require_current_organization_id(current_user)
    
    # Verify event exists
    event = await exhibition_service.get_exhibition_event(db, event_id, org_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exhibition event not found"
        )
    
    # TODO: Implement export functionality based on format
    # This would generate CSV/Excel/JSON exports of prospects, scans, etc.
    
    return {"message": f"Export functionality for {format} format is not yet implemented"}


@router.post("/test-ocr", response_model=OCRExtractionResult)
async def test_ocr_extraction(
    file: UploadFile = File(..., description="Business card image for testing"),
    current_user: User = Depends(get_current_active_user)
):
    """Test OCR extraction without creating a scan record"""
    
    from app.services.ocr_service import ocr_service
    
    try:
        result = await ocr_service.process_business_card(file)
        
        return OCRExtractionResult(
            raw_text=result.get("raw_text", ""),
            extracted_data=result.get("extracted_data", {}),
            confidence_score=result.get("confidence_score", 0.0),
            full_name=result.get("full_name"),
            company_name=result.get("company_name"),
            designation=result.get("designation"),
            email=result.get("email"),
            phone=result.get("phone"),
            mobile=result.get("mobile"),
            website=result.get("website"),
            address=result.get("address")
        )
        
    except Exception as e:
        logger.error(f"OCR test failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OCR extraction failed: {str(e)}"
        )
    finally:
        # Cleanup temp file if created
        if hasattr(result, 'image_path') and result.get('image_path'):
            ocr_service.cleanup_temp_file(result['image_path'])