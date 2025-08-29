# app/schemas/mail_schemas.py

"""
Pydantic schemas for Mail and Email Management system
"""

from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class EmailAccountType(str, Enum):
    IMAP = "imap"
    POP3 = "pop3"
    EXCHANGE = "exchange"
    GMAIL = "gmail"
    OUTLOOK = "outlook"

class EmailStatus(str, Enum):
    UNREAD = "unread"
    READ = "read"
    REPLIED = "replied"
    FORWARDED = "forwarded"
    ARCHIVED = "archived"
    DELETED = "deleted"
    SPAM = "spam"

class EmailPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

# Email Account schemas
class EmailAccountBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email_address: EmailStr
    account_type: EmailAccountType
    incoming_server: Optional[str] = Field(None, max_length=255)
    incoming_port: Optional[int] = Field(None, ge=1, le=65535)
    incoming_ssl: bool = True
    outgoing_server: Optional[str] = Field(None, max_length=255)
    outgoing_port: Optional[int] = Field(None, ge=1, le=65535)
    outgoing_ssl: bool = True
    sync_enabled: bool = True
    sync_frequency_minutes: int = Field(default=15, ge=1, le=1440)
    sync_folders: Optional[List[str]] = None
    auto_link_to_tasks: bool = True
    auto_link_to_calendar: bool = True

class EmailAccountCreate(EmailAccountBase):
    username: Optional[str] = Field(None, max_length=255)
    password: Optional[str] = None  # Will be encrypted
    oauth_token: Optional[str] = None

class EmailAccountUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    incoming_server: Optional[str] = Field(None, max_length=255)
    incoming_port: Optional[int] = Field(None, ge=1, le=65535)
    incoming_ssl: Optional[bool] = None
    outgoing_server: Optional[str] = Field(None, max_length=255)
    outgoing_port: Optional[int] = Field(None, ge=1, le=65535)
    outgoing_ssl: Optional[bool] = None
    username: Optional[str] = Field(None, max_length=255)
    password: Optional[str] = None
    sync_enabled: Optional[bool] = None
    sync_frequency_minutes: Optional[int] = Field(None, ge=1, le=1440)
    sync_folders: Optional[List[str]] = None
    auto_link_to_tasks: Optional[bool] = None
    auto_link_to_calendar: Optional[bool] = None
    is_active: Optional[bool] = None

