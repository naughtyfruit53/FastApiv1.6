# app/api/v1/email.py

"""
Email API endpoints with RBAC, sync management, and CRUD operations
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database import get_db
from app.services.rbac import check_permissions, RoleChecker
from app.services.email_service import email_management_service, link_email_to_customer_vendor, auto_link_emails_by_sender
from app.services.email_sync_worker import email_sync_worker
from app.services.oauth_service import OAuthService
from app.services.calendar_sync_service import calendar_sync_service
from app.services.email_search_service import email_search_service
from app.services.email_ai_service import email_ai_service
from app.services.ocr_service import email_attachment_ocr_service
from app.models.email import (
    MailAccount, Email, EmailThread, EmailAttachment, EmailSyncLog,
    EmailAccountType, EmailSyncStatus, EmailStatus
)
from app.models.user_models import User
from app.schemas.email_schemas import (
    MailAccountCreate, MailAccountUpdate, MailAccountResponse,
    EmailResponse, EmailThreadResponse, EmailAttachmentResponse,
    SyncStatusResponse, ManualSyncRequest
)

router = APIRouter(prefix="/email", tags=["Email"])

# RBAC permissions
ADMIN_PERMISSIONS = ["email:admin"]
MANAGER_PERMISSIONS = ["email:manage", "email:admin"] 
USER_PERMISSIONS = ["email:read", "email:manage", "email:admin"]


@router.post("/accounts", response_model=MailAccountResponse)
async def create_mail_account(
    account_data: MailAccountCreate,
    current_user: User = Depends(RoleChecker(MANAGER_PERMISSIONS)),
    db: Session = Depends(get_db)
):
    """
    Create new email account for IMAP/SMTP sync
    Requires email:manage or email:admin permissions
    """
    try:
        # Check if account already exists
        existing = db.query(MailAccount).filter(
            MailAccount.email_address == account_data.email_address,
            MailAccount.user_id == current_user.id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email account already exists for this user"
            )
        
        # Create account
        account = MailAccount(
            name=account_data.name,
            email_address=account_data.email_address,
            display_name=account_data.display_name,
            account_type=account_data.account_type,
            provider=account_data.provider,
            incoming_server=account_data.incoming_server,
            incoming_port=account_data.incoming_port,
            incoming_ssl=account_data.incoming_ssl,
            incoming_auth_method=account_data.incoming_auth_method,
            outgoing_server=account_data.outgoing_server,
            outgoing_port=account_data.outgoing_port,
            outgoing_ssl=account_data.outgoing_ssl,
            outgoing_auth_method=account_data.outgoing_auth_method,
            username=account_data.username,
            oauth_token_id=account_data.oauth_token_id,
            sync_enabled=account_data.sync_enabled,
            sync_frequency_minutes=account_data.sync_frequency_minutes,
            sync_folders=account_data.sync_folders,
            auto_link_to_customers=account_data.auto_link_to_customers,
            auto_link_to_vendors=account_data.auto_link_to_vendors,
            auto_create_tasks=account_data.auto_create_tasks,
            organization_id=current_user.organization_id,
            user_id=current_user.id
        )
        
        # Encrypt password if provided
        if account_data.password:
            from app.utils.encryption import encrypt_field, EncryptionKeys
            account.password_encrypted = encrypt_field(account_data.password, EncryptionKeys.PII_KEY)
        
        db.add(account)
        db.commit()
        db.refresh(account)
        
        return account
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create email account: {str(e)}"
        )


@router.get("/accounts", response_model=List[MailAccountResponse])
async def list_mail_accounts(
    current_user: User = Depends(RoleChecker(USER_PERMISSIONS)),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500)
):
    """
    List email accounts for current user
    Requires email:read permissions
    """
    accounts = db.query(MailAccount).filter(
        MailAccount.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    return accounts


@router.get("/accounts/{account_id}", response_model=MailAccountResponse)
async def get_mail_account(
    account_id: int = Path(..., gt=0),
    current_user: User = Depends(RoleChecker(USER_PERMISSIONS)),
    db: Session = Depends(get_db)
):
    """
    Get specific email account details
    """
    account = db.query(MailAccount).filter(
        MailAccount.id == account_id,
        MailAccount.user_id == current_user.id
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email account not found"
        )
    
    return account


@router.put("/accounts/{account_id}", response_model=MailAccountResponse)
async def update_mail_account(
    account_id: int,
    update_data: MailAccountUpdate,
    current_user: User = Depends(RoleChecker(MANAGER_PERMISSIONS)),
    db: Session = Depends(get_db)
):
    """
    Update email account settings
    """
    account = db.query(MailAccount).filter(
        MailAccount.id == account_id,
        MailAccount.user_id == current_user.id
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email account not found"
        )
    
    # Update fields
    update_dict = update_data.dict(exclude_unset=True)
    
    # Handle password encryption
    if 'password' in update_dict and update_dict['password']:
        from app.utils.encryption import encrypt_field, EncryptionKeys
        account.password_encrypted = encrypt_field(update_dict['password'], EncryptionKeys.PII_KEY)
        del update_dict['password']
    
    for field, value in update_dict.items():
        setattr(account, field, value)
    
    account.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(account)
    
    return account


@router.delete("/accounts/{account_id}")
async def delete_mail_account(
    account_id: int,
    current_user: User = Depends(RoleChecker(MANAGER_PERMISSIONS)),
    db: Session = Depends(get_db)
):
    """
    Delete email account and all associated data
    """
    account = db.query(MailAccount).filter(
        MailAccount.id == account_id,
        MailAccount.user_id == current_user.id
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email account not found"
        )
    
    try:
        # Soft delete by setting inactive and disabled
        account.is_active = False
        account.sync_enabled = False
        account.sync_status = EmailSyncStatus.DISABLED
        account.updated_at = datetime.utcnow()
        
        db.commit()
        
        return {"message": "Email account deleted successfully"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete email account: {str(e)}"
        )


@router.post("/accounts/{account_id}/sync")
async def trigger_manual_sync(
    account_id: int,
    sync_request: ManualSyncRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(RoleChecker(USER_PERMISSIONS)),
    db: Session = Depends(get_db)
):
    """
    Trigger manual sync for specific account
    """
    account = db.query(MailAccount).filter(
        MailAccount.id == account_id,
        MailAccount.user_id == current_user.id
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email account not found"
        )
    
    if not account.sync_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sync is disabled for this account"
        )
    
    # Trigger sync in background
    success = email_sync_worker.sync_account_now(account_id)
    
    if success:
        return {"message": "Sync triggered successfully", "account_id": account_id}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to trigger sync"
        )


@router.get("/accounts/{account_id}/status", response_model=SyncStatusResponse)
async def get_account_sync_status(
    account_id: int,
    current_user: User = Depends(RoleChecker(USER_PERMISSIONS)),
    db: Session = Depends(get_db)
):
    """
    Get detailed sync status for email account
    """
    account = db.query(MailAccount).filter(
        MailAccount.id == account_id,
        MailAccount.user_id == current_user.id
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email account not found"
        )
    
    status_info = email_management_service.get_account_status(account_id)
    
    if not status_info:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get account status"
        )
    
    return status_info


@router.get("/accounts/{account_id}/emails", response_model=Dict[str, Any])
async def get_account_emails(
    account_id: int,
    current_user: User = Depends(RoleChecker(USER_PERMISSIONS)),
    folder: str = Query("INBOX", description="Email folder to fetch from"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    status_filter: Optional[EmailStatus] = Query(None, description="Filter by email status"),
    db: Session = Depends(get_db)
):
    """
    Get emails from specific account and folder
    """
    account = db.query(MailAccount).filter(
        MailAccount.id == account_id,
        MailAccount.user_id == current_user.id
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email account not found"
        )
    
    # Build query
    query = db.query(Email).filter(
        Email.account_id == account_id,
        Email.folder == folder
    )
    
    if status_filter:
        query = query.filter(Email.status == status_filter)
    
    # Get total count and emails
    total_count = query.count()
    emails = query.order_by(Email.received_at.desc()).offset(offset).limit(limit).all()
    
    return {
        "emails": emails,
        "total_count": total_count,
        "offset": offset,
        "limit": limit,
        "has_more": offset + limit < total_count,
        "folder": folder
    }


@router.get("/emails/{email_id}", response_model=EmailResponse)
async def get_email_detail(
    email_id: int,
    current_user: User = Depends(RoleChecker(USER_PERMISSIONS)),
    include_attachments: bool = Query(True),
    db: Session = Depends(get_db)
):
    """
    Get detailed email information
    """
    email = db.query(Email).join(MailAccount).filter(
        Email.id == email_id,
        MailAccount.user_id == current_user.id
    ).first()
    
    if not email:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found"
        )
    
    email_detail = email_management_service.get_email_detail(email_id, include_attachments)
    
    return email_detail


@router.put("/emails/{email_id}/status")
async def update_email_status(
    email_id: int,
    new_status: EmailStatus,
    current_user: User = Depends(RoleChecker(USER_PERMISSIONS)),
    db: Session = Depends(get_db)
):
    """
    Update email status (read, unread, archived, etc.)
    """
    email = db.query(Email).join(MailAccount).filter(
        Email.id == email_id,
        MailAccount.user_id == current_user.id
    ).first()
    
    if not email:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found"
        )
    
    email.status = new_status
    email.updated_at = datetime.utcnow()
    
    # Update thread unread count if marking as read/unread
    if email.thread_id:
        thread = db.query(EmailThread).filter(EmailThread.id == email.thread_id).first()
        if thread:
            if new_status == EmailStatus.UNREAD:
                thread.unread_count += 1
            elif email.status == EmailStatus.UNREAD and new_status != EmailStatus.UNREAD:
                thread.unread_count = max(0, thread.unread_count - 1)
    
    db.commit()
    
    return {"message": "Email status updated", "new_status": new_status.value}


@router.get("/threads", response_model=List[EmailThreadResponse])
async def list_email_threads(
    current_user: User = Depends(RoleChecker(USER_PERMISSIONS)),
    account_id: Optional[int] = Query(None, description="Filter by account"),
    status_filter: Optional[EmailStatus] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    List email threads with filtering
    """
    # Build query
    query = db.query(EmailThread).join(MailAccount).filter(
        MailAccount.user_id == current_user.id
    )
    
    if account_id:
        query = query.filter(EmailThread.account_id == account_id)
    
    if status_filter:
        query = query.filter(EmailThread.status == status_filter)
    
    threads = query.order_by(EmailThread.last_activity_at.desc()).offset(offset).limit(limit).all()
    
    return threads


