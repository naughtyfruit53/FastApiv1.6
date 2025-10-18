# app/core/security.py

from datetime import datetime, timedelta, timezone
from typing import Any, Union, Optional
from jose import jwt, exceptions
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging

from app.core.config import settings
from app.core.database import get_db
from app.models.user_models import User, PlatformUser
from app.schemas.user import UserInDB, PlatformUserInDB

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(
    subject: Union[str, Any],
    organization_id: Optional[int] = None,
    user_role: Optional[str] = None,
    user_type: str = "organization",
    expires_delta: Optional[timedelta] = None
) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "organization_id": organization_id,
        "user_role": user_role,
        "user_type": user_type
    }

    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(
    subject: Union[str, Any],
    organization_id: Optional[int] = None,
    user_role: Optional[str] = None,
    user_type: str = "organization",
    expires_delta: Optional[timedelta] = None
) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "organization_id": organization_id,
        "user_role": user_role,
        "user_type": user_type,
        "token_type": "refresh"
    }

    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_token(token: str, expected_type: Optional[str] = None) -> tuple[Union[str, None], Union[int, None], Union[str, None], Union[str, None]]:
    """Verify token and return email, organization_id, user_role, and user_type"""
    try:
        logger.debug("Token to decode: %s...", token[:20])
        payload = jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.ALGORITHM]
        )
        logger.debug("Decoded payload: %s", payload)
        if expected_type and payload.get("token_type") != expected_type:
            raise exceptions.JWTError("Invalid token type")
        email = payload.get("sub")
        organization_id = payload.get("organization_id")
        user_role = payload.get("user_role")
        user_type = payload.get("user_type", "organization")
        return email, organization_id, user_role, user_type
    except exceptions.ExpiredSignatureError:
        logger.warning("Token expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except exceptions.JWTError as e:
        logger.error("JWT decode error: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

def is_super_admin_email(email: str) -> bool:
    """Check if email belongs to a super admin"""
    super_admin_emails = getattr(settings, 'SUPER_ADMIN_EMAILS', [])
    return email.lower() in [e.lower() for e in super_admin_emails]

async def get_current_user(db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)) -> Union[UserInDB, PlatformUserInDB]:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    logger.debug("get_current_user called")
    email, organization_id, user_role, user_type = verify_token(token)
    if not email:
        logger.debug("Invalid email in token, raising credentials_exception")
        raise credentials_exception

    if user_type == "platform":
        result = await db.execute(select(PlatformUser).filter_by(email=email))
        user = result.scalars().first()
        if not user:
            logger.debug("Platform user not found in DB, raising credentials_exception")
            raise credentials_exception
        
        logger.debug("Authenticated platform user: %s", user.email)
        return PlatformUserInDB.model_validate(user)
    else:
        result = await db.execute(select(User).filter_by(email=email))
        user = result.scalars().first()
        if not user:
            logger.debug("User not found in DB, raising credentials_exception")
            raise credentials_exception

        logger.debug("Authenticated user: %s", user.email)
        return UserInDB.model_validate(user)

async def get_current_active_user(current_user: Union[UserInDB, PlatformUserInDB] = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_active_admin(current_user: Union[UserInDB, PlatformUserInDB] = Depends(get_current_active_user)):
    if not (current_user.user_role == "admin" or current_user.is_super_admin):
        raise HTTPException(status_code=403, detail="Not authorized: Admin access required")
    return current_user