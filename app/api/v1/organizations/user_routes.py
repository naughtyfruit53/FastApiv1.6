# app/api/v1/organizations/user_routes.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict
import logging
import secrets
import string

from app.core.database import get_db
from app.core.security import get_password_hash
from app.core.permissions import PermissionChecker, Permission
from app.models import User, Organization
from app.schemas.user import UserRole
from app.schemas import UserCreate, UserInDB
from app.core.security import get_current_user
from app.api.v1.auth import get_current_active_user
from app.utils.supabase_auth import supabase_auth_service, SupabaseAuthError
from app.services.email_service import email_service  # Assuming email_service exists for sending emails

logger = logging.getLogger(__name__)

user_router = APIRouter()

@user_router.get("/{organization_id:int}/users", response_model=List[UserInDB])
async def list_organization_users(
    organization_id: int,
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List users in organization"""
    if not current_user.is_super_admin and current_user.organization_id != organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this organization"
        )
  
    if not current_user.is_super_admin and current_user.role != UserRole.ORG_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to list users"
        )
  
    query = db.query(User).filter(User.organization_id == organization_id)
  
    if active_only:
        query = query.filter(User.is_active == True)
  
    users = query.offset(skip).limit(limit).all()
    return users

@user_router.post("/{organization_id:int}/users", response_model=UserInDB)
async def create_user_in_organization(
    organization_id: int,
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create user in organization (org admin or super admin only)"""
    if not current_user.is_super_admin and current_user.organization_id != organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this organization"
        )
  
    if not current_user.is_super_admin and current_user.role not in [UserRole.ORG_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organization administrators can create users"
        )
  
    org = db.query(Organization).filter(Organization.id == organization_id).first()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
  
    existing_user = db.query(User).filter(
        User.email == user_data.email,
        User.organization_id == organization_id
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered in this organization"
        )
  
    if user_data.username:
        existing_username = db.query(User).filter(
            User.username == user_data.username,
            User.organization_id == organization_id
        ).first()
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken in this organization"
            )
  
    if not current_user.is_super_admin:
        user_count = db.query(User).filter(
            User.organization_id == organization_id,
            User.is_active == True
        ).count()
      
        if user_count >= org.max_users:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Maximum user limit ({org.max_users}) reached for this organization"
            )
  
    if user_data.role == UserRole.ORG_ADMIN.value and not current_user.is_super_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super administrators can assign organization administrator role"
        )
  
    supabase_uuid = None
    try:
        supabase_user = supabase_auth_service.create_user(
            email=user_data.email,
            password=user_data.password,
            user_metadata={
                "full_name": user_data.full_name,
                "role": user_data.role.value if user_data.role else UserRole.STANDARD_USER.value,
                "organization_id": organization_id
            }
        )
        supabase_uuid = supabase_user["supabase_uuid"]
    except SupabaseAuthError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
  
    try:
        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            organization_id=organization_id,
            email=user_data.email,
            username=user_data.username or user_data.email.split('@')[0],
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            role=user_data.role or UserRole.STANDARD_USER.value,
            department=user_data.department,
            designation=user_data.designation,
            employee_id=user_data.employee_id,
            phone=user_data.phone,
            is_active=user_data.is_active if user_data.is_active is not None else True,
            supabase_uuid=supabase_uuid
        )
      
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
      
        logger.info(f"User {new_user.email} created in organization {org.name} by {current_user.email}")
        return new_user
      
    except Exception as e:
        try:
            supabase_auth_service.delete_user(supabase_uuid)
        except Exception as cleanup_e:
            logger.error(f"Failed to cleanup Supabase user {supabase_uuid}: {cleanup_e}")
        db.rollback()
        logger.error(f"Error creating user in organization: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user in organization"
        )

