"""
OAuth2 and Email Token Schemas
"""

from pydantic import BaseModel, EmailStr, HttpUrl, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

from app.models.oauth_models import OAuthProvider, TokenStatus


class OAuthProviderEnum(str, Enum):
    GOOGLE = "google"
    MICROSOFT = "microsoft"
    OUTLOOK = "outlook"
    GMAIL = "gmail"


class TokenStatusEnum(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    REFRESH_FAILED = "refresh_failed"


# OAuth2 Flow Schemas
class OAuthLoginRequest(BaseModel):
    provider: OAuthProviderEnum
    redirect_uri: Optional[str] = None
    scope: Optional[str] = None


class OAuthLoginResponse(BaseModel):
    authorization_url: str
    state: str
    provider: OAuthProviderEnum


class OAuthCallbackRequest(BaseModel):
    code: str
    state: str
    scope: Optional[str] = None
    error: Optional[str] = None
    error_description: Optional[str] = None


class OAuthTokenResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    expires_in: Optional[int] = None
    scope: Optional[str] = None
    token_type: str = "Bearer"


# User Email Token Schemas
class UserEmailTokenBase(BaseModel):
    provider: OAuthProviderEnum
    email_address: EmailStr
    display_name: Optional[str] = None
    scope: Optional[str] = None
    sync_enabled: bool = True
    sync_folders: Optional[List[str]] = None


class UserEmailTokenCreate(UserEmailTokenBase):
    access_token: str
    refresh_token: Optional[str] = None
    id_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    provider_metadata: Optional[Dict[str, Any]] = None


class UserEmailTokenUpdate(BaseModel):
    display_name: Optional[str] = None
    sync_enabled: Optional[bool] = None
    sync_folders: Optional[List[str]] = None
    status: Optional[TokenStatusEnum] = None


class UserEmailTokenResponse(UserEmailTokenBase):
    id: int
    user_id: int
    organization_id: int
    token_type: str
    expires_at: Optional[datetime]
    status: TokenStatusEnum
    last_sync_at: Optional[datetime]
    last_sync_status: Optional[str]
    last_sync_error: Optional[str]
    created_at: datetime
    updated_at: datetime
    last_used_at: Optional[datetime]
    refresh_count: int
    
    # Hide sensitive token data in response
    has_access_token: bool = True
    has_refresh_token: bool = False
    is_expired: bool = False
    is_active: bool = False

    class Config:
        from_attributes = True


class UserEmailTokenWithDetails(UserEmailTokenResponse):
    provider_metadata: Optional[Dict[str, Any]] = None


# OAuth State Schemas
class OAuthStateCreate(BaseModel):
    state: str
    provider: OAuthProviderEnum
    redirect_uri: Optional[str] = None
    scope: Optional[str] = None
    code_verifier: Optional[str] = None
    nonce: Optional[str] = None
    expires_at: datetime


class OAuthStateResponse(BaseModel):
    id: int
    state: str
    provider: OAuthProviderEnum
    user_id: Optional[int]
    organization_id: Optional[int]
    redirect_uri: Optional[str]
    scope: Optional[str]
    expires_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# Email Management Schemas (OAuth2-specific)
class EmailSyncRequest(BaseModel):
    token_id: int
    folders: Optional[List[str]] = None
    force_sync: bool = False


class EmailSyncResponse(BaseModel):
    success: bool
    message: str
    synced_emails: int = 0
    errors: List[str] = []
    last_sync_at: datetime


class EmailProviderConfig(BaseModel):
    provider: OAuthProviderEnum
    client_id: str
    scopes: List[str]
    authorization_endpoint: str
    token_endpoint: str
    api_base_url: str


class EmailComposeRequest(BaseModel):
    token_id: int
    to: List[EmailStr]
    cc: Optional[List[EmailStr]] = None
    bcc: Optional[List[EmailStr]] = None
    subject: str
    body: str
    html_body: Optional[str] = None
    attachments: Optional[List[str]] = None  # File paths or base64 data


class EmailComposeResponse(BaseModel):
    success: bool
    message: str
    message_id: Optional[str] = None
    sent_at: Optional[datetime] = None


class EmailListRequest(BaseModel):
    token_id: int
    folder: str = "INBOX"
    limit: int = 50
    offset: int = 0
    unread_only: bool = False
    search_query: Optional[str] = None


class EmailMessage(BaseModel):
    id: str
    subject: str
    sender: str
    recipients: List[str]
    received_at: datetime
    body_preview: Optional[str] = None
    is_read: bool = False
    has_attachments: bool = False
    folder: str


class EmailListResponse(BaseModel):
    emails: List[EmailMessage]
    total_count: int
    has_more: bool = False


class EmailDetailRequest(BaseModel):
    token_id: int
    message_id: str
    folder: str = "INBOX"


class EmailAttachment(BaseModel):
    id: str
    name: str
    content_type: str
    size: int
    download_url: Optional[str] = None


class EmailDetailResponse(EmailMessage):
    body_html: Optional[str] = None
    body_text: Optional[str] = None
    attachments: List[EmailAttachment] = []
    headers: Optional[Dict[str, str]] = None