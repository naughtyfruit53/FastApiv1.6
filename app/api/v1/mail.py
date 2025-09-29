# app/api/v1/mail.py

"""
Mail and Email Management API endpoints - Enhanced Brevo transactional email support
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Body
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import secrets
import string
import logging

from app.core.database import get_db
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.config import settings
from app.models import User, EmailSend, EmailStatus, EmailProvider, EmailType
from app.services.email_service import email_service
from app.api.v1.user import get_current_active_user
from app.schemas.user import (
    PasswordResetTokenRequest, PasswordResetConfirmRequest, 
    PasswordResetResponse, EmailSendResponse
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/password/request-reset", response_model=Dict[str, str])
async def request_password_reset(
    request_data: PasswordResetTokenRequest = Body(...),
    request: Request = None,
    db: Session = Depends(get_db)
):
    """
    Request password reset - generates secure token and sends email
    Enhanced with secure token handling (single-use, TTL)
    """
    try:
        # Check if user exists
        user = db.query(User).filter(User.email == request_data.email).first()
        
        if not user:
            # For security, don't reveal if email exists
            logger.warning(f"Password reset requested for non-existent email: {request_data.email}")
            return {
                "message": "If the email exists in our system, a password reset link has been sent.",
                "email": request_data.email
            }
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is inactive"
            )
        
        # Generate secure reset token (single-use, 1-hour TTL)
        reset_token = secrets.token_urlsafe(32)
        reset_expires = datetime.utcnow() + timedelta(hours=1)
        
        # Store token with user (you may need to add reset_token and reset_expires fields to User model)
        user.reset_token = get_password_hash(reset_token)  # Hash the token for security
        user.reset_token_expires = reset_expires
        user.reset_token_used = False
        
        # Generate reset URL
        reset_url = f"{getattr(settings, 'FRONTEND_URL', 'https://fast-apiv1-6.vercel.app')}/reset-password?token={reset_token}&email={user.email}"
        
        # Send reset email with token
        success, error = email_service.send_password_reset_token_email(
            user_email=user.email,
            user_name=user.full_name or user.username,
            reset_url=reset_url,
            organization_name=user.organization.name if user.organization else "Your Organization",
            organization_id=user.organization_id,
            user_id=user.id,
            db=db
        )
        
        if success:
            db.commit()
            logger.info(f"Password reset token sent successfully to {user.email}")
            return {
                "message": "Password reset link sent successfully to your email address.",
                "email": user.email
            }
        else:
            db.rollback()
            logger.error(f"Failed to send password reset email to {user.email}: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send password reset email. Please try again."
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password reset request error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during password reset request"
        )


@router.post("/password/confirm-reset", response_model=PasswordResetResponse)
async def confirm_password_reset(
    reset_data: PasswordResetConfirmRequest = Body(...),
    request: Request = None,
    db: Session = Depends(get_db)
):
    """
    Confirm password reset using secure token
    Enhanced with single-use token validation and TTL checks
    """
    try:
        # Find user by email
        user = db.query(User).filter(User.email == reset_data.email).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid reset token or email"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is inactive"
            )
        
        # Validate reset token
        if not user.reset_token or not user.reset_token_expires:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No valid reset token found"
            )
        
        if user.reset_token_used:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Reset token has already been used"
            )
        
        if datetime.utcnow() > user.reset_token_expires:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Reset token has expired"
            )
        
        # Verify token
        if not verify_password(reset_data.token, user.reset_token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid reset token"
            )
        
        # Update password
        user.hashed_password = get_password_hash(reset_data.new_password)
        user.must_change_password = False
        user.force_password_reset = False
        
        # Invalidate reset token (single-use)
        user.reset_token = None
        user.reset_token_expires = None
        user.reset_token_used = True
        
        # Reset failed login attempts
        user.failed_login_attempts = 0
        user.locked_until = None
        
        db.commit()
        
        # Generate new access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        new_access_token = create_access_token(
            subject=user.email,
            organization_id=user.organization_id,
            user_role=user.role,
            user_type="platform" if getattr(user, 'is_platform_user', False) else "organization",
            expires_delta=access_token_expires
        )
        
        logger.info(f"Password reset completed successfully for {user.email}")
        return PasswordResetResponse(
            message="Password reset successfully",
            access_token=new_access_token,
            token_type="bearer"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password reset confirmation error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during password reset confirmation"
        )