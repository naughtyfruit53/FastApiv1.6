# app/core/tenant.py

from typing import Optional, Any, Type, TypeVar, List
from contextvars import ContextVar
from fastapi import Request, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy import select
from app.core.database import get_db
from app.models import Organization, User, Company
from starlette.responses import Response
from app.core.config import settings as config_settings
from app.core.security import oauth2_scheme, verify_token
import logging

logger = logging.getLogger(__name__)

_current_organization_id: ContextVar[Optional[int]] = ContextVar("current_organization_id", default=None)
_current_user_id: ContextVar[Optional[int]] = ContextVar("current_user_id", default=None)

ModelType = TypeVar("ModelType")

class TenantContext:
    @staticmethod
    def get_organization_id() -> Optional[int]:
        return _current_organization_id.get()
    
    @staticmethod
    def set_organization_id(org_id: int) -> None:
        _current_organization_id.set(org_id)
        logger.debug(f"Set tenant context: organization_id={org_id}")
    
    @staticmethod
    def get_user_id() -> Optional[int]:
        return _current_user_id.get()
    
    @staticmethod
    def set_user_id(user_id: int) -> None:
        _current_user_id.set(user_id)
        logger.debug(f"Set tenant context: user_id={user_id}")
    
    @staticmethod
    def clear() -> None:
        _current_organization_id.set(None)
        _current_user_id.set(None)
        logger.debug("Cleared tenant context")
    
    @staticmethod
    def validate_organization_access(organization_id: int, user: User) -> bool:
        if user.is_super_admin or user.organization_id is None:
            return True
        return user.organization_id == organization_id

class TenantQueryFilter:
    @staticmethod
    def apply_organization_filter(
        stmt: select, 
        model: Type[ModelType], 
        organization_id: Optional[int] = None,
        user: Optional[User] = None
    ) -> select:
        org_id = organization_id or TenantContext.get_organization_id()
        
        if not hasattr(model, 'organization_id'):
            logger.warning(f"Model {model.__name__} does not have organization_id field")
            return stmt
        
        if user and user.is_super_admin and org_id is not None:
            return stmt.where(model.organization_id == org_id)
        
        if org_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization context is required"
            )
        
        if user and not TenantContext.validate_organization_access(org_id, user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied to organization {org_id}"
            )
        
        return stmt.where(model.organization_id == org_id)
    
    @staticmethod
    def validate_organization_data(data: dict, user: User) -> dict:
        current_org_id = TenantContext.get_organization_id()
        
        if user.is_super_admin:
            if 'organization_id' not in data or data['organization_id'] is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Super admins must specify organization_id"
                )
            return data
        
        if 'organization_id' in data and data['organization_id'] is not None and data['organization_id'] != user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Cannot create/update data for organization {data['organization_id']}"
            )
        
        data['organization_id'] = user.organization_id
        return data

class TenantQueryMixin:
    @staticmethod
    def filter_by_tenant(result, model_class, org_id: Optional[int] = None):
        if org_id is None:
            org_id = TenantContext.get_organization_id()
        
        if org_id is None:
            raise HTTPException(
                status_code=500,
                detail="No organization context available for query"
            )
        
        if hasattr(model_class, 'organization_id'):
            return result.filter(model_class.organization_id == org_id)
        
        return result
    
    @staticmethod
    def ensure_tenant_access(obj: Any, org_id: Optional[int] = None) -> None:
        if org_id is None:
            org_id = TenantContext.get_organization_id()
        
        if org_id is None:
            raise HTTPException(
                status_code=500,
                detail="No organization context available"
            )
        
        if hasattr(obj, 'organization_id') and obj.organization_id != org_id:
            raise HTTPException(
                status_code=404,
                detail="Resource not found"
            )

class TenantMiddleware:
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive)
            
            if request.method == "OPTIONS":
                await self.app(scope, receive, send)
                return
            
            if request.url.path.startswith("/api/v1/auth/"):
                logger.debug(f"Skipping tenant extraction for auth path: {request.url.path}")
                await self.app(scope, receive, send)
                return
            
            excluded_paths = [
                "/api/users/me",
                "/organizations/app-statistics",
                "/api/v1/organizations/app-statistics",
                "/organizations/org-statistics",
                "/api/v1/organizations/org-statistics",
                "/organizations/license/create",
                "/api/v1/organizations/license/create",
                "/organizations/factory-default",
                "/api/v1/organizations/factory-default",
                "/organizations/reset-data",
                "/api/v1/organizations/reset-data",
            ]
            if request.url.path in excluded_paths:
                logger.debug(f"Skipping tenant extraction for app-level path: {request.url.path}")
                await self.app(scope, receive, send)
                return
            
            org_id = self._extract_organization_id(request)
            
            if org_id:
                TenantContext.set_organization_id(org_id)
                logger.debug(f"Middleware set organization context: {org_id}")
                await self.app(scope, receive, send)
            else:
                origin = request.headers.get("origin")
                response = Response("Not Found", status_code=404)
                if origin and (origin in config_settings.BACKEND_CORS_ORIGINS or '*' in config_settings.BACKEND_CORS_ORIGINS):
                    response.headers["Access-Control-Allow-Origin"] = origin
                    response.headers["Access-Control-Allow-Credentials"] = "true"
                    response.headers["Access-Control-Allow-Methods"] = "*"
                    response.headers["Access-Control-Allow-Headers"] = "*"
                await response(scope, receive, send)
                return
        
        TenantContext.clear()
    
    def _extract_organization_id(self, request: Request) -> Optional[int]:
        try:
            org_header = request.headers.get("X-Organization-ID")
            if org_header and org_header.isdigit():
                return int(org_header)
            
            host = request.headers.get("host", "")
            if "." in host:
                subdomain = host.split(".")[0]
                if subdomain and subdomain not in ["www", "api", "admin"]:
                    pass
            
            path_parts = request.url.path.split("/")
            if len(path_parts) >= 5 and path_parts[3] == "org":
                if path_parts[4].isdigit():
                    return int(path_parts[4])
                    
        except Exception as e:
            logger.warning(f"Error extracting organization ID: {e}")
        
        return None

