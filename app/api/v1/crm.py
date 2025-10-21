# app/api/v1/crm.py

from fastapi import APIRouter, Depends, HTTPException, Query, Path, BackgroundTasks, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc, asc
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
import logging

from app.core.database import get_db
from app.core.tenant import require_current_organization_id
from app.models.crm_models import (
    Lead, Opportunity, OpportunityProduct, LeadActivity, OpportunityActivity,
    SalesPipeline, SalesForecast, LeadStatus, LeadSource, OpportunityStage
)
from app.models.customer_models import Customer
from app.models.user_models import User
from app.models.vouchers.sales import SalesVoucher
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
from app.core.security import get_current_user as core_get_current_user
import secrets
import string

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/crm", tags=["CRM"])

async def generate_unique_number(db: AsyncSession, model_class, org_id: int, prefix: str) -> str:
    """Generate unique number for leads/opportunities"""
    while True:
        random_suffix = ''.join(secrets.choice(string.digits) for _ in range(6))
        number = f"{prefix}{random_suffix}"
        
        stmt = select(model_class).where(
            and_(
                model_class.organization_id == org_id,
                getattr(model_class, f"{prefix.lower()}_number") == number
            )
        )
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()
        
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
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(core_get_current_user),
    org_id: int = Depends(require_current_organization_id)
):
    """Get all leads with filtering and pagination"""
    # Check RBAC permissions
    rbac = RBACService(db)
    user_permissions = await rbac.get_user_service_permissions(current_user.id)
    logger.debug(f"User {current_user.email} permissions: {user_permissions}")
    if "crm_lead_read" not in user_permissions:
        logger.error(f"User {current_user.email} lacks 'crm_lead_read' permission")
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions to view leads"
        )

    try:
        stmt = select(Lead).where(Lead.organization_id == org_id)
        
        # Apply filters
        if status:
            if status not in [s.value for s in LeadStatus]:
                logger.error(f"Invalid status filter: {status}")
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid status: {status}. Valid values are {[s.value for s in LeadStatus]}"
                )
            stmt = stmt.where(Lead.status == status)
        if source:
            if source not in [s.value for s in LeadSource]:
                logger.error(f"Invalid source filter: {source}")
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid source: {source}. Valid values are {[s.value for s in LeadSource]}"
                )
            stmt = stmt.where(Lead.source == source)
        if assigned_to_id:
            stmt = stmt.where(Lead.assigned_to_id == assigned_to_id)
        if search:
            search_term = f"%{search}%"
            stmt = stmt.where(
                or_(
                    Lead.first_name.ilike(search_term),
                    Lead.last_name.ilike(search_term),
                    Lead.email.ilike(search_term),
                    Lead.company.ilike(search_term)
                )
            )
        
        # Order by created date descending
        stmt = stmt.order_by(desc(Lead.created_at))
        
        # Apply pagination
        stmt = stmt.offset(skip).limit(limit)
        
        result = await db.execute(stmt)
        leads = result.scalars().all()
        logger.info(f"Fetched {len(leads)} leads for org_id={org_id}, user={current_user.email}")
        return leads

    except Exception as e:
        logger.error(f"Error fetching leads for org_id={org_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch leads: {str(e)}"
        )

@router.post("/leads", response_model=LeadSchema)
async def create_lead(
    lead_data: LeadCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(core_get_current_user),
    org_id: int = Depends(require_current_organization_id)
):
    """Create a new lead"""
    # Check RBAC permissions
    rbac = RBACService(db)
    user_permissions = await rbac.get_user_service_permissions(current_user.id)
    logger.debug(f"User {current_user.email} permissions: {user_permissions}")
    if "crm_lead_create" not in user_permissions:
        logger.error(f"User {current_user.email} lacks 'crm_lead_create' permission")
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions to create leads"
        )

    try:
        # Generate unique lead number
        lead_number = await generate_unique_number(db, Lead, org_id, "LD")
        
        # Create lead
        lead = Lead(
            organization_id=org_id,
            lead_number=lead_number,
            created_by_id=current_user.id,
            **lead_data.model_dump()
        )
        
        db.add(lead)
        await db.commit()
        await db.refresh(lead)
        
        logger.info(f"Lead {lead_number} created by {current_user.email} in org {org_id}")
        return lead

    except Exception as e:
        logger.error(f"Error creating lead for org_id={org_id}: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create lead: {str(e)}"
        )

