"""
Enhanced admin endpoints (API v1) with comprehensive permission checking and audit logging
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from sqlalchemy.orm import Session
from typing import Optional, List
import secrets
import string
from datetime import datetime

from app.core.database import get_db
from app.api.v1.auth import get_current_active_user, get_current_super_admin, get_current_admin_user
from app.core.permissions import (
    PermissionChecker, Permission, require_super_admin, require_org_admin, 
    require_password_reset_permission
)
from app.core.audit import AuditLogger, get_client_ip, get_user_agent
from app.models import User, Organization, PlatformUser
from app.schemas.user import (
    UserCreate, UserUpdate, UserInDB, AdminPasswordResetRequest, 
    AdminPasswordResetResponse, BulkPasswordResetRequest, BulkPasswordResetResponse,
    TemporaryPasswordRequest, TemporaryPasswordResponse, PlatformUserCreate, PlatformUserInDB
)
from app.schemas.reset import ResetScope
from app.schemas.organization import OrganizationCreate, OrganizationInDB  # Assume this exists or add if needed
from app.services.user_service import UserService
from app.services.organization_service import OrganizationService  # Assume service for org creation
from app.services.email_service import email_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/users", response_model=UserInDB)
async def create_user(
    user_create: UserCreate,
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Create a new user with permission checking"""
    try:
        # Check permissions
        PermissionChecker.require_permission(
            Permission.CREATE_USERS, 
            current_user, 
            db, 
            request
        )
        
        # Validate organization access
        target_org_id = user_create.organization_id or current_user.organization_id
        if target_org_id and not PermissionChecker.can_access_organization(current_user, target_org_id):
            PermissionChecker.require_organization_access(current_user, target_org_id, db, request)
        
        # Create user
        new_user = UserService.create_user(db, user_create)
        
        # Log user creation
        AuditLogger.log_login_attempt(
            db=db,
            email=current_user.email,
            success=True,
            organization_id=current_user.organization_id,
            user_id=current_user.id,
            user_role=current_user.role,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            details={
                "action": "create_user",
                "created_user_email": new_user.email,
                "created_user_id": new_user.id,
                "target_organization_id": target_org_id
            }
        )
        
        logger.info(f"User {new_user.email} created by {current_user.email}")
        return new_user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"User creation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )


@router.put("/users/{user_id}", response_model=UserInDB)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Update user with permission checking"""
    try:
        # Get target user
        target_user = db.query(User).filter(User.id == user_id).first()
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check permissions
        PermissionChecker.require_permission(
            Permission.MANAGE_USERS, 
            current_user, 
            db, 
            request
        )
        
        # Check organization access
        if target_user.organization_id and not PermissionChecker.can_access_organization(current_user, target_user.organization_id):
            PermissionChecker.require_organization_access(current_user, target_user.organization_id, db, request)
        
        # Update user
        updated_user = UserService.update_user(db, user_id, user_update)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Log user update
        AuditLogger.log_login_attempt(
            db=db,
            email=current_user.email,
            success=True,
            organization_id=current_user.organization_id,
            user_id=current_user.id,
            user_role=current_user.role,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            details={
                "action": "update_user",
                "updated_user_email": updated_user.email,
                "updated_user_id": updated_user.id,
                "update_fields": list(user_update.dict(exclude_unset=True).keys())
            }
        )
        
        logger.info(f"User {updated_user.email} updated by {current_user.email}")
        return updated_user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"User update error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user"
        )


@router.post("/password/reset", response_model=AdminPasswordResetResponse)
async def admin_reset_user_password(
    reset_request: AdminPasswordResetRequest,
    background_tasks: BackgroundTasks,
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_password_reset_permission)
):
    """Reset password for a specific user (admin operation)"""
    try:
        # Find target user
        target_user = UserService.get_user_by_email(db, reset_request.target_email)
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with email {reset_request.target_email} not found"
            )
        
        # Check if current user can reset this user's password
        if not PermissionChecker.can_reset_user_password(current_user, target_user):
            PermissionChecker.require_permission(
                Permission.RESET_ANY_PASSWORD,
                current_user,
                db,
                request,
                target_user.organization_id
            )
        
        # Reset password using UserService
        reset_response = UserService.reset_user_password(
            db=db,
            admin_user=current_user,
            target_email=reset_request.target_email,
            request=request
        )
        
        # Send password reset email
        email_service.send_password_reset_email(
            user_email=reset_request.target_email,
            user_name=target_user.full_name,
            new_password=reset_response.new_password,
            reset_by=current_user.full_name
        )
        
        logger.info(f"Password reset by {current_user.email} for user {reset_request.target_email}")
        return reset_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Admin password reset error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset user password"
        )


@router.post("/password/reset/bulk", response_model=BulkPasswordResetResponse)
async def admin_bulk_password_reset(
    reset_request: BulkPasswordResetRequest,
    background_tasks: BackgroundTasks,
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_password_reset_permission)
):
    """Bulk password reset for organization or all organizations"""
    try:
        if reset_request.scope == ResetScope.ORGANIZATION:
            if not reset_request.organization_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="organization_id is required for organization scope"
                )
            
            # Check if user can reset passwords for this organization
            if not PermissionChecker.can_reset_organization_data(current_user, reset_request.organization_id):
                PermissionChecker.require_permission(
                    Permission.RESET_ANY_PASSWORD,
                    current_user,
                    db,
                    request,
                    reset_request.organization_id
                )
            
            # Reset passwords for organization
            reset_response = UserService.reset_organization_passwords(
                db=db,
                admin_user=current_user,
                organization_id=reset_request.organization_id,
                request=request
            )
            
            return BulkPasswordResetResponse(
                message=reset_response.message,
                scope=reset_request.scope,
                total_users_affected=reset_response.total_users_reset,
                organizations_affected=reset_response.organizations_affected,
                successful_resets=reset_response.total_users_reset - len(reset_response.failed_resets),
                failed_resets=reset_response.failed_resets
            )
            
        elif reset_request.scope == ResetScope.ALL_ORGANIZATIONS:
            # Only super admin can reset all passwords
            PermissionChecker.require_permission(
                Permission.RESET_ANY_PASSWORD,
                current_user,
                db,
                request
            )
            
            # Reset passwords for all organizations
            reset_response = UserService.reset_all_passwords(
                db=db,
                admin_user=current_user,
                request=request
            )
            
            return BulkPasswordResetResponse(
                message=reset_response.message,
                scope=reset_request.scope,
                total_users_affected=reset_response.total_users_reset,
                organizations_affected=reset_response.organizations_affected,
                successful_resets=reset_response.total_users_reset - len(reset_response.failed_resets),
                failed_resets=reset_response.failed_resets
            )
            
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid reset scope"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Bulk password reset error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to perform bulk password reset"
        )


@router.post("/password/temporary", response_model=TemporaryPasswordResponse)
async def set_temporary_password(
    temp_request: TemporaryPasswordRequest,
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_password_reset_permission)
):
    """Set temporary password for a user"""
    try:
        # Find target user
        target_user = UserService.get_user_by_email(db, temp_request.target_email)
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with email {temp_request.target_email} not found"
            )
        
        # Check if current user can reset this user's password
        if not PermissionChecker.can_reset_user_password(current_user, target_user):
            PermissionChecker.require_permission(
                Permission.RESET_ANY_PASSWORD,
                current_user,
                db,
                request,
                target_user.organization_id
            )
        
        # Generate temporary password
        temp_password = UserService.generate_secure_password()
        
        # Set temporary password
        UserService.set_temporary_password(
            db=db,
            user=target_user,
            temp_password=temp_password,
            expires_hours=temp_request.expires_hours
        )
        
        # Calculate expiry time
        from datetime import datetime, timedelta
        expires_at = datetime.utcnow() + timedelta(hours=temp_request.expires_hours)
        
        # Log temporary password creation
        AuditLogger.log_password_reset(
            db=db,
            admin_email=current_user.email,
            target_email=temp_request.target_email,
            admin_user_id=current_user.id,
            target_user_id=target_user.id,
            organization_id=target_user.organization_id,
            success=True,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            reset_type="TEMPORARY_PASSWORD"
        )
        
        # Try to send email notification
        try:
            if email_service.send_temporary_password_notification(
                temp_request.target_email,
                temp_password,
                expires_at,
                current_user.full_name or current_user.email
            ):
                logger.info(f"Temporary password email sent to {temp_request.target_email}")
        except Exception as e:
            logger.warning(f"Failed to send temporary password email: {e}")
        
        logger.info(f"Temporary password set by {current_user.email} for user {temp_request.target_email}")
        return TemporaryPasswordResponse(
            message="Temporary password set successfully",
            target_email=temp_request.target_email,
            temporary_password=temp_password,
            expires_at=expires_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Temporary password error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to set temporary password"
        )


@router.get("/users", response_model=List[UserInDB])
async def list_users(
    organization_id: Optional[int] = None,
    limit: int = 100,
    offset: int = 0,
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """List users with organization filtering"""
    try:
        # Check permissions
        PermissionChecker.require_permission(
            Permission.VIEW_USERS, 
            current_user, 
            db, 
            request
        )
        
        # Determine which organizations the user can access
        accessible_orgs = PermissionChecker.get_accessible_organizations(current_user, db)
        
        # Build query
        query = db.query(User)
        
        if organization_id:
            # Check if user can access the specified organization
            if organization_id not in accessible_orgs:
                PermissionChecker.require_organization_access(current_user, organization_id, db, request)
            query = query.filter(User.organization_id == organization_id)
        else:
            # Filter to accessible organizations
            if accessible_orgs:
                query = query.filter(User.organization_id.in_(accessible_orgs))
            else:
                # No accessible organizations
                return []
        
        # Apply pagination
        users = query.offset(offset).limit(limit).all()
        
        # Log user list access
        AuditLogger.log_login_attempt(
            db=db,
            email=current_user.email,
            success=True,
            organization_id=current_user.organization_id,
            user_id=current_user.id,
            user_role=current_user.role,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            details={
                "action": "list_users",
                "organization_filter": organization_id,
                "accessible_organizations": accessible_orgs,
                "result_count": len(users)
            }
        )
        
        return users
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"List users error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list users"
        )


@router.get("/users/{user_id}", response_model=UserInDB)
async def get_user(
    user_id: int,
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get specific user details with permission checking"""
    try:
        # Find user
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check permissions
        PermissionChecker.require_permission(
            Permission.VIEW_USERS, 
            current_user, 
            db, 
            request
        )
        
        # Check organization access
        if user.organization_id and not PermissionChecker.can_access_organization(current_user, user.organization_id):
            PermissionChecker.require_organization_access(current_user, user.organization_id, db, request)
        
        # Log user access
        AuditLogger.log_login_attempt(
            db=db,
            email=current_user.email,
            success=True,
            organization_id=current_user.organization_id,
            user_id=current_user.id,
            user_role=current_user.role,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            details={
                "action": "get_user",
                "target_user_id": user_id,
                "target_user_email": user.email
            }
        )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user"
        )


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Delete user with permission checking"""
    try:
        # Find user
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check permissions
        PermissionChecker.require_permission(
            Permission.DELETE_USERS, 
            current_user, 
            db, 
            request
        )
        
        # Check organization access
        if user.organization_id and not PermissionChecker.can_access_organization(current_user, user.organization_id):
            PermissionChecker.require_organization_access(current_user, user.organization_id, db, request)
        
        # Prevent deletion of super admin users
        if user.is_super_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot delete super admin users"
            )
        
        # Prevent self-deletion
        if user.id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot delete your own account"
            )
        
        # Store user details for logging
        deleted_email = user.email
        deleted_org_id = user.organization_id
        
        # Delete user
        db.delete(user)
        db.commit()
        
        # Log user deletion
        AuditLogger.log_login_attempt(
            db=db,
            email=current_user.email,
            success=True,
            organization_id=current_user.organization_id,
            user_id=current_user.id,
            user_role=current_user.role,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            details={
                "action": "delete_user",
                "deleted_user_id": user_id,
                "deleted_user_email": deleted_email,
                "deleted_user_organization_id": deleted_org_id
            }
        )
        
        logger.info(f"User {deleted_email} deleted by {current_user.email}")
        return {"message": f"User {deleted_email} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete user error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )


@router.post("/organizations/{organization_id}/setup-admin")
async def setup_organization_admin(
    organization_id: int,
    admin_data: UserCreate,
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_super_admin)
):
    """Setup initial admin account for an organization (super admin only)"""
    try:
        # Verify organization exists
        organization = db.query(Organization).filter(Organization.id == organization_id).first()
        if not organization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Organization {organization_id} not found"
            )
        
        # Set organization ID and role
        admin_data.organization_id = organization_id
        admin_data.role = "org_admin"
        
        # Create admin user
        admin_user = UserService.create_user(db, admin_data)
        
        # Log admin creation
        AuditLogger.log_login_attempt(
            db=db,
            email=current_user.email,
            success=True,
            organization_id=current_user.organization_id,
            user_id=current_user.id,
            user_role=current_user.role,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            details={
                "action": "setup_organization_admin",
                "target_organization_id": organization_id,
                "admin_user_email": admin_user.email,
                "admin_user_id": admin_user.id
            }
        )
        
        logger.info(f"Organization admin {admin_user.email} created for organization {organization_id} by {current_user.email}")
        return {
            "message": "Organization admin created successfully",
            "admin_user": admin_user,
            "organization": organization.name
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Setup organization admin error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to setup organization admin"
        )


@router.post("/platform-users", response_model=PlatformUserInDB)
async def create_platform_user(
    user_data: PlatformUserCreate,
    db: Session = Depends(get_db),
    current_user: PlatformUser = Depends(require_super_admin)
):
    """Create a new platform user (app admin) - only by app super admin"""
    if current_user.role != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only app super admin can create app admins"
        )
    
    if user_data.role == "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create another super admin"
        )
    
    return UserService.create_platform_user(db, user_data, current_user.email)


@router.post("/licenses", response_model=OrganizationInDB)
async def activate_license(
    org_data: OrganizationCreate,
    admin_data: UserCreate,  # Data for org_super_admin
    db: Session = Depends(get_db),
    current_user: PlatformUser = Depends(get_current_active_user)  # Both super_admin and platform_admin
):
    """Activate license: create organization and org_super_admin"""
    if current_user.role not in ["super_admin", "platform_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only app super admin or app admin can activate licenses"
        )
    
    # Create organization
    new_org = OrganizationService.create_organization(db, org_data)  # Assume service method
    
    # Create org_super_admin
    admin_data.organization_id = new_org.id
    admin_data.role = "org_admin"
    org_admin = UserService.create_user(db, admin_data)
    
    logger.info(f"License activated for org {new_org.name} with admin {org_admin.email} by {current_user.email}")
    return new_org


@router.get("/email-logs")
async def get_email_logs(
    organization_id: Optional[int] = None,
    email_type: Optional[str] = None,
    status: Optional[str] = None,
    provider: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get email send audit logs (RBAC-protected)
    Requires admin permissions to view email logs
    """
    try:
        from app.models import EmailSend, EmailStatus, EmailProvider, EmailType
        
        # Check permissions - only admins can view email logs
        if organization_id:
            # Check if user can access specific organization
            if not PermissionChecker.can_access_organization(current_user, organization_id):
                PermissionChecker.require_organization_access(current_user, organization_id, db, request)
        else:
            # Viewing all email logs requires super admin
            PermissionChecker.require_permission(
                Permission.VIEW_ALL_AUDIT_LOGS,
                current_user,
                db,
                request
            )
        
        # Build query
        query = db.query(EmailSend)
        
        # Apply filters
        if organization_id:
            query = query.filter(EmailSend.organization_id == organization_id)
        
        if email_type:
            try:
                email_type_enum = EmailType(email_type)
                query = query.filter(EmailSend.email_type == email_type_enum)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid email_type: {email_type}"
                )
        
        if status:
            try:
                status_enum = EmailStatus(status)
                query = query.filter(EmailSend.status == status_enum)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid status: {status}"
                )
        
        if provider:
            try:
                provider_enum = EmailProvider(provider)
                query = query.filter(EmailSend.provider_used == provider_enum)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid provider: {provider}"
                )
        
        # Order by created_at descending (most recent first)
        query = query.order_by(EmailSend.created_at.desc())
        
        # Get total count for pagination
        total_count = query.count()
        
        # Apply pagination
        email_logs = query.offset(offset).limit(limit).all()
        
        # Convert to response format
        logs_response = []
        for log in email_logs:
            logs_response.append({
                "id": log.id,
                "to_email": log.to_email,
                "from_email": log.from_email,
                "subject": log.subject,
                "email_type": log.email_type.value,
                "provider_used": log.provider_used.value,
                "status": log.status.value,
                "organization_id": log.organization_id,
                "user_id": log.user_id,
                "provider_message_id": log.provider_message_id,
                "error_message": log.error_message,
                "retry_count": log.retry_count,
                "max_retries": log.max_retries,
                "created_at": log.created_at.isoformat(),
                "sent_at": log.sent_at.isoformat() if log.sent_at else None,
                "delivered_at": log.delivered_at.isoformat() if log.delivered_at else None,
                "failed_at": log.failed_at.isoformat() if log.failed_at else None,
                "updated_at": log.updated_at.isoformat() if log.updated_at else None,
                "is_brevo_enabled": log.is_brevo_enabled
            })
        
        # Log access to email logs
        AuditLogger.log_data_reset(
            db=db,
            admin_email=current_user.email,
            admin_user_id=current_user.id,
            organization_id=organization_id,
            success=True,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            reset_scope="EMAIL_LOG_ACCESS",
            details={
                "action": "view_email_logs",
                "filters": {
                    "organization_id": organization_id,
                    "email_type": email_type,
                    "status": status,
                    "provider": provider
                },
                "result_count": len(logs_response),
                "total_count": total_count
            }
        )
        
        logger.info(f"Email logs accessed by {current_user.email}: {len(logs_response)} records returned")
        
        return {
            "email_logs": logs_response,
            "total_count": total_count,
            "returned_count": len(logs_response),
            "offset": offset,
            "limit": limit,
            "filters": {
                "organization_id": organization_id,
                "email_type": email_type,
                "status": status,
                "provider": provider
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Email logs access error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve email logs"
        )