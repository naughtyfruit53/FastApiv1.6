"""
Email API endpoints with RBAC, sync management, and CRUD operations
"""

import logging
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func, delete
from sqlalchemy.orm import Session, joinedload
from datetime import datetime
from pydantic import BaseModel

from app.core.database import get_db, SessionLocal
from app.services.rbac import PermissionChecker
from app.services.system_email_service import system_email_service, link_email_to_customer_vendor, auto_link_emails_by_sender
from app.services.user_email_service import user_email_service
from app.services.email_sync_worker import email_sync_worker
from app.services.oauth_service import OAuth2Service
from app.services.calendar_sync_service import calendar_sync_service
from app.services.email_search_service import email_search_service
from app.services.email_ai_service import email_ai_service
from app.services.ocr_service import email_attachment_ocr_service
from app.models.email import (
    MailAccount, Email, EmailThread, EmailAttachment, EmailSyncLog,
    EmailAccountType, EmailSyncStatus, EmailStatus
)
from app.models.organization_settings import OrganizationSettings
from app.models.user_models import User
from app.schemas.email_schemas import (
    MailAccountCreate, MailAccountUpdate, MailAccountResponse,
    EmailResponse, EmailThreadResponse, EmailAttachmentResponse,
    SyncStatusResponse, ManualSyncRequest, EmailListResponse, EmailListItemResponse
)

router = APIRouter(tags=["email"])

logger = logging.getLogger(__name__)

# RBAC permissions - updated to match default permissions naming
ADMIN_PERMISSIONS = ["crm_admin"]
MANAGER_PERMISSIONS = ["mail:accounts:update", "crm_admin"] 
USER_PERMISSIONS = ["mail:accounts:read", "mail:accounts:update", "crm_admin"]

class UpdateEmailStatus(BaseModel):
    new_status: EmailStatus

@router.post("/accounts", response_model=MailAccountResponse)
async def create_mail_account(
    account_data: MailAccountCreate,
    current_user: User = Depends(PermissionChecker(MANAGER_PERMISSIONS)),
    db: AsyncSession = Depends(get_db)
):
    """
    Create new email account for IMAP/SMTP sync
    Requires email:manage or email:admin permissions
    """
    try:
        # Check if account already exists
        stmt = select(MailAccount).filter(
            MailAccount.email_address == account_data.email_address,
            MailAccount.user_id == current_user.id
        )
        result = await db.execute(stmt)
        existing = result.scalars().first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email account already exists for this user"
            )
        
        # Set defaults based on provider
        if account_data.provider == 'google':
            account_data.incoming_server = 'imap.gmail.com'
            account_data.incoming_port = 993
            account_data.incoming_ssl = True
            account_data.outgoing_server = 'smtp.gmail.com'
            account_data.outgoing_port = 587
            account_data.outgoing_ssl = True
            if account_data.oauth_token_id:
                account_data.incoming_auth_method = 'oauth2'
                account_data.outgoing_auth_method = 'oauth2'
            elif account_data.username and account_data.password:
                account_data.incoming_auth_method = 'password'
                account_data.outgoing_auth_method = 'password'
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="For Google provider, provide either OAuth token or username/password"
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
        await db.commit()
        await db.refresh(account)
        
        return account
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create email account: {str(e)}"
        )


@router.get("/accounts", response_model=List[MailAccountResponse])
async def list_mail_accounts(
    current_user: User = Depends(PermissionChecker(USER_PERMISSIONS)),
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500)
):
    """
    List email accounts for current user
    Requires email:read permissions
    """
    stmt = select(MailAccount).filter(
        MailAccount.user_id == current_user.id
    ).offset(skip).limit(limit)
    result = await db.execute(stmt)
    accounts = result.scalars().all()
    
    return accounts


