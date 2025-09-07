# app/api/v1/mail.py

"""
Mail and Email Management API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc, asc
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.api.v1.auth import get_current_active_user as get_current_user
from app.models import User, Organization, EmailAccount, Email, EmailAttachment, SentEmail, EmailAction, EmailTemplate, EmailRule
from app.schemas.mail_schemas import (
    EmailAccountCreate, EmailAccountUpdate, EmailAccountResponse, EmailAccountWithDetails,
    EmailCreate, EmailUpdate, EmailResponse, EmailWithDetails, EmailList, EmailFilter,
    SentEmailCreate, SentEmailUpdate, SentEmailResponse, SentEmailWithDetails,
    EmailTemplateCreate, EmailTemplateUpdate, EmailTemplateResponse, EmailTemplateWithDetails,
    EmailRuleCreate, EmailRuleUpdate, EmailRuleResponse, EmailRuleWithDetails,
    MailDashboardStats, MailComposeRequest, MailSyncRequest, MailSyncResponse
)

router = APIRouter()

# Mail Dashboard
@router.get("/dashboard", response_model=MailDashboardStats)
async def get_mail_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get mail dashboard statistics for current user's organization"""
    org_id = current_user.organization_id
    if not org_id:
        return MailDashboardStats(
            total_emails=0,
            unread_emails=0,
            flagged_emails=0,
            today_emails=0,
            this_week_emails=0,
            sent_emails=0,
            draft_emails=0,
            spam_emails=0
        )
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    week_end = today_start + timedelta(days=7)
    
    try:
        # Base query for user's organization emails
        base_query = db.query(Email).filter(Email.organization_id == org_id)
        
        # Total emails
        total_emails = base_query.count()
        
        # Unread emails
        unread_emails = base_query.filter(Email.status == "unread").count()
        
        # Flagged emails
        flagged_emails = base_query.filter(Email.is_flagged == True).count()
        
        # Today's emails
        today_emails = base_query.filter(
            and_(
                Email.received_at >= today_start,
                Email.received_at < today_end
            )
        ).count()
        
        # This week's emails
        this_week_emails = base_query.filter(
            and_(
                Email.received_at >= today_start,
                Email.received_at < week_end
            )
        ).count()
        
        # Sent emails
        sent_emails = db.query(SentEmail).filter(
            SentEmail.organization_id == org_id
        ).count()
        
        # Draft emails (assuming status = "pending")
        draft_emails = db.query(SentEmail).filter(
            and_(
                SentEmail.organization_id == org_id,
                SentEmail.status == "pending"
            )
        ).count()
        
        # Spam emails
        spam_emails = base_query.filter(Email.status == "spam").count()
        
        return MailDashboardStats(
            total_emails=total_emails,
            unread_emails=unread_emails,
            flagged_emails=flagged_emails,
            today_emails=today_emails,
            this_week_emails=this_week_emails,
            sent_emails=sent_emails,
            draft_emails=draft_emails,
            spam_emails=spam_emails
        )
    except Exception as e:
        print(f"Error fetching mail dashboard stats: {str(e)}")
        return MailDashboardStats(
            total_emails=0,
            unread_emails=0,
            flagged_emails=0,
            today_emails=0,
            this_week_emails=0,
            sent_emails=0,
            draft_emails=0,
            spam_emails=0
        )

