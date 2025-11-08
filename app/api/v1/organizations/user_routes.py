# app/api/v1/organizations/user_routes.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func as sql_func
from typing import List, Dict
import logging
import secrets
import string

from app.core.database import get_db
from app.core.security import get_password_hash
from app.core.permissions import PermissionChecker, Permission
from app.core.enforcement import require_access
from app.models import User, Organization, OrganizationRole, UserOrganizationRole
from app.schemas.user import UserRole
from app.schemas import UserCreate, UserInDB
from app.core.security import get_current_user
from app.api.v1.auth import get_current_active_user
from app.utils.supabase_auth import supabase_auth_service, SupabaseAuthError
from app.services.system_email_service import system_email_service  # Use system_email_service for sending emails
from app.services.otp_service import OTPService  # Import OTP service class

logger = logging.getLogger(__name__)

router = APIRouter()
user_router = router  # Alias for backward compatibility

@router.get("/{organization_id:int}/users", response_model=List[UserInDB])
async def list_organization_users(
    organization_id: int,
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    auth: tuple = Depends(require_access("user", "read")),
    db: AsyncSession = Depends(get_db)
):
    """List users in organization"""
    current_user, org_id = auth
    try:
        # Enforce tenant isolation - can only list users in own organization
        if organization_id != org_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )
      
        stmt = select(User).filter(User.organization_id == organization_id)
      
        if active_only:
            stmt = stmt.filter(User.is_active == True)
      
        stmt = stmt.offset(skip).limit(limit)
        result = await db.execute(stmt)
        users = result.scalars().all()
        return users
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing organization users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list users"
        )

