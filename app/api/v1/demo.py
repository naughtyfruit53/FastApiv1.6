# app/api/v1/demo.py
"""
Demo OTP Users API - Ephemeral Sessions
Provides demo user login flow with OTP verification and 30-minute sessions.
- No org id; use demo session context
- Purge temp data on logout/expiry
- Retain audit logs
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from app.core.database import get_db
from app.core.audit import AuditLogger, get_client_ip, get_user_agent, create_audit_log
from app.services.demo_user_service import (
    DemoUserService,
    get_demo_user_service,
    DEMO_SESSION_DURATION_MINUTES
)

import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/demo", tags=["Demo"])


class DemoSessionRequest(BaseModel):
    """Request to initiate a demo session"""
    phone_number: Optional[str] = Field(None, description="Optional phone number for WhatsApp OTP")


class DemoSessionResponse(BaseModel):
    """Response after initiating demo session"""
    success: bool
    message: str
    demo_email: Optional[str] = None
    session_duration_minutes: int = DEMO_SESSION_DURATION_MINUTES


class DemoVerifyRequest(BaseModel):
    """Request to verify demo OTP"""
    demo_email: str = Field(..., description="Demo email returned from initiate")
    otp: str = Field(..., min_length=6, max_length=6, description="6-digit OTP")


class DemoSessionInfo(BaseModel):
    """Demo session information"""
    demo_email: str
    is_demo: bool = True
    session_duration_minutes: int
    time_remaining_seconds: int
    expires_at: str


class DemoTokenResponse(BaseModel):
    """Response after successful demo OTP verification"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    expires_at: str
    demo_email: str
    session_duration_minutes: int
    is_demo: bool = True
    must_change_password: bool = False


class DemoLogoutResponse(BaseModel):
    """Response after demo logout"""
    success: bool
    message: str


@router.post("/initiate", response_model=DemoSessionResponse)
async def initiate_demo_session(
    request_data: DemoSessionRequest,
    request: Request = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Initiate a demo session by generating and sending OTP.
    
    - Phone number is optional; if provided, WhatsApp delivery is attempted
    - Returns a demo_email that must be used for verification
    - Session will be valid for 30 minutes after verification
    """
    try:
        demo_service = get_demo_user_service(db)
        
        success, message, demo_email = await demo_service.initiate_demo_session(
            phone_number=request_data.phone_number
        )
        
        # Log demo session initiation for audit
        await create_audit_log(
            db=db,
            entity_type="demo_session",
            entity_id=demo_email,
            action="demo_session_initiate",
            user_id=None,
            changes={
                "success": success,
                "phone_number_provided": request_data.phone_number is not None
            },
            ip_address=get_client_ip(request) if request else None,
            user_agent=get_user_agent(request) if request else None,
            organization_id=None
        )
        
        return DemoSessionResponse(
            success=success,
            message=message,
            demo_email=demo_email,
            session_duration_minutes=DEMO_SESSION_DURATION_MINUTES
        )
        
    except Exception as e:
        logger.error(f"Error initiating demo session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initiate demo session"
        )


@router.post("/verify", response_model=DemoTokenResponse)
async def verify_demo_otp(
    request_data: DemoVerifyRequest,
    request: Request = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Verify OTP for demo login and create demo session.
    
    - Returns access token valid for 30 minutes
    - Demo sessions have restricted access (no org data)
    - All temporary data is purged on logout or expiry
    """
    try:
        demo_service = get_demo_user_service(db)
        
        success, message, session_data = await demo_service.verify_demo_otp(
            demo_email=request_data.demo_email,
            otp=request_data.otp
        )
        
        # Log demo verification for audit
        await create_audit_log(
            db=db,
            entity_type="demo_session",
            entity_id=request_data.demo_email,
            action="demo_session_verify",
            user_id=None,
            changes={"success": success},
            ip_address=get_client_ip(request) if request else None,
            user_agent=get_user_agent(request) if request else None,
            organization_id=None
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=message
            )
        
        return DemoTokenResponse(
            access_token=session_data["access_token"],
            token_type=session_data["token_type"],
            expires_in=session_data["expires_in"],
            expires_at=session_data["expires_at"],
            demo_email=session_data["demo_email"],
            session_duration_minutes=session_data["session_duration_minutes"],
            is_demo=True,
            must_change_password=False
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying demo OTP: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify demo OTP"
        )


@router.get("/session/{demo_email}", response_model=DemoSessionInfo)
async def get_demo_session_info(
    demo_email: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get demo session information including time remaining.
    
    - Returns session status and time remaining
    - Use for displaying session countdown in frontend
    """
    try:
        demo_service = get_demo_user_service(db)
        
        session = demo_service.get_demo_session(demo_email)
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Demo session not found or expired"
            )
        
        time_remaining = demo_service.get_session_time_remaining(demo_email)
        
        return DemoSessionInfo(
            demo_email=demo_email,
            is_demo=True,
            session_duration_minutes=DEMO_SESSION_DURATION_MINUTES,
            time_remaining_seconds=time_remaining or 0,
            expires_at=session.get("expires_at", datetime.utcnow()).isoformat() if session.get("expires_at") else ""
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting demo session info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get demo session info"
        )


@router.post("/logout/{demo_email}", response_model=DemoLogoutResponse)
async def logout_demo_session(
    demo_email: str,
    request: Request = None,
    db: AsyncSession = Depends(get_db)
):
    """
    End demo session and purge all temporary data.
    
    - All temporary data created during the session is deleted
    - Audit logs are retained for compliance
    - Frontend should show purge notice
    """
    try:
        demo_service = get_demo_user_service(db)
        
        success, message = await demo_service.end_demo_session(demo_email)
        
        # Log demo logout for audit (retained even after purge)
        await create_audit_log(
            db=db,
            entity_type="demo_session",
            entity_id=demo_email,
            action="demo_session_logout",
            user_id=None,
            changes={
                "success": success,
                "data_purged": True
            },
            ip_address=get_client_ip(request) if request else None,
            user_agent=get_user_agent(request) if request else None,
            organization_id=None
        )
        
        return DemoLogoutResponse(
            success=success,
            message=message
        )
        
    except Exception as e:
        logger.error(f"Error logging out demo session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to end demo session"
        )


@router.get("/stats")
async def get_demo_stats(
    db: AsyncSession = Depends(get_db)
):
    """
    Get demo session statistics (admin/internal use).
    
    - Returns count of active demo sessions
    - Useful for monitoring demo usage
    """
    try:
        active_count = DemoUserService.get_active_demo_session_count()
        
        return {
            "active_demo_sessions": active_count,
            "session_duration_minutes": DEMO_SESSION_DURATION_MINUTES
        }
        
    except Exception as e:
        logger.error(f"Error getting demo stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get demo stats"
        )


@router.post("/cleanup")
async def cleanup_expired_sessions(
    db: AsyncSession = Depends(get_db)
):
    """
    Cleanup expired demo sessions (admin/internal use).
    
    - Should be called periodically by a background task
    - Purges all data for expired sessions
    """
    try:
        cleaned_count = DemoUserService.cleanup_expired_sessions()
        
        return {
            "success": True,
            "cleaned_sessions": cleaned_count
        }
        
    except Exception as e:
        logger.error(f"Error cleaning up demo sessions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cleanup demo sessions"
        )