# Email Accounts
@router.get("/accounts", response_model=List[EmailAccountWithDetails])
async def get_email_accounts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all email accounts for current user"""
    accounts = db.query(EmailAccount).filter(
        and_(
            EmailAccount.organization_id == current_user.organization_id,
            EmailAccount.user_id == current_user.id
        )
    ).options(
        joinedload(EmailAccount.user)
    ).all()
    
    account_details = []
    for account in accounts:
        # Count emails and unread emails
        emails_count = db.query(Email).filter(Email.account_id == account.id).count()
        unread_count = db.query(Email).filter(
            and_(Email.account_id == account.id, Email.status == "unread")
        ).count()
        
        account_dict = {
            **account.__dict__,
            "user": {"id": account.user.id, "full_name": account.user.full_name} if account.user else None,
            "emails_count": emails_count,
            "unread_count": unread_count
        }
        account_details.append(EmailAccountWithDetails(**account_dict))
    
    return account_details

@router.post("/accounts", response_model=EmailAccountResponse)
async def create_email_account(
    account_data: EmailAccountCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new email account"""
    # Check if account with same email already exists for user
    existing_account = db.query(EmailAccount).filter(
        and_(
            EmailAccount.user_id == current_user.id,
            EmailAccount.email_address == account_data.email_address
        )
    ).first()
    
    if existing_account:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email account already exists"
        )
    
    # Create account (password should be encrypted in production)
    account_dict = account_data.model_dump()
    if "password" in account_dict:
        # In production, encrypt the password before storing
        account_dict["password_encrypted"] = account_dict.pop("password")
    
    account = EmailAccount(
        **account_dict,
        organization_id=current_user.organization_id,
        user_id=current_user.id
    )
    
    db.add(account)
    db.commit()
    db.refresh(account)
    
    return EmailAccountResponse.model_validate(account)

