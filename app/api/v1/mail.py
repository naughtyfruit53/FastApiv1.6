# app/api/v1/mail.py

"""
Mail and Email Management API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Query, Form, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
import traceback
from datetime import datetime, timedelta
from sqlalchemy import and_, or_, func, desc, asc
import json

from app.core.database import get_db
from app.api.v1.auth import get_current_active_user as get_current_user
from app.models.user_models import User
from app.models.oauth_models import UserEmailToken, OAuthProvider
from app.schemas.oauth_schemas import UserEmailTokenResponse
from app.schemas.mail_schemas import MailDashboardStats, MailSyncRequest, MailSyncResponse, MailComposeRequest, SentEmailResponse
from app.services.oauth_service import OAuth2Service
from app.services.email_api_service import EmailAPIService
from app.models.mail_management import Email, SentEmail

router = APIRouter()


@router.get("/dashboard", response_model=MailDashboardStats)
async def get_mail_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get mail dashboard statistics"""
    try:
        org_id = current_user.organization_id
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        week_start = today_start - timedelta(days=today_start.weekday())
        week_end = week_start + timedelta(days=7)
        
        # Base query for emails
        email_query = db.query(Email).filter(Email.organization_id == org_id)
        
        # Total emails
        total_emails = email_query.count()
        
        # Unread emails
        unread_emails = email_query.filter(Email.status == "UNREAD").count()
        
        # Flagged emails
        flagged_emails = email_query.filter(Email.is_flagged == True).count()
        
        # Today's emails
        today_emails = email_query.filter(
            Email.received_at >= today_start,
            Email.received_at < today_end
        ).count()
        
        # This week's emails
        this_week_emails = email_query.filter(
            Email.received_at >= week_start,
            Email.received_at < week_end
        ).count()
        
        # Sent emails
        sent_emails = db.query(SentEmail).filter(SentEmail.organization_id == org_id).count()
        
        # Draft emails
        draft_emails = db.query(SentEmail).filter(
            SentEmail.organization_id == org_id,
            SentEmail.status == "DRAFT"
        ).count()
        
        # Spam emails
        spam_emails = email_query.filter(Email.status == "SPAM").count()
        
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
        logger.error(f"Error fetching mail dashboard stats: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Failed to fetch dashboard stats")


@router.get("/emails")
async def list_emails(
    token_id: Optional[int] = Query(None),
    folder: Optional[str] = Query('INBOX'),
    page: int = Query(1),
    per_page: int = Query(20),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List emails from specific token or all"""
    email_service = EmailAPIService(db)
    return await email_service.list_emails(current_user, token_id, folder, page, per_page)


@router.get("/emails/{email_id}")
async def get_email(
    email_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get email details"""
    email_service = EmailAPIService(db)
    return await email_service.get_email_detail(current_user, email_id)


@router.put("/emails/{email_id}")
async def update_email(
    email_id: int,
    update_data: Dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update email status"""
    email_service = EmailAPIService(db)
    return await email_service.update_email(current_user, email_id, update_data)


@router.delete("/emails/{email_id}")
async def delete_email(
    email_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete email"""
    email_service = EmailAPIService(db)
    return await email_service.delete_email(current_user, email_id)


@router.get("/sent-emails")
async def list_sent_emails(
    page: int = Query(1),
    per_page: int = Query(20),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List sent emails"""
    email_service = EmailAPIService(db)
    return await email_service.list_sent_emails(current_user, page, per_page)


@router.post("/tokens/{token_id}/emails/send", response_model=SentEmailResponse)
async def send_email(
    token_id: int,
    to_addresses: str = Form(...),
    cc_addresses: str = Form("[]"),
    bcc_addresses: str = Form("[]"),
    subject: str = Form(...),
    body_html: str = Form(""),
    body_text: str = Form(""),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    attachments: List[UploadFile] = File(None)
):
    """Send email using specific token"""
    try:
        compose_request = MailComposeRequest(
            to_addresses=json.loads(to_addresses),
            cc_addresses=json.loads(cc_addresses),
            bcc_addresses=json.loads(bcc_addresses),
            subject=subject,
            body_html=body_html,
            body_text=body_text
        )
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Invalid input format: {str(e)}")
    email_service = EmailAPIService(db)
    return await email_service.send_email(current_user, token_id, compose_request)


@router.post("/sync", response_model=MailSyncResponse)
async def sync_emails(
    sync_request: MailSyncRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Sync emails from one or all tokens"""
    email_service = EmailAPIService(db)
    return await email_service.sync_emails(current_user, sync_request.token_id, sync_request.force_sync)


@router.get("/sync/jobs")
async def list_sync_jobs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List active sync jobs"""
    # Implement job tracking if needed
    return []


@router.get("/sync/settings")
async def get_sync_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get sync settings"""
    # Implement or return defaults
    return {
        "auto_sync_enabled": True,
        "sync_interval_minutes": 15,
        "max_concurrent_syncs": 3,
        "sync_folders": ["INBOX", "SENT"],
        "sync_attachments": True,
        "keep_local_copies": True
    }


@router.put("/sync/settings")
async def update_sync_settings(
    settings_data: Dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update sync settings"""
    # Implement saving
    return settings_data


@router.get("/sync/stats")
async def get_sync_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get sync statistics"""
    # Implement or return defaults
    return {
        "total_syncs_today": 0,
        "successful_syncs": 0,
        "failed_syncs": 0,
        "emails_synced_today": 0,
        "last_full_sync": None,
        "next_scheduled_sync": None
    }


@router.get("/templates")
async def get_templates(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get email templates"""
    # From existing
    pass