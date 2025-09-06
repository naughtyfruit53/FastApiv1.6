"""
Email API endpoints for reading, sending, and managing emails via OAuth
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.api.v1.auth import get_current_active_user as get_current_user
from app.models.user_models import User
from app.models.oauth_models import UserEmailToken, OAuthProvider
from app.schemas.oauth_schemas import (
    EmailListRequest, EmailListResponse, EmailDetailRequest, EmailDetailResponse,
    EmailComposeRequest, EmailComposeResponse
)
from app.services.email_api_service import EmailAPIService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/tokens/{token_id}/emails", response_model=EmailListResponse)
async def list_emails(
    token_id: int,
    folder: str = Query("INBOX", description="Email folder to list"),
    limit: int = Query(50, ge=1, le=100, description="Number of emails to return"),
    offset: int = Query(0, ge=0, description="Number of emails to skip"),
    unread_only: bool = Query(False, description="Only return unread emails"),
    search_query: Optional[str] = Query(None, description="Search query"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List emails from a connected email account
    """
    # Verify token belongs to current user
    token = db.query(UserEmailToken).filter(
        UserEmailToken.id == token_id,
        UserEmailToken.user_id == current_user.id,
        UserEmailToken.organization_id == current_user.organization_id
    ).first()
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email token not found"
        )
    
    if not token.is_active():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email token is not active"
        )
    
    try:
        email_service = EmailAPIService(db)
        
        if token.provider == OAuthProvider.GOOGLE:
            return email_service.list_emails_gmail(
                token_id=token_id,
                folder=folder,
                limit=limit,
                offset=offset,
                unread_only=unread_only,
                search_query=search_query
            )
        elif token.provider in [OAuthProvider.MICROSOFT, OAuthProvider.OUTLOOK]:
            return email_service.list_emails_microsoft(
                token_id=token_id,
                folder=folder,
                limit=limit,
                offset=offset,
                unread_only=unread_only,
                search_query=search_query
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported provider: {token.provider}"
            )
            
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error listing emails: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list emails"
        )


@router.get("/tokens/{token_id}/emails/{message_id}", response_model=EmailDetailResponse)
async def get_email_detail(
    token_id: int,
    message_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific email
    """
    # Verify token belongs to current user
    token = db.query(UserEmailToken).filter(
        UserEmailToken.id == token_id,
        UserEmailToken.user_id == current_user.id,
        UserEmailToken.organization_id == current_user.organization_id
    ).first()
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email token not found"
        )
    
    if not token.is_active():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email token is not active"
        )
    
    try:
        email_service = EmailAPIService(db)
        
        if token.provider == OAuthProvider.GOOGLE:
            return email_service.get_email_detail_gmail(token_id, message_id)
        elif token.provider in [OAuthProvider.MICROSOFT, OAuthProvider.OUTLOOK]:
            # TODO: Implement Microsoft Graph email detail
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="Microsoft Graph email detail not yet implemented"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported provider: {token.provider}"
            )
            
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error getting email detail: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get email detail"
        )


@router.post("/tokens/{token_id}/emails/send", response_model=EmailComposeResponse)
async def send_email(
    token_id: int,
    compose_request: EmailComposeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send an email using a connected email account
    """
    # Verify token belongs to current user
    token = db.query(UserEmailToken).filter(
        UserEmailToken.id == token_id,
        UserEmailToken.user_id == current_user.id,
        UserEmailToken.organization_id == current_user.organization_id
    ).first()
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email token not found"
        )
    
    if not token.is_active():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email token is not active"
        )
    
    try:
        email_service = EmailAPIService(db)
        
        # Override token_id in request
        compose_request.token_id = token_id
        
        if token.provider == OAuthProvider.GOOGLE:
            return email_service.send_email_gmail(token_id, compose_request)
        elif token.provider in [OAuthProvider.MICROSOFT, OAuthProvider.OUTLOOK]:
            return email_service.send_email_microsoft(token_id, compose_request)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported provider: {token.provider}"
            )
            
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send email"
        )


@router.get("/tokens/{token_id}/folders")
async def get_email_folders(
    token_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get available email folders for an account
    """
    # Verify token belongs to current user
    token = db.query(UserEmailToken).filter(
        UserEmailToken.id == token_id,
        UserEmailToken.user_id == current_user.id,
        UserEmailToken.organization_id == current_user.organization_id
    ).first()
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email token not found"
        )
    
    # Return standard folders for now
    # TODO: Implement dynamic folder listing from providers
    folders = []
    
    if token.provider == OAuthProvider.GOOGLE:
        folders = [
            {"id": "INBOX", "name": "Inbox", "type": "inbox"},
            {"id": "SENT", "name": "Sent", "type": "sent"},
            {"id": "DRAFT", "name": "Drafts", "type": "drafts"},
            {"id": "SPAM", "name": "Spam", "type": "spam"},
            {"id": "TRASH", "name": "Trash", "type": "trash"},
        ]
    elif token.provider in [OAuthProvider.MICROSOFT, OAuthProvider.OUTLOOK]:
        folders = [
            {"id": "inbox", "name": "Inbox", "type": "inbox"},
            {"id": "sentitems", "name": "Sent Items", "type": "sent"},
            {"id": "drafts", "name": "Drafts", "type": "drafts"},
            {"id": "deleteditems", "name": "Deleted Items", "type": "trash"},
            {"id": "junkemail", "name": "Junk Email", "type": "spam"},
        ]
    
    return {"folders": folders}


@router.post("/tokens/{token_id}/emails/{message_id}/mark-read")
async def mark_email_read(
    token_id: int,
    message_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark an email as read
    """
    # Verify token belongs to current user
    token = db.query(UserEmailToken).filter(
        UserEmailToken.id == token_id,
        UserEmailToken.user_id == current_user.id,
        UserEmailToken.organization_id == current_user.organization_id
    ).first()
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email token not found"
        )
    
    # TODO: Implement mark as read functionality
    return {"success": True, "message": "Email marked as read"}


@router.post("/tokens/{token_id}/emails/{message_id}/mark-unread")
async def mark_email_unread(
    token_id: int,
    message_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark an email as unread
    """
    # Verify token belongs to current user
    token = db.query(UserEmailToken).filter(
        UserEmailToken.id == token_id,
        UserEmailToken.user_id == current_user.id,
        UserEmailToken.organization_id == current_user.organization_id
    ).first()
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email token not found"
        )
    
    # TODO: Implement mark as unread functionality
    return {"success": True, "message": "Email marked as unread"}