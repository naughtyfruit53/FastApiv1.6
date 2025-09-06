# app/api/v1/api_gateway.py

"""
API Gateway Management API endpoints for unified API access control and monitoring
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status, BackgroundTasks
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc, asc
from typing import List, Optional
from datetime import datetime, timedelta
import secrets
import hashlib

from app.core.database import get_db
from app.api.v1.auth import get_current_active_user as get_current_user
from app.models.user_models import User
from app.models.api_gateway_models import (
    APIKey, APIUsageLog, APIEndpoint, Webhook, WebhookDelivery,
    RateLimitRule, APIError
)
from app.schemas.api_gateway import (
    APIKeyCreate, APIKeyUpdate, APIKeyResponse, APIKeyWithDetails, APIKeyList, APIKeyFilter,
    APIKeyGenerated, APIKeyTestRequest, APIKeyTestResponse,
    APIUsageLogResponse, APIUsageLogWithDetails, APIUsageLogList, APIUsageLogFilter,
    APIEndpointCreate, APIEndpointUpdate, APIEndpointResponse,
    WebhookCreate, WebhookUpdate, WebhookResponse, WebhookWithDetails, WebhookList, WebhookFilter,
    WebhookTestRequest, WebhookTestResponse, WebhookDeliveryResponse, WebhookDeliveryWithDetails,
    RateLimitRuleCreate, RateLimitRuleUpdate, RateLimitRuleResponse, RateLimitRuleWithDetails,
    APIErrorResponse, APIErrorWithDetails, APIErrorResolve,
    APIGatewayDashboardStats, APIUsageStats, BulkAPIKeyUpdate, BulkWebhookUpdate
)
from app.services.rbac import require_permission, RBACService

router = APIRouter()

# Dashboard
@router.get("/dashboard", response_model=APIGatewayDashboardStats)
async def get_api_gateway_dashboard(
    company_id: Optional[int] = Query(None, description="Filter by specific company"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get API Gateway dashboard statistics"""
    org_id = current_user.organization_id
    rbac = RBACService(db)
    
    # Get user's accessible companies
    user_companies = rbac.get_user_companies(current_user.id)
    
    # Build base queries
    api_key_query = db.query(APIKey).filter(APIKey.organization_id == org_id)
    usage_query = db.query(APIUsageLog).filter(APIUsageLog.organization_id == org_id)
    webhook_query = db.query(Webhook).filter(Webhook.organization_id == org_id)
    
    if company_id is not None:
        if company_id not in user_companies:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: User does not have access to the specified company"
            )
        api_key_query = api_key_query.filter(APIKey.company_id == company_id)
        webhook_query = webhook_query.filter(Webhook.company_id == company_id)
    else:
        api_key_query = api_key_query.filter(
            or_(APIKey.company_id.in_(user_companies), APIKey.company_id.is_(None))
        )
        webhook_query = webhook_query.filter(
            or_(Webhook.company_id.in_(user_companies), Webhook.company_id.is_(None))
        )
    
    # Calculate statistics
    total_api_keys = api_key_query.count()
    active_api_keys = api_key_query.filter(APIKey.status == 'active').count()
    
    # Today's requests
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    total_requests_today = usage_query.filter(APIUsageLog.timestamp >= today_start).count()
    successful_requests_today = usage_query.filter(
        APIUsageLog.timestamp >= today_start,
        APIUsageLog.status_code.between(200, 299)
    ).count()
    
    error_rate = 0.0
    if total_requests_today > 0:
        error_rate = ((total_requests_today - successful_requests_today) / total_requests_today) * 100
    
    # Average response time today
    avg_response_time = db.query(
        func.avg(APIUsageLog.response_time_ms).label('avg_ms')
    ).filter(
        APIUsageLog.organization_id == org_id,
        APIUsageLog.timestamp >= today_start
    ).scalar() or 0.0
    
    # Top endpoints
    top_endpoints = db.query(
        APIUsageLog.endpoint,
        func.count(APIUsageLog.id).label('request_count'),
        func.avg(APIUsageLog.response_time_ms).label('avg_response_time')
    ).filter(
        APIUsageLog.organization_id == org_id,
        APIUsageLog.timestamp >= today_start
    ).group_by(APIUsageLog.endpoint).order_by(
        desc('request_count')
    ).limit(10).all()
    
    top_endpoints_data = [
        {
            "endpoint": endpoint,
            "request_count": count,
            "avg_response_time": float(avg_time) if avg_time else 0.0
        }
        for endpoint, count, avg_time in top_endpoints
    ]
    
    # Recent errors
    recent_errors = db.query(APIError).filter(
        APIError.organization_id == org_id,
        APIError.occurred_at >= today_start
    ).order_by(desc(APIError.occurred_at)).limit(10).all()
    
    # Rate limit violations
    rate_limit_violations = usage_query.filter(
        APIUsageLog.timestamp >= today_start,
        APIUsageLog.status_code == 429
    ).count()
    
    # Webhook success rate
    webhook_deliveries = db.query(WebhookDelivery).join(Webhook).filter(
        Webhook.organization_id == org_id,
        WebhookDelivery.delivered_at >= today_start
    ).count()
    
    successful_deliveries = db.query(WebhookDelivery).join(Webhook).filter(
        Webhook.organization_id == org_id,
        WebhookDelivery.delivered_at >= today_start,
        WebhookDelivery.is_successful == True
    ).count()
    
    webhook_success_rate = 0.0
    if webhook_deliveries > 0:
        webhook_success_rate = (successful_deliveries / webhook_deliveries) * 100
    
    return APIGatewayDashboardStats(
        total_api_keys=total_api_keys,
        active_api_keys=active_api_keys,
        total_requests_today=total_requests_today,
        successful_requests_today=successful_requests_today,
        error_rate_percentage=error_rate,
        average_response_time_ms=avg_response_time,
        top_endpoints=top_endpoints_data,
        recent_errors=[APIErrorResponse.from_orm(e) for e in recent_errors],
        rate_limit_violations=rate_limit_violations,
        webhook_success_rate=webhook_success_rate
    )

