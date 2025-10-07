# app/services/otp_service.py

from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, Any, Union
from sqlalchemy.ext.asyncio import AsyncSession
import logging
import random
import string

from app.models.system_models import OTPVerification
from app.core.security import get_password_hash, verify_password
from app.services.system_email_service import system_email_service  # Import for sending email
from app.services.whatsapp_service import whatsapp_service  # Import for sending WhatsApp

logger = logging.getLogger(__name__)


class OTPService:
    """OTP service using database for storage"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def generate_and_send_otp(self, email: str, purpose: str = "login", organization_id: Optional[int] = None, additional_data: Optional[Dict[str, Any]] = None, phone_number: Optional[str] = None, delivery_method: str = "email") -> Tuple[bool, Optional[str]]:
        """Generate OTP and send via specified method (WhatsApp preferred, email fallback). Returns success and the plain OTP."""
        try:
            # Generate 6-digit OTP
            otp = ''.join(random.choices(string.digits, k=6))
            
            # Hash OTP for secure storage
            otp_hash = get_password_hash(otp)
            
            # Create OTP verification record
            expiry = datetime.utcnow() + timedelta(minutes=10)  # Extended to 10 minutes for WhatsApp
            otp_verification = OTPVerification(
                email=email,
                otp_hash=otp_hash,
                purpose=purpose,
                expires_at=expiry,
                organization_id=organization_id
            )
            
            self.db.add(otp_verification)
            await self.db.commit()
            
            # Try WhatsApp first if phone number provided and delivery method allows
            delivery_success = False
            delivery_method_used = "none"
            
            if phone_number and delivery_method in ["whatsapp", "auto"]:
                if whatsapp_service.is_available():
                    success, error = whatsapp_service.send_otp(phone_number, otp, purpose)
                    if success:
                        delivery_success = True
                        delivery_method_used = "whatsapp"
                        logger.info(f"OTP sent via WhatsApp to {phone_number} for {purpose}")
                    else:
                        logger.warning(f"WhatsApp delivery failed for {phone_number}: {error}")
                else:
                    logger.warning("WhatsApp service not available")
            
            # Fallback to email if WhatsApp failed or not requested
            if not delivery_success:
                template = "factory_reset_otp.html" if purpose == "reset_data" else "otp.html"
                success, error = await system_email_service.send_otp_email(email, otp, purpose, template=template)
                
                if success:
                    delivery_success = True
                    delivery_method_used = "email"
                    logger.info(f"OTP sent via email to {email} for {purpose}")
                else:
                    logger.error(f"Failed to send OTP via email to {email} for {purpose}")
            
            if not delivery_success:
                await self.db.rollback()
                return False, None
            
            # Update the OTP record for audit purposes (using existing fields)
            # We'll log the delivery method in the application logs instead of modifying the schema
            logger.info(f"OTP delivery completed: method={delivery_method_used}, email={email}, phone={phone_number if delivery_method_used == 'whatsapp' else 'N/A'}")
            
            return True, otp
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to generate OTP for {email}: {e}")
            return False, None
    
    async def verify_otp(self, email: str, otp: str, purpose: str = "login", return_data: bool = False) -> Union[bool, Tuple[bool, Dict[str, Any]]]:
        """Verify OTP"""
        try:
            # Find latest OTP record
            otp_record = (await self.db.execute(
                select(OTPVerification).filter(
                    OTPVerification.email == email,
                    OTPVerification.purpose == purpose,
                    OTPVerification.is_used == False,
                    OTPVerification.expires_at > datetime.utcnow()
                ).order_by(OTPVerification.created_at.desc())
            )).scalars().first()
            
            if not otp_record:
                logger.warning(f"No valid OTP found for {email} ({purpose})")
                return False if not return_data else (False, {})
            
            # Verify hashed OTP
            if not verify_password(otp, otp_record.otp_hash):
                otp_record.attempts += 1
                if otp_record.attempts >= otp_record.max_attempts:
                    otp_record.is_used = True  # Mark as used after max attempts
                await self.db.commit()
                logger.warning(f"Invalid OTP attempt for {email} ({purpose}), attempts: {otp_record.attempts}")
                return False if not return_data else (False, {})
            
            # Mark as used
            otp_record.is_used = True
            otp_record.used_at = datetime.utcnow()
            await self.db.commit()
            
            logger.info(f"OTP verified successfully for {email} ({purpose})")
            return True if not return_data else (True, {})
            
        except Exception as e:
            logger.error(f"Failed to verify OTP for {email}: {e}")
            return False if not return_data else (False, {})