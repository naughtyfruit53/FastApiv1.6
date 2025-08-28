# app/api/v1/crm.py

from fastapi import APIRouter, Depends, HTTPException, Query, Path, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta

from app.core.database import get_db
from app.core.tenant import require_current_organization_id
from app.models.crm_models import (
    Lead, Opportunity, OpportunityProduct, LeadActivity, OpportunityActivity,
    SalesPipeline, SalesForecast, LeadStatus, LeadSource, OpportunityStage
)
from app.models.customer_models import Customer
from app.models.user_models import User
from app.schemas.crm import (
    Lead as LeadSchema, LeadCreate, LeadUpdate,
    Opportunity as OpportunitySchema, OpportunityCreate, OpportunityUpdate,
    OpportunityProduct as OpportunityProductSchema, OpportunityProductCreate, OpportunityProductUpdate,
    LeadActivity as LeadActivitySchema, LeadActivityCreate, LeadActivityUpdate,
    OpportunityActivity as OpportunityActivitySchema, OpportunityActivityCreate, OpportunityActivityUpdate,
    SalesPipeline as SalesPipelineSchema, SalesPipelineCreate, SalesPipelineUpdate,
    SalesForecast as SalesForecastSchema, SalesForecastCreate, SalesForecastUpdate,
    LeadConversionRequest, LeadConversionResponse,
    CRMAnalytics, CustomerAnalytics
)
from app.services.rbac import RBACService
import secrets
import string

router = APIRouter(prefix="/crm", tags=["CRM"])

def generate_unique_number(db: Session, model_class, org_id: int, prefix: str) -> str:
    """Generate unique number for leads/opportunities"""
    while True:
        # Generate a random number
        random_suffix = ''.join(secrets.choice(string.digits) for _ in range(6))
        number = f"{prefix}{random_suffix}"
        
        # Check if it exists
        existing = db.query(model_class).filter(
            and_(
                model_class.organization_id == org_id,
                getattr(model_class, f"{prefix.lower()}_number") == number
            )
        ).first()
        
        if not existing:
            return number

# Lead Management Endpoints
@router.get("/leads", response_model=List[LeadSchema])
async def get_leads(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    assigned_to_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    org_id: int = Depends(require_current_organization_id)
):
    """Get all leads with filtering and pagination"""
    query = db.query(Lead).filter(Lead.organization_id == org_id)
    
    # Apply filters
    if status:
        query = query.filter(Lead.status == status)
    if source:
        query = query.filter(Lead.source == source)
    if assigned_to_id:
        query = query.filter(Lead.assigned_to_id == assigned_to_id)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Lead.first_name.ilike(search_term),
                Lead.last_name.ilike(search_term),
                Lead.email.ilike(search_term),
                Lead.company.ilike(search_term)
            )
        )
    
    # Order by created date descending
    query = query.order_by(desc(Lead.created_at))
    
    # Apply pagination
    leads = query.offset(skip).limit(limit).all()
    return leads

@router.post("/leads", response_model=LeadSchema)
async def create_lead(
    lead_data: LeadCreate,
    db: Session = Depends(get_db),
    org_id: int = Depends(require_current_organization_id)
):
    """Create a new lead"""
    # Generate unique lead number
    lead_number = generate_unique_number(db, Lead, org_id, "LD")
    
    # Create lead
    lead = Lead(
        organization_id=org_id,
        lead_number=lead_number,
        **lead_data.model_dump()
    )
    
    db.add(lead)
    db.commit()
    db.refresh(lead)
    
    return lead

@router.get("/leads/{lead_id}", response_model=LeadSchema)
async def get_lead(
    lead_id: int = Path(...),
    db: Session = Depends(get_db),
    org_id: int = Depends(require_current_organization_id)
):
    """Get a specific lead"""
    lead = db.query(Lead).filter(
        and_(Lead.id == lead_id, Lead.organization_id == org_id)
    ).first()
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    return lead

