# app/api/v1/user.py

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.core.config import settings
from app.core.database import get_db
from app.core.permissions import PermissionChecker, Permission, require_super_admin, require_org_admin
from app.core.tenant import TenantQueryMixin
from app.models import User, Organization
from app.schemas.user import UserCreate, UserUpdate, UserInDB, UserRole
from app.schemas.user import TokenData  # Adjust if in schemas.base
from app.core.security import get_password_hash, get_current_user as core_get_current_user
from app.utils.supabase_auth import supabase_auth_service, SupabaseAuthError
import logging
from sqlalchemy import select

logger = logging.getLogger(__name__)

# OAuth2 setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")  # Adjust tokenUrl to match your auth endpoint

# Dependency functions
async def get_current_user(db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        print("DEBUG: Token to decode (user.py):", token)
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.ALGORITHM])
        print("DEBUG: Decoded payload (user.py):", payload)
        email: str = payload.get("sub")
        if email is None:
            print("DEBUG: No email in payload (user.py), raising credentials_exception")
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError as e:
        print("JWT decode error (user.py):", str(e))
        raise credentials_exception
    result = await db.execute(select(User).filter_by(email=token_data.email))
    user = result.scalars().first()
    if user is None:
        print("DEBUG: User not found in DB (user.py), raising credentials_exception")
        raise credentials_exception
    print("DEBUG: Authenticated user (user.py):", user.email)
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_admin_user(current_user: User = Depends(get_current_active_user)):
    if current_user.role != UserRole.ORG_ADMIN and not current_user.is_super_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user

async def get_current_super_admin(current_user: User = Depends(get_current_active_user)):
    if not current_user.is_super_admin:
        raise HTTPException(status_code=403, detail="Super admin access required")
    return current_user

async def get_current_platform_user(current_user: User = Depends(get_current_active_user)):
    if current_user.organization_id is not None:
        raise HTTPException(status_code=403, detail="Platform-level access required")
    return current_user

def get_current_organization_id(current_user: User = Depends(get_current_active_user)):
    if current_user.organization_id is None:
        raise HTTPException(status_code=400, detail="No organization context")
    return current_user.organization_id

def require_current_organization_id(current_user: User = Depends(get_current_active_user)):
    org_id = get_current_organization_id(current_user)
    return org_id

def validate_organization_access(current_user: User, org_id: int):
    if not current_user.is_super_admin and current_user.organization_id != org_id:
        raise HTTPException(status_code=403, detail="Access denied to different organization")
    return True

# Router and endpoints
router = APIRouter()

@router.get("/", response_model=List[UserInDB])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    organization_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    request: Request = None
):
    """Get users in current organization (admin only)"""
    
    # Check permissions
    PermissionChecker.require_permission(Permission.VIEW_USERS, current_user, db, request)
    
    stmt = select(User)
    
    # Super admins can see all users across organizations
    if PermissionChecker.has_permission(current_user, Permission.SUPER_ADMIN):
        # If organization_id specified, filter by it
        if organization_id is not None:
            stmt = stmt.filter_by(organization_id=organization_id)
        if active_only:
            stmt = stmt.filter_by(is_active=True)
    else:
        # Regular admins only see users in their organization
        org_id = get_current_organization_id(current_user)
        stmt = TenantQueryMixin.filter_by_tenant(stmt, User, org_id)
        if active_only:
            stmt = stmt.filter_by(is_active=True)
    
    result = await db.execute(stmt.offset(skip).limit(limit))
    users = result.scalars().all()
    return users