@router.get("/threads/{thread_id}", response_model=EmailThreadResponse)
async def get_email_thread(
    thread_id: int,
    current_user: User = Depends(RoleChecker(USER_PERMISSIONS)),
    db: Session = Depends(get_db)
):
    """
    Get email thread with all messages
    """
    thread = db.query(EmailThread).join(MailAccount).filter(
        EmailThread.id == thread_id,
        MailAccount.user_id == current_user.id
    ).first()
    
    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email thread not found"
        )
    
    return thread


@router.get("/attachments/{attachment_id}/download")
async def download_attachment(
    attachment_id: int,
    current_user: User = Depends(RoleChecker(USER_PERMISSIONS)),
    db: Session = Depends(get_db)
):
    """
    Download email attachment
    """
    attachment = db.query(EmailAttachment).join(Email).join(MailAccount).filter(
        EmailAttachment.id == attachment_id,
        MailAccount.user_id == current_user.id
    ).first()
    
    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found"
        )
    
    # Security check
    if attachment.is_quarantined:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Attachment is quarantined and cannot be downloaded"
        )
    
    # Update download tracking
    attachment.download_count += 1
    attachment.last_downloaded_at = datetime.utcnow()
    db.commit()
    
    # Return file content (implementation depends on file storage method)
    # This is a placeholder - actual implementation would handle file serving
    return {"message": "Attachment download", "filename": attachment.filename}