@router.get("/leads/{lead_id}", response_model=LeadSchema)
async def get_lead(
    lead_id: int = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(core_get_current_user),
    org_id: int = Depends(require_current_organization_id)
):
    """Get a specific lead"""
    # Check RBAC permissions
    rbac = RBACService(db)
    user_permissions = await rbac.get_user_service_permissions(current_user.id)
    logger.debug(f"User {current_user.email} permissions: {user_permissions}")
    if "crm_lead_read" not in user_permissions:
        logger.error(f"User {current_user.email} lacks 'crm_lead_read' permission")
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions to view lead"
        )

    try:
        stmt = select(Lead).where(
            and_(Lead.id == lead_id, Lead.organization_id == org_id)
        )
        result = await db.execute(stmt)
        lead = result.scalar_one_or_none()
        
        if not lead:
            logger.error(f"Lead {lead_id} not found for org_id={org_id}")
            raise HTTPException(status_code=404, detail="Lead not found")
        
        logger.info(f"Fetched lead {lead_id} for org_id={org_id}, user={current_user.email}")
        return lead

    except Exception as e:
        logger.error(f"Error fetching lead {lead_id} for org_id={org_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch lead: {str(e)}"
        )

@router.put("/leads/{lead_id}", response_model=LeadSchema)
async def update_lead(
    lead_data: LeadUpdate,
    lead_id: int = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(core_get_current_user),
    org_id: int = Depends(require_current_organization_id)
):
    """Update a lead"""
    # Check RBAC permissions
    rbac = RBACService(db)
    user_permissions = await rbac.get_user_service_permissions(current_user.id)
    logger.debug(f"User {current_user.email} permissions: {user_permissions}")
    if "crm_lead_update" not in user_permissions:
        logger.error(f"User {current_user.email} lacks 'crm_lead_update' permission")
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions to update lead"
        )

    try:
        stmt = select(Lead).where(
            and_(Lead.id == lead_id, Lead.organization_id == org_id)
        )
        result = await db.execute(stmt)
        lead = result.scalar_one_or_none()
        
        if not lead:
            logger.error(f"Lead {lead_id} not found for org_id={org_id}")
            raise HTTPException(status_code=404, detail="Lead not found")
        
        # Update fields
        update_data = lead_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(lead, field, value)
        
        lead.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(lead)
        
        logger.info(f"Lead {lead_id} updated by {current_user.email} in org {org_id}")
        return lead

    except Exception as e:
        logger.error(f"Error updating lead {lead_id} for org_id={org_id}: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update lead: {str(e)}"
        )

@router.delete("/leads/{lead_id}")
async def delete_lead(
    lead_id: int = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(core_get_current_user),
    org_id: int = Depends(require_current_organization_id)
):
    """Delete a lead"""
    # Check RBAC permissions
    rbac = RBACService(db)
    user_permissions = await rbac.get_user_service_permissions(current_user.id)
    logger.debug(f"User {current_user.email} permissions: {user_permissions}")
    if "crm_lead_delete" not in user_permissions:
        logger.error(f"User {current_user.email} lacks 'crm_lead_delete' permission")
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions to delete lead"
        )

    try:
        stmt = select(Lead).where(
            and_(Lead.id == lead_id, Lead.organization_id == org_id)
        )
        result = await db.execute(stmt)
        lead = result.scalar_one_or_none()
        
        if not lead:
            logger.error(f"Lead {lead_id} not found for org_id={org_id}")
            raise HTTPException(status_code=404, detail="Lead not found")
        
        await db.delete(lead)
        await db.commit()
        
        logger.info(f"Lead {lead_id} deleted by {current_user.email} in org {org_id}")
        return {"message": "Lead deleted successfully"}

    except Exception as e:
        logger.error(f"Error deleting lead {lead_id} for org_id={org_id}: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete lead: {str(e)}"
        )