async def get_organization_from_request(request: Request, db: AsyncSession = Depends(get_db)) -> Optional[Organization]:
    try:
        host = request.headers.get("host", "")
        if "." in host:
            subdomain = host.split(".")[0]
            if subdomain and subdomain not in ["www", "api", "admin"]:
                result = await db.execute(select(Organization).filter_by(subdomain=subdomain, status="active"))
                org = result.scalars().first()
                if org:
                    TenantContext.set_organization_id(org.id)
                    return org
        
        org_id = request.headers.get("X-Organization-ID")
        if org_id and org_id.isdigit():
            result = await db.execute(select(Organization).filter_by(id=int(org_id), status="active"))
            org = result.scalars().first()
            if org:
                TenantContext.set_organization_id(org.id)
                return org
        
        path_parts = request.url.path.split("/")
        if len(path_parts) >= 5 and path_parts[3] == "org":
            if path_parts[4].isdigit():
                org_id = int(path_parts[4])
                result = await db.execute(select(Organization).filter_by(id=org_id, status="active"))
                org = result.scalars().first()
                if org:
                    TenantContext.set_organization_id(org.id)
                    return org
    
    except Exception as e:
        logger.error(f"Error getting organization from request: {e}")
    
    return None

async def require_organization(
    request: Request, 
    db: AsyncSession = Depends(get_db)
) -> Organization:
    org = await get_organization_from_request(request, db)
    if not org:
        raise HTTPException(
            status_code=400,
            detail="Invalid or missing organization context"
        )
    
    TenantContext.set_organization_id(org.id)
    return org

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        email, organization_id, user_role, user_type = verify_token(token)
        logger.debug(f"Token decoded: email={email}, org_id={organization_id}, role={user_role}, type={user_type}")
        if email is None:
            raise credentials_exception
        result = await db.execute(select(User).filter_by(email=email))
        user = result.scalars().first()
        if user is None:
            raise credentials_exception

        # Set organization context
        if not user.is_super_admin:
            if user.organization_id is None:
                raise credentials_exception
            TenantContext.set_organization_id(user.organization_id)
            logger.debug(f"Set organization context for user {email}: org_id={user.organization_id}")
        elif organization_id is not None:
            TenantContext.set_organization_id(organization_id)
            logger.debug(f"Set organization context for super admin {email}: org_id={organization_id}")
        
        TenantContext.set_user_id(user.id)
        return user
    except Exception as e:
        logger.error(f"Error validating user: {str(e)}")
        raise credentials_exception

def require_current_organization_id(current_user: User = Depends(get_current_user)) -> int:
    org_id = TenantContext.get_organization_id()
    if org_id is None:
        if current_user.organization_id is not None:
            TenantContext.set_organization_id(current_user.organization_id)
            org_id = current_user.organization_id
        else:
            raise HTTPException(
                status_code=400,
                detail="No current organization specified"
            )
    if not current_user.is_super_admin and current_user.organization_id != org_id:
        raise HTTPException(
            status_code=403,
            detail="User does not belong to the requested organization"
        )
    return org_id

async def get_current_org_user(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    org_id = TenantContext.get_organization_id()
    if org_id is None:
        if current_user.organization_id is not None:
            TenantContext.set_organization_id(current_user.organization_id)
            org_id = current_user.organization_id
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization context is required"
            )
    
    if current_user.organization_id is not None and current_user.organization_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not belong to the requested organization"
        )
    
    return current_user

async def validate_company_setup(db: AsyncSession = Depends(get_db), organization_id: int = Depends(require_current_organization_id)) -> None:
    result = await db.execute(select(Organization).filter_by(id=organization_id))
    org = result.scalars().first()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found. Please contact system administrator."
        )
    
    if not org.company_details_completed:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail="Company details must be completed before performing this operation."
        )
    
    result = await db.execute(select(Company).filter_by(organization_id=organization_id))
    company = result.scalars().first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail="Company record not found. Please complete company setup."
        )