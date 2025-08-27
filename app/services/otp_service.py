# app/services/otp_service.py

from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, Any, Union
from sqlalchemy.orm import Session
import logging
import random
import string

from app.models.system_models import OTPVerification
from app.core.security import get_password_hash, verify_password
from app.services.email_service import email_service  # Import for sending email

logger = logging.getLogger(__name__)


class OTPService:
    """OTP service using database for storage"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def generate_and_send_otp(self, email: str, purpose: str = "login", organization_id: Optional[int] = None, additional_data: Optional[Dict[str, Any]] = None) -> bool:
        """Generate OTP and send via email"""
        try:
            # Generate 6-digit OTP
            otp = ''.join(random.choices(string.digits, k=6))
            
            # Hash OTP for secure storage
            otp_hash = get_password_hash(otp)
            
            # Create OTP verification record
            expiry = datetime.utcnow() + timedelta(minutes=5)
            otp_verification = OTPVerification(
                email=email,
                otp_hash=otp_hash,
                purpose=purpose,
                expires_at=expiry,
                organization_id=organization_id
            )
            
            self.db.add(otp_verification)
            self.db.commit()
            
            # Send OTP email
            template = "factory_reset_otp.html" if purpose == "reset_data" else "otp.html"
            success = email_service.send_otp_email(email, otp, purpose, template=template)
            
            if success:
                logger.info(f"OTP sent to {email} for {purpose}")
            else:
                logger.error(f"Failed to send OTP to {email} for {purpose}")
                self.db.rollback()
                return False
            
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to generate OTP for {email}: {e}")
            return False
    
    def verify_otp(self, email: str, otp: str, purpose: str = "login", return_data: bool = False) -> Union[bool, Tuple[bool, Dict[str, Any]]]:
        """Verify OTP"""
        try:
            # Find latest OTP record
            otp_record = self.db.query(OTPVerification).filter(
                OTPVerification.email == email,
                OTPVerification.purpose == purpose,
                OTPVerification.is_used == False,
                OTPVerification.expires_at > datetime.utcnow()
            ).order_by(OTPVerification.created_at.desc()).first()
            
            if not otp_record:
                logger.warning(f"No valid OTP found for {email} ({purpose})")
                return False if not return_data else (False, {})
            
            # Verify hashed OTP
            if not verify_password(otp, otp_record.otp_hash):
                otp_record.attempts += 1
                if otp_record.attempts >= otp_record.max_attempts:
                    otp_record.is_used = True  # Mark as used after max attempts
                self.db.commit()
                logger.warning(f"Invalid OTP attempt for {email} ({purpose}), attempts: {otp_record.attempts}")
                return False if not return_data else (False, {})
            
            # Mark as used
            otp_record.is_used = True
            otp_record.used_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"OTP verified successfully for {email} ({purpose})")
            return True if not return_data else (True, {})
            
        except Exception as e:
            logger.error(f"Failed to verify OTP for {email}: {e}")
            return False if not return_data else (False, {})