@router.get("/accounts/{account_id}", response_model=EmailAccountWithDetails)
async def get_email_account(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific email account by ID"""
    account = db.query(EmailAccount).filter(
        and_(
            EmailAccount.id == account_id,
            EmailAccount.organization_id == current_user.organization_id,
            EmailAccount.user_id == current_user.id
        )
    ).options(
        joinedload(EmailAccount.user)
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email account not found"
        )
    
    # Count emails and unread emails
    emails_count = db.query(Email).filter(Email.account_id == account.id).count()
    unread_count = db.query(Email).filter(
        and_(Email.account_id == account.id, Email.status == "unread")
    ).count()
    
    account_dict = {
        **account.__dict__,
        "user": {"id": account.user.id, "full_name": account.user.full_name} if account.user else None,
        "emails_count": emails_count,
        "unread_count": unread_count
    }
    
    return EmailAccountWithDetails(**account_dict)

@router.put("/accounts/{account_id}", response_model=EmailAccountResponse)
async def update_email_account(
    account_id: int,
    account_data: EmailAccountUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an email account"""
    account = db.query(EmailAccount).filter(
        and_(
            EmailAccount.id == account_id,
            EmailAccount.organization_id == current_user.organization_id,
            EmailAccount.user_id == current_user.id
        )
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email account not found"
        )
    
    # Update account fields
    update_data = account_data.model_dump(exclude_unset=True)
    if "password" in update_data:
        # In production, encrypt the password before storing
        update_data["password_encrypted"] = update_data.pop("password")
    
    for field, value in update_data.items():
        setattr(account, field, value)
    
    db.commit()
    db.refresh(account)
    
    return EmailAccountResponse.model_validate(account)

@router.delete("/accounts/{account_id}")
async def delete_email_account(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an email account"""
    account = db.query(EmailAccount).filter(
        and_(
            EmailAccount.id == account_id,
            EmailAccount.organization_id == current_user.organization_id,
            EmailAccount.user_id == current_user.id
        )
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email account not found"
        )
    
    db.delete(account)
    db.commit()
    
    return {"message": "Email account deleted successfully"}

# Emails
@router.get("/emails", response_model=EmailList)
async def get_emails(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: Optional[List[str]] = Query(None),
    priority: Optional[List[str]] = Query(None),
    account_ids: Optional[List[int]] = Query(None),
    from_addresses: Optional[List[str]] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    has_attachments: Optional[bool] = Query(None),
    is_flagged: Optional[bool] = Query(None),
    is_important: Optional[bool] = Query(None),
    folders: Optional[List[str]] = Query(None),
    labels: Optional[List[str]] = Query(None),
    search: Optional[str] = Query(None),
    sort_by: str = Query("received_at", regex=r"^(received_at|sent_at|subject|from_address)$"),
    sort_order: str = Query("desc", regex=r"^(asc|desc)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get paginated list of emails with filtering and sorting"""
    org_id = current_user.organization_id
    
    # Base query with eager loading
    query = db.query(Email).filter(Email.organization_id == org_id).options(
        joinedload(Email.account),
        joinedload(Email.task),
        joinedload(Email.calendar_event),
        joinedload(Email.attachments)
    )
    
    # Filter by user's accounts only
    user_account_ids = db.query(EmailAccount.id).filter(
        and_(
            EmailAccount.organization_id == org_id,
            EmailAccount.user_id == current_user.id
        )
    ).subquery()
    query = query.filter(Email.account_id.in_(user_account_ids))
    
    # Apply filters
    if status:
        query = query.filter(Email.status.in_(status))
    
    if priority:
        query = query.filter(Email.priority.in_(priority))
    
    if account_ids:
        query = query.filter(Email.account_id.in_(account_ids))
    
    if from_addresses:
        query = query.filter(Email.from_address.in_(from_addresses))
    
    if date_from:
        query = query.filter(Email.received_at >= date_from)
    
    if date_to:
        query = query.filter(Email.received_at <= date_to)
    
    if has_attachments is not None:
        query = query.filter(Email.has_attachments == has_attachments)
    
    if is_flagged is not None:
        query = query.filter(Email.is_flagged == is_flagged)
    
    if is_important is not None:
        query = query.filter(Email.is_important == is_important)
    
    if folders:
        query = query.filter(Email.folder.in_(folders))
    
    if labels:
        # Search for any of the provided labels in the JSON array
        label_filters = [Email.labels.contains([label]) for label in labels]
        query = query.filter(or_(*label_filters))
    
    if search:
        search_filter = or_(
            Email.subject.contains(search),
            Email.body_text.contains(search),
            Email.from_address.contains(search)
        )
        query = query.filter(search_filter)
    
    # Apply sorting
    sort_column = getattr(Email, sort_by)
    if sort_order == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(asc(sort_column))
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * per_page
    emails = query.offset(offset).limit(per_page).all()
    
    # Calculate total pages
    total_pages = (total + per_page - 1) // per_page
    
    # Convert to response models with details
    email_details = []
    for email in emails:
        email_dict = {
            **email.__dict__,
            "account": {"id": email.account.id, "name": email.account.name, "email_address": email.account.email_address} if email.account else None,
            "task": {"id": email.task.id, "title": email.task.title} if email.task else None,
            "calendar_event": {"id": email.calendar_event.id, "title": email.calendar_event.title} if email.calendar_event else None,
            "attachments": [
                {
                    "id": attachment.id,
                    "filename": attachment.filename,
                    "size_bytes": attachment.size_bytes,
                    "content_type": attachment.content_type,
                    "is_inline": attachment.is_inline
                }
                for attachment in email.attachments
            ] if email.attachments else []
        }
        email_details.append(EmailWithDetails(**email_dict))
    
    return EmailList(
        emails=email_details,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages
    )

@router.get("/emails/{email_id}", response_model=EmailWithDetails)
async def get_email(
    email_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific email by ID"""
    # Verify email belongs to user's account
    user_account_ids = db.query(EmailAccount.id).filter(
        and_(
            EmailAccount.organization_id == current_user.organization_id,
            EmailAccount.user_id == current_user.id
        )
    ).subquery()
    
    email = db.query(Email).filter(
        and_(
            Email.id == email_id,
            Email.organization_id == current_user.organization_id,
            Email.account_id.in_(user_account_ids)
        )
    ).options(
        joinedload(Email.account),
        joinedload(Email.task),
        joinedload(Email.calendar_event),
        joinedload(Email.attachments),
        joinedload(Email.actions)
    ).first()
    
    if not email:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found"
        )
    
    # Mark as read if it's unread
    if email.status == "unread":
        email.status = "read"
        # Log the action
        action = EmailAction(
            email_id=email.id,
            user_id=current_user.id,
            action_type="read"
        )
        db.add(action)
        db.commit()
    
    # Convert to response model with details
    email_dict = {
        **email.__dict__,
        "account": {"id": email.account.id, "name": email.account.name, "email_address": email.account.email_address} if email.account else None,
        "task": {"id": email.task.id, "title": email.task.title} if email.task else None,
        "calendar_event": {"id": email.calendar_event.id, "title": email.calendar_event.title} if email.calendar_event else None,
        "attachments": [
            {
                "id": attachment.id,
                "filename": attachment.filename,
                "size_bytes": attachment.size_bytes,
                "content_type": attachment.content_type,
                "is_inline": attachment.is_inline,
                "file_path": attachment.file_path
            }
            for attachment in email.attachments
        ] if email.attachments else [],
        "actions": [
            {
                "id": action.id,
                "action_type": action.action_type,
                "performed_at": action.performed_at
            }
            for action in email.actions
        ] if email.actions else []
    }
    
    return EmailWithDetails(**email_dict)

@router.put("/emails/{email_id}", response_model=EmailResponse)
async def update_email(
    email_id: int,
    email_data: EmailUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an email (status, flags, labels, etc.)"""
    # Verify email belongs to user's account
    user_account_ids = db.query(EmailAccount.id).filter(
        and_(
            EmailAccount.organization_id == current_user.organization_id,
            EmailAccount.user_id == current_user.id
        )
    ).subquery()
    
    email = db.query(Email).filter(
        and_(
            Email.id == email_id,
            Email.organization_id == current_user.organization_id,
            Email.account_id.in_(user_account_ids)
        )
    ).first()
    
    if not email:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found"
        )
    
    # Update email fields
    update_data = email_data.model_dump(exclude_unset=True)
    
    # Log actions for certain changes
    actions_to_log = []
    if "status" in update_data and update_data["status"] != email.status:
        actions_to_log.append(update_data["status"])
    if "is_flagged" in update_data and update_data["is_flagged"] != email.is_flagged:
        actions_to_log.append("flag" if update_data["is_flagged"] else "unflag")
    
    for field, value in update_data.items():
        setattr(email, field, value)
    
    # Log actions
    for action_type in actions_to_log:
        action = EmailAction(
            email_id=email.id,
            user_id=current_user.id,
            action_type=action_type
        )
        db.add(action)
    
    db.commit()
    db.refresh(email)
    
    return EmailResponse.model_validate(email)

# Email composition and sending
@router.post("/compose", response_model=SentEmailResponse)
async def compose_and_send_email(
    compose_request: MailComposeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Compose and send an email"""
    # Verify account belongs to user
    account = db.query(EmailAccount).filter(
        and_(
            EmailAccount.id == compose_request.account_id,
            EmailAccount.organization_id == current_user.organization_id,
            EmailAccount.user_id == current_user.id
        )
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email account not found"
        )
    
    # Process template if provided
    subject = compose_request.subject
    body_text = compose_request.body_text
    body_html = compose_request.body_html
    
    if compose_request.template_id:
        template = db.query(EmailTemplate).filter(
            and_(
                EmailTemplate.id == compose_request.template_id,
                EmailTemplate.organization_id == current_user.organization_id
            )
        ).first()
        
        if template:
            # Replace template variables
            template_vars = compose_request.template_variables or {}
            
            subject = template.subject_template
            body_text = template.body_text_template
            body_html = template.body_html_template
            
            for var, value in template_vars.items():
                if subject:
                    subject = subject.replace(f"{{{var}}}", str(value))
                if body_text:
                    body_text = body_text.replace(f"{{{var}}}", str(value))
                if body_html:
                    body_html = body_html.replace(f"{{{var}}}", str(value))
    
    # Create sent email record
    sent_email = SentEmail(
        subject=subject,
        to_addresses=compose_request.to_addresses,
        cc_addresses=compose_request.cc_addresses,
        bcc_addresses=compose_request.bcc_addresses,
        body_text=body_text,
        body_html=body_html,
        account_id=compose_request.account_id,
        organization_id=current_user.organization_id,
        sent_by=current_user.id,
        task_id=compose_request.task_id,
        calendar_event_id=compose_request.calendar_event_id,
        in_reply_to_id=compose_request.in_reply_to_id,
        scheduled_at=compose_request.scheduled_at,
        sent_at=datetime.utcnow() if not compose_request.scheduled_at else None,
        status="sent" if not compose_request.scheduled_at else "pending"
    )
    
    db.add(sent_email)
    db.commit()
    db.refresh(sent_email)
    
    # TODO: Integrate with actual email sending service (SMTP, etc.)
    # For now, we just create the record
    
    return SentEmailResponse.model_validate(sent_email)

# Email sync
@router.post("/sync", response_model=MailSyncResponse)
async def sync_emails(
    sync_request: MailSyncRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Sync emails from email accounts"""
    org_id = current_user.organization_id
    
    # Get accounts to sync
    if sync_request.account_id:
        accounts = db.query(EmailAccount).filter(
            and_(
                EmailAccount.id == sync_request.account_id,
                EmailAccount.organization_id == org_id,
                EmailAccount.user_id == current_user.id,
                EmailAccount.sync_enabled == True
            )
        ).all()
    else:
        accounts = db.query(EmailAccount).filter(
            and_(
                EmailAccount.organization_id == org_id,
                EmailAccount.user_id == current_user.id,
                EmailAccount.sync_enabled == True
            )
        ).all()
    
    if not accounts:
        return MailSyncResponse(
            success=False,
            message="No accounts found for syncing",
            accounts_synced=0,
            emails_imported=0
        )
    
    accounts_synced = 0
    emails_imported = 0
    errors = []
    
    for account in accounts:
        try:
            # TODO: Implement actual email sync logic based on account type
            # This would involve connecting to IMAP/POP3/Exchange servers
            # and importing new emails
            
            # Update last sync time
            account.last_sync_at = datetime.utcnow()
            account.last_sync_status = "success"
            account.last_sync_error = None
            
            accounts_synced += 1
            # emails_imported += imported_count  # Would be set by actual sync logic
            
        except Exception as e:
            errors.append(f"Account {account.name}: {str(e)}")
            account.last_sync_status = "error"
            account.last_sync_error = str(e)
    
    db.commit()
    
    return MailSyncResponse(
        success=len(errors) == 0,
        message="Email sync completed" if len(errors) == 0 else "Email sync completed with errors",
        accounts_synced=accounts_synced,
        emails_imported=emails_imported,
        errors=errors if errors else None
    )

# Email Templates
@router.get("/templates", response_model=List[EmailTemplateWithDetails])
async def get_email_templates(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all email templates for current user's organization"""
    templates = db.query(EmailTemplate).filter(
        EmailTemplate.organization_id == current_user.organization_id
    ).options(
        joinedload(EmailTemplate.creator)
    ).all()
    
    template_details = []
    for template in templates:
        template_dict = {
            **template.__dict__,
            "creator": {"id": template.creator.id, "full_name": template.creator.full_name} if template.creator else None
        }
        template_details.append(EmailTemplateWithDetails(**template_dict))
    
    return template_details

@router.post("/templates", response_model=EmailTemplateResponse)
async def create_email_template(
    template_data: EmailTemplateCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new email template"""
    template = EmailTemplate(
        **template_data.model_dump(),
        organization_id=current_user.organization_id,
        created_by=current_user.id
    )
    
    db.add(template)
    db.commit()
    db.refresh(template)
    
    return EmailTemplateResponse.model_validate(template)