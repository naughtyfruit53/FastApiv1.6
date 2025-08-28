# app/services/exhibition_service.py

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from fastapi import HTTPException, status, UploadFile
from datetime import datetime

from app.models.exhibition_models import ExhibitionEvent, BusinessCardScan, ExhibitionProspect
from app.models.customer_models import Customer
from app.models.user_models import User
from app.schemas.exhibition import (
    ExhibitionEventCreate, ExhibitionEventUpdate, ExhibitionEventInDB,
    BusinessCardScanCreate, BusinessCardScanUpdate, BusinessCardScanInDB,
    ExhibitionProspectCreate, ExhibitionProspectUpdate, ExhibitionProspectInDB,
    OCRExtractionResult, ExhibitionAnalytics, ExhibitionEventMetrics
)
from app.services.ocr_service import ocr_service
from app.services.notification_service import notification_service
import logging

logger = logging.getLogger(__name__)


class ExhibitionService:
    """Service for managing exhibition events and business card scanning"""
    
    def __init__(self):
        pass
    
    # Exhibition Event Management
    
    async def create_exhibition_event(
        self, 
        db: Session, 
        event_data: ExhibitionEventCreate, 
        organization_id: int, 
        created_by_id: int
    ) -> ExhibitionEvent:
        """Create a new exhibition event"""
        
        db_event = ExhibitionEvent(
            organization_id=organization_id,
            created_by_id=created_by_id,
            **event_data.dict()
        )
        
        db.add(db_event)
        db.commit()
        db.refresh(db_event)
        
        logger.info(f"Created exhibition event {db_event.id} for organization {organization_id}")
        return db_event
    
    def get_exhibition_events(
        self, 
        db: Session, 
        organization_id: int,
        status: Optional[str] = None,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[ExhibitionEvent]:
        """Get exhibition events for an organization"""
        
        query = db.query(ExhibitionEvent).filter(ExhibitionEvent.organization_id == organization_id)
        
        if status:
            query = query.filter(ExhibitionEvent.status == status)
        if is_active is not None:
            query = query.filter(ExhibitionEvent.is_active == is_active)
        
        return query.order_by(desc(ExhibitionEvent.created_at)).offset(skip).limit(limit).all()
    
    def get_exhibition_event(self, db: Session, event_id: int, organization_id: int) -> Optional[ExhibitionEvent]:
        """Get a specific exhibition event"""
        
        return db.query(ExhibitionEvent).filter(
            and_(
                ExhibitionEvent.id == event_id,
                ExhibitionEvent.organization_id == organization_id
            )
        ).first()
    
    async def update_exhibition_event(
        self, 
        db: Session, 
        event_id: int, 
        organization_id: int, 
        event_data: ExhibitionEventUpdate
    ) -> Optional[ExhibitionEvent]:
        """Update an exhibition event"""
        
        db_event = self.get_exhibition_event(db, event_id, organization_id)
        if not db_event:
            return None
        
        update_data = event_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_event, field, value)
        
        db.commit()
        db.refresh(db_event)
        
        logger.info(f"Updated exhibition event {event_id}")
        return db_event
    
    def delete_exhibition_event(self, db: Session, event_id: int, organization_id: int) -> bool:
        """Delete an exhibition event"""
        
        db_event = self.get_exhibition_event(db, event_id, organization_id)
        if not db_event:
            return False
        
        db.delete(db_event)
        db.commit()
        
        logger.info(f"Deleted exhibition event {event_id}")
        return True
    
    # Business Card Scanning
    
    async def scan_business_card(
        self, 
        db: Session, 
        file: UploadFile, 
        exhibition_event_id: int,
        organization_id: int,
        scanned_by_id: int
    ) -> BusinessCardScan:
        """Process a business card scan"""
        
        # Verify exhibition event exists and belongs to organization
        event = self.get_exhibition_event(db, exhibition_event_id, organization_id)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exhibition event not found"
            )
        
        # Process the image with OCR
        ocr_result = await ocr_service.process_business_card(file)
        
        # Create business card scan record
        db_scan = BusinessCardScan(
            organization_id=organization_id,
            exhibition_event_id=exhibition_event_id,
            scanned_by_id=scanned_by_id,
            image_path=ocr_result.get("image_path"),
            raw_text=ocr_result.get("raw_text"),
            extracted_data=ocr_result.get("extracted_data"),
            confidence_score=ocr_result.get("confidence_score"),
            full_name=ocr_result.get("full_name"),
            company_name=ocr_result.get("company_name"),
            designation=ocr_result.get("designation"),
            email=ocr_result.get("email"),
            phone=ocr_result.get("phone"),
            mobile=ocr_result.get("mobile"),
            website=ocr_result.get("website"),
            address=ocr_result.get("address")
        )
        
        db.add(db_scan)
        db.commit()
        db.refresh(db_scan)
        
        # Auto-create prospect if confidence is high enough
        if db_scan.confidence_score and db_scan.confidence_score > 0.7:
            try:
                await self._auto_create_prospect(db, db_scan, scanned_by_id)
            except Exception as e:
                logger.error(f"Failed to auto-create prospect for scan {db_scan.id}: {str(e)}")
        
        logger.info(f"Created business card scan {db_scan.id} for event {exhibition_event_id}")
        return db_scan
    
    def get_card_scans(
        self, 
        db: Session, 
        organization_id: int,
        exhibition_event_id: Optional[int] = None,
        validation_status: Optional[str] = None,
        processing_status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[BusinessCardScan]:
        """Get business card scans"""
        
        query = db.query(BusinessCardScan).filter(BusinessCardScan.organization_id == organization_id)
        
        if exhibition_event_id:
            query = query.filter(BusinessCardScan.exhibition_event_id == exhibition_event_id)
        if validation_status:
            query = query.filter(BusinessCardScan.validation_status == validation_status)
        if processing_status:
            query = query.filter(BusinessCardScan.processing_status == processing_status)
        
        return query.order_by(desc(BusinessCardScan.created_at)).offset(skip).limit(limit).all()
    
    def get_card_scan(self, db: Session, scan_id: int, organization_id: int) -> Optional[BusinessCardScan]:
        """Get a specific business card scan"""
        
        return db.query(BusinessCardScan).filter(
            and_(
                BusinessCardScan.id == scan_id,
                BusinessCardScan.organization_id == organization_id
            )
        ).first()
    
    async def update_card_scan(
        self, 
        db: Session, 
        scan_id: int, 
        organization_id: int, 
        scan_data: BusinessCardScanUpdate,
        validated_by_id: Optional[int] = None
    ) -> Optional[BusinessCardScan]:
        """Update a business card scan"""
        
        db_scan = self.get_card_scan(db, scan_id, organization_id)
        if not db_scan:
            return None
        
        update_data = scan_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_scan, field, value)
        
        if validated_by_id and scan_data.validation_status:
            db_scan.validated_by_id = validated_by_id
        
        db.commit()
        db.refresh(db_scan)
        
        # If validated, try to create prospect
        if db_scan.validation_status == "validated" and not db_scan.prospect_created:
            try:
                await self._auto_create_prospect(db, db_scan, validated_by_id or db_scan.scanned_by_id)
            except Exception as e:
                logger.error(f"Failed to create prospect after validation for scan {scan_id}: {str(e)}")
        
        logger.info(f"Updated business card scan {scan_id}")
        return db_scan
    
    # Prospect Management
    
    async def create_prospect(
        self, 
        db: Session, 
        prospect_data: ExhibitionProspectCreate, 
        organization_id: int, 
        created_by_id: int
    ) -> ExhibitionProspect:
        """Create a new exhibition prospect"""
        
        # Verify exhibition event exists
        event = self.get_exhibition_event(db, prospect_data.exhibition_event_id, organization_id)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exhibition event not found"
            )
        
        db_prospect = ExhibitionProspect(
            organization_id=organization_id,
            created_by_id=created_by_id,
            **prospect_data.dict()
        )
        
        db.add(db_prospect)
        db.commit()
        db.refresh(db_prospect)
        
        # Send intro email if configured
        if event.auto_send_intro_email:
            try:
                await self._send_intro_email(db, db_prospect, event)
            except Exception as e:
                logger.error(f"Failed to send intro email for prospect {db_prospect.id}: {str(e)}")
        
        logger.info(f"Created exhibition prospect {db_prospect.id}")
        return db_prospect
    
    def get_prospects(
        self, 
        db: Session, 
        organization_id: int,
        exhibition_event_id: Optional[int] = None,
        status: Optional[str] = None,
        qualification_status: Optional[str] = None,
        assigned_to_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[ExhibitionProspect]:
        """Get exhibition prospects"""
        
        query = db.query(ExhibitionProspect).filter(ExhibitionProspect.organization_id == organization_id)
        
        if exhibition_event_id:
            query = query.filter(ExhibitionProspect.exhibition_event_id == exhibition_event_id)
        if status:
            query = query.filter(ExhibitionProspect.status == status)
        if qualification_status:
            query = query.filter(ExhibitionProspect.qualification_status == qualification_status)
        if assigned_to_id:
            query = query.filter(ExhibitionProspect.assigned_to_id == assigned_to_id)
        
        return query.order_by(desc(ExhibitionProspect.created_at)).offset(skip).limit(limit).all()
    
    def get_prospect(self, db: Session, prospect_id: int, organization_id: int) -> Optional[ExhibitionProspect]:
        """Get a specific exhibition prospect"""
        
        return db.query(ExhibitionProspect).filter(
            and_(
                ExhibitionProspect.id == prospect_id,
                ExhibitionProspect.organization_id == organization_id
            )
        ).first()
    
    async def update_prospect(
        self, 
        db: Session, 
        prospect_id: int, 
        organization_id: int, 
        prospect_data: ExhibitionProspectUpdate
    ) -> Optional[ExhibitionProspect]:
        """Update an exhibition prospect"""
        
        db_prospect = self.get_prospect(db, prospect_id, organization_id)
        if not db_prospect:
            return None
        
        update_data = prospect_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_prospect, field, value)
        
        db.commit()
        db.refresh(db_prospect)
        
        logger.info(f"Updated exhibition prospect {prospect_id}")
        return db_prospect
    
    async def convert_prospect_to_customer(
        self, 
        db: Session, 
        prospect_id: int, 
        organization_id: int
    ) -> Optional[Customer]:
        """Convert an exhibition prospect to a CRM customer"""
        
        prospect = self.get_prospect(db, prospect_id, organization_id)
        if not prospect:
            return None
        
        # Check if already converted
        if prospect.crm_customer_id:
            return db.query(Customer).filter(Customer.id == prospect.crm_customer_id).first()
        
        # Create new customer
        customer_data = {
            "name": prospect.full_name,
            "company_name": prospect.company_name,
            "email": prospect.email,
            "phone": prospect.phone or prospect.mobile,
            "address": prospect.address,
            "organization_id": organization_id,
            "created_by_id": prospect.created_by_id,
            "source": f"Exhibition: {prospect.exhibition_event.name}"
        }
        
        db_customer = Customer(**customer_data)
        db.add(db_customer)
        db.commit()
        db.refresh(db_customer)
        
        # Update prospect
        prospect.crm_customer_id = db_customer.id
        prospect.conversion_status = "customer"
        prospect.status = "converted"
        db.commit()
        
        logger.info(f"Converted prospect {prospect_id} to customer {db_customer.id}")
        return db_customer
    
    # Private helper methods
    
    async def _auto_create_prospect(
        self, 
        db: Session, 
        card_scan: BusinessCardScan, 
        created_by_id: int
    ) -> None:
        """Auto-create prospect from validated card scan"""
        
        if not card_scan.full_name or not card_scan.company_name:
            logger.warning(f"Insufficient data to create prospect from scan {card_scan.id}")
            return
        
        prospect_data = ExhibitionProspectCreate(
            exhibition_event_id=card_scan.exhibition_event_id,
            card_scan_id=card_scan.id,
            full_name=card_scan.full_name,
            company_name=card_scan.company_name,
            designation=card_scan.designation,
            email=card_scan.email,
            phone=card_scan.phone,
            mobile=card_scan.mobile,
            website=card_scan.website,
            address=card_scan.address
        )
        
        prospect = await self.create_prospect(
            db, 
            prospect_data, 
            card_scan.organization_id, 
            created_by_id
        )
        
        # Update scan record
        card_scan.prospect_created = True
        card_scan.processing_status = "converted"
        db.commit()
        
        logger.info(f"Auto-created prospect {prospect.id} from card scan {card_scan.id}")
    
    async def _send_intro_email(
        self, 
        db: Session, 
        prospect: ExhibitionProspect, 
        event: ExhibitionEvent
    ) -> None:
        """Send intro email to prospect"""
        
        if not prospect.email or prospect.intro_email_sent_at:
            return
        
        try:
            # Get email template
            template_id = event.intro_email_template_id
            if not template_id:
                # Use default exhibition intro template
                template_id = await self._get_default_intro_template_id(db, event.organization_id)
            
            if template_id:
                # Prepare email context
                context = {
                    "prospect_name": prospect.full_name,
                    "company_name": prospect.company_name,
                    "exhibition_name": event.name,
                    "exhibition_location": event.location,
                    "contact_person": prospect.created_by.full_name,
                    "contact_email": prospect.created_by.email,
                    "follow_up_date": prospect.follow_up_date.isoformat() if prospect.follow_up_date else None
                }
                
                # Send email via notification service
                await notification_service.send_template_notification(
                    db=db,
                    template_id=template_id,
                    recipient_email=prospect.email,
                    context=context,
                    organization_id=event.organization_id
                )
                
                # Update prospect
                prospect.intro_email_sent_at = datetime.utcnow()
                prospect.contact_attempts += 1
                db.commit()
                
                logger.info(f"Sent intro email to prospect {prospect.id}")
        
        except Exception as e:
            logger.error(f"Failed to send intro email to prospect {prospect.id}: {str(e)}")
            raise
    
    async def _get_default_intro_template_id(self, db: Session, organization_id: int) -> Optional[int]:
        """Get the default exhibition intro email template"""
        # This would query the notification_templates table for a default exhibition template
        # Implementation depends on the notification template structure
        return None
    
    # Analytics and Reporting
    
    def get_exhibition_analytics(self, db: Session, organization_id: int) -> ExhibitionAnalytics:
        """Get overall exhibition analytics"""
        
        # Get basic counts
        total_events = db.query(func.count(ExhibitionEvent.id)).filter(
            ExhibitionEvent.organization_id == organization_id
        ).scalar()
        
        active_events = db.query(func.count(ExhibitionEvent.id)).filter(
            and_(
                ExhibitionEvent.organization_id == organization_id,
                ExhibitionEvent.status == "active"
            )
        ).scalar()
        
        total_scans = db.query(func.count(BusinessCardScan.id)).filter(
            BusinessCardScan.organization_id == organization_id
        ).scalar()
        
        total_prospects = db.query(func.count(ExhibitionProspect.id)).filter(
            ExhibitionProspect.organization_id == organization_id
        ).scalar()
        
        # Calculate conversion rate
        conversion_rate = (total_prospects / total_scans * 100) if total_scans > 0 else 0
        
        # Get top companies
        top_companies = db.query(
            ExhibitionProspect.company_name,
            func.count(ExhibitionProspect.id).label('prospect_count')
        ).filter(
            ExhibitionProspect.organization_id == organization_id
        ).group_by(
            ExhibitionProspect.company_name
        ).order_by(
            desc('prospect_count')
        ).limit(10).all()
        
        return ExhibitionAnalytics(
            total_events=total_events or 0,
            active_events=active_events or 0,
            total_scans=total_scans or 0,
            total_prospects=total_prospects or 0,
            conversion_rate=conversion_rate,
            top_companies=[{"company": comp[0], "count": comp[1]} for comp in top_companies],
            scan_trends=[],  # Implementation depends on time-series requirements
            lead_quality_distribution={}
        )
    
    def get_event_metrics(self, db: Session, event_id: int, organization_id: int) -> Optional[ExhibitionEventMetrics]:
        """Get detailed metrics for a specific exhibition event"""
        
        event = self.get_exhibition_event(db, event_id, organization_id)
        if not event:
            return None
        
        # Get counts
        total_scans = db.query(func.count(BusinessCardScan.id)).filter(
            BusinessCardScan.exhibition_event_id == event_id
        ).scalar()
        
        validated_scans = db.query(func.count(BusinessCardScan.id)).filter(
            and_(
                BusinessCardScan.exhibition_event_id == event_id,
                BusinessCardScan.validation_status == "validated"
            )
        ).scalar()
        
        prospects_created = db.query(func.count(ExhibitionProspect.id)).filter(
            ExhibitionProspect.exhibition_event_id == event_id
        ).scalar()
        
        emails_sent = db.query(func.count(ExhibitionProspect.id)).filter(
            and_(
                ExhibitionProspect.exhibition_event_id == event_id,
                ExhibitionProspect.intro_email_sent_at.isnot(None)
            )
        ).scalar()
        
        qualified_leads = db.query(func.count(ExhibitionProspect.id)).filter(
            and_(
                ExhibitionProspect.exhibition_event_id == event_id,
                ExhibitionProspect.qualification_status.in_(["qualified", "hot"])
            )
        ).scalar()
        
        converted_customers = db.query(func.count(ExhibitionProspect.id)).filter(
            and_(
                ExhibitionProspect.exhibition_event_id == event_id,
                ExhibitionProspect.conversion_status == "customer"
            )
        ).scalar()
        
        return ExhibitionEventMetrics(
            event_id=event_id,
            event_name=event.name,
            total_scans=total_scans or 0,
            validated_scans=validated_scans or 0,
            prospects_created=prospects_created or 0,
            emails_sent=emails_sent or 0,
            qualified_leads=qualified_leads or 0,
            converted_customers=converted_customers or 0,
            top_industries=[],
            scan_timeline=[],
            quality_scores={}
        )


# Global service instance
exhibition_service = ExhibitionService()