# app/api/v1/password.py

"""
Password management endpoints for authentication
"""

import logging  # <-- ADDED THIS IMPORT

from fastapi import APIRouter, Depends, HTTPException, status, Request, Body
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token  # ADDED create_refresh_token
from app.core.config import settings
from app.core.audit import AuditLogger, get_client_ip, get_user_agent
from app.models import User
from app.schemas.user import (
    PasswordChangeRequest, ForgotPasswordRequest, PasswordResetRequest, 
    PasswordChangeResponse, OTPResponse, AdminPasswordResetResponse, AdminPasswordResetRequest
)
from app.services.user_service import UserService
from app.services.otp_service import OTPService
from app.services.system_email_service import system_email_service
from .user import get_current_active_user, get_current_super_admin
from app.core.logging import log_password_change
import secrets
import string

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/change", response_model=PasswordChangeResponse)
async def change_password(
    password_data: PasswordChangeRequest = Body(...),
    request: Request = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Change user password with audit logging"""
    logger.info(f"🔐 Password change request received for user {current_user.email}")
    logger.info(f"📝 Request payload: new_password=*****, current_password={'PROVIDED' if password_data.current_password else 'NOT_PROVIDED'}, confirm_password={'PROVIDED' if password_data.confirm_password else 'NOT_PROVIDED'}")
    logger.info(f"👤 User details: must_change_password={current_user.must_change_password}, role={current_user.role}")
    
    try:
        # Handle mandatory password change (e.g., for super admin first login)
        if current_user.must_change_password:
            logger.info(f"🔄 Processing mandatory password change for user {current_user.email}")
            # For mandatory password changes, confirm_password is required if provided
            if password_data.confirm_password is not None and password_data.new_password != password_data.confirm_password:
                logger.error(f"❌ Password confirmation mismatch for mandatory password change")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="New passwords do not match"
                )
        else:
            logger.info(f"🔄 Processing normal password change for user {current_user.email}")
            # For normal password changes, require and verify current password
            if not password_data.current_password:
                logger.error(f"❌ Current password not provided for normal password change")
                # Log failed password change attempt
                AuditLogger.log_password_reset(
                    db=db,
                    admin_email=current_user.email,
                    target_email=current_user.email,
                    admin_user_id=current_user.id,
                    target_user_id=current_user.id,
                    organization_id=current_user.organization_id,
                    success=False,
                    ip_address=get_client_ip(request),
                    user_agent=get_user_agent(request),
                    error_message="Current password is required for normal password change",
                    reset_type="SELF_PASSWORD_CHANGE"
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Current password is required"
                )
            
            if not verify_password(password_data.current_password, current_user.hashed_password):
                logger.error(f"❌ Current password verification failed for user {current_user.email}")
                # Log failed password change attempt
                AuditLogger.log_password_reset(
                    db=db,
                    admin_email=current_user.email,
                    target_email=current_user.email,
                    admin_user_id=current_user.id,
                    target_user_id=current_user.id,
                    organization_id=current_user.organization_id,
                    success=False,
                    ip_address=get_client_ip(request),
                    user_agent=get_user_agent(request),
                    error_message="Current password is incorrect",
                    reset_type="SELF_PASSWORD_CHANGE"
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Current password is incorrect"
                )
            
            # For normal password changes, validate confirm_password if provided
            if password_data.confirm_password is not None and password_data.new_password != password_data.confirm_password:
                logger.error(f"❌ Password confirmation mismatch for normal password change")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="New passwords do not match"
                )
        
        logger.info(f"✅ Password validation successful, updating password for user {current_user.email}")
        
        # Update password
        current_user.hashed_password = get_password_hash(password_data.new_password)
        current_user.must_change_password = False
        current_user.force_password_reset = False
        
        # Clear temporary password if exists
        UserService.clear_temporary_password(db, current_user)
        
        db.commit()
        
        # Generate new JWT token to prevent session invalidation
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        new_access_token = create_access_token(
            subject=current_user.email,
            organization_id=current_user.organization_id,
            user_role=current_user.role,
            user_type="platform" if getattr(current_user, 'is_platform_user', False) else "organization",
            expires_delta=access_token_expires
        )
        
        refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
        new_refresh_token = create_refresh_token(
            subject=current_user.email,
            organization_id=current_user.organization_id,
            user_role=current_user.role,
            user_type="platform" if getattr(current_user, 'is_platform_user', False) else "organization",
            expires_delta=refresh_token_expires
        )
        
        # Log successful password change
        AuditLogger.log_password_reset(
            db=db,
            admin_email=current_user.email,
            target_email=current_user.email,
            admin_user_id=current_user.id,
            target_user_id=current_user.id,
            organization_id=current_user.organization_id,
            success=True,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            reset_type="SELF_PASSWORD_CHANGE"
        )
        
        # Enhanced logging for password change with JWT information
        change_type = "MANDATORY" if current_user.must_change_password else "NORMAL"
        log_password_change(current_user.email, change_type, True, None, True)
        
        logger.info(f"🎉 Password changed successfully for user {current_user.email}, new JWT token issued")
        return PasswordChangeResponse(
            message="Password changed successfully",
            access_token=new_access_token,
            refresh_token=new_refresh_token,  # ADDED
            token_type="bearer"
        )
        
    except HTTPException as he:
        logger.error(f"❌ HTTP Exception during password change: {he.detail}")
        log_password_change(current_user.email, "UNKNOWN", False, he.detail, False)
        raise he
    except Exception as e:
        logger.error(f"💥 Unexpected error during password change for user {current_user.email}: {str(e)}")
        log_password_change(current_user.email, "UNKNOWN", False, str(e), False)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error changing password"
        )


@router.post("/forgot", response_model=OTPResponse)
async def forgot_password(
    forgot_data: ForgotPasswordRequest = Body(...),
    request: Request = None,
    db: Session = Depends(get_db)
):
    """Request password reset via OTP with audit logging"""
    try:
        # Check if user exists
        user = UserService.get_user_by_email(db, forgot_data.email)
        
        # Log forgot password request
        AuditLogger.log_password_reset(
            db=db,
            admin_email="system",
            target_email=forgot_data.email,
            target_user_id=user.id if user else None,
            organization_id=user.organization_id if user else None,
            success=user is not None and user.is_active,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            error_message="User not found or inactive" if not (user and user.is_active) else None,
            reset_type="FORGOT_PASSWORD_REQUEST"
        )
        
        if not user:
            # For security, we don't reveal if email exists in our system
            logger.warning(f"Password reset requested for non-existent email: {forgot_data.email}")
            return OTPResponse(
                message="If the email exists in our system, a password reset OTP has been sent.",
                email=forgot_data.email
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is inactive"
            )
        
        # Generate and send OTP for password reset
        otp_service = OTPService(db)
        success = otp_service.generate_and_send_otp(forgot_data.email, "password_reset")
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate OTP. Please try again."
            )
        
        logger.info(f"Password reset OTP requested for {forgot_data.email}")
        return OTPResponse(
            message="Password reset OTP sent successfully to your email address.",
            email=forgot_data.email
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Forgot password error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during password reset request"
        )


@router.post("/reset", response_model=PasswordChangeResponse)
async def reset_password(
    reset_data: PasswordResetRequest = Body(...),
    request: Request = None,
    db: Session = Depends(get_db)
):
    """Reset password using OTP with audit logging"""
    try:
        # Verify OTP for password reset
        otp_service = OTPService(db)
        otp_valid = otp_service.verify_otp(reset_data.email, reset_data.otp, "password_reset")
        
        # Find user
        user = UserService.get_user_by_email(db, reset_data.email)
        
        # Log password reset attempt
        AuditLogger.log_password_reset(
            db=db,
            admin_email="system",
            target_email=reset_data.email,
            target_user_id=user.id if user else None,
            organization_id=user.organization_id if user else None,
            success=otp_valid and user is not None and user.is_active,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            error_message="Invalid OTP or user not found" if not (otp_valid and user) else None,
            reset_type="OTP_PASSWORD_RESET"
        )
        
        if not otp_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired OTP"
            )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is inactive"
            )
        
        # Update password
        user.hashed_password = get_password_hash(reset_data.new_password)
        user.must_change_password = False
        user.force_password_reset = False
        
        # Reset failed login attempts and clear temporary password
        user.failed_login_attempts = 0
        user.locked_until = None
        UserService.clear_temporary_password(db, user)
        
        db.commit()
        
        # Generate new JWT token to prevent session invalidation after password reset
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        new_access_token = create_access_token(
            subject=user.email,
            organization_id=user.organization_id,
            user_role=user.role,
            user_type="platform" if getattr(user, 'is_platform_user', False) else "organization",
            expires_delta=access_token_expires
        )
        
        refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
        new_refresh_token = create_refresh_token(
            subject=user.email,
            organization_id=user.organization_id,
            user_role=user.role,
            user_type="platform" if getattr(user, 'is_platform_user', False) else "organization",
            expires_delta=refresh_token_expires
        )
        
        logger.info(f"Password reset successfully for {user.email}, new JWT token issued")
        return PasswordChangeResponse(
            message="Password reset successfully",
            access_token=new_access_token,
            refresh_token=new_refresh_token,  # ADDED
            token_type="bearer"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password reset error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during password reset"
        )


@router.post("/admin-reset", response_model=AdminPasswordResetResponse)
async def admin_reset_password(
    reset_data: AdminPasswordResetRequest = Body(...),
    request: Request = None,
    current_user: User = Depends(get_current_super_admin),
    db: Session = Depends(get_db)
):
    """Admin password reset endpoint"""
    try:
        user = db.query(User).filter(User.email == reset_data.user_email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        new_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
        user.hashed_password = get_password_hash(new_password)
        user.must_change_password = True
        db.commit()
        
        # Send email (system-level: app password reset)
        success, error = await system_email_service.send_password_reset_email(
            user_email=reset_data.user_email,
            user_name=user.full_name or user.username,
            new_password=new_password,
            reset_by=current_user.email,
            organization_name=user.organization.name if user.organization else None,
            organization_id=user.organization_id,
            user_id=user.id
        )
        
        # Log successful password reset with enhanced details
        from app.core.logging import log_password_reset, log_security_event
        log_password_reset(user.email, current_user.email, True)
        log_security_event(
            "Admin Password Reset Success",
            user_email=current_user.email,
            details=f"Reset password for {user.email}"
        )
        
        return AdminPasswordResetResponse(
            message="Password reset successfully",
            target_email=user.email,
            new_password=new_password,
            email_sent=success,
            email_error=error,
            must_change_password=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Admin password reset error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error during admin password reset"
        )