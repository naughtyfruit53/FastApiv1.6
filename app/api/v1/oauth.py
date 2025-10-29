# app/api/v1/oauth.py

"""
OAuth2 Authentication API endpoints for Google and Microsoft
"""

import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
import traceback

from app.core.database import get_db
from app.core.enforcement import require_access
from app.models.user_models import User
from app.models.oauth_models import UserEmailToken, OAuthProvider, TokenStatus
from app.models.email import MailAccount, EmailAccountType, EmailSyncStatus
from app.schemas.oauth_schemas import (
    OAuthLoginRequest, OAuthLoginResponse, OAuthCallbackRequest,
    UserEmailTokenResponse, UserEmailTokenWithDetails, UserEmailTokenUpdate,
    EmailSyncRequest, EmailSyncResponse
)
from app.services.oauth_service import OAuth2Service
from app.services.email_sync_worker import email_sync_worker
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/providers")
async def get_oauth_providers():
    """Get list of configured OAuth2 providers"""
    providers = []
    
    if settings.GOOGLE_CLIENT_ID:
        providers.append({
            "name": "google",
            "display_name": "Google",
            "icon": "google",
            "scopes": ["gmail.readonly", "gmail.send", "gmail.modify"]
        })
    
    if settings.MICROSOFT_CLIENT_ID:
        providers.append({
            "name": "microsoft", 
            "display_name": "Microsoft",
            "icon": "microsoft",
            "scopes": ["Mail.Read", "Mail.Send", "Mail.ReadWrite"]
        })
    
    return {"providers": providers}


@router.post("/login/{provider}", response_model=OAuthLoginResponse)
async def oauth_login(
    provider: str,
    request: Request,
    auth: tuple = Depends(require_access("oauth", "create")),
    db: AsyncSession = Depends(get_db)
):
    """
    Initiate OAuth2 login flow for specified provider
    """
    current_user, org_id = auth
    
    # Validate provider
    try:
        oauth_provider = OAuthProvider(provider.upper())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported OAuth provider: {provider}"
        )
    
    # Get redirect URI from request or use default, now with provider in path
    redirect_uri = f"{settings.OAUTH_REDIRECT_URI}/{provider}"
    
    # Create OAuth service and generate authorization URL
    oauth_service = OAuth2Service(db)
    try:
        auth_url, state = await oauth_service.create_authorization_url(
            provider=oauth_provider,
            user_id=current_user.id,
            organization_id=current_user.organization_id,
            redirect_uri=redirect_uri
        )
        
        return OAuthLoginResponse(
            authorization_url=auth_url,
            state=state,
            provider=oauth_provider
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"OAuth login error: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create authorization URL"
        )