@router.put("/leads/{lead_id}", response_model=LeadSchema)
async def update_lead(
    lead_data: LeadUpdate,
    lead_id: int = Path(...),
    db: Session = Depends(get_db),
    org_id: int = Depends(require_current_organization_id)
):
    """Update a lead"""
    lead = db.query(Lead).filter(
        and_(Lead.id == lead_id, Lead.organization_id == org_id)
    ).first()
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Update fields
    update_data = lead_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(lead, field, value)
    
    lead.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(lead)
    
    return lead

@router.delete("/leads/{lead_id}")
async def delete_lead(
    lead_id: int = Path(...),
    db: Session = Depends(get_db),
    org_id: int = Depends(require_current_organization_id)
):
    """Delete a lead"""
    lead = db.query(Lead).filter(
        and_(Lead.id == lead_id, Lead.organization_id == org_id)
    ).first()
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    db.delete(lead)
    db.commit()
    
    return {"message": "Lead deleted successfully"}

@router.post("/leads/{lead_id}/convert", response_model=LeadConversionResponse)
async def convert_lead(
    conversion_data: LeadConversionRequest,
    lead_id: int = Path(...),
    db: Session = Depends(get_db),
    org_id: int = Depends(require_current_organization_id)
):
    """Convert lead to customer and/or opportunity"""
    lead = db.query(Lead).filter(
        and_(Lead.id == lead_id, Lead.organization_id == org_id)
    ).first()
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    if lead.status == LeadStatus.CONVERTED:
        raise HTTPException(status_code=400, detail="Lead already converted")
    
    customer_id = None
    opportunity_id = None
    
    try:
        # Convert to customer
        if conversion_data.convert_to_customer:
            customer_data = conversion_data.customer_data or {}
            customer = Customer(
                organization_id=org_id,
                name=f"{lead.first_name} {lead.last_name}".strip(),
                email=lead.email,
                contact_number=lead.phone or "",
                address1=lead.address1 or "",
                address2=lead.address2 or "",
                city=lead.city or "",
                state=lead.state or "",
                pin_code=lead.pin_code or "",
                **customer_data
            )
            db.add(customer)
            db.flush()
            customer_id = customer.id
        
        # Convert to opportunity
        if conversion_data.convert_to_opportunity:
            opportunity_data = conversion_data.opportunity_data or {}
            opportunity_number = generate_unique_number(db, Opportunity, org_id, "OP")
            opportunity = Opportunity(
                organization_id=org_id,
                opportunity_number=opportunity_number,
                name=opportunity_data.get("name", f"Opportunity - {lead.company or lead.full_name}"),
                amount=opportunity_data.get("amount", lead.estimated_value or 0),
                expected_close_date=opportunity_data.get("expected_close_date", lead.expected_close_date or (date.today() + timedelta(days=30))),
                stage=OpportunityStage.PROSPECTING,
                probability=25.0,  # Default for prospecting stage
                customer_id=customer_id,
                lead_id=lead.id,
                assigned_to_id=lead.assigned_to_id,
                source=lead.source,
                **{k: v for k, v in opportunity_data.items() if k not in ["name", "amount", "expected_close_date"]}
            )
            # Calculate expected revenue
            opportunity.expected_revenue = opportunity.amount * (opportunity.probability / 100)
            db.add(opportunity)
            db.flush()
            opportunity_id = opportunity.id
        
        # Update lead status
        lead.status = LeadStatus.CONVERTED
        lead.converted_at = datetime.utcnow()
        lead.converted_to_customer_id = customer_id
        lead.converted_to_opportunity_id = opportunity_id
        
        db.commit()
        
        return LeadConversionResponse(
            success=True,
            customer_id=customer_id,
            opportunity_id=opportunity_id,
            message="Lead converted successfully"
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")

# Lead Activities
@router.get("/leads/{lead_id}/activities", response_model=List[LeadActivitySchema])
async def get_lead_activities(
    lead_id: int = Path(...),
    db: Session = Depends(get_db),
    org_id: int = Depends(require_current_organization_id)
):
    """Get activities for a lead"""
    # Verify lead exists
    lead = db.query(Lead).filter(
        and_(Lead.id == lead_id, Lead.organization_id == org_id)
    ).first()
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    activities = db.query(LeadActivity).filter(
        and_(LeadActivity.lead_id == lead_id, LeadActivity.organization_id == org_id)
    ).order_by(desc(LeadActivity.activity_date)).all()
    
    return activities

@router.post("/leads/{lead_id}/activities", response_model=LeadActivitySchema)
async def create_lead_activity(
    activity_data: LeadActivityCreate,
    lead_id: int = Path(...),
    db: Session = Depends(get_db),
    org_id: int = Depends(require_current_organization_id)
):
    """Create a new lead activity"""
    # Verify lead exists
    lead = db.query(Lead).filter(
        and_(Lead.id == lead_id, Lead.organization_id == org_id)
    ).first()
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    activity = LeadActivity(
        organization_id=org_id,
        lead_id=lead_id,
        **activity_data.model_dump(exclude={"lead_id"})
    )
    
    db.add(activity)
    
    # Update lead's last contacted time
    lead.last_contacted = datetime.utcnow()
    
    db.commit()
    db.refresh(activity)
    
    return activity

# Opportunity Management Endpoints
@router.get("/opportunities", response_model=List[OpportunitySchema])
async def get_opportunities(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    stage: Optional[str] = Query(None),
    assigned_to_id: Optional[int] = Query(None),
    customer_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    org_id: int = Depends(require_current_organization_id)
):
    """Get all opportunities with filtering and pagination"""
    query = db.query(Opportunity).filter(Opportunity.organization_id == org_id)
    
    # Apply filters
    if stage:
        query = query.filter(Opportunity.stage == stage)
    if assigned_to_id:
        query = query.filter(Opportunity.assigned_to_id == assigned_to_id)
    if customer_id:
        query = query.filter(Opportunity.customer_id == customer_id)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Opportunity.name.ilike(search_term),
                Opportunity.description.ilike(search_term)
            )
        )
    
    # Order by expected close date
    query = query.order_by(asc(Opportunity.expected_close_date))
    
    # Apply pagination
    opportunities = query.offset(skip).limit(limit).all()
    return opportunities