@router.post("/leads/{lead_id}/convert", response_model=LeadConversionResponse)
async def convert_lead(
    conversion_data: LeadConversionRequest,
    lead_id: int = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(core_get_current_user),
    org_id: int = Depends(require_current_organization_id)
):
    """Convert lead to customer and/or opportunity"""
    # Check RBAC permissions
    rbac = RBACService(db)
    user_permissions = await rbac.get_user_service_permissions(current_user.id)
    logger.debug(f"User {current_user.email} permissions: {user_permissions}")
    if "crm_lead_convert" not in user_permissions:
        logger.error(f"User {current_user.email} lacks 'crm_lead_convert' permission")
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions to convert lead"
        )

    try:
        stmt = select(Lead).where(
            and_(Lead.id == lead_id, Lead.organization_id == org_id)
        )
        result = await db.execute(stmt)
        lead = result.scalar_one_or_none()
        
        if not lead:
            logger.error(f"Lead {lead_id} not found for org_id={org_id}")
            raise HTTPException(status_code=404, detail="Lead not found")
        
        if lead.status == LeadStatus.CONVERTED:
            logger.error(f"Lead {lead_id} already converted in org_id={org_id}")
            raise HTTPException(status_code=400, detail="Lead already converted")
        
        customer_id = None
        opportunity_id = None
        
        # Convert to customer
        if conversion_data.convert_to_customer:
            customer_data = conversion_data.customer_data or {}
            customer = Customer(
                organization_id=org_id,
                name=f"{lead.first_name} {lead.last_name}".strip(),
                email=lead.email,
                contact_number=lead.phone or "",
                contact_person=lead.full_name,
                address1=lead.address1 or "",
                address2=lead.address2 or "",
                city=lead.city or "",
                state=lead.state or "",
                pin_code=lead.pin_code or "",
                **customer_data
            )
            db.add(customer)
            await db.flush()
            customer_id = customer.id
        
        # Convert to opportunity
        if conversion_data.convert_to_opportunity:
            opportunity_data = conversion_data.opportunity_data or {}
            opportunity_number = await generate_unique_number(db, Opportunity, org_id, "OP")
            opportunity = Opportunity(
                organization_id=org_id,
                opportunity_number=opportunity_number,
                name=opportunity_data.get("name", f"Opportunity - {lead.company or lead.full_name}"),
                amount=opportunity_data.get("amount", lead.estimated_value or 0),
                expected_close_date=opportunity_data.get("expected_close_date", lead.expected_close_date or (date.today() + timedelta(days=30))),
                stage=OpportunityStage.PROSPECTING,
                probability=25.0,
                customer_id=customer_id,
                lead_id=lead.id,
                assigned_to_id=lead.assigned_to_id,
                source=lead.source,
                created_by_id=current_user.id,
                **{k: v for k, v in opportunity_data.items() if k not in ["name", "amount", "expected_close_date"]}
            )
            opportunity.expected_revenue = opportunity.amount * (opportunity.probability / 100)
            db.add(opportunity)
            await db.flush()
            opportunity_id = opportunity.id
        
        # Update lead status
        lead.status = LeadStatus.CONVERTED
        lead.converted_at = datetime.utcnow()
        lead.converted_to_customer_id = customer_id
        lead.converted_to_opportunity_id = opportunity_id
        
        await db.commit()
        
        logger.info(f"Lead {lead_id} converted by {current_user.email} in org {org_id}: customer_id={customer_id}, opportunity_id={opportunity_id}")
        return LeadConversionResponse(
            success=True,
            customer_id=customer_id,
            opportunity_id=opportunity_id,
            message="Lead converted successfully"
        )
        
    except Exception as e:
        logger.error(f"Error converting lead {lead_id} for org_id={org_id}: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")

# Lead Activities
@router.get("/leads/{lead_id}/activities", response_model=List[LeadActivitySchema])
async def get_lead_activities(
    lead_id: int = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(core_get_current_user),
    org_id: int = Depends(require_current_organization_id)
):
    """Get activities for a lead"""
    # Check RBAC permissions
    rbac = RBACService(db)
    user_permissions = await rbac.get_user_service_permissions(current_user.id)
    logger.debug(f"User {current_user.email} permissions: {user_permissions}")
    if "crm_lead_read" not in user_permissions:
        logger.error(f"User {current_user.email} lacks 'crm_lead_read' permission")
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions to view lead activities"
        )

    try:
        # Verify lead exists
        stmt = select(Lead).where(
            and_(Lead.id == lead_id, Lead.organization_id == org_id)
        )
        result = await db.execute(stmt)
        lead = result.scalar_one_or_none()
        
        if not lead:
            logger.error(f"Lead {lead_id} not found for org_id={org_id}")
            raise HTTPException(status_code=404, detail="Lead not found")
        
        stmt = select(LeadActivity).where(
            and_(LeadActivity.lead_id == lead_id, LeadActivity.organization_id == org_id)
        ).order_by(desc(LeadActivity.activity_date))
        
        result = await db.execute(stmt)
        activities = result.scalars().all()
        
        logger.info(f"Fetched {len(activities)} activities for lead {lead_id} in org {org_id}")
        return activities

    except Exception as e:
        logger.error(f"Error fetching activities for lead {lead_id} in org_id={org_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch lead activities: {str(e)}"
        )

