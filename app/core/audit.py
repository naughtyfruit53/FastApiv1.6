# app/core/audit.py

"""
Audit logging system for security-sensitive operations
"""
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
import json
import logging

from app.models import AuditLog

logger = logging.getLogger(__name__)


async def create_audit_log(
    db: AsyncSession,
    entity_type: str,
    entity_id: Any,
    action: str,
    user_id: Optional[int] = None,
    changes: Optional[Dict] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    organization_id: Optional[int] = None
) -> Optional[AuditLog]:
    try:
        audit_log = AuditLog(
            organization_id=organization_id,
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            user_id=user_id,
            changes=changes,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.add(audit_log)
        await db.commit()
        await db.refresh(audit_log)
        logger.info(f"Audit log created for {entity_type}:{action}")
        return audit_log
    except Exception as e:
        logger.error(f"Failed to create audit log: {e}")
        await db.rollback()
        return None


class AuditLogger:
    """Service for logging audit events"""
    
    @staticmethod
    async def log_login_attempt(
        db: AsyncSession,
        email: str,
        success: bool,
        organization_id: Optional[int] = None,
        user_id: Optional[int] = None,
        user_role: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        error_message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> Optional[object]:
        """Log login attempt"""
        return await AuditLogger._create_security_audit_log(
            db=db,
            event_type="LOGIN",
            action="LOGIN_ATTEMPT",
            user_email=email,
            user_id=user_id,
            user_role=user_role,
            organization_id=organization_id,
            ip_address=ip_address,
            user_agent=user_agent,
            success="SUCCESS" if success else "FAILED",
            error_message=error_message,
            details=details
        )
    
    @staticmethod
    async def log_master_password_usage(
        db: AsyncSession,
        email: str,
        organization_id: Optional[int] = None,
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> Optional[object]:
        """Log temporary master password usage"""
        return await AuditLogger._create_security_audit_log(
            db=db,
            event_type="SECURITY",
            action="MASTER_PASSWORD_USED",
            user_email=email,
            user_id=user_id,
            user_role="super_admin",
            organization_id=organization_id,
            ip_address=ip_address,
            user_agent=user_agent,
            success="SUCCESS",
            details=details
        )
    
    @staticmethod
    async def log_password_reset(
        db: AsyncSession,
        admin_email: str,
        target_email: str,
        admin_user_id: Optional[int] = None,
        target_user_id: Optional[int] = None,
        organization_id: Optional[int] = None,
        success: bool = True,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        error_message: Optional[str] = None,
        reset_type: str = "SINGLE_USER"
    ) -> Optional[object]:
        """Log password reset operation"""
        details = {
            "target_email": target_email,
            "target_user_id": target_user_id,
            "reset_type": reset_type
        }
        
        return await AuditLogger._create_security_audit_log(
            db=db,
            event_type="PASSWORD_RESET",
            action="ADMIN_PASSWORD_RESET",
            user_email=admin_email,
            user_id=admin_user_id,
            organization_id=organization_id,
            ip_address=ip_address,
            user_agent=user_agent,
            success="SUCCESS" if success else "FAILED",
            error_message=error_message,
            details=details
        )
    
    @staticmethod
    async def log_data_reset(
        db: AsyncSession,
        admin_email: str,
        admin_user_id: Optional[int] = None,
        organization_id: Optional[int] = None,
        success: bool = True,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        error_message: Optional[str] = None,
        reset_scope: str = "ORGANIZATION",
        affected_organizations: Optional[list] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> Optional[object]:
        """Log data reset operation"""
        log_details = {
            "reset_scope": reset_scope,
            "affected_organizations": affected_organizations or [],
            **(details or {})
        }
        
        return await AuditLogger._create_security_audit_log(
            db=db,
            event_type="DATA_RESET",
            action="ADMIN_DATA_RESET",
            user_email=admin_email,
            user_id=admin_user_id,
            organization_id=organization_id,
            ip_address=ip_address,
            user_agent=user_agent,
            success="SUCCESS" if success else "FAILED",
            error_message=error_message,
            details=log_details
        )
    
    @staticmethod
    async def log_permission_denied(
        db: AsyncSession,
        user_email: str,
        attempted_action: str,
        user_id: Optional[int] = None,
        user_role: Optional[str] = None,
        organization_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> Optional[object]:
        """Log permission denied events"""
        log_details = {
            "attempted_action": attempted_action,
            **(details or {})
        }
        
        return await AuditLogger._create_security_audit_log(
            db=db,
            event_type="SECURITY",
            action="PERMISSION_DENIED",
            user_email=user_email,
            user_id=user_id,
            user_role=user_role,
            organization_id=organization_id,
            ip_address=ip_address,
            user_agent=user_agent,
            success="FAILED",
            error_message="Insufficient permissions",
            details=log_details
        )
    
    @staticmethod
    async def _create_security_audit_log(
        db: AsyncSession,
        event_type: str,
        action: str,
        user_email: str,
        success: str,
        user_id: Optional[int] = None,
        user_role: Optional[str] = None,
        organization_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        error_message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> Optional[object]:
        """Create and save security audit log entry using the existing AuditLog model"""
        changes = {
            "event_type": event_type,
            "action": action,
            "user_email": user_email,
            "user_role": user_role,
            "success": success,
            "error_message": error_message,
            "details": details,
            "ip_address": ip_address,
            "user_agent": user_agent
        }
        return await create_audit_log(
            db=db,
            entity_type="security_events",
            entity_id=user_id or 0,
            action=f"{event_type}:{action}",
            user_id=user_id,
            changes=changes,
            ip_address=ip_address,
            user_agent=user_agent,
            organization_id=organization_id
        )
    
def get_client_ip(request) -> Optional[str]:
    """Extract client IP address from request"""
    try:
        # Check for forwarded headers first (for reverse proxy scenarios)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to client host
        if hasattr(request, 'client') and request.client:
            return request.client.host
        
        return None
    except Exception:
        return None


def get_user_agent(request) -> Optional[str]:
    """Extract user agent from request"""
    try:
        return request.headers.get("User-Agent")
    except Exception:
        return None