@router.get("/sync/status")
async def get_sync_worker_status(
    current_user: User = Depends(RoleChecker(ADMIN_PERMISSIONS))
):
    """
    Get email sync worker status
    Requires admin permissions
    """
    return email_sync_worker.get_status()


@router.post("/sync/start")
async def start_sync_worker(
    current_user: User = Depends(RoleChecker(ADMIN_PERMISSIONS))
):
    """
    Start email sync worker
    """
    success = email_sync_worker.start()
    
    if success:
        return {"message": "Email sync worker started successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start email sync worker"
        )


@router.post("/sync/stop")
async def stop_sync_worker(
    current_user: User = Depends(RoleChecker(ADMIN_PERMISSIONS))
):
    """
    Stop email sync worker
    """
    success = email_sync_worker.stop()
    
    if success:
        return {"message": "Email sync worker stopped successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to stop email sync worker"
        )


@router.get("/oauth/tokens")
async def list_oauth_tokens(
    current_user: User = Depends(RoleChecker(USER_PERMISSIONS)),
    db: Session = Depends(get_db)
):
    """
    List OAuth tokens for current user
    """
    oauth_service = OAuthService(db)
    tokens = oauth_service.list_user_tokens(current_user.id, current_user.organization_id)
    
    # Return safe token information
    token_info = []
    for token in tokens:
        info = oauth_service.get_token_info(token.id)
        if info:
            token_info.append(info)
    
    return {"tokens": token_info}


# ERP Integration Endpoints

