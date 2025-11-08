# app/api/v1/marketing.py

from fastapi import APIRouter, Depends, HTTPException, Query, Path, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta

from app.core.database import get_db
from app.core.enforcement import require_access
from app.core.tenant import require_current_organization_id
from app.models.marketing_models import (
    Campaign, Promotion, PromotionRedemption, CampaignAnalytics,
    MarketingList, MarketingListContact, CampaignType, CampaignStatus, PromotionType
)
from app.models.customer_models import Customer
from app.models.user_models import User
from app.schemas.marketing import (
    Campaign as CampaignSchema, CampaignCreate, CampaignUpdate,
    Promotion as PromotionSchema, PromotionCreate, PromotionUpdate,
    PromotionRedemption as PromotionRedemptionSchema, PromotionRedemptionCreate,
    CampaignAnalytics as CampaignAnalyticsSchema, CampaignAnalyticsCreate, CampaignAnalyticsUpdate,
    MarketingList as MarketingListSchema, MarketingListCreate, MarketingListUpdate,
    MarketingListContact as MarketingListContactSchema, MarketingListContactCreate, MarketingListContactUpdate,
    CampaignPerformanceReport, MarketingAnalytics, PromotionAnalytics,
    CampaignImportData, CampaignImportResponse, ContactImportData, ContactImportResponse
)
from app.services.rbac import RBACService
import secrets
import string
import uuid

router = APIRouter(prefix="/marketing", tags=["Marketing"])

def generate_campaign_number(db: Session, org_id: int) -> str:
    """Generate unique campaign number"""
    while True:
        random_suffix = ''.join(secrets.choice(string.digits) for _ in range(6))
        number = f"CMP{random_suffix}"
        
        existing = db.query(Campaign).filter(
            and_(Campaign.organization_id == org_id, Campaign.campaign_number == number)
        ).first()
        
        if not existing:
            return number

def generate_promotion_code(db: Session, org_id: int) -> str:
    """Generate unique promotion code"""
    while True:
        random_suffix = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        code = f"PROMO-{random_suffix}"
        
        existing = db.query(Promotion).filter(
            and_(Promotion.organization_id == org_id, Promotion.promotion_code == code)
        ).first()
        
        if not existing:
            return code

# Campaign Management Endpoints
@router.get("/campaigns", response_model=List[CampaignSchema])
async def get_campaigns(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    campaign_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    assigned_to_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    auth: tuple = Depends(require_access("marketing", "read"))
):
    """Get all campaigns with filtering and pagination"""
    query = db.query(Campaign).filter(Campaign.organization_id == org_id)
    
    # Apply filters
    if campaign_type:
        query = query.filter(Campaign.campaign_type == campaign_type)
    if status:
        query = query.filter(Campaign.status == status)
    if assigned_to_id:
        query = query.filter(Campaign.assigned_to_id == assigned_to_id)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Campaign.name.ilike(search_term),
                Campaign.description.ilike(search_term)
            )
        )
    
    # Order by created date descending
    query = query.order_by(desc(Campaign.created_at))
    
    # Apply pagination
    campaigns = query.offset(skip).limit(limit).all()
    return campaigns

@router.post("/campaigns", response_model=CampaignSchema)
async def create_campaign(
    campaign_data: CampaignCreate,
    db: Session = Depends(get_db),
    auth: tuple = Depends(require_access("marketing", "create"))
):
    """Create a new campaign"""
    current_user, org_id = auth

    # Generate unique campaign number
    campaign_number = generate_campaign_number(db, org_id)
    
    # Create campaign
    campaign = Campaign(
        organization_id=org_id,
        campaign_number=campaign_number,
        **campaign_data.model_dump()
    )
    
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    
    return campaign

@router.get("/campaigns/{campaign_id}", response_model=CampaignSchema)
async def get_campaign(
    campaign_id: int = Path(...),
    db: Session = Depends(get_db),
    auth: tuple = Depends(require_access("marketing", "read"))
):
    """Get a specific campaign"""
    current_user, org_id = auth

    campaign = db.query(Campaign).filter(
        and_(Campaign.id == campaign_id, Campaign.organization_id == org_id)
    ).first()
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    return campaign

