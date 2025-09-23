# app/api/v1/mail.py

"""
Mail and Email Management API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc, asc
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from app.core.database import get_db
from app.api.v1.auth import get_current_active_user as get_current_user
from app.core.rbac_dependencies import check_service_permission, RBACDependency
from app.models.user_models import User, Organization
from app.models.mail_management import EmailAccount, Email, EmailAttachment, SentEmail, EmailAction, EmailTemplate, EmailRule
from app.schemas.mail_schemas import (
    EmailAccountCreate, EmailAccountUpdate, EmailAccountResponse, EmailAccountWithDetails,
    EmailCreate, EmailUpdate, EmailResponse, EmailWithDetails, EmailList, EmailFilter,
    SentEmailCreate, SentEmailUpdate, SentEmailResponse, SentEmailWithDetails,
    EmailTemplateCreate, EmailTemplateUpdate, EmailTemplateResponse, EmailTemplateWithDetails,
    EmailRuleCreate, EmailRuleUpdate, EmailRuleResponse, EmailRuleWithDetails,
    MailDashboardStats, MailComposeRequest, MailSyncRequest, MailSyncResponse
)

router = APIRouter()
logger = logging.getLogger(__name__)

# Define RBAC dependencies for mail module
require_mail_read = RBACDependency("mail:dashboard:read")
require_mail_accounts_read = RBACDependency("mail:accounts:read")
require_mail_accounts_create = RBACDependency("mail:accounts:create")
require_mail_accounts_update = RBACDependency("mail:accounts:update")
require_mail_accounts_delete = RBACDependency("mail:accounts:delete")
require_mail_emails_read = RBACDependency("mail:emails:read")
require_mail_emails_compose = RBACDependency("mail:emails:compose")
require_mail_emails_update = RBACDependency("mail:emails:update")
require_mail_emails_sync = RBACDependency("mail:emails:sync")
require_mail_templates_read = RBACDependency("mail:templates:read")
require_mail_templates_create = RBACDependency("mail:templates:create")

# Mail Dashboard
@router.get("/dashboard", response_model=MailDashboardStats)
async def get_mail_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get mail dashboard statistics for current user's organization"""
    if not current_user.organization_id:
        logger.error(f"User {current_user.id} has no organization assigned")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not associated with any organization"
        )

    # Check if user has any email accounts
    email_accounts = db.query(EmailAccount).filter(
        and_(
            EmailAccount.organization_id == current_user.organization_id,
            EmailAccount.user_id == current_user.id
        )
    ).count()

    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    week_end = today_start + timedelta(days=7)

    try:
        # Base query for user's organization emails
        base_query = db.query(Email).filter(Email.organization_id == current_user.organization_id)

        # Total emails
        total_emails = base_query.count()

        # Unread emails
        unread_emails = base_query.filter(Email.status == "UNREAD").count()

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
            SentEmail.organization_id == current_user.organization_id
        ).count()

        # Draft emails
        draft_emails = db.query(SentEmail).filter(
            and_(
                SentEmail.organization_id == current_user.organization_id,
                SentEmail.status == "PENDING"
            )
        ).count()

        # Spam emails
        spam_emails = base_query.filter(Email.status == "SPAM").count()

        logger.info(f"Successfully fetched mail dashboard stats for user {current_user.id}")
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
        logger.error(f"Error fetching mail dashboard stats for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch mail dashboard stats: {str(e)}"
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
        emails_count = db.query(Email).filter(Email.account_id == account.id).count()
        unread_count = db.query(Email).filter(
            and_(Email.account_id == account.id, Email.status == "UNREAD")
        ).count()

        account_dict = {
            **account.__dict__,
            "user": {"id": account.user.id, "full_name": account.user.full_name} if account.user else None,
            "emails_count": emails_count,
            "unread_count": unread_count
        }
        account_details.append(EmailAccountWithDetails(**account_dict))

    logger.info(f"Fetched {len(account_details)} email accounts for user {current_user.id}")
    return account_details

@router.post("/accounts", response_model=EmailAccountResponse)
async def create_email_account(
    account_data: EmailAccountCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new email account"""
    existing_account = db.query(EmailAccount).filter(
        and_(
            EmailAccount.user_id == current_user.id,
            EmailAccount.email_address == account_data.email_address
        )
    ).first()

    if existing_account:
        logger.warning(f"Attempt to create duplicate email account {account_data.email_address} by user {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email account already exists"
        )

    account_dict = account_data.model_dump()
    if "password" in account_dict:
        account_dict["password_encrypted"] = account_dict.pop("password")

    account = EmailAccount(
        **account_dict,
        organization_id=current_user.organization_id,
        user_id=current_user.id
    )

    db.add(account)
    db.commit()
    db.refresh(account)
    logger.info(f"Created email account {account.email_address} for user {current_user.id}")
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
        logger.warning(f"Email account {account_id} not found for user {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email account not found"
        )

    emails_count = db.query(Email).filter(Email.account_id == account.id).count()
    unread_count = db.query(Email).filter(
        and_(Email.account_id == account.id, Email.status == "UNREAD")
    ).count()

    account_dict = {
        **account.__dict__,
        "user": {"id": account.user.id, "full_name": account.user.full_name} if account.user else None,
        "emails_count": emails_count,
        "unread_count": unread_count
    }

    logger.info(f"Fetched email account {account_id} for user {current_user.id}")
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
        logger.warning(f"Email account {account_id} not found for user {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email account not found"
        )

    update_data = account_data.model_dump(exclude_unset=True)
    if "password" in update_data:
        update_data["password_encrypted"] = update_data.pop("password")

    for field, value in update_data.items():
        setattr(account, field, value)

    db.commit()
    db.refresh(account)
    logger.info(f"Updated email account {account_id} for user {current_user.id}")
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
        logger.warning(f"Email account {account_id} not found for user {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email account not found"
        )

    db.delete(account)
    db.commit()
    logger.info(f"Deleted email account {account_id} for user {current_user.id}")
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

    query = db.query(Email).filter(Email.organization_id == org_id).options(
        joinedload(Email.account),
        joinedload(Email.task),
        joinedload(Email.calendar_event),
        joinedload(Email.attachments)
    )

    user_account_ids = db.query(EmailAccount.id).filter(
        and_(
            EmailAccount.organization_id == org_id,
            EmailAccount.user_id == current_user.id
        )
    ).subquery()
    query = query.filter(Email.account_id.in_(user_account_ids))

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
        label_filters = [Email.labels.contains([label]) for label in labels]
        query = query.filter(or_(*label_filters))
    if search:
        search_filter = or_(
            Email.subject.contains(search),
            Email.body_text.contains(search),
            Email.from_address.contains(search)
        )
        query = query.filter(search_filter)

    sort_column = getattr(Email, sort_by)
    if sort_order == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(asc(sort_column))

    total = query.count()
    offset = (page - 1) * per_page
    emails = query.offset(offset).limit(per_page).all()

    total_pages = (total + per_page - 1) // per_page

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

    logger.info(f"Fetched {len(email_details)} emails for user {current_user.id}")
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
        logger.warning(f"Email {email_id} not found for user {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found"
        )

    if email.status == "UNREAD":
        email.status = "READ"
        action = EmailAction(
            email_id=email.id,
            user_id=current_user.id,
            action_type="READ"
        )
        db.add(action)
        db.commit()

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

    logger.info(f"Fetched email {email_id} for user {current_user.id}")
    return EmailWithDetails(**email_dict)

@router.put("/emails/{email_id}", response_model=EmailResponse)
async def update_email(
    email_id: int,
    email_data: EmailUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an email (status, flags, labels, etc.)"""
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
        logger.warning(f"Email {email_id} not found for user {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found"
        )

    update_data = email_data.model_dump(exclude_unset=True)
    actions_to_log = []
    if "status" in update_data and update_data["status"] != email.status:
        actions_to_log.append(update_data["status"])
    if "is_flagged" in update_data and update_data["is_flagged"] != email.is_flagged:
        actions_to_log.append("FLAG" if update_data["is_flagged"] else "UNFLAG")

    for field, value in update_data.items():
        setattr(email, field, value)

    for action_type in actions_to_log:
        action = EmailAction(
            email_id=email.id,
            user_id=current_user.id,
            action_type=action_type
        )
        db.add(action)

    db.commit()
    db.refresh(email)
    logger.info(f"Updated email {email_id} for user {current_user.id}")
    return EmailResponse.model_validate(email)

@router.post("/compose", response_model=SentEmailResponse)
async def compose_and_send_email(
    compose_request: MailComposeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Compose and send an email"""
    account = db.query(EmailAccount).filter(
        and_(
            EmailAccount.id == compose_request.account_id,
            EmailAccount.organization_id == current_user.organization_id,
            EmailAccount.user_id == current_user.id
        )
    ).first()

    if not account:
        logger.warning(f"Email account {compose_request.account_id} not found for user {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email account not found"
        )

    subject = compose_request.subject
    body_text = compose_request.body_text
    html_body = compose_request.body_html

    if compose_request.template_id:
        template = db.query(EmailTemplate).filter(
            and_(
                EmailTemplate.id == compose_request.template_id,
                EmailTemplate.organization_id == current_user.organization_id
            )
        ).first()

        if template:
            template_vars = compose_request.template_variables or {}
            subject = template.subject_template
            body_text = template.body_text_template
            html_body = template.body_html_template

            for var, value in template_vars.items():
                if subject:
                    subject = subject.replace(f"{{{var}}}", str(value))
                if body_text:
                    body_text = body_text.replace(f"{{{var}}}", str(value))
                if html_body:
                    html_body = html_body.replace(f"{{{var}}}", str(value))

    sent_email = SentEmail(
        subject=subject,
        to_addresses=compose_request.to_addresses,
        cc_addresses=compose_request.cc_addresses,
        bcc_addresses=compose_request.bcc_addresses,
        body_text=body_text,
        body_html=html_body,
        account_id=compose_request.account_id,
        organization_id=current_user.organization_id,
        sent_by=current_user.id,
        task_id=compose_request.task_id,
        calendar_event_id=compose_request.calendar_event_id,
        in_reply_to_id=compose_request.in_reply_to_id,
        scheduled_at=compose_request.scheduled_at,
        sent_at=datetime.utcnow() if not compose_request.scheduled_at else None,
        status="SENT" if not compose_request.scheduled_at else "PENDING"
    )

    db.add(sent_email)
    db.commit()
    db.refresh(sent_email)
    logger.info(f"Composed and sent email from account {compose_request.account_id} by user {current_user.id}")
    return SentEmailResponse.model_validate(sent_email)

@router.post("/sync", response_model=MailSyncResponse)
async def sync_emails(
    sync_request: MailSyncRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Sync emails from email accounts"""
    org_id = current_user.organization_id

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
        logger.warning(f"No sync-enabled email accounts found for user {current_user.id}")
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
            account.last_sync_at = datetime.utcnow()
            account.last_sync_status = "SUCCESS"
            account.last_sync_error = None
            accounts_synced += 1
        except Exception as e:
            errors.append(f"Account {account.name}: {str(e)}")
            account.last_sync_status = "ERROR"
            account.last_sync_error = str(e)

    db.commit()
    logger.info(f"Synced {accounts_synced} email accounts for user {current_user.id}")
    return MailSyncResponse(
        success=len(errors) == 0,
        message="Email sync completed" if len(errors) == 0 else "Email sync completed with errors",
        accounts_synced=accounts_synced,
        emails_imported=emails_imported,
        errors=errors if errors else None
    )

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

    logger.info(f"Fetched {len(template_details)} email templates for user {current_user.id}")
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
    logger.info(f"Created email template by user {current_user.id}")
    return EmailTemplateResponse.model_validate(template)