@router.post("/opportunities", response_model=OpportunitySchema)
async def create_opportunity(
    opportunity_data: OpportunityCreate,
    db: Session = Depends(get_db),
    org_id: int = Depends(require_current_organization_id)
):
    """Create a new opportunity"""
    # Generate unique opportunity number
    opportunity_number = generate_unique_number(db, Opportunity, org_id, "OP")
    
    # Create opportunity
    opportunity = Opportunity(
        organization_id=org_id,
        opportunity_number=opportunity_number,
        **opportunity_data.model_dump()
    )
    
    # Calculate expected revenue
    opportunity.expected_revenue = opportunity.amount * (opportunity.probability / 100)
    
    db.add(opportunity)
    db.commit()
    db.refresh(opportunity)
    
    return opportunity

@router.get("/opportunities/{opportunity_id}", response_model=OpportunitySchema)
async def get_opportunity(
    opportunity_id: int = Path(...),
    db: Session = Depends(get_db),
    org_id: int = Depends(require_current_organization_id)
):
    """Get a specific opportunity"""
    opportunity = db.query(Opportunity).filter(
        and_(Opportunity.id == opportunity_id, Opportunity.organization_id == org_id)
    ).first()
    
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    
    return opportunity

@router.put("/opportunities/{opportunity_id}", response_model=OpportunitySchema)
async def update_opportunity(
    opportunity_data: OpportunityUpdate,
    opportunity_id: int = Path(...),
    db: Session = Depends(get_db),
    org_id: int = Depends(require_current_organization_id)
):
    """Update an opportunity"""
    opportunity = db.query(Opportunity).filter(
        and_(Opportunity.id == opportunity_id, Opportunity.organization_id == org_id)
    ).first()
    
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    
    # Update fields
    update_data = opportunity_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(opportunity, field, value)
    
    # Recalculate expected revenue if amount or probability changed
    if "amount" in update_data or "probability" in update_data:
        opportunity.expected_revenue = opportunity.amount * (opportunity.probability / 100)
    
    # Set actual close date if stage changed to closed
    if "stage" in update_data and opportunity.stage in [OpportunityStage.CLOSED_WON, OpportunityStage.CLOSED_LOST]:
        if not opportunity.actual_close_date:
            opportunity.actual_close_date = date.today()
    
    opportunity.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(opportunity)
    
    return opportunity

