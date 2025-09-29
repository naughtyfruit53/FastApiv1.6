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
from app.services.email_service import email_management_service
from app.services.email_sync_worker import email_sync_worker
from app.services.oauth_service import OAuthService
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