@router.post("/attachments/{attachment_id}/parse-calendar")
async def parse_calendar_attachment(
    attachment_id: int = Path(..., description="Email attachment ID"),
    current_user: User = Depends(RoleChecker(USER_PERMISSIONS)),
    db: Session = Depends(get_db)
):
    """
    Parse .ics calendar file from email attachment and extract events/tasks
    """
    try:
        result = calendar_sync_service.parse_ics_attachment(
            attachment_id, current_user.organization_id
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error parsing calendar attachment: {str(e)}"
        )


@router.post("/calendar/sync-events")
async def sync_calendar_events(
    events: List[Dict[str, Any]],
    current_user: User = Depends(RoleChecker(USER_PERMISSIONS))
):
    """
    Sync parsed calendar events to database
    """
    try:
        result = calendar_sync_service.sync_events_to_database(events, current_user.id)
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error syncing calendar events: {str(e)}"
        )


@router.post("/calendar/sync-tasks")
async def sync_calendar_tasks(
    tasks: List[Dict[str, Any]],
    current_user: User = Depends(RoleChecker(USER_PERMISSIONS))
):
    """
    Sync parsed calendar tasks to database
    """
    try:
        result = calendar_sync_service.sync_tasks_to_database(tasks, current_user.id)
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error syncing calendar tasks: {str(e)}"
        )


# Advanced Search Endpoints

@router.get("/search")
async def search_emails(
    query: str = Query(..., description="Search query"),
    account_ids: Optional[List[int]] = Query(None, description="Email account IDs to search"),
    customer_id: Optional[int] = Query(None, description="Filter by customer ID"),
    vendor_id: Optional[int] = Query(None, description="Filter by vendor ID"),
    date_from: Optional[str] = Query(None, description="Start date filter (ISO format)"),
    date_to: Optional[str] = Query(None, description="End date filter (ISO format)"),
    has_attachments: Optional[bool] = Query(None, description="Filter by attachment presence"),
    limit: int = Query(50, ge=1, le=100, description="Maximum results"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    current_user: User = Depends(RoleChecker(USER_PERMISSIONS))
):
    """
    Full-text search across emails using PostgreSQL tsvector
    """
    try:
        result = email_search_service.full_text_search(
            query=query,
            organization_id=current_user.organization_id,
            account_ids=account_ids,
            customer_id=customer_id,
            vendor_id=vendor_id,
            date_from=date_from,
            date_to=date_to,
            has_attachments=has_attachments,
            limit=limit,
            offset=offset
        )
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search error: {str(e)}"
        )


@router.get("/search/attachments")
async def search_attachments(
    query: str = Query(..., description="Search query"),
    file_types: Optional[List[str]] = Query(None, description="File extensions to filter by"),
    limit: int = Query(50, ge=1, le=100, description="Maximum results"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    current_user: User = Depends(RoleChecker(USER_PERMISSIONS))
):
    """
    Search email attachments by filename and extracted content
    """
    try:
        result = email_search_service.search_attachments(
            query=query,
            organization_id=current_user.organization_id,
            file_types=file_types,
            limit=limit,
            offset=offset
        )
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Attachment search error: {str(e)}"
        )


@router.get("/search/by-customer-vendor")
async def search_by_customer_vendor(
    customer_id: Optional[int] = Query(None, description="Customer ID"),
    vendor_id: Optional[int] = Query(None, description="Vendor ID"),
    limit: int = Query(50, ge=1, le=100, description="Maximum results"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    current_user: User = Depends(RoleChecker(USER_PERMISSIONS))
):
    """
    Search emails linked to specific customers or vendors
    """
    try:
        result = email_search_service.search_by_customer_vendor(
            organization_id=current_user.organization_id,
            customer_id=customer_id,
            vendor_id=vendor_id,
            limit=limit,
            offset=offset
        )
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Customer/vendor search error: {str(e)}"
        )


# OCR Processing Endpoints

@router.post("/attachments/{attachment_id}/ocr")
async def process_attachment_ocr(
    attachment_id: int = Path(..., description="Email attachment ID"),
    current_user: User = Depends(RoleChecker(USER_PERMISSIONS))
):
    """
    Process email attachment with OCR to extract text content
    """
    try:
        result = await email_attachment_ocr_service.process_email_attachment(attachment_id)
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OCR processing error: {str(e)}"
        )