@router.get("/accounts/{account_id}", response_model=MailAccountResponse)
async def get_mail_account(
    account_id: int = Path(..., gt=0),
    current_user: User = Depends(PermissionChecker(USER_PERMISSIONS)),
    db: AsyncSession = Depends(get_db)
):
    """
    Get specific email account details
    """
    stmt = select(MailAccount).filter(
        MailAccount.id == account_id,
        MailAccount.user_id == current_user.id
    )
    result = await db.execute(stmt)
    account = result.scalars().first()
    
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
    current_user: User = Depends(PermissionChecker(MANAGER_PERMISSIONS)),
    db: AsyncSession = Depends(get_db)
):
    """
    Update email account settings
    """
    stmt = select(MailAccount).filter(
        MailAccount.id == account_id,
        MailAccount.user_id == current_user.id
    )
    result = await db.execute(stmt)
    account = result.scalars().first()
    
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
    await db.commit()
    await db.refresh(account)
    
    return account


@router.delete("/accounts/{account_id}")
async def delete_mail_account(
    account_id: int,
    current_user: User = Depends(PermissionChecker(MANAGER_PERMISSIONS)),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete email account and all associated data
    """
    stmt = select(MailAccount).filter(
        MailAccount.id == account_id,
        MailAccount.user_id == current_user.id
    )
    result = await db.execute(stmt)
    account = result.scalars().first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email account not found"
        )
    
    try:
        # Delete related attachments (through emails)
        await db.execute(
            delete(EmailAttachment)
            .where(EmailAttachment.email_id.in_(
                select(Email.id).where(Email.account_id == account_id)
            ))
        )

        # Delete related emails
        await db.execute(delete(Email).where(Email.account_id == account_id))
        
        # Delete related threads
        await db.execute(delete(EmailThread).where(EmailThread.account_id == account_id))
        
        # Delete related sync logs
        await db.execute(delete(EmailSyncLog).where(EmailSyncLog.account_id == account_id))
        
        # Delete the account
        await db.delete(account)
        
        await db.commit()
        
        return {"message": "Email account and associated data deleted successfully"}
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete email account: {str(e)}"
        )


@router.post("/accounts/{account_id}/sync")
async def trigger_manual_sync(
    account_id: int,
    sync_request: ManualSyncRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(PermissionChecker(USER_PERMISSIONS)),
    db: AsyncSession = Depends(get_db)
):
    """
    Trigger manual sync for specific account
    """
    stmt = select(MailAccount).filter(
        MailAccount.id == account_id,
        MailAccount.user_id == current_user.id
    )
    result = await db.execute(stmt)
    account = result.scalars().first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email account not found"
        )
    
    if not account.sync_enabled:
        logger.warning(f"Manual sync triggered for disabled account {account_id}")

    # Trigger sync in background with manual=True
    background_tasks.add_task(email_sync_worker.sync_account_now, account_id)
    
    return {"message": "Sync triggered in background", "account_id": account_id}


@router.get("/accounts/{account_id}/status", response_model=SyncStatusResponse)
async def get_account_sync_status(
    account_id: int,
    current_user: User = Depends(PermissionChecker(USER_PERMISSIONS)),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed sync status for email account
    """
    stmt = select(MailAccount).filter(
        MailAccount.id == account_id,
        MailAccount.user_id == current_user.id
    )
    result = await db.execute(stmt)
    account = result.scalars().first()
    
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


@router.get("/accounts/{account_id}/emails", response_model=EmailListResponse)
async def get_account_emails(
    account_id: int = Path(..., gt=0),
    current_user: User = Depends(PermissionChecker(USER_PERMISSIONS)),
    folder: str = Query("INBOX", description="Filter by folder"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    status_filter: Optional[EmailStatus] = Query(None, description="Filter by status"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get emails from specific account and folder
    """
    stmt = select(MailAccount).filter(
        MailAccount.id == account_id,
        MailAccount.user_id == current_user.id
    )
    result = await db.execute(stmt)
    account = result.scalars().first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email account not found"
        )
    
    # Build query
    stmt = select(Email).filter(
        Email.account_id == account_id,
        Email.folder == folder
    )
    
    if status_filter:
        stmt = stmt.filter(Email.status == status_filter)
    
    result = await db.execute(stmt.order_by(Email.received_at.desc()).offset(offset).limit(limit))
    emails = result.scalars().all()
    
    total_stmt = select(func.count()).select_from(Email).filter(
        Email.account_id == account_id,
        Email.folder == folder
    )
    if status_filter:
        total_stmt = total_stmt.filter(Email.status == status_filter)
    total_result = await db.execute(total_stmt)
    total_count = total_result.scalar()
    
    # Convert to Pydantic models
    email_responses = [EmailListItemResponse.from_orm(email) for email in emails]
    
    return EmailListResponse(
        emails=email_responses,
        total_count=total_count,
        offset=offset,
        limit=limit,
        has_more=offset + limit < total_count,
        folder=folder
    )


@router.get("/emails/{email_id}", response_model=EmailResponse)
async def get_email_detail(
    email_id: int,
    current_user: User = Depends(PermissionChecker(USER_PERMISSIONS)),
    include_attachments: bool = Query(True),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed email information
    """
    stmt = select(Email).join(MailAccount).filter(
        Email.id == email_id,
        MailAccount.user_id == current_user.id
    )
    if include_attachments:
        stmt = stmt.options(joinedload(Email.attachments))
    result = await db.execute(stmt)
    email = result.scalars().first()
    
    if not email:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found"
        )
    
    return EmailResponse.from_orm(email)


@router.put("/emails/{email_id}/status")
async def update_email_status(
    email_id: int,
    update_data: UpdateEmailStatus,
    current_user: User = Depends(PermissionChecker(USER_PERMISSIONS)),
    db: AsyncSession = Depends(get_db)
):
    """
    Update email status (read, unread, archived, etc.)
    """
    stmt = select(Email).join(MailAccount).filter(
        Email.id == email_id,
        MailAccount.user_id == current_user.id
    )
    result = await db.execute(stmt)
    email = result.scalars().first()
    
    if not email:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found"
        )
    
    email.status = update_data.new_status
    email.updated_at = datetime.utcnow()
    
    # Update thread unread count if marking as read/unread
    if email.thread_id:
        thread_stmt = select(EmailThread).filter(EmailThread.id == email.thread_id)
        thread_result = await db.execute(thread_stmt)
        thread = thread_result.scalars().first()
        if thread:
            if update_data.new_status == EmailStatus.UNREAD:
                thread.unread_count += 1
            elif email.status == EmailStatus.UNREAD and update_data.new_status != EmailStatus.UNREAD:
                thread.unread_count = max(0, thread.unread_count - 1)
    
    await db.commit()
    
    return {"message": "Email status updated", "new_status": update_data.new_status.value}


@router.get("/threads", response_model=List[EmailThreadResponse])
async def list_email_threads(
    current_user: User = Depends(PermissionChecker(USER_PERMISSIONS)),
    account_id: Optional[int] = Query(None, description="Filter by account"),
    status_filter: Optional[EmailStatus] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """
    List email threads with filtering
    """
    # Build query
    stmt = select(EmailThread).join(MailAccount).filter(
        MailAccount.user_id == current_user.id
    )
    
    if account_id:
        stmt = stmt.filter(EmailThread.account_id == account_id)
    
    if status_filter:
        stmt = stmt.filter(EmailThread.status == status_filter)
    
    result = await db.execute(stmt.order_by(EmailThread.last_activity_at.desc()).offset(offset).limit(limit))
    threads = result.scalars().all()
    
    return threads


@router.get("/threads/{thread_id}", response_model=EmailThreadResponse)
async def get_email_thread(
    thread_id: int,
    current_user: User = Depends(PermissionChecker(USER_PERMISSIONS)),
    db: AsyncSession = Depends(get_db)
):
    """
    Get email thread with all messages
    """
    stmt = select(EmailThread).join(MailAccount).filter(
        EmailThread.id == thread_id,
        MailAccount.user_id == current_user.id
    )
    result = await db.execute(stmt)
    thread = result.scalars().first()
    
    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email thread not found"
        )
    
    return thread


@router.get("/threads/{thread_id}/emails", response_model=List[EmailResponse])
async def get_thread_emails(
    thread_id: int = Path(..., gt=0),
    current_user: User = Depends(PermissionChecker(USER_PERMISSIONS)),
    include_attachments: bool = Query(True, description="Include attachment details"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all emails in a thread, ordered by received date
    Requires email:read permissions
    """
    # Verify thread access
    thread_stmt = select(EmailThread).join(MailAccount).filter(
        EmailThread.id == thread_id,
        MailAccount.user_id == current_user.id
    )
    thread_result = await db.execute(thread_stmt)
    thread = thread_result.scalars().first()
    
    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email thread not found or access denied"
        )
    
    # Fetch emails
    stmt = select(Email).filter(
        Email.thread_id == thread_id
    ).order_by(Email.received_at.asc())
    
    if include_attachments:
        stmt = stmt.options(joinedload(Email.attachments))
    
    result = await db.execute(stmt)
    emails = result.scalars().all()
    
    if not emails:
        return []
    
    return [EmailResponse.from_orm(email) for email in emails]


@router.get("/attachments/{attachment_id}/download")
async def download_attachment(
    attachment_id: int,
    current_user: User = Depends(PermissionChecker(USER_PERMISSIONS)),
    db: AsyncSession = Depends(get_db)
):
    """
    Download email attachment
    """
    stmt = select(EmailAttachment).join(Email).join(MailAccount).filter(
        EmailAttachment.id == attachment_id,
        MailAccount.user_id == current_user.id
    )
    result = await db.execute(stmt)
    attachment = result.scalars().first()
    
    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found"
        )
    
    # Return file content (implementation depends on file storage method)
    # This is a placeholder - actual implementation would handle file serving
    return {"message": "Attachment download", "filename": attachment.filename}


@router.get("/sync/status")
async def get_sync_worker_status(
    current_user: User = Depends(PermissionChecker(ADMIN_PERMISSIONS))
):
    """
    Get email sync worker status
    Requires admin permissions
    """
    return email_sync_worker.get_status()


@router.post("/sync/start")
async def start_sync_worker(
    current_user: User = Depends(PermissionChecker(ADMIN_PERMISSIONS))
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
    current_user: User = Depends(PermissionChecker(ADMIN_PERMISSIONS))
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
    current_user: User = Depends(PermissionChecker(USER_PERMISSIONS)),
    db: AsyncSession = Depends(get_db)
):
    """
    List OAuth tokens for current user
    """
    oauth_service = OAuth2Service(db)
    tokens = await oauth_service.list_user_tokens(current_user.id, current_user.organization_id)
    
    # Return safe token information
    token_info = []
    for token in tokens:
        info = await oauth_service.get_token_info(token.id)
        if info:
            token_info.append(info)
    
    return {"tokens": token_info}


# ERP Integration Endpoints

@router.post("/attachments/{attachment_id}/parse-calendar")
async def parse_calendar_attachment(
    attachment_id: int = Path(..., description="Email attachment ID"),
    current_user: User = Depends(PermissionChecker(USER_PERMISSIONS)),
    db: AsyncSession = Depends(get_db)
):
    """
    Parse .ics calendar file from email attachment and extract events/tasks
    """
    try:
        result = await calendar_sync_service.parse_ics_attachment(
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
    current_user: User = Depends(PermissionChecker(USER_PERMISSIONS))
):
    """
    Sync parsed calendar events to database
    """
    try:
        result = await calendar_sync_service.sync_events_to_database(events, current_user.id)
        
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
    current_user: User = Depends(PermissionChecker(USER_PERMISSIONS))
):
    """
    Sync parsed calendar tasks to database
    """
    try:
        result = await calendar_sync_service.sync_tasks_to_database(tasks, current_user.id)
        
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
    account_ids: Optional[List[int]] = Query(None, description="Filter by account IDs"),
    customer_id: Optional[int] = Query(None, description="Filter by customer ID"),
    vendor_id: Optional[int] = Query(None, description="Filter by vendor ID"),
    date_from: Optional[str] = Query(None, description="Start date filter (ISO format)"),
    date_to: Optional[str] = Query(None, description="End date filter (ISO format)"),
    has_attachments: Optional[bool] = Query(None, description="Filter by attachment presence"),
    limit: int = Query(50, ge=1, le=100, description="Maximum results"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    current_user: User = Depends(PermissionChecker(USER_PERMISSIONS))
):
    """
    Full-text search across emails using PostgreSQL tsvector
    """
    try:
        result = await email_search_service.full_text_search(
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
    current_user: User = Depends(PermissionChecker(USER_PERMISSIONS))
):
    """
    Search email attachments by filename and extracted content
    """
    try:
        result = await email_search_service.search_attachments(
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
    current_user: User = Depends(PermissionChecker(USER_PERMISSIONS))
):
    """
    Search emails linked to specific customers or vendors
    """
    try:
        result = await email_search_service.search_by_customer_vendor(
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
    current_user: User = Depends(PermissionChecker(USER_PERMISSIONS))
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
    current_user: User = Depends(PermissionChecker(USER_PERMISSIONS))
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
    current_user: User = Depends(PermissionChecker(USER_PERMISSIONS))
):
    """
    Generate AI-powered summary of an email
    """
    try:
        result = await email_ai_service.generate_email_summary(email_id)
        
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
    current_user: User = Depends(PermissionChecker(USER_PERMISSIONS))
):
    """
    Generate AI-powered reply suggestions for an email
    """
    try:
        result = await email_ai_service.generate_reply_suggestions(email_id, context)
        
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
    current_user: User = Depends(PermissionChecker(USER_PERMISSIONS))
):
    """
    Categorize multiple emails using AI
    """
    try:
        result = await email_ai_service.categorize_email_batch(email_ids)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI categorization error: {str(e)}"
        )


@router.get("/ai/action-items/{email_id}")
async def extract_action_items(
    email_id: int = Path(..., description="Email ID"),
    current_user: User = Depends(PermissionChecker(USER_PERMISSIONS))
):
    """
    Extract action items and tasks from email content using AI
    """
    try:
        result = await email_ai_service.extract_action_items(email_id)
        
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
    current_user: User = Depends(PermissionChecker(USER_PERMISSIONS)),
    db: AsyncSession = Depends(get_db)
):
    """
    List shared inboxes accessible to current user based on RBAC
    """
    try:
        # Get mail accounts that are shared or owned by user
        stmt = select(MailAccount).filter(
            MailAccount.organization_id == current_user.organization_id,
            or_(
                MailAccount.user_id == current_user.id,
                MailAccount.is_shared == True
            )
        )
        result = await db.execute(stmt)
        shared_accounts = result.scalars().all()
        
        account_list = []
        for account in shared_accounts:
            unread_stmt = select(func.count()).filter(
                Email.account_id == account.id,
                Email.status == EmailStatus.UNREAD
            )
            unread_result = await db.execute(unread_stmt)
            unread_count = unread_result.scalar()
            
            account_dict = {
                'id': account.id,
                'email_address': account.email_address,
                'display_name': account.display_name,
                'is_shared': account.is_shared,
                'sync_status': account.sync_status.value,
                'last_sync_at': account.last_sync_at,
                'owner_id': account.user_id,
                'unread_count': unread_count
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
    current_user: User = Depends(PermissionChecker(USER_PERMISSIONS))
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
        
        success, error = await link_email_to_customer_vendor(
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
    current_user: User = Depends(PermissionChecker(MANAGER_PERMISSIONS))
):
    """
    Automatically link emails to customers/vendors based on sender addresses
    """
    try:
        result = await auto_link_emails_by_sender(
            organization_id=current_user.organization_id,
            limit=limit
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error auto-linking emails: {str(e)}"
        )

@router.post("/compose", response_model=Dict[str, Any])
async def compose_email(
    account_id: int = Query(..., description="ID of the email account to send from"),
    to_email: str = Query(..., description="Recipient email"),
    subject: str = Query(..., description="Email subject"),
    body: str = Query(..., description="Plain text body"),
    html_body: Optional[str] = Query(None, description="Optional HTML body"),
    current_user: User = Depends(PermissionChecker(USER_PERMISSIONS)),
    db: AsyncSession = Depends(get_db)
):
    """
    Compose and send email from user's connected account using provider API.
    Supports Mail 1 Level Up BCC if enabled in organization settings.
    """
    from app.services.system_email_service import system_email_service
    
    try:
        # Check if Mail 1 Level Up is enabled
        stmt = select(OrganizationSettings).filter(OrganizationSettings.organization_id == current_user.organization_id)
        result = await db.execute(stmt)
        org_settings = result.scalars().first()
        
        bcc_emails = []
        if org_settings and org_settings.mail_1_level_up_enabled and current_user:
            bcc_emails = await system_email_service.role_hierarchy_service.get_bcc_recipient_for_user(db, current_user)
        
        # Send via user email service
        success, error = await user_email_service.send_email(
            db=db,
            account_id=account_id,
            to_email=to_email,
            subject=subject,
            body=body,
            html_body=html_body,
            bcc_emails=bcc_emails
        )
        
        if success:
            return {
                "message": "Email sent successfully",
                "to_email": to_email,
                "subject": subject,
                "sender_role": current_user.role,
                "mail_1_level_up_applied": bool(bcc_emails)
            }
        else:
            if "REFRESH_FAILED" in error or "cannot be reused" in error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"{error} To fix, revoke the token using POST /api/v1/email/oauth/revoke/{account.oauth_token_id}, then re-authorize via POST /api/v1/oauth/login/{account.provider}. If recently recently changed to production, the old refresh token may still expire (7-day limit from testing). Revoke and re-auth to get a permanent one."
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to send email: {error}"
                )
            
    except Exception as e:
        if "REFRESH_FAILED" in str(e) or "cannot be reused" in str(e):
            # Get account to get token_id
            stmt = select(MailAccount).filter(MailAccount.id == account_id)
            result = await db.execute(stmt)
            account = result.scalars().first()
            token_id = account.oauth_token_id if account else "unknown"
            provider = account.provider if account else "unknown"
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token refresh failed: {str(e)}. Revoke token with POST /api/v1/email/oauth/revoke/{token_id}, then re-authorize with POST /api/v1/oauth/login/{provider}. If recently changed to production, re-auth to get non-expiring refresh token. If recently recently changed to production, the old refresh token may still expire (7-day limit from testing). Revoke and re-auth to get a permanent one."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error composing email: {str(e)}"
            )


@router.post("/oauth/revoke/{token_id}")
async def revoke_oauth_token(
    token_id: int = Path(..., description="OAuth token ID to revoke"),
    current_user: User = Depends(PermissionChecker(USER_PERMISSIONS)),
    db: AsyncSession = Depends(get_db)
):
    """
    Revoke OAuth token and mark as REVOKED
    Allows users to revoke failed tokens and re-authorize
    """
    try:
        oauth_service = OAuth2Service(db)
        success = await oauth_service.revoke_token(token_id)
        
        if success:
            return {
                "message": "Token revoked successfully. You can now re-authorize the account. If recently changed to production, re-auth to get non-expiring refresh token. If issues persist, check Google account permissions at myaccount.google.com/permissions and revoke old access."
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to revoke token"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error revoking token: {str(e)}"
        )