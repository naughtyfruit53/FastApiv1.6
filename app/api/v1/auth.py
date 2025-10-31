# app/api/v1/auth.py

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, Body, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.core.database import get_db, execute_with_retry
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
    get_password_hash,
    oauth2_scheme,
    verify_token,
    get_current_user as core_get_current_user
)
from app.core.audit import create_audit_log
from app.models.user_models import User, PlatformUser
from app.schemas.user import UserResponse, Token, EmailLogin, LoginResponse, PlatformUserInDB, UserInDB
from app.core.config import settings
from app.services.otp_service import OTPService
from pydantic import BaseModel, EmailStr

logger = logging.getLogger(__name__)
router = APIRouter()

async def fetch_user(db: AsyncSession, email: str):
    result = await db.execute(select(User).options(joinedload(User.organization)).filter_by(email=email))
    return result.scalars().first()

async def fetch_platform_user(db: AsyncSession, email: str):
    result = await db.execute(select(PlatformUser).filter_by(email=email))
    return result.scalars().first()

@router.post("/login", response_model=LoginResponse)
async def login(
    response: Response,
    email_login: Optional[EmailLogin] = Body(None),
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
    request: Request = None
):
    # Handle JSON payload (EmailLogin) or FormData (OAuth2PasswordRequestForm)
    if email_login:
        email = email_login.email
        password = email_login.password
    else:
        email = form_data.username  # OAuth2 uses 'username', but treat as email
        password = form_data.password

    # Use retry for database queries to handle transient failures
    user: Union[User, PlatformUser, None] = await execute_with_retry(fetch_user, email=email)
    if not user:
        user = await execute_with_retry(fetch_platform_user, email=email)

    # Merge the user into the current session to attach it properly
    if user:
        user = await db.merge(user)

    # Check if password is 6-digit OTP (for admin reset flow)
    if len(password) == 6 and password.isdigit():
        otp_service = OTPService(db)
        otp_valid, _ = await otp_service.verify_otp(email, password, "admin_password_reset")
        if otp_valid:
            # OTP valid - force password change on success
            user.force_password_reset = True
            user.must_change_password = True
            await db.commit()
            # Proceed to login with OTP as temp auth
        else:
            logger.info(f"[LOGIN:FAILED] Invalid OTP for {email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid OTP",
                headers={"WWW-Authenticate": "Bearer"},
            )

    if not user or not verify_password(password, user.hashed_password):
        logger.info(f"[LOGIN:FAILED] Email: {email}")
        await create_audit_log(
            db=db,
            table_name="security_events",
            record_id=user.id if user else None,
            action="LOGIN:FAILED",
            user_id=user.id if user else None,
            changes={
                "event_type": "LOGIN",
                "action": "FAILED",
                "user_email": email,
                "success": "FAILURE",
                "error_message": "Invalid credentials",
                "ip_address": request.client.host if request else "unknown",
                "user_agent": request.headers.get("user-agent", "unknown") if request else "unknown"
            },
            ip_address=request.client.host if request else "unknown",
            user_agent=request.headers.get("user-agent", "unknown") if request else "unknown"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if isinstance(user, PlatformUser):
        user_type = "platform"
        organization_id = None
        user_role = user.role
        company_completed = True
        organization_name = None
    else:
        user_type = "organization"
        organization_id = user.organization_id
        user_role = user.role
        company_completed = user.organization.company_details_completed if user.organization else True
        organization_name = user.organization.name if user.organization else None

    user.last_login = datetime.utcnow()
    await db.commit()
    await db.refresh(user)

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.email,
        organization_id=organization_id,
        user_role=user_role,
        user_type=user_type,
        expires_delta=access_token_expires
    )

    refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    refresh_token = create_refresh_token(
        subject=user.email,
        organization_id=organization_id,
        user_role=user_role,
        user_type=user_type,
        expires_delta=refresh_token_expires
    )

    await create_audit_log(
        db=db,
        table_name="security_events",
        record_id=user.id,
        action="LOGIN:SUCCESS",
        user_id=user.id,
        changes={
            "event_type": "LOGIN",
            "action": "SUCCESS",
            "user_email": user.email,
            "user_role": user_role,
            "organization_id": organization_id,
            "ip_address": request.client.host if request else "unknown",
            "user_agent": request.headers.get("user-agent", "unknown") if request else "unknown"
        },
        ip_address=request.client.host if request else "unknown",
        user_agent=request.headers.get("user-agent", "unknown") if request else "unknown"
    )

    if isinstance(user, PlatformUser):
        user_out = PlatformUserInDB.model_validate(user)
    else:
        user_out = UserResponse.model_validate(user)

    # Optional: Set cookies in development mode if AUTH_COOKIE_DEV is enabled
    # Production always prefers JSON response with Authorization: Bearer
    if settings.AUTH_COOKIE_DEV and settings.ENVIRONMENT == "development":
        # Development cookie settings: Secure=False, SameSite=Lax
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=False,  # Allow HTTP in development
            samesite="lax",  # Lax for development
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60
        )
        logger.info(f"[AUTH] Cookies set for development (user: {user.email})")
    elif settings.ENVIRONMENT == "production":
        # Production cookie settings: Secure=True, SameSite=Lax
        # Note: SameSite=Lax provides better CSRF protection than 'none'
        # Use 'none' only if cross-site requests are explicitly required
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,  # Require HTTPS in production
            samesite="lax",  # Better CSRF protection, allows same-site requests
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60
        )
        logger.info(f"[AUTH] Production cookies set (user: {user.email})")

    # Always return tokens in JSON (preferred for Authorization: Bearer in headers)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "organization_id": organization_id,
        "organization_name": organization_name,
        "user_role": user_role,
        "must_change_password": user.must_change_password,
        "force_password_reset": user.force_password_reset,
        "is_first_login": user.last_login is None,
        "company_details_completed": company_completed,
        "user": user_out
    }

