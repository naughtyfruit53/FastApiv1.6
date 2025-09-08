"""
OAuth2 Authentication API endpoints for Google and Microsoft
"""

import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.api.v1.auth import get_current_active_user as get_current_user
from app.models.user_models import User
from app.models.oauth_models import UserEmailToken, OAuthProvider, TokenStatus
from app.schemas.oauth_schemas import (
    OAuthLoginRequest, OAuthLoginResponse, OAuthCallbackRequest,
    UserEmailTokenResponse, UserEmailTokenWithDetails, UserEmailTokenUpdate,
    EmailSyncRequest, EmailSyncResponse
)
from app.services.oauth_service import OAuth2Service
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
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Initiate OAuth2 login flow for specified provider
    """
    # Validate provider
    try:
        oauth_provider = OAuthProvider(provider.lower())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported OAuth provider: {provider}"
        )
    
    # Get redirect URI from request or use default
    redirect_uri = settings.OAUTH_REDIRECT_URI
    
    # Create OAuth service and generate authorization URL
    oauth_service = OAuth2Service(db)
    try:
        auth_url, state = oauth_service.create_authorization_url(
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
        logger.error(f"OAuth login error: {e}")
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
    db: Session = Depends(get_db)
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
        oauth_provider = OAuthProvider(provider.lower())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported OAuth provider: {provider}"
        )
    
    # Exchange code for tokens
    oauth_service = OAuth2Service(db)
    try:
        redirect_uri = settings.OAUTH_REDIRECT_URI
        token_response, user_info = oauth_service.exchange_code_for_tokens(
            provider=oauth_provider,
            code=code,
            state=state,
            redirect_uri=redirect_uri
        )
        
        # Get user from state (this is a simplified approach)
        from app.models.oauth_models import OAuthState
        oauth_state = db.query(OAuthState).filter(
            OAuthState.state == state
        ).first()
        
        if not oauth_state:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid state parameter"
            )
        
        # Store tokens
        user_token = oauth_service.store_user_tokens(
            user_id=oauth_state.user_id,
            organization_id=oauth_state.organization_id,
            provider=oauth_provider,
            token_response=token_response,
            user_info=user_info
        )
        
        return {
            "success": True,
            "message": "OAuth authentication successful",
            "token_id": user_token.id,
            "email": user_token.email_address,
            "provider": provider
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"OAuth callback error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process OAuth callback"
        )


@router.get("/tokens", response_model=List[UserEmailTokenResponse])
async def get_user_tokens(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all OAuth tokens for current user
    """
    tokens = db.query(UserEmailToken).filter(
        UserEmailToken.user_id == current_user.id,
        UserEmailToken.organization_id == current_user.organization_id
    ).all()
    
    # Convert to response format with computed fields
    token_responses = []
    for token in tokens:
        response = UserEmailTokenResponse.model_validate(token)
        response.has_access_token = bool(token.access_token)
        response.has_refresh_token = bool(token.refresh_token)
        response.is_expired = token.is_expired()
        response.is_active = token.is_active()
        token_responses.append(response)
    
    return token_responses


@router.get("/tokens/{token_id}", response_model=UserEmailTokenWithDetails)
async def get_token_details(
    token_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific token
    """
    token = db.query(UserEmailToken).filter(
        UserEmailToken.id == token_id,
        UserEmailToken.user_id == current_user.id,
        UserEmailToken.organization_id == current_user.organization_id
    ).first()
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token not found"
        )
    
    response = UserEmailTokenWithDetails.model_validate(token)
    response.has_access_token = bool(token.access_token)
    response.has_refresh_token = bool(token.refresh_token)
    response.is_expired = token.is_expired()
    response.is_active = token.is_active()
    
    return response


@router.put("/tokens/{token_id}", response_model=UserEmailTokenResponse)
async def update_token(
    token_id: int,
    token_update: UserEmailTokenUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update token settings
    """
    token = db.query(UserEmailToken).filter(
        UserEmailToken.id == token_id,
        UserEmailToken.user_id == current_user.id,
        UserEmailToken.organization_id == current_user.organization_id
    ).first()
    
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
    db.commit()
    
    response = UserEmailTokenResponse.model_validate(token)
    response.has_access_token = bool(token.access_token)
    response.has_refresh_token = bool(token.refresh_token)
    response.is_expired = token.is_expired()
    response.is_active = token.is_active()
    
    return response


@router.post("/tokens/{token_id}/refresh")
async def refresh_token(
    token_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Manually refresh an OAuth token
    """
    token = db.query(UserEmailToken).filter(
        UserEmailToken.id == token_id,
        UserEmailToken.user_id == current_user.id,
        UserEmailToken.organization_id == current_user.organization_id
    ).first()
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token not found"
        )
    
    oauth_service = OAuth2Service(db)
    success = oauth_service.refresh_token(token_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to refresh token"
        )
    
    return {"success": True, "message": "Token refreshed successfully"}


@router.delete("/tokens/{token_id}")
async def revoke_token(
    token_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Revoke an OAuth token
    """
    token = db.query(UserEmailToken).filter(
        UserEmailToken.id == token_id,
        UserEmailToken.user_id == current_user.id,
        UserEmailToken.organization_id == current_user.organization_id
    ).first()
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token not found"
        )
    
    oauth_service = OAuth2Service(db)
    oauth_service.revoke_token(token_id)
    
    return {"success": True, "message": "Token revoked successfully"}


@router.post("/tokens/{token_id}/sync", response_model=EmailSyncResponse)
async def sync_emails(
    token_id: int,
    sync_request: EmailSyncRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Trigger email sync for a specific token
    """
    token = db.query(UserEmailToken).filter(
        UserEmailToken.id == token_id,
        UserEmailToken.user_id == current_user.id,
        UserEmailToken.organization_id == current_user.organization_id
    ).first()
    
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
        last_sync_at=datetime.utcnow()
    )