# Sales Analytics
@router.get("/analytics", response_model=CRMAnalytics)
async def get_crm_analytics(
    period_start: date = Query(...),
    period_end: date = Query(...),
    db: Session = Depends(get_db),
    org_id: int = Depends(require_current_organization_id)
):
    """Get CRM analytics for a specific period"""
    # Lead analytics
    leads_query = db.query(Lead).filter(
        and_(
            Lead.organization_id == org_id,
            Lead.created_at >= period_start,
            Lead.created_at <= period_end + timedelta(days=1)
        )
    )
    
    leads_total = leads_query.count()
    leads_by_status = {}
    leads_by_source = {}
    
    for status in LeadStatus:
        count = leads_query.filter(Lead.status == status).count()
        leads_by_status[status.value] = count
    
    for source in LeadSource:
        count = leads_query.filter(Lead.source == source).count()
        leads_by_source[source.value] = count
    
    # Opportunity analytics
    opportunities_query = db.query(Opportunity).filter(
        and_(
            Opportunity.organization_id == org_id,
            Opportunity.created_at >= period_start,
            Opportunity.created_at <= period_end + timedelta(days=1)
        )
    )
    
    opportunities_total = opportunities_query.count()
    opportunities_by_stage = {}
    
    for stage in OpportunityStage:
        count = opportunities_query.filter(Opportunity.stage == stage).count()
        opportunities_by_stage[stage.value] = count
    
    # Pipeline values
    pipeline_value = db.query(func.sum(Opportunity.amount)).filter(
        and_(
            Opportunity.organization_id == org_id,
            Opportunity.stage.notin_([OpportunityStage.CLOSED_WON, OpportunityStage.CLOSED_LOST])
        )
    ).scalar() or 0
    
    weighted_pipeline_value = db.query(func.sum(Opportunity.expected_revenue)).filter(
        and_(
            Opportunity.organization_id == org_id,
            Opportunity.stage.notin_([OpportunityStage.CLOSED_WON, OpportunityStage.CLOSED_LOST])
        )
    ).scalar() or 0
    
    # Conversion rate
    converted_leads = leads_query.filter(Lead.status == LeadStatus.CONVERTED).count()
    conversion_rate = (converted_leads / leads_total * 100) if leads_total > 0 else 0
    
    # Win rate
    won_opportunities = opportunities_query.filter(Opportunity.stage == OpportunityStage.CLOSED_WON).count()
    closed_opportunities = opportunities_query.filter(
        Opportunity.stage.in_([OpportunityStage.CLOSED_WON, OpportunityStage.CLOSED_LOST])
    ).count()
    win_rate = (won_opportunities / closed_opportunities * 100) if closed_opportunities > 0 else 0
    
    # Average deal size
    avg_deal_size = db.query(func.avg(Opportunity.amount)).filter(
        and_(
            Opportunity.organization_id == org_id,
            Opportunity.stage == OpportunityStage.CLOSED_WON
        )
    ).scalar() or 0
    
    # Sales cycle (placeholder - would need more complex calculation)
    sales_cycle_days = 30.0  # Placeholder
    
    return CRMAnalytics(
        leads_total=leads_total,
        leads_by_status=leads_by_status,
        leads_by_source=leads_by_source,
        opportunities_total=opportunities_total,
        opportunities_by_stage=opportunities_by_stage,
        pipeline_value=float(pipeline_value),
        weighted_pipeline_value=float(weighted_pipeline_value),
        conversion_rate=conversion_rate,
        average_deal_size=float(avg_deal_size),
        sales_cycle_days=sales_cycle_days,
        win_rate=win_rate,
        period_start=period_start,
        period_end=period_end
    )