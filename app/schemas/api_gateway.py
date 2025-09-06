# app/schemas/api_gateway.py

"""
API Gateway Management Schemas for unified API access control and monitoring
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum


class APIKeyStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    REVOKED = "revoked"
    EXPIRED = "expired"


class RateLimitType(str, Enum):
    PER_MINUTE = "per_minute"
    PER_HOUR = "per_hour"
    PER_DAY = "per_day"
    PER_MONTH = "per_month"


class AccessLevel(str, Enum):
    READ_ONLY = "read_only"
    READ_WRITE = "read_write"
    ADMIN = "admin"
    FULL_ACCESS = "full_access"


class LogLevel(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    DEBUG = "debug"


class WebhookStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    FAILED = "failed"


# API Key Schemas
class APIKeyBase(BaseModel):
    key_name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    access_level: AccessLevel = AccessLevel.READ_ONLY
    allowed_endpoints: Optional[List[str]] = None
    restricted_endpoints: Optional[List[str]] = None
    allowed_methods: Optional[List[str]] = Field(default=["GET"])
    rate_limit_requests: Optional[int] = Field(default=1000, gt=0)
    rate_limit_type: RateLimitType = RateLimitType.PER_HOUR
    allowed_ips: Optional[List[str]] = None
    expires_at: Optional[datetime] = None

    @validator('allowed_methods')
    def validate_http_methods(cls, v):
        if v:
            valid_methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']
            for method in v:
                if method.upper() not in valid_methods:
                    raise ValueError(f'Invalid HTTP method: {method}')
            return [method.upper() for method in v]
        return v

    @validator('allowed_ips')
    def validate_ip_addresses(cls, v):
        if v:
            import ipaddress
            for ip in v:
                try:
                    # Support both individual IPs and CIDR ranges
                    ipaddress.ip_network(ip, strict=False)
                except ipaddress.AddressValueError:
                    raise ValueError(f'Invalid IP address or CIDR range: {ip}')
        return v


class APIKeyCreate(APIKeyBase):
    company_id: Optional[int] = None


class APIKeyUpdate(BaseModel):
    key_name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[APIKeyStatus] = None
    access_level: Optional[AccessLevel] = None
    allowed_endpoints: Optional[List[str]] = None
    restricted_endpoints: Optional[List[str]] = None
    allowed_methods: Optional[List[str]] = None
    rate_limit_requests: Optional[int] = Field(None, gt=0)
    rate_limit_type: Optional[RateLimitType] = None
    allowed_ips: Optional[List[str]] = None
    expires_at: Optional[datetime] = None


class APIKeyResponse(APIKeyBase):
    id: int
    organization_id: int
    company_id: Optional[int]
    key_prefix: str
    status: APIKeyStatus
    current_usage: int
    last_used_at: Optional[datetime]
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class APIKeyWithDetails(APIKeyResponse):
    creator_name: Optional[str] = None
    usage_percentage: Optional[float] = None
    days_until_expiry: Optional[int] = None
    recent_usage_count: Optional[int] = None


class APIKeyGenerated(BaseModel):
    """Response when a new API key is generated"""
    api_key: str
    key_details: APIKeyResponse


# API Usage Log Schemas
class APIUsageLogResponse(BaseModel):
    id: int
    organization_id: int
    api_key_id: Optional[int]
    endpoint: str
    method: str
    request_ip: str
    user_agent: Optional[str]
    status_code: int
    response_size: Optional[int]
    response_time_ms: float
    error_message: Optional[str]
    timestamp: datetime
    request_id: Optional[str]

    class Config:
        from_attributes = True


class APIUsageLogWithDetails(APIUsageLogResponse):
    api_key_name: Optional[str] = None


# API Endpoint Schemas
class APIEndpointBase(BaseModel):
    path: str = Field(..., min_length=1, max_length=500)
    method: str = Field(..., pattern="^(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)$")
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    is_public: bool = False
    requires_auth: bool = True
    is_deprecated: bool = False
    rate_limit_requests: Optional[int] = Field(None, gt=0)
    rate_limit_type: Optional[RateLimitType] = None
    version: str = Field(default="v1", max_length=20)
    documentation_url: Optional[str] = Field(None, max_length=500)


class APIEndpointCreate(APIEndpointBase):
    pass


class APIEndpointUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    is_public: Optional[bool] = None
    requires_auth: Optional[bool] = None
    is_deprecated: Optional[bool] = None
    rate_limit_requests: Optional[int] = Field(None, gt=0)
    rate_limit_type: Optional[RateLimitType] = None
    version: Optional[str] = Field(None, max_length=20)
    documentation_url: Optional[str] = Field(None, max_length=500)


class APIEndpointResponse(APIEndpointBase):
    id: int
    organization_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Webhook Schemas
class WebhookBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    url: str = Field(..., min_length=1, max_length=1000)
    secret_key: Optional[str] = Field(None, max_length=255)
    events: List[str] = Field(..., min_items=1)
    entity_types: Optional[List[str]] = None
    headers: Optional[Dict[str, str]] = None
    auth_type: Optional[str] = Field(None, max_length=50)
    auth_config: Optional[Dict[str, Any]] = None
    max_retries: int = Field(default=3, ge=0, le=10)
    retry_delay_seconds: int = Field(default=60, ge=1)
    timeout_seconds: int = Field(default=30, ge=1, le=300)
    success_status_codes: Optional[List[int]] = Field(default=[200, 201, 202, 204])

    @validator('url')
    def validate_url(cls, v):
        import re
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        if not url_pattern.match(v):
            raise ValueError('Invalid URL format')
        return v

    @validator('success_status_codes')
    def validate_status_codes(cls, v):
        if v:
            for code in v:
                if not (100 <= code <= 599):
                    raise ValueError(f'Invalid HTTP status code: {code}')
        return v


class WebhookCreate(WebhookBase):
    company_id: Optional[int] = None


class WebhookUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    url: Optional[str] = Field(None, min_length=1, max_length=1000)
    status: Optional[WebhookStatus] = None
    secret_key: Optional[str] = Field(None, max_length=255)
    events: Optional[List[str]] = Field(None, min_items=1)
    entity_types: Optional[List[str]] = None
    headers: Optional[Dict[str, str]] = None
    auth_type: Optional[str] = Field(None, max_length=50)
    auth_config: Optional[Dict[str, Any]] = None
    max_retries: Optional[int] = Field(None, ge=0, le=10)
    retry_delay_seconds: Optional[int] = Field(None, ge=1)
    timeout_seconds: Optional[int] = Field(None, ge=1, le=300)
    success_status_codes: Optional[List[int]] = None


class WebhookResponse(WebhookBase):
    id: int
    organization_id: int
    company_id: Optional[int]
    status: WebhookStatus
    created_by: int
    created_at: datetime
    updated_at: datetime
    last_triggered_at: Optional[datetime]

    class Config:
        from_attributes = True


class WebhookWithDetails(WebhookResponse):
    creator_name: Optional[str] = None
    total_deliveries: int = 0
    successful_deliveries: int = 0
    failed_deliveries: int = 0
    success_rate_percentage: Optional[float] = None
    last_delivery_status: Optional[str] = None


# Webhook Delivery Schemas
class WebhookDeliveryResponse(BaseModel):
    id: int
    organization_id: int
    webhook_id: int
    event_type: str
    entity_type: str
    entity_id: int
    request_url: str
    response_status_code: Optional[int]
    response_time_ms: Optional[float]
    is_successful: bool
    error_message: Optional[str]
    attempt_number: int
    max_attempts: int
    next_retry_at: Optional[datetime]
    delivered_at: datetime

    class Config:
        from_attributes = True


class WebhookDeliveryWithDetails(WebhookDeliveryResponse):
    webhook_name: Optional[str] = None
    request_headers: Optional[Dict[str, Any]] = None
    response_headers: Optional[Dict[str, Any]] = None
    request_body: Optional[str] = None
    response_body: Optional[str] = None


# Rate Limit Rule Schemas
class RateLimitRuleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    api_key_id: Optional[int] = None
    endpoint_pattern: Optional[str] = Field(None, max_length=500)
    method: Optional[str] = Field(None, pattern="^(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)$")
    requests_limit: int = Field(..., gt=0)
    time_window_type: RateLimitType
    time_window_value: int = Field(default=1, gt=0)
    is_active: bool = True
    priority: int = Field(default=0, ge=0)
    block_request: bool = True
    send_warning: bool = False
    custom_message: Optional[str] = None


class RateLimitRuleCreate(RateLimitRuleBase):
    pass


class RateLimitRuleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    api_key_id: Optional[int] = None
    endpoint_pattern: Optional[str] = Field(None, max_length=500)
    method: Optional[str] = Field(None, pattern="^(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)$")
    requests_limit: Optional[int] = Field(None, gt=0)
    time_window_type: Optional[RateLimitType] = None
    time_window_value: Optional[int] = Field(None, gt=0)
    is_active: Optional[bool] = None
    priority: Optional[int] = Field(None, ge=0)
    block_request: Optional[bool] = None
    send_warning: Optional[bool] = None
    custom_message: Optional[str] = None


class RateLimitRuleResponse(RateLimitRuleBase):
    id: int
    organization_id: int
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RateLimitRuleWithDetails(RateLimitRuleResponse):
    api_key_name: Optional[str] = None
    creator_name: Optional[str] = None


# API Error Schemas
class APIErrorResponse(BaseModel):
    id: int
    organization_id: int
    api_key_id: Optional[int]
    error_code: str
    error_message: str
    endpoint: str
    method: str
    request_ip: str
    error_type: str
    severity: LogLevel
    is_resolved: bool
    resolved_by: Optional[int]
    resolved_at: Optional[datetime]
    resolution_notes: Optional[str]
    occurred_at: datetime
    request_id: Optional[str]

    class Config:
        from_attributes = True


class APIErrorWithDetails(APIErrorResponse):
    api_key_name: Optional[str] = None
    resolver_name: Optional[str] = None
    stack_trace: Optional[str] = None


class APIErrorResolve(BaseModel):
    resolution_notes: Optional[str] = None


# Dashboard and Analytics Schemas
class APIGatewayDashboardStats(BaseModel):
    total_api_keys: int
    active_api_keys: int
    total_requests_today: int
    successful_requests_today: int
    error_rate_percentage: float
    average_response_time_ms: float
    top_endpoints: List[Dict[str, Any]]
    recent_errors: List[APIErrorResponse]
    rate_limit_violations: int
    webhook_success_rate: float


class APIUsageStats(BaseModel):
    api_key_id: Optional[int]
    api_key_name: Optional[str]
    total_requests: int
    successful_requests: int
    error_requests: int
    average_response_time_ms: float
    data_transferred_mb: float
    last_request_at: Optional[datetime]
    top_endpoints: List[Dict[str, Any]]


# Filter Schemas
class APIKeyFilter(BaseModel):
    status: Optional[APIKeyStatus] = None
    access_level: Optional[AccessLevel] = None
    created_by: Optional[int] = None
    expires_from: Optional[datetime] = None
    expires_to: Optional[datetime] = None
    search: Optional[str] = None


class APIUsageLogFilter(BaseModel):
    api_key_id: Optional[int] = None
    endpoint: Optional[str] = None
    method: Optional[str] = None
    status_code_from: Optional[int] = None
    status_code_to: Optional[int] = None
    timestamp_from: Optional[datetime] = None
    timestamp_to: Optional[datetime] = None
    request_ip: Optional[str] = None
    has_error: Optional[bool] = None


class WebhookFilter(BaseModel):
    status: Optional[WebhookStatus] = None
    event_type: Optional[str] = None
    created_by: Optional[int] = None
    search: Optional[str] = None


# List Response Schemas
class APIKeyList(BaseModel):
    api_keys: List[APIKeyWithDetails]
    total: int
    page: int
    per_page: int
    total_pages: int


class APIUsageLogList(BaseModel):
    logs: List[APIUsageLogWithDetails]
    total: int
    page: int
    per_page: int
    total_pages: int


class WebhookList(BaseModel):
    webhooks: List[WebhookWithDetails]
    total: int
    page: int
    per_page: int
    total_pages: int


# Bulk Operations
class BulkAPIKeyUpdate(BaseModel):
    api_key_ids: List[int] = Field(..., min_items=1)
    status: Optional[APIKeyStatus] = None
    rate_limit_requests: Optional[int] = Field(None, gt=0)
    rate_limit_type: Optional[RateLimitType] = None


class BulkWebhookUpdate(BaseModel):
    webhook_ids: List[int] = Field(..., min_items=1)
    status: Optional[WebhookStatus] = None


# Test and Validation Schemas
class WebhookTestRequest(BaseModel):
    test_event: str
    test_data: Dict[str, Any]


class WebhookTestResponse(BaseModel):
    success: bool
    status_code: Optional[int]
    response_time_ms: Optional[float]
    error_message: Optional[str]
    response_body: Optional[str]


class APIKeyTestRequest(BaseModel):
    endpoint: str
    method: str = "GET"
    headers: Optional[Dict[str, str]] = None
    body: Optional[Dict[str, Any]] = None


class APIKeyTestResponse(BaseModel):
    success: bool
    status_code: Optional[int]
    response_time_ms: Optional[float]
    error_message: Optional[str]
    rate_limit_remaining: Optional[int]