@user_router.put("/{organization_id:int}/users/{user_id:int}", response_model=UserInDB)
async def update_user_in_organization(
    organization_id: int,
    user_id: int,
    user_update: Dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update user in organization (org admin or super admin only)"""
    if not current_user.is_super_admin and current_user.organization_id != organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this organization"
        )
  
    user = db.query(User).filter(
        User.id == user_id,
        User.organization_id == organization_id
    ).first()
  
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in this organization"
        )
  
    is_self_update = current_user.id == user_id
    if not is_self_update and not current_user.is_super_admin and current_user.role not in [UserRole.ORG_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organization administrators can update other users"
        )
  
    if is_self_update and not current_user.is_super_admin and current_user.role not in [UserRole.ORG_ADMIN]:
        allowed_fields = {"email", "username", "full_name", "phone", "department", "designation"}
        if not all(field in allowed_fields for field in user_update.keys()):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot update administrative fields"
            )
  
    if "role" in user_update:
        if user_update["role"] == UserRole.ORG_ADMIN.value and not current_user.is_super_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only super administrators can assign organization administrator role"
            )
  
    try:
        for field, value in user_update.items():
            if field == "password" and value:
                setattr(user, "hashed_password", get_password_hash(value))
            elif hasattr(user, field):
                setattr(user, field, value)
      
        db.commit()
        db.refresh(user)
      
        logger.info(f"User {user.email} updated in organization {organization_id} by {current_user.email}")
        return user
      
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating user in organization: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user in organization"
        )

@user_router.delete("/{organization_id:int}/users/{user_id:int}")
async def delete_user_from_organization(
    organization_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete user from organization (org admin or super admin only)"""
    if not current_user.is_super_admin and current_user.organization_id != organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this organization"
        )
  
    if not current_user.is_super_admin and current_user.role not in [UserRole.ORG_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organization administrators can delete users"
        )
  
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
  
    user = db.query(User).filter(
        User.id == user_id,
        User.organization_id == organization_id
    ).first()
  
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in this organization"
        )
  
    if user.role == UserRole.ORG_ADMIN.value and not current_user.is_super_admin:
        admin_count = db.query(User).filter(
            User.organization_id == organization_id,
            User.role == UserRole.ORG_ADMIN.value,
            User.is_active == True
        ).count()
      
        if admin_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete the last organization administrator"
            )
  
    try:
        db.delete(user)
        db.commit()
      
        logger.info(f"User {user.email} deleted from organization {organization_id} by {current_user.email}")
        return {"message": f"User {user.email} deleted successfully"}
      
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting user from organization: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user from organization"
        )

@user_router.post("/{organization_id:int}/users/{user_id:int}/reset-password")
async def reset_user_password(
    organization_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Reset user password (org admin or super admin only)"""
    if not current_user.is_super_admin and current_user.organization_id != organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this organization"
        )
  
    if not current_user.is_super_admin and current_user.role not in [UserRole.ORG_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organization administrators can reset passwords"
        )
  
    user = db.query(User).filter(
        User.id == user_id,
        User.organization_id == organization_id
    ).first()
  
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in this organization"
        )
  
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Use the password change endpoint to reset your own password"
        )
  
    try:
        # Generate secure random password (12 characters: letters, digits, symbols)
        alphabet = string.ascii_letters + string.digits + string.punctuation
        new_password = ''.join(secrets.choice(alphabet) for i in range(12))
        
        # Update hashed password
        user.hashed_password = get_password_hash(new_password)
        user.must_change_password = True  # Force password change on next login
        db.commit()
        
        # Send email with new password
        success, error = email_service.send_password_reset_email(
            user_email=user.email,
            user_name=user.full_name or user.username,
            new_password=new_password,
            reset_by=current_user.email
        )
        
        if not success:
            logger.warning(f"Password reset succeeded but email failed for user {user.email}: {error}")
        
        logger.info(f"Password reset for user {user.email} in organization {organization_id} by {current_user.email}")
        return {
            "message": "Password reset successful" + (" but email notification failed" if not success else ". New password sent to user's email"),
            "new_password": new_password,  # Return for admin to manually share
            "email_sent": success,
            "email_error": error if not success else None
        }
      
    except Exception as e:
        db.rollback()
        logger.error(f"Error resetting user password: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset user password"
        )