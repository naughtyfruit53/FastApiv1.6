# app/api/v1/user.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.core.database import get_db
from app.core.enforcement import require_access
from app.api.v1.auth import get_current_active_user
from app.models import User, Organization
from app.schemas.user import UserCreate, UserUpdate, UserInDB, UserRole
from app.core.security import get_password_hash
from app.utils.supabase_auth import supabase_auth_service, SupabaseAuthError
import logging
from sqlalchemy import select

logger = logging.getLogger(__name__)

# Router and endpoints
router = APIRouter()

@router.get("/", response_model=List[UserInDB])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    auth: tuple = Depends(require_access("user", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get users in current organization"""
    current_user, org_id = auth
    
    stmt = select(User).where(User.organization_id == org_id)
    
    if active_only:
        stmt = stmt.where(User.is_active == True)
    
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
    auth: tuple = Depends(require_access("user", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get user by ID"""
    current_user, org_id = auth
    
    # Users can view their own info
    if current_user.id == user_id:
        return current_user
    
    result = await db.execute(
        select(User).where(User.id == user_id, User.organization_id == org_id)
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user

@router.post("/", response_model=UserInDB)
async def create_user(
    user: UserCreate,
    auth: tuple = Depends(require_access("user", "create")),
    db: AsyncSession = Depends(get_db)
):
    """Create new user"""
    current_user, org_id = auth
    
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
    result = await db.execute(select(Organization).filter_by(id=org_id))
    org = result.scalars().first()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    result = await db.execute(select(User).filter_by(organization_id=org_id, is_active=True))
    user_count = len(result.scalars().all())
    
    if user_count >= org.max_users:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum user limit ({org.max_users}) reached for this organization"
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
    auth: tuple = Depends(require_access("user", "update")),
    db: AsyncSession = Depends(get_db)
):
    """Update user"""
    current_user, org_id = auth
    
    # Find user with tenant isolation
    result = await db.execute(
        select(User).where(User.id == user_id, User.organization_id == org_id)
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if user is updating themselves
    is_self_update = current_user.id == user_id
    
    # Restrict self-update fields for non-admin users
    if is_self_update:
        # Allow only basic updates for self
        allowed_fields = {"email", "username", "full_name", "phone", "department", "designation"}
        update_data = user_update.dict(exclude_unset=True)
        if not all(field in allowed_fields for field in update_data.keys()):
            # Users need admin permission to update administrative fields
            pass  # Will be caught by permission check above
    
    # Check email uniqueness if being updated
    if user_update.email and user_update.email != user.email:
        result = await db.execute(select(User).filter_by(email=user_update.email, organization_id=org_id))
        existing_email = result.scalars().first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered in this organization"
            )
    
    # Check username uniqueness if being updated
    if user_update.username and user_update.username != user.username:
        result = await db.execute(select(User).filter_by(username=user_update.username, organization_id=org_id))
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
    auth: tuple = Depends(require_access("user", "delete")),
    db: AsyncSession = Depends(get_db)
):
    """Delete user"""
    current_user, org_id = auth
    
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    # Find user with tenant isolation
    result = await db.execute(
        select(User).where(User.id == user_id, User.organization_id == org_id)
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent deleting the last admin in an organization
    if user.role == UserRole.ORG_ADMIN:
        result = await db.execute(
            select(User).where(
                User.organization_id == org_id,
                User.role == UserRole.ORG_ADMIN,
                User.is_active == True
            )
        )
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
    auth: tuple = Depends(require_access("user", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get users in specific organization"""
    current_user, org_id = auth
    
    # Enforce tenant isolation - return 404 for cross-org access
    if organization_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    stmt = select(User).where(User.organization_id == organization_id)
    
    if active_only:
        stmt = stmt.where(User.is_active == True)
    
    result = await db.execute(stmt.offset(skip).limit(limit))
    users = result.scalars().all()
    return users