# API Key Management
@router.post("/api-keys", response_model=APIKeyGenerated)
@require_permission("api_gateway", "create")
async def create_api_key(
    api_key_data: APIKeyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new API key"""
    org_id = current_user.organization_id
    rbac = RBACService(db)
    
    # Validate company access
    if api_key_data.company_id:
        user_companies = rbac.get_user_companies(current_user.id)
        if api_key_data.company_id not in user_companies:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: User does not have access to the specified company"
            )
    
    # Check for duplicate name
    existing = db.query(APIKey).filter(
        APIKey.organization_id == org_id,
        APIKey.key_name == api_key_data.key_name
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="API key with this name already exists"
        )
    
    # Generate API key
    api_key = f"sk-{secrets.token_urlsafe(32)}"
    key_prefix = api_key[:8]
    
    # Hash the API key for storage
    hashed_key = hashlib.sha256(api_key.encode()).hexdigest()
    
    # Create API key record
    db_api_key = APIKey(
        organization_id=org_id,
        company_id=api_key_data.company_id,
        key_name=api_key_data.key_name,
        api_key=hashed_key,
        key_prefix=key_prefix,
        description=api_key_data.description,
        access_level=api_key_data.access_level,
        allowed_endpoints=api_key_data.allowed_endpoints,
        restricted_endpoints=api_key_data.restricted_endpoints,
        allowed_methods=api_key_data.allowed_methods,
        rate_limit_requests=api_key_data.rate_limit_requests,
        rate_limit_type=api_key_data.rate_limit_type,
        allowed_ips=api_key_data.allowed_ips,
        expires_at=api_key_data.expires_at,
        created_by=current_user.id
    )
    
    db.add(db_api_key)
    db.commit()
    db.refresh(db_api_key)
    
    return APIKeyGenerated(
        api_key=api_key,  # Return the actual key only once
        key_details=APIKeyResponse.from_orm(db_api_key)
    )

@router.get("/api-keys", response_model=APIKeyList)
async def list_api_keys(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(50, ge=1, le=100, description="Items per page"),
    company_id: Optional[int] = Query(None, description="Filter by company"),
    filters: APIKeyFilter = Depends(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List API keys with filtering and pagination"""
    org_id = current_user.organization_id
    rbac = RBACService(db)
    
    # Get user's accessible companies
    user_companies = rbac.get_user_companies(current_user.id)
    
    # Build query
    query = db.query(APIKey).filter(APIKey.organization_id == org_id)
    
    # Company filtering
    if company_id is not None:
        if company_id not in user_companies:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: User does not have access to the specified company"
            )
        query = query.filter(APIKey.company_id == company_id)
    else:
        query = query.filter(
            or_(APIKey.company_id.in_(user_companies), APIKey.company_id.is_(None))
        )
    
    # Apply filters
    if filters.status:
        query = query.filter(APIKey.status == filters.status)
    if filters.access_level:
        query = query.filter(APIKey.access_level == filters.access_level)
    if filters.created_by:
        query = query.filter(APIKey.created_by == filters.created_by)
    if filters.expires_from:
        query = query.filter(APIKey.expires_at >= filters.expires_from)
    if filters.expires_to:
        query = query.filter(APIKey.expires_at <= filters.expires_to)
    if filters.search:
        search_term = f"%{filters.search}%"
        query = query.filter(
            or_(
                APIKey.key_name.ilike(search_term),
                APIKey.description.ilike(search_term)
            )
        )
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * per_page
    api_keys = query.options(
        joinedload(APIKey.creator)
    ).offset(offset).limit(per_page).all()
    
    # Build response with details
    api_key_details = []
    for key in api_keys:
        # Calculate usage percentage
        usage_percentage = None
        if key.rate_limit_requests and key.rate_limit_requests > 0:
            usage_percentage = (key.current_usage / key.rate_limit_requests) * 100
        
        # Days until expiry
        days_until_expiry = None
        if key.expires_at:
            days_until_expiry = (key.expires_at.date() - datetime.now().date()).days
        
        # Recent usage
        recent_usage = db.query(APIUsageLog).filter(
            APIUsageLog.api_key_id == key.id,
            APIUsageLog.timestamp >= datetime.now() - timedelta(hours=24)
        ).count()
        
        key_detail = APIKeyWithDetails(
            **key.__dict__,
            creator_name=key.creator.full_name if key.creator else None,
            usage_percentage=usage_percentage,
            days_until_expiry=days_until_expiry,
            recent_usage_count=recent_usage
        )
        api_key_details.append(key_detail)
    
    total_pages = (total + per_page - 1) // per_page
    
    return APIKeyList(
        api_keys=api_key_details,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages
    )