@router.post("/{organization_id:int}/users", response_model=UserInDB)
async def create_user_in_organization(
    organization_id: int,
    user_data: UserCreate,
    auth: tuple = Depends(require_access("user", "create")),
    db: AsyncSession = Depends(get_db)
):
    """Create user in organization (requires user create permission)"""
    current_user, org_id = auth
    try:
        # Enforce tenant isolation - can only create users in own organization
        if organization_id != org_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )
      
        result = await db.execute(select(Organization).filter(Organization.id == organization_id))
        org = result.scalars().first()
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )
      
        result = await db.execute(select(User).filter(
            User.email == user_data.email,
            User.organization_id == organization_id
        ))
        existing_user = result.scalars().first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered in this organization"
            )
  
        # Check user limit (skip for super admins)
        if not getattr(current_user, 'is_super_admin', False):
            result = await db.execute(select(sql_func.count()).select_from(User).filter(
                User.organization_id == organization_id,
                User.is_active == True
            ))
            user_count = result.scalar()
          
            if user_count >= org.max_users:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Maximum user limit ({org.max_users}) reached for this organization"
                )
      
        # Management role requires special permission
        if user_data.role == "management" and current_user.role not in ["org_admin", "management"]:
            if not getattr(current_user, 'is_super_admin', False):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only super administrators or organization administrators can assign management role"
                )
      
        if user_data.role in ["super_admin", "app_admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot create app-level users in organization"
            )
      
        # Additional check for managers creating users
        if current_user.role == "manager":
            if user_data.role != "executive":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Managers can only create executives"
                )
            user_data.reporting_manager_id = current_user.id
      
        # Role-specific validation
        if user_data.role == "manager":
            if not user_data.assigned_modules or not any(user_data.assigned_modules.values()):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Managers must have at least one module assigned"
                )
        elif user_data.role == "executive":
            if not user_data.reporting_manager_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Executives must have a reporting manager"
                )
            result = await db.execute(select(User).filter(
                User.id == user_data.reporting_manager_id,
                User.role == "manager",
                User.organization_id == organization_id,
                User.is_active == True
            ))
            manager = result.scalars().first()
            if not manager:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid reporting manager - must be an active manager in the same organization"
                )
            if not user_data.sub_module_permissions:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Executives must have sub-module permissions defined"
                )
            # Validate sub_modules against manager's assigned modules
            for module in user_data.sub_module_permissions.keys():
                if not manager.assigned_modules.get(module, False):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Cannot assign sub-modules for {module} - reporting manager does not have access to this module"
                    )
  
        supabase_uuid = None
        try:
            # If no password provided, generate and send OTP
            if user_data.password is None:
                otp_service_instance = OTPService(db)
                success, otp = await otp_service_instance.generate_and_send_otp(
                    email=user_data.email,
                    purpose="registration",
                    organization_id=organization_id,
                    phone_number=user_data.phone
                )
                if not success:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Failed to generate and send OTP"
                    )
                user_data.password = otp  # Set OTP as initial password
            
            supabase_user = supabase_auth_service.create_user(
                email=user_data.email,
                password=user_data.password,
                user_metadata={
                    "full_name": user_data.full_name,
                    "role": user_data.role if user_data.role else "executive",
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
                hashed_password=hashed_password,
                full_name=user_data.full_name,
                role=user_data.role or "executive",
                department=user_data.department,
                designation=user_data.designation,
                employee_id=user_data.employee_id,
                phone=user_data.phone,
                is_active=True,
                is_super_admin=False,
                must_change_password=True,  # Force change on first login
                supabase_uuid=supabase_uuid,
                assigned_modules=user_data.assigned_modules,
                reporting_manager_id=user_data.reporting_manager_id,
                sub_module_permissions=user_data.sub_module_permissions
            )
            
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)
            
            # Assign OrganizationRole
            stmt = select(OrganizationRole).filter(
                OrganizationRole.organization_id == organization_id,
                OrganizationRole.name == new_user.role
            )
            result = await db.execute(stmt)
            org_role = result.scalars().first()
            
            if org_role:
                assignment = UserOrganizationRole(
                    organization_id=organization_id,
                    user_id=new_user.id,
                    role_id=org_role.id,
                    assigned_by_id=current_user.id,
                    is_active=True
                )
                db.add(assignment)
                await db.commit()
                logger.info(f"Assigned role '{new_user.role}' to user {new_user.email}")
            else:
                logger.warning(f"Role '{new_user.role}' not found - skipping assignment")
            
            logger.info(f"User {new_user.email} created in org {org.name} by {current_user.email}")
            
            # Setup comprehensive RBAC for the user based on their role
            try:
                from app.services.user_rbac_service import UserRBACService
                user_rbac_service = UserRBACService(db)
                
                # Auto-assign modules based on role
                if new_user.role in ["org_admin", "management"]:
                    # Grant full access to all organization modules
                    await user_rbac_service.setup_user_rbac_by_role(
                        user_id=new_user.id,
                        role=new_user.role
                    )
                    logger.info(f"Granted full module access to {new_user.role} user {new_user.id}")
                elif new_user.role == "manager":
                    # Manager should already have assigned_modules from user_data
                    if new_user.assigned_modules:
                        logger.info(f"Manager {new_user.id} has assigned modules: {list(new_user.assigned_modules.keys())}")
                elif new_user.role == "executive":
                    # Executive should already have inherited from manager
                    if new_user.reporting_manager_id:
                        # Refresh to get the latest data
                        await db.refresh(new_user)
                        logger.info(f"Executive {new_user.id} reports to manager {new_user.reporting_manager_id}")
            except Exception as rbac_error:
                logger.warning(f"RBAC setup warning for user {new_user.id}: {rbac_error}")
                # Don't fail user creation if RBAC setup has issues

            # Send welcome email with login link (OTP already sent if password was None)
            success, error = await system_email_service.send_user_creation_email(
                user_email=new_user.email,
                user_name=new_user.full_name,
                temp_password=user_data.password,
                organization_name=org.name,
                login_url="https://fast-apiv1-6.vercel.app/",
                organization_id=new_user.organization_id,
                user_id=new_user.id,
                db=db
            )
            
            if not success:
                logger.warning(f"User created but welcome email failed for {new_user.email}: {error}")

            return new_user
      
        except Exception as e:
            try:
                supabase_auth_service.delete_user(supabase_uuid)
            except Exception as cleanup_e:
                logger.error(f"Failed to cleanup Supabase user {supabase_uuid}: {cleanup_e}")
            await db.rollback()
            logger.error(f"Error creating user in organization: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user in organization"
            )

    except Exception as e:
        await db.rollback()
        logger.error(f"Error in create_user_in_organization: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )

@router.put("/{organization_id:int}/users/{user_id:int}", response_model=UserInDB)
async def update_user_in_organization(
    organization_id: int,
    user_id: int,
    user_update: Dict,
    auth: tuple = Depends(require_access("user", "update")),
    db: AsyncSession = Depends(get_db)
):
    """Update user in organization (requires user update permission)"""
    current_user, org_id = auth
    
    # Enforce tenant isolation - can only update users in own organization
    if organization_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
  
    stmt = select(User).filter(
        User.id == user_id,
        User.organization_id == organization_id
    )
    result = await db.execute(stmt)
    user = result.scalars().first()
  
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in this organization"
        )
  
    is_self_update = current_user.id == user_id
    if not is_self_update and not current_user.is_super_admin and current_user.role != "management":
        # Allow managers to update their executives
        if current_user.role == "manager" and user.reporting_manager_id == current_user.id:
            # Managers can update limited fields for executives
            allowed_fields = {"full_name", "phone", "department", "designation", "sub_module_permissions"}
            if not all(field in allowed_fields for field in user_update.keys()):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Managers can only update limited fields for their executives"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only management can update other users"
            )
  
    if is_self_update and not current_user.is_super_admin and current_user.role != "management":
        allowed_fields = {"email", "full_name", "phone", "department", "designation"}
        if not all(field in allowed_fields for field in user_update.keys()):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot update administrative fields"
            )
  
    if "role" in user_update:
        if user_update["role"] == "management" and not current_user.is_super_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only super administrators can assign management role"
            )
  
    # Role-specific validation if updating fields
    if "assigned_modules" in user_update and user.role == "manager":
        if not user_update["assigned_modules"] or not any(user_update["assigned_modules"].values()):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Managers must have at least one module assigned"
            )
    if "reporting_manager_id" in user_update and user.role == "executive":
        stmt = select(User).filter(
            User.id == user_update["reporting_manager_id"],
            User.role == "manager",
            User.organization_id == organization_id,
            User.is_active == True
        )
        result = await db.execute(stmt)
        manager = result.scalars().first()
        if not manager:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid reporting manager"
            )
    if "sub_module_permissions" in user_update and user.role == "executive":
        reporting_manager_id = user_update.get("reporting_manager_id", user.reporting_manager_id)
        stmt = select(User).filter(User.id == reporting_manager_id)
        result = await db.execute(stmt)
        manager = result.scalars().first()
        if manager:
            for module in user_update["sub_module_permissions"].keys():
                if not manager.assigned_modules.get(module, False):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Cannot assign sub-modules for {module} - reporting manager does not have access"
                    )
  
    try:
        for field, value in user_update.items():
            if field == "password" and value:
                setattr(user, "hashed_password", get_password_hash(value))
            elif hasattr(user, field):
                setattr(user, field, value)
      
        await db.commit()
        await db.refresh(user)
        
        # Update OrganizationRole assignment if role changed
        if "role" in user_update:
            # Remove old assignment
            stmt = select(UserOrganizationRole).filter(
                UserOrganizationRole.user_id == user.id
            )
            result = await db.execute(stmt)
            old_assignment = result.scalars().first()
            if old_assignment:
                db.delete(old_assignment)
                await db.commit()
            
            # Add new
            stmt = select(OrganizationRole).filter(
                OrganizationRole.organization_id == organization_id,
                OrganizationRole.name == user_update["role"]
            )
            result = await db.execute(stmt)
            new_role = result.scalars().first()
            if new_role:
                new_assignment = UserOrganizationRole(
                    organization_id=organization_id,
                    user_id=user.id,
                    role_id=new_role.id,
                    assigned_by_id=current_user.id,
                    is_active=True
                )
                db.add(new_assignment)
                await db.commit()
                logger.info(f"Updated role to '{user_update['role']}' for user {user.email}")
      
        logger.info(f"User {user.email} updated in organization {organization_id} by {current_user.email}")
        return user
      
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating user in organization: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user in organization"
        )