@router.post("/leads/{lead_id}/activities", response_model=LeadActivitySchema)
async def create_lead_activity(
    activity_data: LeadActivityCreate,
    lead_id: int = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(core_get_current_user),
    org_id: int = Depends(require_current_organization_id)
):
    """Create a new lead activity"""
    # Check RBAC permissions
    rbac = RBACService(db)
    user_permissions = await rbac.get_user_service_permissions(current_user.id)
    logger.debug(f"User {current_user.email} permissions: {user_permissions}")
    if "crm_lead_activity_create" not in user_permissions:
        logger.error(f"User {current_user.email} lacks 'crm_lead_activity_create' permission")
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions to create lead activity"
        )

    try:
        # Verify lead exists
        stmt = select(Lead).where(
            and_(Lead.id == lead_id, Lead.organization_id == org_id)
        )
        result = await db.execute(stmt)
        lead = result.scalar_one_or_none()
        
        if not lead:
            logger.error(f"Lead {lead_id} not found for org_id={org_id}")
            raise HTTPException(status_code=404, detail="Lead not found")
        
        activity = LeadActivity(
            organization_id=org_id,
            lead_id=lead_id,
            created_by_id=current_user.id,
            **activity_data.model_dump(exclude={"lead_id"})
        )
        
        db.add(activity)
        
        # Update lead's last contacted time
        lead.last_contacted = datetime.utcnow()
        
        await db.commit()
        await db.refresh(activity)
        
        logger.info(f"Activity created for lead {lead_id} by {current_user.email} in org {org_id}")
        return activity

    except Exception as e:
        logger.error(f"Error creating activity for lead {lead_id} in org_id={org_id}: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create lead activity: {str(e)}"
        )

# Opportunity Management Endpoints
@router.get("/opportunities", response_model=List[OpportunitySchema])
async def get_opportunities(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    stage: Optional[str] = Query(None),
    assigned_to_id: Optional[int] = Query(None),
    customer_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(core_get_current_user),
    org_id: int = Depends(require_current_organization_id)
):
    """Get all opportunities with filtering and pagination"""
    # Check RBAC permissions
    rbac = RBACService(db)
    user_permissions = await rbac.get_user_service_permissions(current_user.id)
    logger.debug(f"User {current_user.email} permissions: {user_permissions}")
    if "crm_opportunity_read" not in user_permissions:
        logger.error(f"User {current_user.email} lacks 'crm_opportunity_read' permission")
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions to view opportunities"
        )

    try:
        stmt = select(Opportunity).where(Opportunity.organization_id == org_id)
        
        # Apply filters
        if stage:
            if stage not in [s.value for s in OpportunityStage]:
                logger.error(f"Invalid stage filter: {stage}")
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid stage: {stage}. Valid values are {[s.value for s in OpportunityStage]}"
                )
            stmt = stmt.where(Opportunity.stage == stage)
        if assigned_to_id:
            stmt = stmt.where(Opportunity.assigned_to_id == assigned_to_id)
        if customer_id:
            stmt = stmt.where(Opportunity.customer_id == customer_id)
        if search:
            search_term = f"%{search}%"
            stmt = stmt.where(
                or_(
                    Opportunity.name.ilike(search_term),
                    Opportunity.description.ilike(search_term)
                )
            )
        
        # Order by expected close date
        stmt = stmt.order_by(asc(Opportunity.expected_close_date))
        
        # Apply pagination
        stmt = stmt.offset(skip).limit(limit)
        
        result = await db.execute(stmt)
        opportunities = result.scalars().all()
        logger.info(f"Fetched {len(opportunities)} opportunities for org_id={org_id}, user={current_user.email}")
        return opportunities

    except Exception as e:
        logger.error(f"Error fetching opportunities for org_id={org_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch opportunities: {str(e)}"
        )

