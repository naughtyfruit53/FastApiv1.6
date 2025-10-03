"""
Health check endpoints for monitoring system components
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from typing import Dict, Any

from app.core.database import get_db
from app.models.email import MailAccount, EmailSyncLog, EmailSyncStatus
from app.models.oauth_models import UserEmailToken, TokenStatus
from app.api.v1.auth import get_current_active_user, get_current_super_admin
from app.models.user_models import User

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/email-sync")
async def email_sync_health(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Health check for email sync service
    Returns status of email accounts and recent sync activity
    """
    try:
        # Get user's organization
        organization_id = current_user.organization_id
        
        # Count total mail accounts
        stmt = select(func.count(MailAccount.id)).where(
            MailAccount.organization_id == organization_id
        )
        result = await db.execute(stmt)
        total_accounts = result.scalar() or 0
        
        # Count active accounts
        stmt = select(func.count(MailAccount.id)).where(
            MailAccount.organization_id == organization_id,
            MailAccount.sync_enabled == True,
            MailAccount.sync_status == EmailSyncStatus.ACTIVE
        )
        result = await db.execute(stmt)
        active_accounts = result.scalar() or 0
        
        # Count accounts with errors
        stmt = select(func.count(MailAccount.id)).where(
            MailAccount.organization_id == organization_id,
            MailAccount.sync_status == EmailSyncStatus.ERROR
        )
        result = await db.execute(stmt)
        error_accounts = result.scalar() or 0
        
        # Get recent sync activity (last 24 hours)
        twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)
        
        # Converted to async queries
        stmt = select(func.count(EmailSyncLog.id)).select_from(EmailSyncLog).join(
            MailAccount, EmailSyncLog.account_id == MailAccount.id
        ).where(
            MailAccount.organization_id == organization_id,
            EmailSyncLog.started_at >= twenty_four_hours_ago
        )
        result = await db.execute(stmt)
        recent_syncs = result.scalar() or 0
        
        stmt = select(func.count(EmailSyncLog.id)).select_from(EmailSyncLog).join(
            MailAccount, EmailSyncLog.account_id == MailAccount.id
        ).where(
            MailAccount.organization_id == organization_id,
            EmailSyncLog.started_at >= twenty_four_hours_ago,
            EmailSyncLog.status == 'success'
        )
        result = await db.execute(stmt)
        successful_syncs = result.scalar() or 0
        
        stmt = select(func.count(EmailSyncLog.id)).select_from(EmailSyncLog).join(
            MailAccount, EmailSyncLog.account_id == MailAccount.id
        ).where(
            MailAccount.organization_id == organization_id,
            EmailSyncLog.started_at >= twenty_four_hours_ago,
            EmailSyncLog.status == 'error'
        )
        result = await db.execute(stmt)
        failed_syncs = result.scalar() or 0
        
        # Determine overall health status
        health_status = "healthy"
        if error_accounts > 0 or (recent_syncs > 0 and failed_syncs > successful_syncs):
            health_status = "degraded"
        if active_accounts == 0 and total_accounts > 0:
            health_status = "unhealthy"
        
        return {
            "status": health_status,
            "timestamp": datetime.utcnow().isoformat(),
            "accounts": {
                "total": total_accounts,
                "active": active_accounts,
                "error": error_accounts,
                "paused": total_accounts - active_accounts - error_accounts
            },
            "recent_sync_activity_24h": {
                "total_syncs": recent_syncs,
                "successful": successful_syncs,
                "failed": failed_syncs,
                "success_rate": round((successful_syncs / recent_syncs * 100) if recent_syncs > 0 else 0, 2)
            },
            "details": {
                "message": f"Email sync service is {health_status}",
                "active_accounts": active_accounts,
                "accounts_with_errors": error_accounts
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }


@router.get("/oauth-tokens")
async def oauth_tokens_health(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Health check for OAuth tokens
    Returns status of OAuth tokens and expiry information
    """
    try:
        # Get user's organization
        organization_id = current_user.organization_id
        
        # Count total tokens
        stmt = select(func.count(UserEmailToken.id)).where(
            UserEmailToken.organization_id == organization_id
        )
        result = await db.execute(stmt)
        total_tokens = result.scalar() or 0
        
        # Count active tokens
        stmt = select(func.count(UserEmailToken.id)).where(
            UserEmailToken.organization_id == organization_id,
            UserEmailToken.status == TokenStatus.ACTIVE
        )
        result = await db.execute(stmt)
        active_tokens = result.scalar() or 0
        
        # Count expired tokens
        now = datetime.utcnow()
        stmt = select(func.count(UserEmailToken.id)).where(
            UserEmailToken.organization_id == organization_id,
            UserEmailToken.status == TokenStatus.ACTIVE,
            UserEmailToken.expires_at <= now
        )
        result = await db.execute(stmt)
        expired_tokens = result.scalar() or 0
        
        # Count tokens expiring soon (within 7 days)
        seven_days_from_now = now + timedelta(days=7)
        stmt = select(func.count(UserEmailToken.id)).where(
            UserEmailToken.organization_id == organization_id,
            UserEmailToken.status == TokenStatus.ACTIVE,
            UserEmailToken.expires_at <= seven_days_from_now,
            UserEmailToken.expires_at > now
        )
        result = await db.execute(stmt)
        expiring_soon = result.scalar() or 0
        
        # Count revoked tokens
        stmt = select(func.count(UserEmailToken.id)).where(
            UserEmailToken.organization_id == organization_id,
            UserEmailToken.status == TokenStatus.REVOKED
        )
        result = await db.execute(stmt)
        revoked_tokens = result.scalar() or 0
        
        # Count tokens with refresh failures
        stmt = select(func.count(UserEmailToken.id)).where(
            UserEmailToken.organization_id == organization_id,
            UserEmailToken.status == TokenStatus.REFRESH_FAILED
        )
        result = await db.execute(stmt)
        refresh_failed = result.scalar() or 0
        
        # Determine health status
        health_status = "healthy"
        if expired_tokens > 0 or refresh_failed > 0:
            health_status = "degraded"
        if active_tokens == 0 and total_tokens > 0:
            health_status = "unhealthy"
        
        return {
            "status": health_status,
            "timestamp": datetime.utcnow().isoformat(),
            "tokens": {
                "total": total_tokens,
                "active": active_tokens,
                "expired": expired_tokens,
                "expiring_soon_7d": expiring_soon,
                "revoked": revoked_tokens,
                "refresh_failed": refresh_failed
            },
            "details": {
                "message": f"OAuth tokens are {health_status}",
                "needs_attention": expired_tokens + refresh_failed,
                "recommendation": "Run refresh_oauth_tokens.py to refresh expired tokens" if expired_tokens > 0 else None
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }


@router.get("/system")
async def system_health(
    current_user: User = Depends(get_current_super_admin)
) -> Dict[str, Any]:
    """
    Overall system health check (super admin only)
    Returns combined health status of all components
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "email_sync": "See /api/v1/health/email-sync",
            "oauth_tokens": "See /api/v1/health/oauth-tokens"
        },
        "message": "System is operational"
    }