@router.delete("/{organization_id:int}/users/{user_id:int}")
async def delete_user_from_organization(
    organization_id: int,
    user_id: int,
    auth: tuple = Depends(require_access("user", "delete")),
    db: AsyncSession = Depends(get_db)
):
    """Delete user from organization (requires user delete permission)"""
    current_user, org_id = auth
    
    # Enforce tenant isolation - can only delete users in own organization
    if organization_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
  
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
  
    stmt = select(User).filter(
        User.id == user_id,
        User.organization_id == organization_id
    )
    result = await db.execute(stmt)
    user = result.scalars().first()
  
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in this organization"
        )
  
    if user.role == "management" and not current_user.is_super_admin:
        stmt = select(sql_func.count()).select_from(User).filter(
            User.organization_id == organization_id,
            User.role == "management",
            User.is_active == True
        )
        result = await db.execute(stmt)
        admin_count = result.scalar()
      
        if admin_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete the last management user"
            )
  
    try:
        # Remove role assignment
        stmt = select(UserOrganizationRole).filter(
            UserOrganizationRole.user_id == user_id
        )
        result = await db.execute(stmt)
        assignment = result.scalars().first()
        if assignment:
            db.delete(assignment)
        
        db.delete(user)
        await db.commit()
        
        logger.info(f"User {user.email} deleted from organization {organization_id} by {current_user.email}")
        return {"message": f"User {user.email} deleted successfully"}
      
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting user from organization: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user from organization"
        )

@router.post("/{organization_id:int}/users/{user_id:int}/reset-password")
async def reset_user_password(
    organization_id: int,
    user_id: int,
    auth: tuple = Depends(require_access("user", "update")),
    db: AsyncSession = Depends(get_db)
):
    """Reset user password (requires user update permission)"""
    current_user, org_id = auth
    
    # Enforce tenant isolation - can only reset passwords in own organization
    if organization_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
  
    stmt = select(User).filter(
        User.id == user_id,
        User.organization_id == organization_id
    )
    result = await db.execute(stmt)
    user = result.scalars().first()
  
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
        await db.commit()
        
        # Send email with new password
        success, error = await system_email_service.send_password_reset_email(
            user_email=user.email,
            user_name=user.full_name,
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
        await db.rollback()
        logger.error(f"Error resetting user password: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset user password"
        )