@router.post("/refresh-token", response_model=Token)
async def refresh_token(
    refresh_token: str = Body(...),
    db: AsyncSession = Depends(get_db)
):
    email, organization_id, user_role, user_type = verify_token(refresh_token, expected_type="refresh")
    if not email:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    if user_type == "platform":
        user = await execute_with_retry(fetch_platform_user, email=email)
    else:
        user = await execute_with_retry(fetch_user, email=email)

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.email,
        organization_id=organization_id,
        user_role=user_role,
        user_type=user_type,
        expires_delta=access_token_expires
    )

    refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    new_refresh_token = create_refresh_token(
        subject=user.email,
        organization_id=organization_id,
        user_role=user_role,
        user_type=user_type,
        expires_delta=refresh_token_expires
    )

    return {"access_token": access_token, "refresh_token": new_refresh_token, "token_type": "bearer"}

@router.get("/logout")
async def logout(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
    request: Request = None
):
    email, organization_id, user_role, user_type = verify_token(token)
    user = await execute_with_retry(fetch_user, email=email)
    if user:
        await create_audit_log(
            db=db,
            table_name="security_events",
            record_id=user.id,
            action="LOGOUT",
            user_id=user.id,
            changes={
                "event_type": "LOGOUT",
                "user_email": user.email,
                "user_role": user_role,
                "organization_id": organization_id,
                "ip_address": request.client.host if request else "unknown",
                "user_agent": request.headers.get("user-agent", "unknown") if request else "unknown"
            },
            ip_address=request.client.host if request else "unknown",
            user_agent=request.headers.get("user-agent", "unknown") if request else "unknown"
        )
    return {"message": "Successfully logged out"}

@router.get("/test-token", tags=["debug"], response_model=dict)
async def test_token(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    """Debug endpoint to verify JWT token"""
    email, organization_id, user_role, user_type = verify_token(token)
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = await execute_with_retry(fetch_user, email=email)
    if not user:
        user = await execute_with_retry(fetch_platform_user, email=email)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return {
        "user": {
            "email": user.email,
            "organization_id": user.organization_id if hasattr(user, "organization_id") else None,
            "role": user.role,
            "type": user_type
        },
        "message": "Token is valid"
    }

async def get_current_active_user(current_user: UserInDB = Depends(core_get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_admin_user(current_user: UserInDB = Depends(get_current_active_user)):
    if current_user.role not in ["admin", "org_admin", "company_admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user

async def get_current_org_admin_user(current_user: UserInDB = Depends(get_current_active_user)):
    """Check if user is organization admin (excludes company admins)"""
    if current_user.role not in ["org_admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Organization admin access required")
    return current_user

async def get_current_company_admin_user(current_user: UserInDB = Depends(get_current_active_user)):
    """Check if user is company admin or higher"""
    if current_user.role not in ["company_admin", "org_admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Company admin access required")
    return current_user

async def get_current_super_admin(current_user: UserInDB = Depends(get_current_active_user)):
    if not current_user.is_super_admin:
        raise HTTPException(status_code=403, detail="Not super admin")
    return current_user

async def get_current_user_optional(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> Optional[User]:
    if not token:
        return None
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    email, organization_id, user_role, user_type = verify_token(token)
    if not email:
        raise credentials_exception
    user = await execute_with_retry(fetch_user, email=email)
    if user is None:
        raise credentials_exception
    return user