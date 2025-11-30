# app/services/demo_user_service.py

"""
Demo User Service
Provides ephemeral session-only demo users with temporary data storage.
Demo users:
- Have no organization ID assignment (use pseudo-org context)
- Session lifetime: 30 minutes
- All data is temporary and purged on logout/expiry
- Only audit logs are retained
"""

import logging
import random
import string
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.models.user_models import User
from app.core.security import get_password_hash, create_access_token
from app.services.otp_service import OTPService

logger = logging.getLogger(__name__)

# Demo session configuration
DEMO_SESSION_DURATION_MINUTES = 30
DEMO_ORG_ID = -1  # Pseudo organization ID for demo users
DEMO_USER_PREFIX = "demo_user_"

# In-memory storage for demo sessions
# NOTE: This in-memory storage is suitable for single-instance deployments.
# For multi-instance production deployments, replace with Redis-based storage:
#   - Use redis-py or aioredis for async operations
#   - Key pattern: f"demo_session:{demo_email}"
#   - Set TTL matching DEMO_SESSION_DURATION_MINUTES
_demo_sessions: Dict[str, Dict[str, Any]] = {}


class DemoUserService:
    """Service for managing demo user sessions and temporary data"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.otp_service = OTPService(db)
    
    @staticmethod
    def generate_demo_email() -> str:
        """Generate a unique demo user email"""
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f"{DEMO_USER_PREFIX}{random_suffix}@demo.local"
    
    @staticmethod
    def is_demo_user(email: str) -> bool:
        """Check if an email belongs to a demo user"""
        return email.startswith(DEMO_USER_PREFIX) and email.endswith("@demo.local")
    
    async def initiate_demo_session(self, phone_number: Optional[str] = None) -> Tuple[bool, str, Optional[str]]:
        """
        Initiate a demo session by generating OTP.
        
        Args:
            phone_number: Optional phone number for WhatsApp OTP delivery
        
        Returns:
            Tuple of (success, message, demo_email)
        """
        try:
            demo_email = self.generate_demo_email()
            
            # Generate and send OTP
            success, otp = await self.otp_service.generate_and_send_otp(
                email=demo_email,
                purpose="demo_login",
                organization_id=None,
                phone_number=phone_number,
                delivery_method="auto" if phone_number else "email"
            )
            
            if success:
                # Store demo session info (pre-verification state)
                _demo_sessions[demo_email] = {
                    "status": "pending_verification",
                    "created_at": datetime.utcnow(),
                    "phone_number": phone_number,
                    "otp_sent": True
                }
                
                logger.info(f"Demo session initiated for {demo_email}")
                return True, f"OTP sent successfully. Demo session valid for {DEMO_SESSION_DURATION_MINUTES} minutes.", demo_email
            else:
                logger.error(f"Failed to send OTP for demo session {demo_email}")
                return False, "Failed to send OTP. Please try again.", None
                
        except Exception as e:
            logger.error(f"Error initiating demo session: {str(e)}")
            return False, "An error occurred while initiating demo session.", None
    
    async def verify_demo_otp(self, demo_email: str, otp: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Verify OTP for demo login and create demo session.
        
        Args:
            demo_email: Demo user email
            otp: OTP code to verify
        
        Returns:
            Tuple of (success, message, session_data)
        """
        try:
            # Verify OTP
            is_valid, message = await self.otp_service.verify_otp(
                email=demo_email,
                otp=otp,
                purpose="demo_login"
            )
            
            if not is_valid:
                return False, message, None
            
            # Create demo user session
            session_data = await self._create_demo_session(demo_email)
            
            if session_data:
                logger.info(f"Demo session verified and created for {demo_email}")
                return True, "Demo session started successfully!", session_data
            else:
                return False, "Failed to create demo session.", None
                
        except Exception as e:
            logger.error(f"Error verifying demo OTP: {str(e)}")
            return False, "An error occurred during verification.", None
    
    async def _create_demo_session(self, demo_email: str) -> Optional[Dict[str, Any]]:
        """
        Create a demo user session with temporary access token.
        
        Args:
            demo_email: Demo user email
        
        Returns:
            Session data including access token, or None on failure
        """
        try:
            expiry_time = datetime.utcnow() + timedelta(minutes=DEMO_SESSION_DURATION_MINUTES)
            
            # Create access token with demo-specific claims
            access_token = create_access_token(
                subject=demo_email,
                organization_id=DEMO_ORG_ID,
                user_role="demo",
                user_type="demo",
                expires_delta=timedelta(minutes=DEMO_SESSION_DURATION_MINUTES)
            )
            
            # Update demo session state
            _demo_sessions[demo_email] = {
                "status": "active",
                "created_at": datetime.utcnow(),
                "expires_at": expiry_time,
                "access_token": access_token,
                "temp_data": {}  # For storing temporary demo data
            }
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": DEMO_SESSION_DURATION_MINUTES * 60,
                "expires_at": expiry_time.isoformat(),
                "demo_email": demo_email,
                "session_duration_minutes": DEMO_SESSION_DURATION_MINUTES,
                "is_demo": True
            }
            
        except Exception as e:
            logger.error(f"Error creating demo session: {str(e)}")
            return None
    
    def get_demo_session(self, demo_email: str) -> Optional[Dict[str, Any]]:
        """Get demo session data if active and not expired."""
        session = _demo_sessions.get(demo_email)
        
        if not session:
            return None
        
        # Check if session has expired
        if session.get("expires_at") and datetime.utcnow() > session["expires_at"]:
            # Session expired, clean up
            self._cleanup_demo_session(demo_email)
            return None
        
        return session
    
    def get_session_time_remaining(self, demo_email: str) -> Optional[int]:
        """Get remaining session time in seconds."""
        session = self.get_demo_session(demo_email)
        
        if not session or not session.get("expires_at"):
            return None
        
        remaining = (session["expires_at"] - datetime.utcnow()).total_seconds()
        return max(0, int(remaining))
    
    async def store_temp_data(self, demo_email: str, key: str, value: Any) -> bool:
        """Store temporary data for a demo session."""
        session = self.get_demo_session(demo_email)
        
        if not session:
            return False
        
        if "temp_data" not in session:
            session["temp_data"] = {}
        
        session["temp_data"][key] = value
        return True
    
    def get_temp_data(self, demo_email: str, key: str) -> Optional[Any]:
        """Get temporary data from a demo session."""
        session = self.get_demo_session(demo_email)
        
        if not session or "temp_data" not in session:
            return None
        
        return session["temp_data"].get(key)
    
    async def end_demo_session(self, demo_email: str) -> Tuple[bool, str]:
        """
        End a demo session and purge all temporary data.
        Audit logs are retained.
        
        Args:
            demo_email: Demo user email
        
        Returns:
            Tuple of (success, message)
        """
        try:
            session = _demo_sessions.get(demo_email)
            
            if not session:
                return True, "Session already ended or not found."
            
            # Log session end for audit
            logger.info(f"Ending demo session for {demo_email}, duration: {(datetime.utcnow() - session.get('created_at', datetime.utcnow())).total_seconds()} seconds")
            
            # Cleanup session data
            self._cleanup_demo_session(demo_email)
            
            return True, "Demo session ended. All temporary data has been purged."
            
        except Exception as e:
            logger.error(f"Error ending demo session: {str(e)}")
            return False, "Error ending demo session."
    
    def _cleanup_demo_session(self, demo_email: str) -> None:
        """Clean up demo session data."""
        if demo_email in _demo_sessions:
            # Log cleanup for audit
            session = _demo_sessions[demo_email]
            data_keys = list(session.get("temp_data", {}).keys())
            logger.info(f"Cleaning up demo session {demo_email}, temp data keys: {data_keys}")
            
            del _demo_sessions[demo_email]
    
    @staticmethod
    def cleanup_expired_sessions() -> int:
        """
        Cleanup all expired demo sessions.
        Should be called periodically by a background task.
        
        Returns:
            Number of sessions cleaned up
        """
        now = datetime.utcnow()
        expired_emails = []
        
        for email, session in _demo_sessions.items():
            if session.get("expires_at") and now > session["expires_at"]:
                expired_emails.append(email)
        
        for email in expired_emails:
            del _demo_sessions[email]
            logger.info(f"Cleaned up expired demo session: {email}")
        
        return len(expired_emails)
    
    @staticmethod
    def get_active_demo_session_count() -> int:
        """Get count of active demo sessions."""
        now = datetime.utcnow()
        active_count = 0
        
        for session in _demo_sessions.values():
            if session.get("status") == "active":
                if not session.get("expires_at") or now < session["expires_at"]:
                    active_count += 1
        
        return active_count


# Singleton instance getter
def get_demo_user_service(db: AsyncSession) -> DemoUserService:
    """Get demo user service instance."""
    return DemoUserService(db)