@router.post("/attachments/batch-ocr")
async def batch_process_attachments_ocr(
    attachment_ids: List[int],
    current_user: User = Depends(RoleChecker(USER_PERMISSIONS))
):
    """
    Process multiple email attachments with OCR in batch
    """
    try:
        result = await email_attachment_ocr_service.batch_process_attachments(attachment_ids)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch OCR processing error: {str(e)}"
        )


# AI-Powered Features

@router.get("/ai/summary/{email_id}")
async def get_email_summary(
    email_id: int = Path(..., description="Email ID"),
    current_user: User = Depends(RoleChecker(USER_PERMISSIONS))
):
    """
    Generate AI-powered summary of an email
    """
    try:
        result = email_ai_service.generate_email_summary(email_id)
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result["error"]
            )
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI summary error: {str(e)}"
        )


@router.get("/ai/reply-suggestions/{email_id}")
async def get_reply_suggestions(
    email_id: int = Path(..., description="Email ID"),
    context: Optional[str] = Query(None, description="Additional context for reply"),
    current_user: User = Depends(RoleChecker(USER_PERMISSIONS))
):
    """
    Generate AI-powered reply suggestions for an email
    """
    try:
        result = email_ai_service.generate_reply_suggestions(email_id, context)
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result["error"]
            )
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI reply suggestions error: {str(e)}"
        )


@router.post("/ai/categorize-batch")
async def categorize_emails_batch(
    email_ids: List[int],
    current_user: User = Depends(RoleChecker(USER_PERMISSIONS))
):
    """
    Categorize multiple emails using AI
    """
    try:
        result = email_ai_service.categorize_email_batch(email_ids)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI categorization error: {str(e)}"
        )


@router.get("/ai/action-items/{email_id}")
async def extract_action_items(
    email_id: int = Path(..., description="Email ID"),
    current_user: User = Depends(RoleChecker(USER_PERMISSIONS))
):
    """
    Extract action items and tasks from email content using AI
    """
    try:
        result = email_ai_service.extract_action_items(email_id)
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result["error"]
            )
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Action item extraction error: {str(e)}"
        )


# Shared Inbox and RBAC Endpoints

@router.get("/shared-inboxes")
async def list_shared_inboxes(
    current_user: User = Depends(RoleChecker(USER_PERMISSIONS)),
    db: Session = Depends(get_db)
):
    """
    List shared inboxes accessible to current user based on RBAC
    """
    try:
        # Get mail accounts that are shared or owned by user
        shared_accounts = db.query(MailAccount).filter(
            MailAccount.organization_id == current_user.organization_id,
            or_(
                MailAccount.user_id == current_user.id,
                MailAccount.is_shared == True
            )
        ).all()
        
        account_list = []
        for account in shared_accounts:
            account_dict = {
                'id': account.id,
                'email_address': account.email_address,
                'display_name': account.display_name,
                'is_shared': account.is_shared,
                'sync_status': account.sync_status.value,
                'last_sync_at': account.last_sync_at,
                'owner_id': account.user_id,
                'unread_count': db.query(Email).filter(
                    Email.account_id == account.id,
                    Email.status == EmailStatus.UNREAD
                ).count()
            }
            account_list.append(account_dict)
        
        return {"shared_inboxes": account_list}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving shared inboxes: {str(e)}"
        )


# ERP Linking Endpoints

@router.post("/emails/{email_id}/link")
async def link_email_to_entity(
    email_id: int = Path(..., description="Email ID"),
    customer_id: Optional[int] = Query(None, description="Customer ID to link to"),
    vendor_id: Optional[int] = Query(None, description="Vendor ID to link to"),
    current_user: User = Depends(RoleChecker(USER_PERMISSIONS))
):
    """
    Link an email to a customer or vendor for ERP integration
    """
    try:
        if not customer_id and not vendor_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Must provide either customer_id or vendor_id"
            )
        
        success, error = link_email_to_customer_vendor(
            email_id=email_id,
            customer_id=customer_id,
            vendor_id=vendor_id,
            user_id=current_user.id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error
            )
        
        return {
            "success": True,
            "message": "Email linked successfully",
            "email_id": email_id,
            "customer_id": customer_id,
            "vendor_id": vendor_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error linking email: {str(e)}"
        )


@router.post("/auto-link")
async def auto_link_emails(
    limit: int = Query(100, ge=1, le=500, description="Maximum emails to process"),
    current_user: User = Depends(RoleChecker(MANAGER_PERMISSIONS))
):
    """
    Automatically link emails to customers/vendors based on sender addresses
    """
    try:
        result = auto_link_emails_by_sender(
            organization_id=current_user.organization_id,
            limit=limit
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error auto-linking emails: {str(e)}"
        )