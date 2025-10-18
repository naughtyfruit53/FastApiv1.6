# app/services/whatsapp_service.py

"""
WhatsApp OTP service using Brevo API with configuration-based provider support
"""

import logging
from typing import Optional, Dict, Any, Tuple
from app.core.config import settings
import brevo_python as sib_api_v3_sdk
from brevo_python.rest import ApiException
from brevo_python.models.send_whatsapp_message import SendWhatsappMessage

logger = logging.getLogger(__name__)

class WhatsAppProvider:
    """Base class for WhatsApp providers"""
    
    def send_otp(self, phone_number: str, otp: str, purpose: str = "login") -> Tuple[bool, Optional[str]]:
        """Send OTP via WhatsApp. Returns (success, error_message)"""
        raise NotImplementedError

class BrevoWhatsAppProvider(WhatsAppProvider):
    """Brevo (SendinBlue) WhatsApp provider"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'BREVO_API_KEY', None)
        self.sender_number = getattr(settings, 'WHATSAPP_SENDER_NUMBER', None)
        self.template_id = getattr(settings, 'WHATSAPP_OTP_TEMPLATE_ID', None)
        
        if not all([self.api_key, self.sender_number]):
            logger.warning("Brevo WhatsApp configuration incomplete")
            self.api_instance = None
            return
            
        try:
            configuration = sib_api_v3_sdk.Configuration()
            configuration.api_key['api-key'] = self.api_key
            self.api_instance = sib_api_v3_sdk.TransactionalWhatsAppApi(
                sib_api_v3_sdk.ApiClient(configuration)
            )
            logger.info("Brevo WhatsApp service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Brevo WhatsApp API: {e}")
            self.api_instance = None
    
    def send_otp(self, phone_number: str, otp: str, purpose: str = "login") -> Tuple[bool, Optional[str]]:
        """Send OTP via WhatsApp using Brevo"""
        if not self.api_instance:
            return False, "WhatsApp service not initialized"
        
        try:
            # Format phone number (ensure it starts with country code)
            if not phone_number.startswith('+'):
                # Default to India if no country code provided
                formatted_number = f"+91{phone_number}" if len(phone_number) == 10 else f"+{phone_number}"
            else:
                formatted_number = phone_number
            
            # Remove + for API call
            contact_number = formatted_number.lstrip('+')
            
            # Create message based on whether we have a template or not
            if self.template_id:
                # Use template-based message
                whatsapp_message = SendWhatsappMessage(
                    template_id=int(self.template_id),
                    sender_number=self.sender_number,
                    contact_numbers=[contact_number]
                )
            else:
                # Use text-based message (may require template approval)
                message_text = f"🔐 TritIQ Business Suite Security Code\n\nYour OTP for {purpose}: {otp}\n\nValid for 10 minutes. Do not share this code.\n\n- TritIQ Business Suite Team"
                whatsapp_message = SendWhatsappMessage(
                    text=message_text,
                    sender_number=self.sender_number,
                    contact_numbers=[contact_number]
                )
            
            response = self.api_instance.send_whatsapp_message(whatsapp_message)
            logger.info(f"WhatsApp OTP sent successfully to {contact_number} via Brevo")
            return True, None
            
        except ApiException as e:
            error_msg = f"Brevo WhatsApp API error: {e.body if hasattr(e, 'body') else str(e)}"
            logger.error(error_msg)
            return False, error_msg
            
        except Exception as e:
            error_msg = f"Failed to send WhatsApp OTP via Brevo: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

class WhatsAppService:
    """WhatsApp service with configurable providers"""
    
    def __init__(self):
        if settings is None:
            logger.error("Settings object is None, cannot initialize WhatsAppService")
            self.provider = None
            return
        self.provider = self._get_provider()
    
    def _get_provider(self) -> Optional[WhatsAppProvider]:
        """Get configured WhatsApp provider"""
        provider_name = getattr(settings, 'WHATSAPP_PROVIDER', 'none')
        if provider_name is None:
            logger.warning("WHATSAPP_PROVIDER is None, defaulting to 'none'")
            provider_name = 'none'
        
        provider_name = provider_name.lower()
        if provider_name == 'brevo' and settings.WHATSAPP_ENABLED:
            return BrevoWhatsAppProvider()
        else:
            logger.info(f"WhatsApp provider set to '{provider_name}' or disabled (WHATSAPP_ENABLED={settings.WHATSAPP_ENABLED})")
            return None
    
    def is_available(self) -> bool:
        """Check if WhatsApp service is available and configured"""
        return self.provider is not None and settings.WHATSAPP_ENABLED
    
    def send_otp(self, phone_number: str, otp: str, purpose: str = "login") -> Tuple[bool, Optional[str]]:
        """Send OTP via WhatsApp"""
        if not self.is_available():
            return False, "WhatsApp service is disabled or not configured"
        
        return self.provider.send_otp(phone_number, otp, purpose)

# Global instance
try:
    whatsapp_service = WhatsAppService()
except Exception as e:
    logger.error(f"Failed to initialize WhatsAppService: {str(e)}")
    whatsapp_service = None