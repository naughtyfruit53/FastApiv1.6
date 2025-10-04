# app/schemas/email_schemas.py

"""
Pydantic schemas for email API endpoints
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, validator

from app.models.email import (
    EmailAccountType, EmailSyncStatus, EmailStatus, EmailPriority
)


# Mail Account Schemas
class MailAccountBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email_address: EmailStr
    display_name: Optional[str] = Field(None, max_length=255)
    account_type: EmailAccountType
    provider: Optional[str] = Field(None, max_length=50)
    
    # IMAP/SMTP settings
    incoming_server: Optional[str] = Field(None, max_length=255)
    incoming_port: Optional[int] = Field(None, ge=1, le=65535)
    incoming_ssl: bool = True
    incoming_auth_method: Optional[str] = Field(None, max_length=50)
    
    outgoing_server: Optional[str] = Field(None, max_length=255)
    outgoing_port: Optional[int] = Field(None, ge=1, le=65535)
    outgoing_ssl: bool = True
    outgoing_auth_method: Optional[str] = Field(None, max_length=50)
    
    # Sync configuration
    sync_enabled: bool = True
    sync_frequency_minutes: int = Field(15, ge=1, le=1440)  # 1 minute to 24 hours
    sync_folders: Optional[List[str]] = Field(default=["INBOX"])
    
    # Integration settings
    auto_link_to_customers: bool = True
    auto_link_to_vendors: bool = True
    auto_create_tasks: bool = False


class MailAccountCreate(MailAccountBase):
    username: Optional[str] = Field(None, max_length=255)
    password: Optional[str] = Field(None, min_length=1)
    oauth_token_id: Optional[int] = None
    
    @validator('password', 'oauth_token_id')
    def validate_auth_method(cls, v, values):
        # Ensure at least one authentication method is provided
        if 'username' in values and values['username']:
            if not v and 'oauth_token_id' not in values:
                raise ValueError('Password or OAuth token required when username is provided')
        return v


class MailAccountUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    display_name: Optional[str] = Field(None, max_length=255)
    
    # IMAP/SMTP settings
    incoming_server: Optional[str] = Field(None, max_length=255)
    incoming_port: Optional[int] = Field(None, ge=1, le=65535)
    incoming_ssl: Optional[bool] = None
    
    outgoing_server: Optional[str] = Field(None, max_length=255)
    outgoing_port: Optional[int] = Field(None, ge=1, le=65535)
    outgoing_ssl: Optional[bool] = None
    
    # Authentication
    username: Optional[str] = Field(None, max_length=255)
    password: Optional[str] = Field(None, min_length=1)
    oauth_token_id: Optional[int] = None
    
    # Sync configuration
    sync_enabled: Optional[bool] = None
    sync_frequency_minutes: Optional[int] = Field(None, ge=1, le=1440)
    sync_folders: Optional[List[str]] = None
    
    # Integration settings
    auto_link_to_customers: Optional[bool] = None
    auto_link_to_vendors: Optional[bool] = None
    auto_create_tasks: Optional[bool] = None


class MailAccountResponse(BaseModel):
    id: int
    name: str
    email_address: str
    display_name: Optional[str]
    account_type: EmailAccountType
    provider: Optional[str]
    
    # Server settings (without sensitive data)
    incoming_server: Optional[str]
    incoming_port: Optional[int]
    incoming_ssl: bool
    
    outgoing_server: Optional[str]
    outgoing_port: Optional[int]
    outgoing_ssl: bool
    
    # Sync configuration
    sync_enabled: bool
    sync_frequency_minutes: int
    sync_folders: Optional[List[str]]
    full_sync_completed: bool
    
    # Integration settings
    auto_link_to_customers: bool
    auto_link_to_vendors: bool
    auto_create_tasks: bool
    
    # Status
    is_active: bool
    sync_status: EmailSyncStatus
    last_sync_at: Optional[datetime]
    last_sync_error: Optional[str]
    total_messages_synced: int
    
    # Organization and user
    organization_id: int
    user_id: int
    
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# Email Schemas
class EmailAddressSchema(BaseModel):
    name: Optional[str]
    email: str


class EmailListItemResponse(BaseModel):
    id: int
    message_id: str
    subject: str
    from_address: str
    from_name: Optional[str]
    reply_to: Optional[str]
    
    to_addresses: List[EmailAddressSchema]
    cc_addresses: Optional[List[EmailAddressSchema]]
    bcc_addresses: Optional[List[EmailAddressSchema]]
    
    body_text: Optional[str]
    body_html: Optional[str]
    
    status: EmailStatus
    priority: EmailPriority
    is_flagged: bool
    is_important: bool
    has_attachments: bool
    
    sent_at: datetime
    received_at: datetime
    folder: Optional[str]
    labels: Optional[List[str]]
    
    # Business linking
    customer_id: Optional[int]
    vendor_id: Optional[int]
    
    # Thread
    thread_id: Optional[int]
    
    # Metadata
    size_bytes: Optional[int]
    
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class EmailResponse(EmailListItemResponse):
    # Attachments (if included)
    attachments: Optional[List['EmailAttachmentResponse']] = None
    
    class Config:
        from_attributes = True

# Email List Response
class EmailListResponse(BaseModel):
    emails: List[EmailListItemResponse]
    total_count: int
    offset: int
    limit: int
    has_more: bool
    folder: str


# Email Thread Schemas
class EmailThreadResponse(BaseModel):
    id: int
    thread_id: str
    subject: str
    original_subject: str
    
    participants: List[str]
    primary_participants: List[str]
    
    message_count: int
    unread_count: int
    has_attachments: bool
    
    status: EmailStatus
    priority: EmailPriority
    is_flagged: bool
    is_important: bool
    
    first_message_at: datetime
    last_message_at: datetime
    last_activity_at: datetime
    
    # Business linking
    customer_id: Optional[int]
    vendor_id: Optional[int]
    
    # Metadata
    folder: Optional[str]
    labels: Optional[List[str]]
    
    # Organization and account
    organization_id: int
    account_id: int
    
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# Email Attachment Schemas
class EmailAttachmentResponse(BaseModel):
    id: int
    filename: str
    original_filename: str
    content_type: Optional[str]
    size_bytes: Optional[int]
    
    content_id: Optional[str]
    content_disposition: Optional[str]
    
    is_inline: bool
    is_safe: Optional[bool]
    is_quarantined: bool
    
    download_count: int
    last_downloaded_at: Optional[datetime]
    
    created_at: datetime
    
    class Config:
        from_attributes = True


# Sync Schemas
class SyncLogResponse(BaseModel):
    id: int
    sync_type: str
    folder: Optional[str]
    status: str
    
    messages_processed: int
    messages_new: int
    messages_updated: int
    messages_deleted: int
    
    error_message: Optional[str]
    
    started_at: datetime
    completed_at: Optional[datetime]
    duration_seconds: Optional[float]
    
    class Config:
        from_attributes = True


class SyncStatusResponse(BaseModel):
    account_id: int
    email_address: str
    sync_enabled: bool
    sync_status: str
    
    last_sync_at: Optional[datetime]
    last_sync_error: Optional[str]
    total_messages_synced: int
    full_sync_completed: bool
    
    latest_sync: Optional[Dict[str, Any]]
    
    class Config:
        from_attributes = True


class ManualSyncRequest(BaseModel):
    full_sync: bool = Field(False, description="Perform full sync instead of incremental")
    folder: Optional[str] = Field(None, description="Sync specific folder only")


# OAuth Token Schemas
class OAuthTokenInfo(BaseModel):
    id: int
    provider: str
    email_address: str
    display_name: Optional[str]
    status: str
    scopes: Optional[List[str]]
    
    is_expired: bool
    is_active: bool
    
    created_at: datetime
    expires_at: Optional[datetime]
    last_used_at: Optional[datetime]
    refresh_count: int
    
    class Config:
        from_attributes = True


# Update forward references
EmailResponse.model_rebuild()
EmailThreadResponse.model_rebuild()