# app/schemas/exhibition.py

from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum


class ExhibitionEventStatus(str, Enum):
    PLANNED = "planned"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class CardScanMethod(str, Enum):
    UPLOAD = "upload"
    CAMERA = "camera"
    SCANNER = "scanner"


class ValidationStatus(str, Enum):
    PENDING = "pending"
    VALIDATED = "validated"
    REJECTED = "rejected"


class ProcessingStatus(str, Enum):
    SCANNED = "scanned"
    PROCESSED = "processed"
    CONVERTED = "converted"
    FAILED = "failed"


class ProspectStatus(str, Enum):
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    CONVERTED = "converted"
    LOST = "lost"


class ConversionStatus(str, Enum):
    PROSPECT = "prospect"
    LEAD = "lead"
    CUSTOMER = "customer"


class QualificationStatus(str, Enum):
    UNQUALIFIED = "unqualified"
    QUALIFIED = "qualified"
    HOT = "hot"
    COLD = "cold"


class InterestLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# Exhibition Event schemas
class ExhibitionEventBase(BaseModel):
    name: str
    description: Optional[str] = None
    location: Optional[str] = None
    venue: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: ExhibitionEventStatus = ExhibitionEventStatus.PLANNED
    is_active: bool = True
    auto_send_intro_email: bool = True
    intro_email_template_id: Optional[int] = None


class ExhibitionEventCreate(ExhibitionEventBase):
    pass


class ExhibitionEventUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    venue: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[ExhibitionEventStatus] = None
    is_active: Optional[bool] = None
    auto_send_intro_email: Optional[bool] = None
    intro_email_template_id: Optional[int] = None


class ExhibitionEventInDB(ExhibitionEventBase):
    id: int
    organization_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by_id: int
    card_scan_count: Optional[int] = None
    prospect_count: Optional[int] = None
    
    class Config:
        from_attributes = True


# Business Card Scan schemas
class BusinessCardScanBase(BaseModel):
    scan_method: CardScanMethod = CardScanMethod.UPLOAD
    full_name: Optional[str] = None
    company_name: Optional[str] = None
    designation: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    validation_notes: Optional[str] = None


class BusinessCardScanCreate(BusinessCardScanBase):
    exhibition_event_id: int


class BusinessCardScanUpdate(BaseModel):
    full_name: Optional[str] = None
    company_name: Optional[str] = None
    designation: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    validation_status: Optional[ValidationStatus] = None
    validation_notes: Optional[str] = None
    processing_status: Optional[ProcessingStatus] = None


class BusinessCardScanInDB(BusinessCardScanBase):
    id: int
    organization_id: int
    exhibition_event_id: int
    scan_id: str
    image_path: Optional[str] = None
    raw_text: Optional[str] = None
    extracted_data: Optional[Dict[str, Any]] = None
    confidence_score: Optional[float] = None
    validation_status: ValidationStatus = ValidationStatus.PENDING
    validated_by_id: Optional[int] = None
    processing_status: ProcessingStatus = ProcessingStatus.SCANNED
    prospect_created: bool = False
    intro_email_sent: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None
    scanned_by_id: int
    
    class Config:
        from_attributes = True


class OCRExtractionResult(BaseModel):
    """Result from OCR extraction of business card"""
    raw_text: str
    extracted_data: Dict[str, Any]
    confidence_score: float
    full_name: Optional[str] = None
    company_name: Optional[str] = None
    designation: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None


# Exhibition Prospect schemas
class ExhibitionProspectBase(BaseModel):
    full_name: str
    company_name: str
    designation: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    interest_level: Optional[InterestLevel] = None
    notes: Optional[str] = None
    follow_up_date: Optional[datetime] = None


class ExhibitionProspectCreate(ExhibitionProspectBase):
    exhibition_event_id: int
    card_scan_id: Optional[int] = None


class ExhibitionProspectUpdate(BaseModel):
    full_name: Optional[str] = None
    company_name: Optional[str] = None
    designation: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    lead_score: Optional[float] = None
    qualification_status: Optional[QualificationStatus] = None
    interest_level: Optional[InterestLevel] = None
    notes: Optional[str] = None
    assigned_to_id: Optional[int] = None
    follow_up_date: Optional[datetime] = None
    status: Optional[ProspectStatus] = None
    conversion_status: Optional[ConversionStatus] = None


class ExhibitionProspectInDB(ExhibitionProspectBase):
    id: int
    organization_id: int
    exhibition_event_id: int
    card_scan_id: Optional[int] = None
    lead_score: Optional[float] = 0.0
    qualification_status: QualificationStatus = QualificationStatus.UNQUALIFIED
    crm_customer_id: Optional[int] = None
    assigned_to_id: Optional[int] = None
    intro_email_sent_at: Optional[datetime] = None
    last_contact_date: Optional[datetime] = None
    contact_attempts: int = 0
    status: ProspectStatus = ProspectStatus.NEW
    conversion_status: ConversionStatus = ConversionStatus.PROSPECT
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by_id: int
    
    class Config:
        from_attributes = True


# Combined response schemas
class CardScanWithProspect(BusinessCardScanInDB):
    prospect: Optional[ExhibitionProspectInDB] = None


class ExhibitionEventWithStats(ExhibitionEventInDB):
    card_scans: List[BusinessCardScanInDB] = []
    prospects: List[ExhibitionProspectInDB] = []
    stats: Dict[str, Any] = {}


# Bulk operation schemas
class BulkCardScanResponse(BaseModel):
    successful_scans: int
    failed_scans: int
    created_prospects: int
    emails_sent: int
    errors: List[str] = []


class ProspectLeadScoring(BaseModel):
    """Schema for lead scoring of prospects"""
    prospect_id: int
    company_size_score: Optional[float] = None
    industry_match_score: Optional[float] = None
    contact_quality_score: Optional[float] = None
    engagement_score: Optional[float] = None
    total_score: float
    recommendation: str  # hot, warm, cold


# Email template integration
class ExhibitionEmailContext(BaseModel):
    """Context data for exhibition intro emails"""
    prospect_name: str
    company_name: str
    exhibition_name: str
    exhibition_location: Optional[str] = None
    contact_person: str  # Person who scanned the card
    contact_email: str
    contact_phone: Optional[str] = None
    follow_up_link: Optional[str] = None


# Analytics and reporting schemas
class ExhibitionAnalytics(BaseModel):
    """Analytics data for exhibition events"""
    total_events: int
    active_events: int
    total_scans: int
    total_prospects: int
    conversion_rate: float
    top_companies: List[Dict[str, Any]]
    scan_trends: List[Dict[str, Any]]
    lead_quality_distribution: Dict[str, int]


class ExhibitionEventMetrics(BaseModel):
    """Detailed metrics for a specific exhibition event"""
    event_id: int
    event_name: str
    total_scans: int
    validated_scans: int
    prospects_created: int
    emails_sent: int
    qualified_leads: int
    converted_customers: int
    top_industries: List[Dict[str, Any]]
    scan_timeline: List[Dict[str, Any]]
    quality_scores: Dict[str, float]