@router.get("/callback/{provider}")
async def oauth_callback(
    provider: str,
    code: str = Query(..., description="Authorization code from OAuth provider"),
    state: str = Query(..., description="State parameter for security"),
    error: Optional[str] = Query(None, description="Error from OAuth provider"),
    error_description: Optional[str] = Query(None, description="Error description"),
    db: AsyncSession = Depends(get_db)
):
    """
    Handle OAuth2 callback from provider
    """
    if error:
        logger.error(f"OAuth callback error: {error} - {error_description}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth error: {error_description or error}"
        )
    
    # Validate provider
    try:
        oauth_provider = OAuthProvider(provider.upper())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported OAuth provider: {provider}"
        )
    
    # Exchange code for tokens
    oauth_service = OAuth2Service(db)
    try:
        redirect_uri = f"{settings.OAUTH_REDIRECT_URI}/{provider}"
        token_response, user_info, user_id, organization_id = await oauth_service.exchange_code_for_tokens(
            provider=oauth_provider,
            code=code,
            state=state,
            redirect_uri=redirect_uri
        )
        
        # Check if refresh_token was received (critical for offline access)
        if 'refresh_token' not in token_response or not token_response['refresh_token']:
            logger.warning(f"No refresh token received for provider {provider}. User may need to revoke app access and re-authorize.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No refresh token received. Please revoke app access in your Google account settings and try authorizing again to grant offline access."
            )
        
        # Store tokens
        try:
            user_token = await oauth_service.store_user_tokens(
                user_id=user_id,
                organization_id=organization_id,
                provider=oauth_provider,
                token_response=token_response,
                user_info=user_info
            )
            # Check if MailAccount already exists
            stmt = select(MailAccount).where(
                MailAccount.email_address == user_token.email_address,
                MailAccount.user_id == user_id,
                MailAccount.organization_id == organization_id
            )
            result = await db.execute(stmt)
            existing_account = result.scalar_one_or_none()

            mail_account_type = EmailAccountType.GMAIL_API if oauth_provider == OAuthProvider.GOOGLE else EmailAccountType.OUTLOOK_API

            if existing_account:
                # Update existing account
                existing_account.name = user_token.display_name or "Default Mail Account"
                existing_account.account_type = mail_account_type
                existing_account.provider = oauth_provider.name
                existing_account.oauth_token_id = user_token.id
                existing_account.sync_enabled = True
                existing_account.sync_frequency_minutes = 15
                existing_account.is_active = True
                existing_account.sync_status = EmailSyncStatus.ACTIVE
                existing_account.updated_at = datetime.utcnow()
                existing_account.incoming_server = 'imap.gmail.com' if oauth_provider == OAuthProvider.GOOGLE else 'outlook.office365.com'
                existing_account.incoming_port = 993
                existing_account.incoming_ssl = True
                existing_account.incoming_auth_method = 'oauth2'
                existing_account.outgoing_server = 'smtp.gmail.com' if oauth_provider == OAuthProvider.GOOGLE else 'smtp.office365.com'
                existing_account.outgoing_port = 587
                existing_account.outgoing_ssl = True
                existing_account.outgoing_auth_method = 'oauth2'
                existing_account.username = user_token.email_address
                mail_account = existing_account
            else:
                # Create new account
                mail_account = MailAccount(
                    name=user_token.display_name or "Default Mail Account",
                    email_address=user_token.email_address,
                    account_type=mail_account_type,
                    provider=oauth_provider.name,
                    oauth_token_id=user_token.id,
                    sync_enabled=True,
                    sync_frequency_minutes=15,
                    organization_id=organization_id,
                    user_id=user_id,
                    is_active=True,
                    sync_status=EmailSyncStatus.ACTIVE,
                    created_at=datetime.utcnow(),
                    incoming_server='imap.gmail.com' if oauth_provider == OAuthProvider.GOOGLE else 'outlook.office365.com',
                    incoming_port=993,
                    incoming_ssl=True,
                    incoming_auth_method='oauth2',
                    outgoing_server='smtp.gmail.com' if oauth_provider == OAuthProvider.GOOGLE else 'smtp.office365.com',
                    outgoing_port=587,
                    outgoing_ssl=True,
                    outgoing_auth_method='oauth2',
                    username=user_token.email_address
                )
                db.add(mail_account)
                mail_account = mail_account

            await db.commit()

            # Trigger initial sync after successful authentication
            email_sync_worker.sync_account_now(mail_account.id)

        except Exception as e:
            logger.error(f"Error storing tokens: {str(e)}\n{traceback.format_exc()}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to store OAuth tokens"
            )
        
        return {
            "success": True,
            "message": "OAuth authentication successful",
            "token_id": user_token.id,
            "account_id": mail_account.id,
            "email": user_token.email_address,
            "provider": provider
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"OAuth callback error: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process OAuth callback"
        )


@router.get("/tokens", response_model=List[UserEmailTokenResponse])
async def get_user_tokens(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all OAuth tokens for current user
    """
    stmt = select(UserEmailToken).filter_by(
        user_id=current_user.id,
        organization_id=current_user.organization_id
    )
    result = await db.execute(stmt)
    tokens = result.scalars().all()
    
    # Convert to response format with computed fields
    token_responses = []
    for token in tokens:
        response = UserEmailTokenResponse(
            id=token.id,
            user_id=token.user_id,
            organization_id=token.organization_id,
            provider=token.provider,
            email_address=token.email_address,
            display_name=token.display_name,
            token_type=token.token_type,
            expires_at=token.expires_at,
            status=token.status,
            last_sync_at=token.last_sync_at,
            last_sync_status=token.last_sync_status,
            last_sync_error=token.last_sync_error,
            created_at=token.created_at,
            updated_at=token.updated_at,
            last_used_at=token.last_used_at,
            refresh_count=token.refresh_count,
            has_access_token=bool(token.access_token_encrypted),
            has_refresh_token=bool(token.refresh_token_encrypted),
            is_expired=token.is_expired(),
            is_active=token.is_active(),
            sync_enabled=token.sync_enabled,
            sync_folders=token.sync_folders,
            scope=token.scope
        )
        token_responses.append(response)
    
    return token_responses


@router.get("/tokens/{token_id}", response_model=UserEmailTokenWithDetails)
async def get_token_details(
    token_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed information about a specific token
    """
    stmt = select(UserEmailToken).filter_by(
        id=token_id,
        user_id=current_user.id,
        organization_id=current_user.organization_id
    )
    result = await db.execute(stmt)
    token = result.scalars().first()
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token not found"
        )
    
    response = UserEmailTokenWithDetails(
        id=token.id,
        user_id=token.user_id,
        organization_id=token.organization_id,
        provider=token.provider,
        email_address=token.email_address,
        display_name=token.display_name,
        token_type=token.token_type,
        expires_at=token.expires_at,
        status=token.status,
        last_sync_at=token.last_sync_at,
        last_sync_status=token.last_sync_status,
        last_sync_error=token.last_sync_error,
        created_at=token.created_at,
        updated_at=token.updated_at,
        last_used_at=token.last_used_at,
        refresh_count=token.refresh_count,
        has_access_token=bool(token.access_token_encrypted),
        has_refresh_token=bool(token.refresh_token_encrypted),
        is_expired=token.is_expired(),
        is_active=token.is_active(),
        sync_enabled=token.sync_enabled,
        sync_folders=token.sync_folders,
        scope=token.scope,
        provider_metadata=token.provider_metadata
    )
    
    return response