@router.put("/api-keys/{api_key_id}", response_model=APIKeyResponse)
@require_permission("api_gateway", "update")
async def update_api_key(
    api_key_id: int,
    api_key_update: APIKeyUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an API key"""
    org_id = current_user.organization_id
    rbac = RBACService(db)
    
    api_key = db.query(APIKey).filter(
        APIKey.id == api_key_id,
        APIKey.organization_id == org_id
    ).first()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    # Check company access
    user_companies = rbac.get_user_companies(current_user.id)
    if api_key.company_id and api_key.company_id not in user_companies:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: User does not have access to this API key's company"
        )
    
    # Update fields
    update_data = api_key_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(api_key, field, value)
    
    api_key.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(api_key)
    
    return APIKeyResponse.from_orm(api_key)

@router.delete("/api-keys/{api_key_id}")
@require_permission("api_gateway", "delete")
async def delete_api_key(
    api_key_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an API key"""
    org_id = current_user.organization_id
    rbac = RBACService(db)
    
    api_key = db.query(APIKey).filter(
        APIKey.id == api_key_id,
        APIKey.organization_id == org_id
    ).first()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    # Check company access
    user_companies = rbac.get_user_companies(current_user.id)
    if api_key.company_id and api_key.company_id not in user_companies:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: User does not have access to this API key's company"
        )
    
    db.delete(api_key)
    db.commit()
    
    return {"message": "API key deleted successfully"}