@router.post("/opportunities", response_model=OpportunitySchema)
async def create_opportunity(
    opportunity_data: OpportunityCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(core_get_current_user),
    org_id: int = Depends(require_current_organization_id)
):
    """Create a new opportunity"""
    # Check RBAC permissions
    rbac = RBACService(db)
    user_permissions = await rbac.get_user_service_permissions(current_user.id)
    logger.debug(f"User {current_user.email} permissions: {user_permissions}")
    if "crm_opportunity_create" not in user_permissions:
        logger.error(f"User {current_user.email} lacks 'crm_opportunity_create' permission")
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions to create opportunity"
        )

    try:
        # Generate unique opportunity number
        opportunity_number = await generate_unique_number(db, Opportunity, org_id, "OP")
        
        # Create opportunity
        opportunity = Opportunity(
            organization_id=org_id,
            opportunity_number=opportunity_number,
            created_by_id=current_user.id,
            **opportunity_data.model_dump()
        )
        
        # Calculate expected revenue
        opportunity.expected_revenue = opportunity.amount * (opportunity.probability / 100)
        
        db.add(opportunity)
        await db.commit()
        await db.refresh(opportunity)
        
        logger.info(f"Opportunity {opportunity_number} created by {current_user.email} in org {org_id}")
        return opportunity

    except Exception as e:
        logger.error(f"Error creating opportunity for org_id={org_id}: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create opportunity: {str(e)}"
        )

@router.get("/opportunities/{opportunity_id}", response_model=OpportunitySchema)
async def get_opportunity(
    opportunity_id: int = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(core_get_current_user),
    org_id: int = Depends(require_current_organization_id)
):
    """Get a specific opportunity"""
    # Check RBAC permissions
    rbac = RBACService(db)
    user_permissions = await rbac.get_user_service_permissions(current_user.id)
    logger.debug(f"User {current_user.email} permissions: {user_permissions}")
    if "crm_opportunity_read" not in user_permissions:
        logger.error(f"User {current_user.email} lacks 'crm_opportunity_read' permission")
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions to view opportunity"
        )

    try:
        stmt = select(Opportunity).where(
            and_(Opportunity.id == opportunity_id, Opportunity.organization_id == org_id)
        )
        result = await db.execute(stmt)
        opportunity = result.scalar_one_or_none()
        
        if not opportunity:
            logger.error(f"Opportunity {opportunity_id} not found for org_id={org_id}")
            raise HTTPException(status_code=404, detail="Opportunity not found")
        
        logger.info(f"Fetched opportunity {opportunity_id} for org_id={org_id}, user={current_user.email}")
        return opportunity

    except Exception as e:
        logger.error(f"Error fetching opportunity {opportunity_id} for org_id={org_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch opportunity: {str(e)}"
        )

@router.put("/opportunities/{opportunity_id}", response_model=OpportunitySchema)
async def update_opportunity(
    opportunity_data: OpportunityUpdate,
    opportunity_id: int = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(core_get_current_user),
    org_id: int = Depends(require_current_organization_id)
):
    """Update an opportunity"""
    # Check RBAC permissions
    rbac = RBACService(db)
    user_permissions = await rbac.get_user_service_permissions(current_user.id)
    logger.debug(f"User {current_user.email} permissions: {user_permissions}")
    if "crm_opportunity_update" not in user_permissions:
        logger.error(f"User {current_user.email} lacks 'crm_opportunity_update' permission")
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions to update opportunity"
        )

    try:
        stmt = select(Opportunity).where(
            and_(Opportunity.id == opportunity_id, Opportunity.organization_id == org_id)
        )
        result = await db.execute(stmt)
        opportunity = result.scalar_one_or_none()
        
        if not opportunity:
            logger.error(f"Opportunity {opportunity_id} not found for org_id={org_id}")
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
        await db.commit()
        await db.refresh(opportunity)
        
        logger.info(f"Opportunity {opportunity_id} updated by {current_user.email} in org {org_id}")
        return opportunity

    except Exception as e:
        logger.error(f"Error updating opportunity {opportunity_id} for org_id={org_id}: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update opportunity: {str(e)}"
        )