@router.put("/campaigns/{campaign_id}", response_model=CampaignSchema)
async def update_campaign(
    campaign_data: CampaignUpdate,
    campaign_id: int = Path(...),
    db: Session = Depends(get_db),
    auth: tuple = Depends(require_access("marketing", "update"))
):
    """Update a campaign"""
    current_user, org_id = auth

    campaign = db.query(Campaign).filter(
        and_(Campaign.id == campaign_id, Campaign.organization_id == org_id)
    ).first()
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Update fields
    update_data = campaign_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(campaign, field, value)
    
    campaign.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(campaign)
    
    return campaign

@router.delete("/campaigns/{campaign_id}")
async def delete_campaign(
    campaign_id: int = Path(...),
    db: Session = Depends(get_db),
    auth: tuple = Depends(require_access("marketing", "delete"))
):
    """Delete a campaign"""
    current_user, org_id = auth

    campaign = db.query(Campaign).filter(
        and_(Campaign.id == campaign_id, Campaign.organization_id == org_id)
    ).first()
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    if campaign.status == CampaignStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Cannot delete active campaign")
    
    db.delete(campaign)
    db.commit()
    
    return {"message": "Campaign deleted successfully"}

@router.post("/campaigns/{campaign_id}/launch")
async def launch_campaign(
    campaign_id: int = Path(...),
    db: Session = Depends(get_db),
    auth: tuple = Depends(require_access("marketing", "create"))
):
    """Launch a campaign"""
    current_user, org_id = auth

    campaign = db.query(Campaign).filter(
        and_(Campaign.id == campaign_id, Campaign.organization_id == org_id)
    ).first()
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    if campaign.status != CampaignStatus.DRAFT:
        raise HTTPException(status_code=400, detail="Only draft campaigns can be launched")
    
    campaign.status = CampaignStatus.ACTIVE
    campaign.launched_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Campaign launched successfully"}

@router.post("/campaigns/{campaign_id}/pause")
async def pause_campaign(
    campaign_id: int = Path(...),
    db: Session = Depends(get_db),
    auth: tuple = Depends(require_access("marketing", "create"))
):
    """Pause a campaign"""
    current_user, org_id = auth

    campaign = db.query(Campaign).filter(
        and_(Campaign.id == campaign_id, Campaign.organization_id == org_id)
    ).first()
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    if campaign.status != CampaignStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Only active campaigns can be paused")
    
    campaign.status = CampaignStatus.PAUSED
    db.commit()
    
    return {"message": "Campaign paused successfully"}

@router.post("/campaigns/{campaign_id}/complete")
async def complete_campaign(
    campaign_id: int = Path(...),
    db: Session = Depends(get_db),
    auth: tuple = Depends(require_access("marketing", "create"))
):
    """Complete a campaign"""
    current_user, org_id = auth

    campaign = db.query(Campaign).filter(
        and_(Campaign.id == campaign_id, Campaign.organization_id == org_id)
    ).first()
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    if campaign.status not in [CampaignStatus.ACTIVE, CampaignStatus.PAUSED]:
        raise HTTPException(status_code=400, detail="Only active or paused campaigns can be completed")
    
    campaign.status = CampaignStatus.COMPLETED
    campaign.completed_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Campaign completed successfully"}

# Promotion Management Endpoints
@router.get("/promotions", response_model=List[PromotionSchema])
async def get_promotions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    promotion_type: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    campaign_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    auth: tuple = Depends(require_access("marketing", "read"))
):
    """Get all promotions with filtering and pagination"""
    current_user, org_id = auth

    query = db.query(Promotion).filter(Promotion.organization_id == org_id)
    
    # Apply filters
    if promotion_type:
        query = query.filter(Promotion.promotion_type == promotion_type)
    if is_active is not None:
        query = query.filter(Promotion.is_active == is_active)
    if campaign_id:
        query = query.filter(Promotion.campaign_id == campaign_id)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Promotion.name.ilike(search_term),
                Promotion.promotion_code.ilike(search_term),
                Promotion.description.ilike(search_term)
            )
        )
    
    # Order by created date descending
    query = query.order_by(desc(Promotion.created_at))
    
    # Apply pagination
    promotions = query.offset(skip).limit(limit).all()
    return promotions

