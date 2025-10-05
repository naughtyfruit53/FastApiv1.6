# app/api/routes/admin.py

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional, List
import secrets
import string
from datetime import datetime

from app.core.database import get_db
from app.api.v1.auth import get_current_super_admin, get_current_active_user
from app.services.user_service import UserService
from app.schemas.user import UserCreate, UserUpdate, UserInDB, AdminPasswordResetRequest, AdminPasswordResetResponse
from app.core.security import get_password_hash
from app.services.system_email_service import system_email_service
from app.core.logging import log_password_reset, log_security_event, log_database_operation
import logging
from app.models.user_models import User

logger = logging.getLogger(__name__)
router = APIRouter()

def generate_secure_password(length: int = 12) -> str:
    """Generate a secure random password"""
    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    password = ''.join(secrets.choice(characters) for _ in range(length))
    # Ensure at least one character from each category
    if not any(c.islower() for c in password):
        password = password[:-1] + secrets.choice(string.ascii_lowercase)
    if not any(c.isupper() for c in password):
        password = password[:-1] + secrets.choice(string.ascii_uppercase)
    if not any(c.isdigit() for c in password):
        password = password[:-1] + secrets.choice(string.digits)
    return password

@router.post("/reset-password", response_model=AdminPasswordResetResponse)
async def reset_user_password(
    reset_request: AdminPasswordResetRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_super_admin)
):
    """
    Reset password for a licenseholder admin user.
    Only super admins can perform this operation.
    Both emails the new password (if email configured) and displays it to super admin.
    """
    try:
        # Find the target user
        target_user = db.query(User).filter(User.email == reset_request.user_email).first()
        if not target_user:
            log_security_event(
                "Password reset failed - user not found", 
                user_email=current_user.email,
                details=f"Target user: {reset_request.user_email}"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if target user is a licenseholder admin
        if not target_user.is_licenseholder_admin and not target_user.is_super_admin:
            log_security_event(
                "Password reset denied - insufficient target user privileges",
                user_email=current_user.email,
                details=f"Target user: {reset_request.user_email}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Can only reset passwords for licenseholder admins"
            )
        
        # Prevent super admin password reset by non-super admin
        if target_user.is_super_admin and not current_user.is_super_admin:
            log_security_event(
                "Password reset denied - super admin protection",
                user_email=current_user.email,
                details=f"Target user: {reset_request.user_email}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot reset super admin password"
            )
        
        # Generate new secure password
        new_password = generate_secure_password()
        hashed_password = get_password_hash(new_password)
        
        # Update password in database
        target_user.hashed_password = hashed_password
        target_user.password_changed_at = datetime.utcnow()
        target_user.must_change_password = True  # Force password change on next login
        
        # Log the database operation
        log_database_operation("UPDATE", "users", target_user.id, current_user.id)
        
        # Attempt to send email notification with retry logic
        email_sent = False
        email_error = None
        email_retry_attempts = 0
        max_email_retries = 3
        
        if target_user.email:
            while email_retry_attempts < max_email_retries and not email_sent:
                try:
                    email_retry_attempts += 1
                    logger.info(f"Attempting to send password reset email (attempt {email_retry_attempts}/{max_email_retries})")
                    
                    email_sent, email_error = await system_email_service.send_password_reset_email(
                        user_email=target_user.email,
                        user_name=target_user.full_name or target_user.email,
                        new_password=new_password,
                        reset_by=current_user.email,
                        organization_name=target_user.organization.name if target_user.organization else None,
                        organization_id=target_user.organization_id,
                        user_id=target_user.id
                    )
                    
                    if email_sent:
                        logger.info(f"Password reset email sent successfully to {target_user.email}")
                        log_password_reset(target_user.email, current_user.email, True)
                        break
                    else:
                        logger.warning(f"Email send attempt {email_retry_attempts} failed: {email_error}")
                        
                except Exception as e:
                    email_error = str(e)
                    logger.error(f"Email attempt {email_retry_attempts} failed for {target_user.email}: {e}")
                    
                    # If this isn't the last attempt, wait before retrying
                    if email_retry_attempts < max_email_retries:
                        logger.info(f"Retrying email send in 2 seconds...")
                        import time
                        time.sleep(2)
                    
            # If all attempts failed, provide specific error guidance
            if not email_sent:
                log_password_reset(target_user.email, current_user.email, False)
                
                # Provide specific error guidance based on error type
                if email_error:
                    if "SMTP" in email_error or "connection" in email_error.lower():
                        email_error = f"Email server connection failed after {max_email_retries} attempts: {email_error}. Please check email configuration or contact system administrator."
                    elif "authentication" in email_error.lower():
                        email_error = f"Email authentication failed: {email_error}. Please verify email credentials."
                    elif "timeout" in email_error.lower():
                        email_error = f"Email sending timed out after {max_email_retries} attempts: {email_error}. Please try again later."
                    else:
                        email_error = f"Email sending failed after {max_email_retries} attempts: {email_error}. Please provide the new password manually to the user."
                else:
                    email_error = f"Email sending failed after {max_email_retries} attempts for unknown reasons. Please provide the new password manually to the user."
        else:
            email_error = "User has no email address configured. Please provide the new password manually to the user."
            logger.warning(f"Cannot send password reset - no email for user {target_user.id}")
        
        # Commit the changes regardless of email status
        try:
            db.commit()
            db.refresh(target_user)
            logger.info(f"Password reset completed successfully for user {target_user.email}")
        except Exception as db_error:
            db.rollback()
            logger.error(f"Database error during password reset: {db_error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save password changes to database: {str(db_error)}"
            )
        
        # Log successful password reset
        log_security_event(
            "Password reset completed",
            user_email=current_user.email,
            details=f"Target user: {reset_request.user_email}, Email sent: {email_sent}"
        )
        
        return AdminPasswordResetResponse(
            message="Password reset successfully",
            target_email=target_user.email,
            new_password=new_password,  # Display to super admin
            email_sent=email_sent,
            email_error=email_error,
            must_change_password=True
        )
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error during password reset: {e}")
        log_security_event(
            "Password reset error",
            user_email=current_user.email,
            details=f"Error: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during password reset"
        )

@router.get("/users", response_model=List[UserInDB])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    organization_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_super_admin)
):
    """List users (super admin only)"""
    try:
        query = db.query(User)
        
        if organization_id:
            query = query.filter(User.organization_id == organization_id)
        
        users = query.offset(skip).limit(limit).all()
        
        log_database_operation("SELECT", "users", None, current_user.id)
        
        return users
        
    except Exception as e:
        logger.error(f"Error listing users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve users"
        )