@router.put("/tokens/{token_id}", response_model=UserEmailTokenResponse)
async def update_token(
    token_id: int,
    token_update: UserEmailTokenUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update token settings
    """
    stmt = select(UserEmailToken).filter_by(
        id=token_id,
        user_id=current_user.id,
        organization_id=current_user.organization_id
    )
    result = await db.execute(stmt)
    token = result.scalars().first()
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token not found"
        )
    
    # Update fields
    update_data = token_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(token, field, value)
    
    token.updated_at = datetime.utcnow()
    await db.commit()
    
    response = UserEmailTokenResponse(
        id=token.id,
        user_id=token.user_id,
        organization_id=token.organization_id,
        provider=token.provider,
        email_address=token.email_address,
        display_name=token.display_name,
        token_type=token.token_type,
        expires_at=token.expires_at,
        status=token.status,
        last_sync_at=token.last_sync_at,
        last_sync_status=token.last_sync_status,
        last_sync_error=token.last_sync_error,
        created_at=token.created_at,
        updated_at=token.updated_at,
        last_used_at=token.last_used_at,
        refresh_count=token.refresh_count,
        has_access_token=bool(token.access_token_encrypted),
        has_refresh_token=bool(token.refresh_token_encrypted),
        is_expired=token.is_expired(),
        is_active=token.is_active(),
        sync_enabled=token.sync_enabled,
        sync_folders=token.sync_folders,
        scope=token.scope
    )
    
    return response


@router.post("/tokens/{token_id}/refresh")
async def refresh_token(
    token_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Manually refresh an OAuth token
    """
    stmt = select(UserEmailToken).filter_by(
        id=token_id,
        user_id=current_user.id,
        organization_id=current_user.organization_id
    )
    result = await db.execute(stmt)
    token = result.scalars().first()
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token not found"
        )
    
    oauth_service = OAuth2Service(db)
    success = await oauth_service.refresh_token(token_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to refresh token. If no refresh token is available, please re-authorize the account after revoking access in your Google settings ."
        )
    
    return {"success": True, "message": "Token refreshed successfully"}


@router.delete("/tokens/{token_id}")
async def revoke_token(
    token_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Revoke an OAuth token
    """
    stmt = select(UserEmailToken).filter_by(
        id=token_id,
        user_id=current_user.id,
        organization_id=current_user.organization_id
    )
    result = await db.execute(stmt)
    token = result.scalars().first()
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token not found"
        )
    
    oauth_service = OAuth2Service(db)
    success = await oauth_service.revoke_token(token_id)
    
    return {"success": True, "message": "Token revoked successfully"}


@router.post("/tokens/{token_id}/sync", response_model=EmailSyncResponse)
async def sync_emails(
    token_id: int,
    sync_request: EmailSyncRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Trigger email sync for a specific token
    """
    stmt = select(UserEmailToken).filter_by(
        id=token_id,
        user_id=current_user.id,
        organization_id=current_user.organization_id
    )
    result = await db.execute(stmt)
    token = result.scalars().first()
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token not found"
        )
    
    # TODO: Implement actual email sync logic
    # This is a placeholder for the email sync functionality
    from datetime import datetime
    
    return EmailSyncResponse(
        success=True,
        message="Email sync completed",
        synced_emails=0,
        errors=[],
        synced_at=datetime.utcnow()
    )