@router.post("/promotions", response_model=PromotionSchema)
async def create_promotion(
    promotion_data: PromotionCreate,
    db: Session = Depends(get_db),
    auth: tuple = Depends(require_access("marketing", "create"))
):
    """Create a new promotion"""
    current_user, org_id = auth

    # Check if promotion code already exists
    existing = db.query(Promotion).filter(
        and_(
            Promotion.organization_id == org_id,
            Promotion.promotion_code == promotion_data.promotion_code
        )
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Promotion code already exists")
    
    # Create promotion
    promotion = Promotion(
        organization_id=org_id,
        **promotion_data.model_dump()
    )
    
    db.add(promotion)
    db.commit()
    db.refresh(promotion)
    
    return promotion

@router.get("/promotions/{promotion_id}", response_model=PromotionSchema)
async def get_promotion(
    promotion_id: int = Path(...),
    db: Session = Depends(get_db),
    auth: tuple = Depends(require_access("marketing", "read"))
):
    """Get a specific promotion"""
    current_user, org_id = auth

    promotion = db.query(Promotion).filter(
        and_(Promotion.id == promotion_id, Promotion.organization_id == org_id)
    ).first()
    
    if not promotion:
        raise HTTPException(status_code=404, detail="Promotion not found")
    
    return promotion

@router.put("/promotions/{promotion_id}", response_model=PromotionSchema)
async def update_promotion(
    promotion_data: PromotionUpdate,
    promotion_id: int = Path(...),
    db: Session = Depends(get_db),
    auth: tuple = Depends(require_access("marketing", "update"))
):
    """Update a promotion"""
    current_user, org_id = auth

    promotion = db.query(Promotion).filter(
        and_(Promotion.id == promotion_id, Promotion.organization_id == org_id)
    ).first()
    
    if not promotion:
        raise HTTPException(status_code=404, detail="Promotion not found")
    
    # Update fields
    update_data = promotion_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(promotion, field, value)
    
    promotion.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(promotion)
    
    return promotion

@router.delete("/promotions/{promotion_id}")
async def delete_promotion(
    promotion_id: int = Path(...),
    db: Session = Depends(get_db),
    auth: tuple = Depends(require_access("marketing", "delete"))
):
    """Delete a promotion"""
    current_user, org_id = auth

    promotion = db.query(Promotion).filter(
        and_(Promotion.id == promotion_id, Promotion.organization_id == org_id)
    ).first()
    
    if not promotion:
        raise HTTPException(status_code=404, detail="Promotion not found")
    
    # Check if promotion has been used
    redemptions = db.query(PromotionRedemption).filter(
        PromotionRedemption.promotion_id == promotion_id
    ).count()
    
    if redemptions > 0:
        raise HTTPException(status_code=400, detail="Cannot delete promotion that has been used")
    
    db.delete(promotion)
    db.commit()
    
    return {"message": "Promotion deleted successfully"}

@router.get("/promotions/validate/{promotion_code}")
async def validate_promotion(
    promotion_code: str = Path(...),
    order_amount: float = Query(..., ge=0),
    customer_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    auth: tuple = Depends(require_access("marketing", "read"))
):
    """Validate a promotion code"""
    current_user, org_id = auth

    promotion = db.query(Promotion).filter(
        and_(
            Promotion.organization_id == org_id,
            Promotion.promotion_code == promotion_code,
            Promotion.is_active == True
        )
    ).first()
    
    if not promotion:
        raise HTTPException(status_code=404, detail="Promotion not found or inactive")
    
    # Check validity dates
    today = date.today()
    if promotion.valid_from > today:
        raise HTTPException(status_code=400, detail="Promotion not yet valid")
    
    if promotion.valid_until and promotion.valid_until < today:
        raise HTTPException(status_code=400, detail="Promotion expired")
    
    # Check minimum purchase amount
    if promotion.minimum_purchase_amount and order_amount < promotion.minimum_purchase_amount:
        raise HTTPException(
            status_code=400,
            detail=f"Minimum purchase amount of {promotion.minimum_purchase_amount} required"
        )
    
    # Check usage limits
    if promotion.usage_limit_total and promotion.current_usage_count >= promotion.usage_limit_total:
        raise HTTPException(status_code=400, detail="Promotion usage limit reached")
    
    if promotion.usage_limit_per_customer and customer_id:
        customer_usage = db.query(PromotionRedemption).filter(
            and_(
                PromotionRedemption.promotion_id == promotion.id,
                PromotionRedemption.customer_id == customer_id
            )
        ).count()
        
        if customer_usage >= promotion.usage_limit_per_customer:
            raise HTTPException(status_code=400, detail="Customer usage limit reached for this promotion")
    
    # Calculate discount
    discount_amount = 0.0
    if promotion.promotion_type == PromotionType.PERCENTAGE_DISCOUNT:
        discount_amount = order_amount * (promotion.discount_percentage / 100)
        if promotion.maximum_discount_amount:
            discount_amount = min(discount_amount, promotion.maximum_discount_amount)
    elif promotion.promotion_type == PromotionType.FIXED_AMOUNT_DISCOUNT:
        discount_amount = promotion.discount_amount
    
    final_amount = max(0, order_amount - discount_amount)
    
    return {
        "valid": True,
        "promotion": promotion,
        "discount_amount": discount_amount,
        "final_amount": final_amount,
        "message": "Promotion is valid"
    }

@router.post("/promotions/{promotion_id}/redeem", response_model=PromotionRedemptionSchema)
async def redeem_promotion(
    redemption_data: PromotionRedemptionCreate,
    promotion_id: int = Path(...),
    db: Session = Depends(get_db),
    auth: tuple = Depends(require_access("marketing", "create"))
):
    """Redeem a promotion"""
    current_user, org_id = auth

    promotion = db.query(Promotion).filter(
        and_(Promotion.id == promotion_id, Promotion.organization_id == org_id)
    ).first()
    
    if not promotion:
        raise HTTPException(status_code=404, detail="Promotion not found")
    
    # Validate promotion first (basic checks)
    today = date.today()
    if not promotion.is_active:
        raise HTTPException(status_code=400, detail="Promotion is inactive")
    
    if promotion.valid_from > today:
        raise HTTPException(status_code=400, detail="Promotion not yet valid")
    
    if promotion.valid_until and promotion.valid_until < today:
        raise HTTPException(status_code=400, detail="Promotion expired")
    
    # Check minimum purchase amount
    if promotion.minimum_purchase_amount and redemption_data.order_amount < promotion.minimum_purchase_amount:
        raise HTTPException(
            status_code=400,
            detail=f"Minimum purchase amount of {promotion.minimum_purchase_amount} required"
        )
    
    # Check usage limits
    if promotion.usage_limit_total and promotion.current_usage_count >= promotion.usage_limit_total:
        raise HTTPException(status_code=400, detail="Promotion usage limit reached")
    
    if promotion.usage_limit_per_customer and redemption_data.customer_id:
        customer_usage = db.query(PromotionRedemption).filter(
            and_(
                PromotionRedemption.promotion_id == promotion.id,
                PromotionRedemption.customer_id == redemption_data.customer_id
            )
        ).count()
        
        if customer_usage >= promotion.usage_limit_per_customer:
            raise HTTPException(status_code=400, detail="Customer usage limit reached for this promotion")
    
    # Create redemption record
    redemption = PromotionRedemption(
        organization_id=org_id,
        promotion_id=promotion_id,
        **redemption_data.model_dump()
    )
    
    # Update promotion usage counts
    promotion.current_usage_count += 1
    promotion.total_redemptions += 1
    promotion.total_discount_given += redemption_data.discount_amount
    promotion.total_revenue_impact += redemption_data.final_amount
    
    db.add(redemption)
    db.commit()
    db.refresh(redemption)
    
    return redemption

# Marketing Lists
@router.get("/lists", response_model=List[MarketingListSchema])
async def get_marketing_lists(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    list_type: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    auth: tuple = Depends(require_access("marketing", "read"))
):
    """Get all marketing lists"""
    current_user, org_id = auth

    query = db.query(MarketingList).filter(MarketingList.organization_id == org_id)
    
    # Apply filters
    if list_type:
        query = query.filter(MarketingList.list_type == list_type)
    if is_active is not None:
        query = query.filter(MarketingList.is_active == is_active)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                MarketingList.name.ilike(search_term),
                MarketingList.description.ilike(search_term)
            )
        )
    
    # Order by created date descending
    query = query.order_by(desc(MarketingList.created_at))
    
    # Apply pagination
    lists = query.offset(skip).limit(limit).all()
    return lists