# API Usage Logs
@router.get("/usage-logs", response_model=APIUsageLogList)
async def list_usage_logs(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(100, ge=1, le=1000, description="Items per page"),
    filters: APIUsageLogFilter = Depends(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List API usage logs with filtering and pagination"""
    org_id = current_user.organization_id
    
    # Build query
    query = db.query(APIUsageLog).filter(APIUsageLog.organization_id == org_id)
    
    # Apply filters
    if filters.api_key_id:
        query = query.filter(APIUsageLog.api_key_id == filters.api_key_id)
    if filters.endpoint:
        query = query.filter(APIUsageLog.endpoint.ilike(f"%{filters.endpoint}%"))
    if filters.method:
        query = query.filter(APIUsageLog.method == filters.method)
    if filters.status_code_from:
        query = query.filter(APIUsageLog.status_code >= filters.status_code_from)
    if filters.status_code_to:
        query = query.filter(APIUsageLog.status_code <= filters.status_code_to)
    if filters.timestamp_from:
        query = query.filter(APIUsageLog.timestamp >= filters.timestamp_from)
    if filters.timestamp_to:
        query = query.filter(APIUsageLog.timestamp <= filters.timestamp_to)
    if filters.request_ip:
        query = query.filter(APIUsageLog.request_ip == filters.request_ip)
    if filters.has_error is not None:
        if filters.has_error:
            query = query.filter(APIUsageLog.error_message.isnot(None))
        else:
            query = query.filter(APIUsageLog.error_message.is_(None))
    
    # Get total count
    total = query.count()
    
    # Apply pagination and ordering
    offset = (page - 1) * per_page
    logs = query.options(
        joinedload(APIUsageLog.api_key)
    ).order_by(desc(APIUsageLog.timestamp)).offset(offset).limit(per_page).all()
    
    # Build response with details
    log_details = []
    for log in logs:
        log_detail = APIUsageLogWithDetails(
            **log.__dict__,
            api_key_name=log.api_key.key_name if log.api_key else None
        )
        log_details.append(log_detail)
    
    total_pages = (total + per_page - 1) // per_page
    
    return APIUsageLogList(
        logs=log_details,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages
    )

# Webhook Management
@router.post("/webhooks", response_model=WebhookResponse)
@require_permission("api_gateway", "create")
async def create_webhook(
    webhook_data: WebhookCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new webhook"""
    org_id = current_user.organization_id
    rbac = RBACService(db)
    
    # Validate company access
    if webhook_data.company_id:
        user_companies = rbac.get_user_companies(current_user.id)
        if webhook_data.company_id not in user_companies:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: User does not have access to the specified company"
            )
    
    # Check for duplicate name
    existing = db.query(Webhook).filter(
        Webhook.organization_id == org_id,
        Webhook.name == webhook_data.name
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Webhook with this name already exists"
        )
    
    # Create webhook
    db_webhook = Webhook(
        organization_id=org_id,
        company_id=webhook_data.company_id,
        name=webhook_data.name,
        description=webhook_data.description,
        url=webhook_data.url,
        secret_key=webhook_data.secret_key,
        events=webhook_data.events,
        entity_types=webhook_data.entity_types,
        headers=webhook_data.headers,
        auth_type=webhook_data.auth_type,
        auth_config=webhook_data.auth_config,
        max_retries=webhook_data.max_retries,
        retry_delay_seconds=webhook_data.retry_delay_seconds,
        timeout_seconds=webhook_data.timeout_seconds,
        success_status_codes=webhook_data.success_status_codes,
        created_by=current_user.id
    )
    
    db.add(db_webhook)
    db.commit()
    db.refresh(db_webhook)
    
    return WebhookResponse.from_orm(db_webhook)

@router.get("/webhooks", response_model=WebhookList)
async def list_webhooks(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(50, ge=1, le=100, description="Items per page"),
    company_id: Optional[int] = Query(None, description="Filter by company"),
    filters: WebhookFilter = Depends(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List webhooks with filtering and pagination"""
    org_id = current_user.organization_id
    rbac = RBACService(db)
    
    # Get user's accessible companies
    user_companies = rbac.get_user_companies(current_user.id)
    
    # Build query
    query = db.query(Webhook).filter(Webhook.organization_id == org_id)
    
    # Company filtering
    if company_id is not None:
        if company_id not in user_companies:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: User does not have access to the specified company"
            )
        query = query.filter(Webhook.company_id == company_id)
    else:
        query = query.filter(
            or_(Webhook.company_id.in_(user_companies), Webhook.company_id.is_(None))
        )
    
    # Apply filters
    if filters.status:
        query = query.filter(Webhook.status == filters.status)
    if filters.event_type:
        query = query.filter(Webhook.events.contains([filters.event_type]))
    if filters.created_by:
        query = query.filter(Webhook.created_by == filters.created_by)
    if filters.search:
        search_term = f"%{filters.search}%"
        query = query.filter(
            or_(
                Webhook.name.ilike(search_term),
                Webhook.description.ilike(search_term),
                Webhook.url.ilike(search_term)
            )
        )
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * per_page
    webhooks = query.options(
        joinedload(Webhook.creator)
    ).offset(offset).limit(per_page).all()
    
    # Build response with details
    webhook_details = []
    for webhook in webhooks:
        # Get delivery statistics
        total_deliveries = db.query(WebhookDelivery).filter(
            WebhookDelivery.webhook_id == webhook.id
        ).count()
        
        successful_deliveries = db.query(WebhookDelivery).filter(
            WebhookDelivery.webhook_id == webhook.id,
            WebhookDelivery.is_successful == True
        ).count()
        
        failed_deliveries = total_deliveries - successful_deliveries
        success_rate = (successful_deliveries / total_deliveries * 100) if total_deliveries > 0 else 0.0
        
        # Last delivery status
        last_delivery = db.query(WebhookDelivery).filter(
            WebhookDelivery.webhook_id == webhook.id
        ).order_by(desc(WebhookDelivery.delivered_at)).first()
        
        webhook_detail = WebhookWithDetails(
            **webhook.__dict__,
            creator_name=webhook.creator.full_name if webhook.creator else None,
            total_deliveries=total_deliveries,
            successful_deliveries=successful_deliveries,
            failed_deliveries=failed_deliveries,
            success_rate_percentage=success_rate,
            last_delivery_status="successful" if last_delivery and last_delivery.is_successful else "failed" if last_delivery else None
        )
        webhook_details.append(webhook_detail)
    
    total_pages = (total + per_page - 1) // per_page
    
    return WebhookList(
        webhooks=webhook_details,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages
    )