# Sales Analytics
@router.get("/analytics", response_model=CRMAnalytics)
async def get_crm_analytics(
    period_start: date = Query(...),
    period_end: date = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(core_get_current_user),
    org_id: int = Depends(require_current_organization_id)
):
    """Get CRM analytics for a specific period"""
    # Check RBAC permissions
    rbac = RBACService(db)
    user_permissions = await rbac.get_user_service_permissions(current_user.id)
    logger.debug(f"User {current_user.email} permissions: {user_permissions}")
    if current_user.role != "org_admin" and "crm_analytics_read" not in user_permissions:
        logger.error(f"User {current_user.email} lacks 'crm_analytics_read' permission")
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions to view CRM analytics"
        )

    try:
        # Lead analytics
        leads_stmt = select(Lead).where(
            and_(
                Lead.organization_id == org_id,
                Lead.created_at >= period_start,
                Lead.created_at <= period_end + timedelta(days=1)
            )
        )
        result = await db.execute(leads_stmt)
        leads = result.scalars().all()
        leads_total = len(leads)
        leads_by_status = {}
        leads_by_source = {}
        
        for status in LeadStatus:
            count = len([l for l in leads if l.status == status])
            leads_by_status[status.value] = count
        
        for source in LeadSource:
            count = len([l for l in leads if l.source == source])
            leads_by_source[source.value] = count
        
        # Opportunity analytics
        opportunities_stmt = select(Opportunity).where(
            and_(
                Opportunity.organization_id == org_id,
                Opportunity.created_at >= period_start,
                Opportunity.created_at <= period_end + timedelta(days=1)
            )
        )
        result = await db.execute(opportunities_stmt)
        opportunities = result.scalars().all()
        opportunities_total = len(opportunities)
        opportunities_by_stage = {}
        
        for stage in OpportunityStage:
            count = len([o for o in opportunities if o.stage == stage])
            opportunities_by_stage[stage.value] = count
        
        # Pipeline values
        pipeline_stmt = select(func.sum(Opportunity.amount)).where(
            and_(
                Opportunity.organization_id == org_id,
                Opportunity.stage.notin_([OpportunityStage.CLOSED_WON, OpportunityStage.CLOSED_LOST])
            )
        )
        pipeline_value = (await db.scalar(pipeline_stmt)) or 0
        
        weighted_stmt = select(func.sum(Opportunity.expected_revenue)).where(
            and_(
                Opportunity.organization_id == org_id,
                Opportunity.stage.notin_([OpportunityStage.CLOSED_WON, OpportunityStage.CLOSED_LOST])
            )
        )
        weighted_pipeline_value = (await db.scalar(weighted_stmt)) or 0
        
        # Conversion rate
        converted_leads = len([l for l in leads if l.status == LeadStatus.CONVERTED])
        conversion_rate = (converted_leads / leads_total * 100) if leads_total > 0 else 0
        
        # Win rate
        won_opportunities = len([o for o in opportunities if o.stage == OpportunityStage.CLOSED_WON])
        closed_opportunities = len([o for o in opportunities if o.stage in [OpportunityStage.CLOSED_WON, OpportunityStage.CLOSED_LOST]])
        win_rate = (won_opportunities / closed_opportunities * 100) if closed_opportunities > 0 else 0
        
        # Average deal size
        avg_stmt = select(func.avg(Opportunity.amount)).where(
            and_(
                Opportunity.organization_id == org_id,
                Opportunity.stage == OpportunityStage.CLOSED_WON
            )
        )
        avg_deal_size = (await db.scalar(avg_stmt)) or 0
        
        # Sales cycle (placeholder - would need more complex calculation)
        sales_cycle_days = 30.0
        
        logger.info(f"Fetched CRM analytics for org_id={org_id}, user={current_user.email}")
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

    except Exception as e:
        logger.error(f"Error fetching CRM analytics for org_id={org_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch CRM analytics: {str(e)}"
        )