@router.post("/lists", response_model=MarketingListSchema)
async def create_marketing_list(
    list_data: MarketingListCreate,
    db: Session = Depends(get_db),
    auth: tuple = Depends(require_access("marketing", "create"))
):
    """Create a new marketing list"""
    current_user, org_id = auth

    # Check if list name already exists
    existing = db.query(MarketingList).filter(
        and_(
            MarketingList.organization_id == org_id,
            MarketingList.name == list_data.name
        )
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Marketing list name already exists")
    
    # Create marketing list
    marketing_list = MarketingList(
        organization_id=org_id,
        **list_data.model_dump()
    )
    
    db.add(marketing_list)
    db.commit()
    db.refresh(marketing_list)
    
    return marketing_list

# Marketing Analytics
@router.get("/analytics", response_model=MarketingAnalytics)
async def get_marketing_analytics(
    period_start: date = Query(...),
    period_end: date = Query(...),
    db: Session = Depends(get_db),
    auth: tuple = Depends(require_access("marketing", "read"))
):
    """Get marketing analytics for a specific period"""
    current_user, org_id = auth

    # Campaign analytics
    campaigns_query = db.query(Campaign).filter(
        and_(
            Campaign.organization_id == org_id,
            Campaign.created_at >= period_start,
            Campaign.created_at <= period_end + timedelta(days=1)
        )
    )
    
    total_campaigns = campaigns_query.count()
    active_campaigns = campaigns_query.filter(Campaign.status == CampaignStatus.ACTIVE).count()
    completed_campaigns = campaigns_query.filter(Campaign.status == CampaignStatus.COMPLETED).count()
    
    # Contact analytics
    contacts_query = db.query(MarketingListContact).filter(
        MarketingListContact.organization_id == org_id
    )
    
    total_contacts = contacts_query.count()
    total_subscribers = contacts_query.filter(MarketingListContact.is_subscribed == True).count()
    total_unsubscribes = contacts_query.filter(MarketingListContact.is_subscribed == False).count()
    
    # Performance metrics (aggregated from campaigns)
    campaigns = campaigns_query.all()
    
    total_delivered = sum(c.delivered_count for c in campaigns)
    total_opened = sum(c.opened_count for c in campaigns)
    total_clicked = sum(c.clicked_count for c in campaigns)
    total_converted = sum(c.converted_count for c in campaigns)
    
    average_open_rate = (total_opened / total_delivered * 100) if total_delivered > 0 else 0
    average_click_rate = (total_clicked / total_delivered * 100) if total_delivered > 0 else 0
    average_conversion_rate = (total_converted / total_delivered * 100) if total_delivered > 0 else 0
    
    # Financial metrics
    total_marketing_spend = sum(c.budget or 0 for c in campaigns)
    total_marketing_revenue = sum(c.revenue_generated for c in campaigns)
    marketing_roi = ((total_marketing_revenue - total_marketing_spend) / total_marketing_spend * 100) if total_marketing_spend > 0 else 0
    
    # Top performing campaigns
    top_performing_campaigns = [
        {
            "id": c.id,
            "name": c.name,
            "revenue": c.revenue_generated,
            "roi": c.return_on_investment or 0,
            "conversion_rate": (c.converted_count / c.delivered_count * 100) if c.delivered_count > 0 else 0
        }
        for c in sorted(campaigns, key=lambda x: x.revenue_generated, reverse=True)[:5]
    ]
    
    return MarketingAnalytics(
        total_campaigns=total_campaigns,
        active_campaigns=active_campaigns,
        completed_campaigns=completed_campaigns,
        total_contacts=total_contacts,
        total_subscribers=total_subscribers,
        total_unsubscribes=total_unsubscribes,
        average_open_rate=average_open_rate,
        average_click_rate=average_click_rate,
        average_conversion_rate=average_conversion_rate,
        total_marketing_spend=total_marketing_spend,
        total_marketing_revenue=total_marketing_revenue,
        marketing_roi=marketing_roi,
        top_performing_campaigns=top_performing_campaigns,
        period_start=period_start,
        period_end=period_end
    )

@router.get("/analytics/promotions", response_model=PromotionAnalytics)
async def get_promotion_analytics(
    period_start: date = Query(...),
    period_end: date = Query(...),
    db: Session = Depends(get_db),
    auth: tuple = Depends(require_access("marketing", "read"))
):
    """Get promotion analytics for a specific period"""
    current_user, org_id = auth

    # Promotion analytics
    promotions_query = db.query(Promotion).filter(
        and_(
            Promotion.organization_id == org_id,
            Promotion.created_at >= period_start,
            Promotion.created_at <= period_end + timedelta(days=1)
        )
    )
    
    total_promotions = promotions_query.count()
    active_promotions = promotions_query.filter(Promotion.is_active == True).count()
    
    # Redemption analytics
    redemptions_query = db.query(PromotionRedemption).join(Promotion).filter(
        and_(
            Promotion.organization_id == org_id,
            PromotionRedemption.redeemed_at >= period_start,
            PromotionRedemption.redeemed_at <= period_end + timedelta(days=1)
        )
    )
    
    total_redemptions = redemptions_query.count()
    total_discount_given = db.query(func.sum(PromotionRedemption.discount_amount)).filter(
        PromotionRedemption.id.in_([r.id for r in redemptions_query.all()])
    ).scalar() or 0
    
    total_revenue_impact = db.query(func.sum(PromotionRedemption.final_amount)).filter(
        PromotionRedemption.id.in_([r.id for r in redemptions_query.all()])
    ).scalar() or 0
    
    average_discount_per_redemption = (total_discount_given / total_redemptions) if total_redemptions > 0 else 0
    
    # Most popular promotions
    promotion_usage = {}
    for redemption in redemptions_query.all():
        if redemption.promotion_id not in promotion_usage:
            promotion_usage[redemption.promotion_id] = 0
        promotion_usage[redemption.promotion_id] += 1
    
    most_popular_promotions = []
    for promotion_id, count in sorted(promotion_usage.items(), key=lambda x: x[1], reverse=True)[:5]:
        promotion = db.query(Promotion).filter(Promotion.id == promotion_id).first()
        if promotion:
            most_popular_promotions.append({
                "id": promotion.id,
                "name": promotion.name,
                "code": promotion.promotion_code,
                "redemptions": count
            })
    
    # Promotion types performance
    promotion_types_performance = {}
    for promotion_type in PromotionType:
        type_promotions = promotions_query.filter(Promotion.promotion_type == promotion_type).all()
        total_type_redemptions = sum(p.total_redemptions for p in type_promotions)
        total_type_discount = sum(p.total_discount_given for p in type_promotions)
        
        promotion_types_performance[promotion_type.value] = {
            "count": len(type_promotions),
            "redemptions": total_type_redemptions,
            "discount_given": total_type_discount
        }
    
    return PromotionAnalytics(
        total_promotions=total_promotions,
        active_promotions=active_promotions,
        total_redemptions=total_redemptions,
        total_discount_given=float(total_discount_given),
        total_revenue_impact=float(total_revenue_impact),
        average_discount_per_redemption=average_discount_per_redemption,
        most_popular_promotions=most_popular_promotions,
        promotion_types_performance=promotion_types_performance,
        period_start=period_start,
        period_end=period_end
    )