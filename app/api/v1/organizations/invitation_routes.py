# app/api/v1/organizations/invitation_routes.py

# Revised app/api/v1/organizations/invitation_routes.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Optional

from app.core.database import get_db
from app.core.security import get_password_hash
from app.core.permissions import PermissionChecker, Permission
from app.models import User
from app.schemas.user import UserRole
from app.schemas import UserCreate, UserInDB
from app.core.security import get_current_user
from app.api.v1.auth import get_current_active_user
from app.utils.supabase_auth import supabase_auth_service, SupabaseAuthError
from .services import email_service, EMAIL_SERVICE_AVAILABLE  # Assuming this is where email_service is defined

import logging
import secrets
import string

logger = logging.getLogger(__name__)

invitation_router = APIRouter()

@invitation_router.get("/{organization_id:int}/invitations")
async def list_organization_invitations(
    organization_id: int,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List organization invitations (org admin or super admin only)"""
  
    # Check access permissions
    if not current_user.is_super_admin and current_user.organization_id != organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this organization"
        )
  
    if not current_user.is_super_admin and current_user.role not in [UserRole.ORG_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organization administrators can view invitations"
        )
  
    # Check if organization exists
    org = db.query(Organization).filter(Organization.id == organization_id).first()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
  
    # For now, return recently invited users as "pending invitations"
    # In a full implementation, you would have a separate Invitation table
    query = db.query(User).filter(
        User.organization_id == organization_id,
        User.must_change_password == True # Indicator of pending invitation
    )
  
    invitations = query.offset(skip).limit(limit).all()
  
    # Transform to invitation-like format
    invitation_data = []
    for user in invitations:
        invitation_data.append({
            "id": user.id,
            "email": user.email,
            "role": user.role,
            "status": "pending" if user.must_change_password else "accepted",
            "invited_at": user.created_at,
            "invited_by": "unknown", # Would track this in full implementation
            "organization_id": organization_id,
            "organization_name": org.name
        })
  
    return invitation_data


@invitation_router.post("/{organization_id:int}/invitations/{invitation_id:int}/resend")
async def resend_organization_invitation(
    organization_id: int,
    invitation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Resend organization invitation (org admin or super admin only)"""
  
    # Check access permissions
    if not current_user.is_super_admin and current_user.organization_id != organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this organization"
        )
  
    if not current_user.is_super_admin and current_user.role not in [UserRole.ORG_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organization administrators can resend invitations"
        )
  
    # Find the user/invitation (using user ID as invitation ID for now)
    user = db.query(User).filter(
        User.id == invitation_id,
        User.organization_id == organization_id,
        User.must_change_password == True # Still pending
    ).first()
  
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found or already accepted"
        )
  
    org = db.query(Organization).filter(Organization.id == organization_id).first()
  
    try:
        # Send invitation email (if email service is configured)
        if EMAIL_SERVICE_AVAILABLE and email_service:
            await email_service.send_email(
                to_email=user.email,
                subject=f"Invitation to join {org.name} (Resent)",
                body=f"You have been invited to join {org.name}. Please login with your credentials to complete your account setup."
            )
            logger.info(f"Invitation email resent to {user.email}")
      
        logger.info(f"Invitation resent for {user.email} in organization {org.name} by {current_user.email}")
        return {"message": f"Invitation resent to {user.email}"}
      
    except Exception as e:
        logger.error(f"Error resending invitation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to resend invitation"
        )


@invitation_router.delete("/{organization_id:int}/invitations/{invitation_id:int}")
async def cancel_organization_invitation(
    organization_id: int,
    invitation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cancel organization invitation (org admin or super admin only)"""
  
    # Check access permissions
    if not current_user.is_super_admin and current_user.organization_id != organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this organization"
        )
  
    if not current_user.is_super_admin and current_user.role not in [UserRole.ORG_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organization administrators can cancel invitations"
        )
  
    # Find the user/invitation (using user ID as invitation ID for now)
    user = db.query(User).filter(
        User.id == invitation_id,
        User.organization_id == organization_id,
        User.must_change_password == True # Still pending
    ).first()
  
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found or already accepted"
        )
  
    try:
        # For now, delete the user since they haven't activated yet
        # In a full implementation, you would mark invitation as cancelled
        db.delete(user)
        db.commit()
      
        logger.info(f"Invitation cancelled for {user.email} in organization {organization_id} by {current_user.email}")
        return {"message": f"Invitation cancelled for {user.email}"}
      
    except Exception as e:
        db.rollback()
        logger.error(f"Error cancelling invitation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel invitation"
        )

@invitation_router.post("/{organization_id:int}/invite")
async def invite_user_to_organization(
    organization_id: int,
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Invite user to organization (org admin only)"""
  
    # Check access permissions
    if not current_user.is_super_admin and current_user.organization_id != organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this organization"
        )
  
    if not current_user.is_super_admin and current_user.role not in [UserRole.ORG_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organization administrators can invite users"
        )
  
    # Check if organization exists
    org = db.query(Organization).filter(Organization.id == organization_id).first()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
  
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
  
    # Generate temporary password if not provided
    temp_password = user_data.password
    if not temp_password:
        temp_password = ''.join(secrets.choice(string.ascii_letters + string.digits + string.punctuation) for _ in range(12))
  
    # Create Supabase Auth user
    supabase_uuid = None
    try:
        supabase_user = supabase_auth_service.create_user(
            email=user_data.email,
            password=temp_password,
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
        # Create new user in organization with Supabase UUID
        hashed_password = get_password_hash(temp_password)
        new_user = User(
            organization_id=organization_id,
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            role=user_data.role or UserRole.STANDARD_USER.value,
            is_active=True,
            must_change_password=True,
            supabase_uuid=supabase_uuid  # Store Supabase UUID
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
      
        # Send invitation email (if email service is configured)
        try:
            if EMAIL_SERVICE_AVAILABLE and email_service:
                await email_service.send_email(
                    to_email=new_user.email,
                    subject=f"Invitation to join {org.name}",
                    body=f"You have been invited to join {org.name}. Please login with your temporary password: {temp_password} and change it upon first login."
                )
                logger.info(f"Invitation email sent to {new_user.email}")
            else:
                logger.info("Email service not available - skipping invitation email")
        except Exception as email_error:
            logger.error(f"Failed to send invitation email: {email_error}")
            # Don't fail the entire operation if email fails
            pass
      
        logger.info(f"User {new_user.email} invited to organization {org.name} by {current_user.email}")
        return {"message": f"User {new_user.email} successfully invited to {org.name}"}
      
    except Exception as e:
        # If DB creation fails, cleanup Supabase user
        try:
            supabase_auth_service.delete_user(supabase_uuid)
        except Exception as cleanup_e:
            logger.error(f"Failed to cleanup Supabase user {supabase_uuid}: {cleanup_e}")
        db.rollback()
        logger.error(f"Error inviting user to organization: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to invite user to organization"
        )