@router.get("/me", response_model=UserInDB)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user info"""
    return current_user

@router.get("/{user_id}", response_model=UserInDB)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    request: Request = None
):
    """Get user by ID"""
    # Users can view their own info, admins can view users in their org
    if current_user.id == user_id:
        return current_user
    
    # Check permissions for viewing other users
    PermissionChecker.require_permission(Permission.VIEW_USERS, current_user, db, request)
    
    result = await db.execute(select(User).filter_by(id=user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Ensure tenant access for non-super-admin users
    if not PermissionChecker.has_permission(current_user, Permission.SUPER_ADMIN):
        if user.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to user from different organization"
            )
    
    return user

@router.post("/", response_model=UserInDB)
async def create_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    request: Request = None
):
    """Create new user (admin only)"""
    
    # Check permissions
    PermissionChecker.require_permission(Permission.CREATE_USERS, current_user, db, request)
    
    # Determine organization for new user
    if PermissionChecker.has_permission(current_user, Permission.SUPER_ADMIN) and user.organization_id:
        org_id = user.organization_id
        # Verify organization exists
        result = await db.execute(select(Organization).filter_by(id=org_id))
        org = result.scalars().first()
        if not org:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization not found"
            )
    else:
        org_id = get_current_organization_id(current_user)
        if org_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No organization context available"
            )
    
    # Check if email already exists in the organization
    result = await db.execute(select(User).filter_by(email=user.email, organization_id=org_id))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered in this organization"
        )
    
    # Check if username already exists in the organization
    result = await db.execute(select(User).filter_by(username=user.username, organization_id=org_id))
    existing_username = result.scalars().first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken in this organization"
        )
    
    # Check user limits for the organization
    if not current_user.is_super_admin:
        result = await db.execute(select(Organization).filter_by(id=org_id))
        org = result.scalars().first()
        result = await db.execute(select(User).filter_by(organization_id=org_id, is_active=True))
        user_count = len(result.scalars().all())
        
        if user_count >= org.max_users:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Maximum user limit ({org.max_users}) reached for this organization"
            )
    
    # Validate role permissions
    if user.role == UserRole.ORG_ADMIN and not current_user.is_super_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super administrators can create organization administrators"
        )
    
    # Create user in Supabase Auth first
    try:
        supabase_user = supabase_auth_service.create_user(
            email=user.email,
            password=user.password,
            user_metadata={
                "full_name": user.full_name,
                "role": user.role,
                "organization_id": org_id,
                "department": user.department,
                "designation": user.designation
            }
        )
        supabase_uuid = supabase_user["supabase_uuid"]
        logger.info(f"Created user {user.email} in Supabase Auth with UUID {supabase_uuid}")
        
    except SupabaseAuthError as e:
        logger.error(f"Failed to create user {user.email} in Supabase Auth: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create user in authentication system: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error creating user {user.email} in Supabase Auth: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user in authentication system"
        )
    
    # Create new user in local database
    try:
        hashed_password = get_password_hash(user.password)
        db_user = User(
            organization_id=org_id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            hashed_password=hashed_password,
            role=user.role,
            department=user.department,
            designation=user.designation,
            employee_id=user.employee_id,
            phone=user.phone,
            is_active=user.is_active,
            supabase_uuid=supabase_uuid  # Store Supabase UUID
        )
        
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        
        logger.info(f"User {user.email} created in org {org_id} by {current_user.email}")
        return db_user
        
    except Exception as e:
        # If local database creation fails, cleanup Supabase user
        try:
            supabase_auth_service.delete_user(supabase_uuid)
            logger.info(f"Cleaned up Supabase user {supabase_uuid} after local DB failure")
        except Exception as cleanup_error:
            logger.error(f"Failed to cleanup Supabase user {supabase_uuid}: {cleanup_error}")
        
        await db.rollback()
        logger.error(f"Failed to create user {user.email} in local database: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user in local database"
        )

@router.put("/{user_id}", response_model=UserInDB)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update user"""
    # Users can update their own info, admins can update users in their org
    result = await db.execute(select(User).filter_by(id=user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check permissions
    is_self_update = current_user.id == user_id
    is_admin = current_user.role == UserRole.ORG_ADMIN or current_user.is_super_admin
    
    if not is_self_update and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Ensure tenant access for non-super-admin users
    if not current_user.is_super_admin:
        TenantQueryMixin.ensure_tenant_access(user, current_user.organization_id)
    
    # Restrict self-update fields for non-admin users
    if is_self_update and not is_admin:
        # Allow only basic updates for self
        allowed_fields = {"email", "username", "full_name", "phone", "department", "designation"}
        update_data = user_update.dict(exclude_unset=True)
        if not all(field in allowed_fields for field in update_data.keys()):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot update administrative fields"
            )
    
    # Check role update permissions
    if user_update.role:
        if user_update.role == UserRole.ORG_ADMIN and not current_user.is_super_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only super administrators can assign organization administrator role"
            )
    
    # Check email uniqueness if being updated
    if user_update.email and user_update.email != user.email:
        result = await db.execute(select(User).filter_by(email=user_update.email, organization_id=user.organization_id))
        existing_email = result.scalars().first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered in this organization"
            )
    
    # Check username uniqueness if being updated
    if user_update.username and user_update.username != user.username:
        result = await db.execute(select(User).filter_by(username=user_update.username, organization_id=user.organization_id))
        existing_username = result.scalars().first()
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken in this organization"
            )
    
    # Update user
    for field, value in user_update.dict(exclude_unset=True).items():
        setattr(user, field, value)
    
    await db.commit()
    await db.refresh(user)
    
    logger.info(f"User {user.email} updated by {current_user.email}")
    return user

@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Delete user (admin only)"""
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    result = await db.execute(select(User).filter_by(id=user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Ensure tenant access for non-super-admin users
    if not current_user.is_super_admin:
        TenantQueryMixin.ensure_tenant_access(user, current_user.organization_id)
    
    # Prevent deleting the last admin in an organization
    if user.role == UserRole.ORG_ADMIN and not current_user.is_super_admin:
        result = await db.execute(select(User).filter_by(organization_id=user.organization_id, role=UserRole.ORG_ADMIN, is_active=True))
        admin_count = len(result.scalars().all())
        
        if admin_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete the last organization administrator"
            )
    
    await db.delete(user)
    await db.commit()
    
    logger.info(f"User {user.email} deleted by {current_user.email}")
    return {"message": "User deleted successfully"}

@router.get("/organization/{organization_id}", response_model=List[UserInDB])
async def get_organization_users(
    organization_id: int,
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_super_admin)
):
    """Get users in specific organization (super admin only)"""
    
    stmt = select(User).filter_by(organization_id=organization_id)
    
    if active_only:
        stmt = stmt.filter_by(is_active=True)
    
    result = await db.execute(stmt.offset(skip).limit(limit))
    users = result.scalars().all()
    return users