@router.get("/customer-analytics", response_model=CustomerAnalytics)
async def get_customer_analytics(
    period_start: date = Query(...),
    period_end: date = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(core_get_current_user),
    org_id: int = Depends(require_current_organization_id)
):
    """Get customer analytics for a specific period"""
    # Check RBAC permissions
    rbac = RBACService(db)
    user_permissions = await rbac.get_user_service_permissions(current_user.id)
    logger.debug(f"User {current_user.email} permissions: {user_permissions}")
    if current_user.role != "org_admin" and "crm_customer_analytics_read" not in user_permissions:
        logger.error(f"User {current_user.email} lacks 'crm_customer_analytics_read' permission")
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions to view customer analytics"
        )

    try:
        # Total customers
        total_customers_stmt = select(func.count(Customer.id.distinct())).where(
            Customer.organization_id == org_id
        )
        total_customers = await db.scalar(total_customers_stmt) or 0
        
        # New customers in period
        new_customers_stmt = select(func.count(Customer.id.distinct())).where(
            and_(
                Customer.organization_id == org_id,
                Customer.created_at >= period_start,
                Customer.created_at <= period_end + timedelta(days=1)
            )
        )
        new_customers = await db.scalar(new_customers_stmt) or 0
        
        # Active customers (with sales in period)
        active_customers_stmt = select(func.count(SalesVoucher.customer_id.distinct())).where(
            and_(
                SalesVoucher.organization_id == org_id,
                SalesVoucher.date >= period_start,
                SalesVoucher.date <= period_end
            )
        )
        active_customers = await db.scalar(active_customers_stmt) or 0
        
        # Last purchase dates
        last_purchase_stmt = select(
            SalesVoucher.customer_id,
            func.max(SalesVoucher.date).label('last_purchase_date')
        ).where(
            SalesVoucher.organization_id == org_id
        ).group_by(SalesVoucher.customer_id)
        
        result = await db.execute(last_purchase_stmt)
        last_purchases = {row.customer_id: row.last_purchase_date for row in result.all()}
        
        # Churned customers (no purchase in last 90 days before period_start)
        churn_threshold = period_start - timedelta(days=90)
        churned_customers_stmt = select(func.count(Customer.id.distinct())).where(
            and_(
                Customer.organization_id == org_id,
                or_(
                    Customer.id.notin_(last_purchases.keys()),
                    func.coalesce(func.max(last_purchases[Customer.id]), Customer.created_at) < churn_threshold
                )
            )
        )
        churned_customers = await db.scalar(churned_customers_stmt) or 0
        
        # Total revenue in period
        revenue_stmt = select(func.sum(SalesVoucher.total_amount)).where(
            and_(
                SalesVoucher.organization_id == org_id,
                SalesVoucher.date >= period_start,
                SalesVoucher.date <= period_end
            )
        )
        total_revenue = float(await db.scalar(revenue_stmt) or 0)
        
        # Average lifetime value (total revenue ever / total customers)
        lifetime_revenue_stmt = select(func.sum(SalesVoucher.total_amount)).where(
            SalesVoucher.organization_id == org_id
        )
        lifetime_revenue = float(await db.scalar(lifetime_revenue_stmt) or 0)
        average_lifetime_value = lifetime_revenue / total_customers if total_customers > 0 else 0
        
        # ARPU (Average Revenue Per User) = total_revenue / active_customers
        arpu = total_revenue / active_customers if active_customers > 0 else 0
        
        # Retention rate = (active_customers / (active_customers + churned_customers)) * 100
        total_retained = active_customers
        retention_rate = (total_retained / (total_retained + churned_customers) * 100) if (total_retained + churned_customers) > 0 else 0
        
        # Average satisfaction score (placeholder - would need feedback data)
        average_satisfaction_score = 4.2
        
        # Customers by segment (placeholder - would need segment field on Customer)
        customers_by_segment = {
            "Enterprise": 45,
            "Mid-Market": 187,
            "Small Business": 456,
            "Startup": 557
        }
        
        # Top customers by revenue
        top_customers_stmt = select(
            Customer.id,
            Customer.name,
            func.sum(SalesVoucher.total_amount).label('revenue')
        ).join(SalesVoucher, SalesVoucher.customer_id == Customer.id).where(
            and_(
                Customer.organization_id == org_id,
                SalesVoucher.organization_id == org_id,
                SalesVoucher.date >= period_start,
                SalesVoucher.date <= period_end
            )
        ).group_by(Customer.id, Customer.name).order_by(desc('revenue')).limit(10)
        
        result = await db.execute(top_customers_stmt)
        top_customers = [{"id": r.id, "name": r.name, "revenue": float(r.revenue or 0)} for r in result.all()]
        
        logger.info(f"Fetched customer analytics for org_id={org_id}, user={current_user.email}")
        return CustomerAnalytics(
            total_customers=total_customers,
            active_customers=active_customers,
            new_customers=new_customers,
            churned_customers=churned_customers,
            total_revenue=total_revenue,
            average_lifetime_value=average_lifetime_value,
            average_satisfaction_score=average_satisfaction_score,
            customers_by_segment=customers_by_segment,
            top_customers=top_customers,
            period_start=period_start,
            period_end=period_end,
            arpu=arpu,
            retention_rate=retention_rate
        )

    except Exception as e:
        logger.error(f"Error fetching customer analytics for org_id={org_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch customer analytics: {str(e)}"
        )