class EmailAccountResponse(EmailAccountBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    user_id: int
    is_active: bool
    last_sync_at: Optional[datetime]
    last_sync_status: str
    last_sync_error: Optional[str]
    created_at: datetime
    updated_at: datetime

class EmailAccountWithDetails(EmailAccountResponse):
    user: Optional[Dict[str, Any]] = None
    emails_count: int = 0
    unread_count: int = 0

# Email schemas
class EmailBase(BaseModel):
    subject: str = Field(..., max_length=500)
    from_address: EmailStr
    from_name: Optional[str] = Field(None, max_length=255)
    to_addresses: List[EmailStr]
    cc_addresses: Optional[List[EmailStr]] = None
    bcc_addresses: Optional[List[EmailStr]] = None
    reply_to: Optional[EmailStr] = None
    body_text: Optional[str] = None
    body_html: Optional[str] = None
    priority: EmailPriority = EmailPriority.NORMAL
    folder: Optional[str] = Field(None, max_length=255)
    labels: Optional[List[str]] = None

class EmailCreate(EmailBase):
    message_id: str = Field(..., max_length=255)
    thread_id: Optional[str] = Field(None, max_length=255)
    sent_at: datetime
    received_at: datetime
    task_id: Optional[int] = None
    calendar_event_id: Optional[int] = None
    size_bytes: Optional[int] = None
    has_attachments: bool = False

class EmailUpdate(BaseModel):
    status: Optional[EmailStatus] = None
    is_flagged: Optional[bool] = None
    is_important: Optional[bool] = None
    folder: Optional[str] = Field(None, max_length=255)
    labels: Optional[List[str]] = None
    task_id: Optional[int] = None
    calendar_event_id: Optional[int] = None

class EmailResponse(EmailBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    message_id: str
    thread_id: Optional[str]
    account_id: int
    organization_id: int
    task_id: Optional[int]
    calendar_event_id: Optional[int]
    status: EmailStatus
    is_flagged: bool
    is_important: bool
    sent_at: datetime
    received_at: datetime
    size_bytes: Optional[int]
    has_attachments: bool
    created_at: datetime
    updated_at: datetime

class EmailWithDetails(EmailResponse):
    account: Optional[Dict[str, Any]] = None
    task: Optional[Dict[str, Any]] = None
    calendar_event: Optional[Dict[str, Any]] = None
    attachments: Optional[List[Dict[str, Any]]] = None
    actions: Optional[List[Dict[str, Any]]] = None

# Email Attachment schemas
class EmailAttachmentBase(BaseModel):
    filename: str = Field(..., max_length=255)
    content_type: Optional[str] = Field(None, max_length=100)
    size_bytes: Optional[int] = None
    content_id: Optional[str] = Field(None, max_length=255)
    is_inline: bool = False

class EmailAttachmentCreate(EmailAttachmentBase):
    file_data: Optional[bytes] = None
    file_path: Optional[str] = Field(None, max_length=500)

class EmailAttachmentResponse(EmailAttachmentBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    email_id: int
    file_path: Optional[str]
    is_downloaded: bool
    created_at: datetime

class EmailAttachmentWithDetails(EmailAttachmentResponse):
    email: Optional[Dict[str, Any]] = None

# Sent Email schemas
class SentEmailBase(BaseModel):
    subject: str = Field(..., max_length=500)
    to_addresses: List[EmailStr]
    cc_addresses: Optional[List[EmailStr]] = None
    bcc_addresses: Optional[List[EmailStr]] = None
    body_text: Optional[str] = None
    body_html: Optional[str] = None

class SentEmailCreate(SentEmailBase):
    account_id: int
    task_id: Optional[int] = None
    calendar_event_id: Optional[int] = None
    in_reply_to_id: Optional[int] = None
    scheduled_at: Optional[datetime] = None

class SentEmailUpdate(BaseModel):
    status: Optional[str] = None
    delivery_status: Optional[str] = None

class SentEmailResponse(SentEmailBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    message_id: Optional[str]
    thread_id: Optional[str]
    account_id: int
    organization_id: int
    sent_by: int
    task_id: Optional[int]
    calendar_event_id: Optional[int]
    in_reply_to_id: Optional[int]
    status: str
    delivery_status: Optional[str]
    sent_at: datetime
    scheduled_at: Optional[datetime]
    created_at: datetime

class SentEmailWithDetails(SentEmailResponse):
    account: Optional[Dict[str, Any]] = None
    sender: Optional[Dict[str, Any]] = None
    task: Optional[Dict[str, Any]] = None
    calendar_event: Optional[Dict[str, Any]] = None
    in_reply_to: Optional[Dict[str, Any]] = None

# Email Action schemas
class EmailActionBase(BaseModel):
    action_type: str = Field(..., max_length=50)
    action_data: Optional[Dict[str, Any]] = None

class EmailActionCreate(EmailActionBase):
    pass

class EmailActionResponse(EmailActionBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    email_id: int
    user_id: int
    performed_at: datetime

class EmailActionWithDetails(EmailActionResponse):
    email: Optional[Dict[str, Any]] = None
    user: Optional[Dict[str, Any]] = None

# Email Template schemas
class EmailTemplateBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    subject_template: str = Field(..., max_length=500)
    body_text_template: Optional[str] = None
    body_html_template: Optional[str] = None
    variables: Optional[List[str]] = None
    is_shared: bool = False
    category: Optional[str] = Field(None, max_length=100)

class EmailTemplateCreate(EmailTemplateBase):
    pass

class EmailTemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    subject_template: Optional[str] = Field(None, max_length=500)
    body_text_template: Optional[str] = None
    body_html_template: Optional[str] = None
    variables: Optional[List[str]] = None
    is_active: Optional[bool] = None
    is_shared: Optional[bool] = None
    category: Optional[str] = Field(None, max_length=100)

class EmailTemplateResponse(EmailTemplateBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    created_by: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

class EmailTemplateWithDetails(EmailTemplateResponse):
    creator: Optional[Dict[str, Any]] = None

# Email Rule schemas
class EmailRuleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    conditions: List[Dict[str, Any]]
    actions: List[Dict[str, Any]]
    priority: int = Field(default=1, ge=1)

class EmailRuleCreate(EmailRuleBase):
    pass

class EmailRuleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    conditions: Optional[List[Dict[str, Any]]] = None
    actions: Optional[List[Dict[str, Any]]] = None
    is_active: Optional[bool] = None
    priority: Optional[int] = Field(None, ge=1)

class EmailRuleResponse(EmailRuleBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

class EmailRuleWithDetails(EmailRuleResponse):
    user: Optional[Dict[str, Any]] = None

# Dashboard and analytics schemas
class MailDashboardStats(BaseModel):
    total_emails: int = 0
    unread_emails: int = 0
    flagged_emails: int = 0
    today_emails: int = 0
    this_week_emails: int = 0
    sent_emails: int = 0
    draft_emails: int = 0
    spam_emails: int = 0

class EmailFilter(BaseModel):
    status: Optional[List[EmailStatus]] = None
    priority: Optional[List[EmailPriority]] = None
    account_ids: Optional[List[int]] = None
    from_addresses: Optional[List[str]] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    has_attachments: Optional[bool] = None
    is_flagged: Optional[bool] = None
    is_important: Optional[bool] = None
    folders: Optional[List[str]] = None
    labels: Optional[List[str]] = None
    search: Optional[str] = None

class EmailList(BaseModel):
    emails: List[EmailWithDetails]
    total: int
    page: int
    per_page: int
    total_pages: int

# Mail compose schemas
class MailComposeRequest(BaseModel):
    account_id: int
    to_addresses: List[EmailStr]
    cc_addresses: Optional[List[EmailStr]] = None
    bcc_addresses: Optional[List[EmailStr]] = None
    subject: str = Field(..., max_length=500)
    body_text: Optional[str] = None
    body_html: Optional[str] = None
    task_id: Optional[int] = None
    calendar_event_id: Optional[int] = None
    in_reply_to_id: Optional[int] = None
    template_id: Optional[int] = None
    template_variables: Optional[Dict[str, Any]] = None
    scheduled_at: Optional[datetime] = None
    attachments: Optional[List[Dict[str, Any]]] = None

class MailSyncRequest(BaseModel):
    account_id: Optional[int] = None  # If None, sync all accounts
    force_sync: bool = False

class MailSyncResponse(BaseModel):
    success: bool
    message: str
    accounts_synced: int = 0
    emails_imported: int = 0
    errors: Optional[List[str]] = None