@router.get("/users/me", response_model=UserInDB)
async def get_current_user_me(current_user: User = Depends(get_current_active_user)):
    """Get current authenticated user details"""
    return current_user

@router.put("/users/{user_id}", response_model=UserInDB)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_super_admin)
):
    """Update user details (super admin only)"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update fields
        update_data = user_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            if field == "password" and value:
                setattr(user, "hashed_password", get_password_hash(value))
                user.password_changed_at = datetime.utcnow()
            else:
                setattr(user, field, value)
        
        db.commit()
        db.refresh(user)
        
        log_database_operation("UPDATE", "users", user_id, current_user.id)
        log_security_event(
            "User updated",
            user_email=current_user.email,
            details=f"Updated user: {user.email}"
        )
        
        return user
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user"
        )

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_super_admin)
):
    """Delete user (super admin only)"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Prevent deletion of super admin accounts
        if user.is_super_admin:
            log_security_event(
                "User deletion denied - super admin protection",
                user_email=current_user.email,
                details=f"Target user: {user.email}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot delete super admin accounts"
            )
        
        user_email = user.email
        db.delete(user)
        db.commit()
        
        log_database_operation("DELETE", "users", user_id, current_user.id)
        log_security_event(
            "User deleted",
            user_email=current_user.email,
            details=f"Deleted user: {user_email}"
        )
        
        return {"message": f"User {user_email} deleted successfully"}
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )