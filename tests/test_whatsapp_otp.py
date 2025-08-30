# tests/test_whatsapp_otp.py

"""
Tests for WhatsApp OTP functionality
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from app.services.whatsapp_service import WhatsAppService, BrevoWhatsAppProvider
from app.services.otp_service import OTPService


class TestBrevoWhatsAppProvider:
    """Test Brevo WhatsApp provider"""
    
    def test_init_with_valid_config(self):
        """Test initialization with valid configuration"""
        with patch('app.services.whatsapp_service.settings') as mock_settings:
            mock_settings.BREVO_API_KEY = 'test-key'
            mock_settings.WHATSAPP_SENDER_NUMBER = '+1234567890'
            mock_settings.WHATSAPP_OTP_TEMPLATE_ID = '123'
            
            with patch('app.services.whatsapp_service.sib_api_v3_sdk') as mock_sdk:
                provider = BrevoWhatsAppProvider()
                assert provider.api_instance is not None
    
    def test_init_with_missing_config(self):
        """Test initialization with missing configuration"""
        with patch('app.services.whatsapp_service.settings') as mock_settings:
            mock_settings.BREVO_API_KEY = None
            mock_settings.WHATSAPP_SENDER_NUMBER = None
            
            provider = BrevoWhatsAppProvider()
            assert provider.api_instance is None
    
    def test_send_otp_success_with_template(self):
        """Test successful OTP sending with template"""
        with patch('app.services.whatsapp_service.settings') as mock_settings:
            mock_settings.BREVO_API_KEY = 'test-key'
            mock_settings.WHATSAPP_SENDER_NUMBER = '+1234567890'
            mock_settings.WHATSAPP_OTP_TEMPLATE_ID = '123'
            
            with patch('app.services.whatsapp_service.sib_api_v3_sdk') as mock_sdk:
                mock_api = Mock()
                mock_sdk.TransactionalWhatsAppApi.return_value = mock_api
                mock_api.send_whatsapp_message.return_value = Mock()
                
                provider = BrevoWhatsAppProvider()
                success, error = provider.send_otp('+919876543210', '123456', 'login')
                
                assert success is True
                assert error is None
                mock_api.send_whatsapp_message.assert_called_once()
    
    def test_send_otp_success_without_template(self):
        """Test successful OTP sending without template"""
        with patch('app.services.whatsapp_service.settings') as mock_settings:
            mock_settings.BREVO_API_KEY = 'test-key'
            mock_settings.WHATSAPP_SENDER_NUMBER = '+1234567890'
            mock_settings.WHATSAPP_OTP_TEMPLATE_ID = None
            
            with patch('app.services.whatsapp_service.sib_api_v3_sdk') as mock_sdk:
                mock_api = Mock()
                mock_sdk.TransactionalWhatsAppApi.return_value = mock_api
                mock_api.send_whatsapp_message.return_value = Mock()
                
                provider = BrevoWhatsAppProvider()
                success, error = provider.send_otp('+919876543210', '123456', 'login')
                
                assert success is True
                assert error is None
                mock_api.send_whatsapp_message.assert_called_once()
    
    def test_send_otp_api_error(self):
        """Test OTP sending with API error"""
        with patch('app.services.whatsapp_service.settings') as mock_settings:
            mock_settings.BREVO_API_KEY = 'test-key'
            mock_settings.WHATSAPP_SENDER_NUMBER = '+1234567890'
            mock_settings.WHATSAPP_OTP_TEMPLATE_ID = '123'
            
            with patch('app.services.whatsapp_service.sib_api_v3_sdk') as mock_sdk:
                mock_api = Mock()
                mock_sdk.TransactionalWhatsAppApi.return_value = mock_api
                mock_api.send_whatsapp_message.side_effect = Exception('API Error')
                
                provider = BrevoWhatsAppProvider()
                success, error = provider.send_otp('+919876543210', '123456', 'login')
                
                assert success is False
                assert 'API Error' in error
    
    def test_phone_number_formatting(self):
        """Test phone number formatting"""
        with patch('app.services.whatsapp_service.settings') as mock_settings:
            mock_settings.BREVO_API_KEY = 'test-key'
            mock_settings.WHATSAPP_SENDER_NUMBER = '+1234567890'
            mock_settings.WHATSAPP_OTP_TEMPLATE_ID = '123'
            
            with patch('app.services.whatsapp_service.sib_api_v3_sdk') as mock_sdk:
                mock_api = Mock()
                mock_sdk.TransactionalWhatsAppApi.return_value = mock_api
                mock_api.send_whatsapp_message.return_value = Mock()
                
                provider = BrevoWhatsAppProvider()
                
                # Test with country code
                provider.send_otp('+919876543210', '123456')
                call_args = mock_api.send_whatsapp_message.call_args[0][0]
                assert '919876543210' in call_args.contact_numbers
                
                # Test without country code (10 digits - assumes India)
                mock_api.reset_mock()
                provider.send_otp('9876543210', '123456')
                call_args = mock_api.send_whatsapp_message.call_args[0][0]
                assert '919876543210' in call_args.contact_numbers


class TestWhatsAppService:
    """Test WhatsApp service"""
    
    def test_get_brevo_provider(self):
        """Test getting Brevo provider"""
        with patch('app.services.whatsapp_service.settings') as mock_settings:
            mock_settings.WHATSAPP_PROVIDER = 'brevo'
            mock_settings.BREVO_API_KEY = 'test-key'
            mock_settings.WHATSAPP_SENDER_NUMBER = '+1234567890'
            
            with patch('app.services.whatsapp_service.sib_api_v3_sdk'):
                service = WhatsAppService()
                assert isinstance(service.provider, BrevoWhatsAppProvider)
    
    def test_unknown_provider(self):
        """Test unknown provider configuration"""
        with patch('app.services.whatsapp_service.settings') as mock_settings:
            mock_settings.WHATSAPP_PROVIDER = 'unknown'
            
            service = WhatsAppService()
            assert service.provider is None
    
    def test_is_available(self):
        """Test service availability check"""
        with patch('app.services.whatsapp_service.settings') as mock_settings:
            mock_settings.WHATSAPP_PROVIDER = 'brevo'
            mock_settings.BREVO_API_KEY = 'test-key'
            mock_settings.WHATSAPP_SENDER_NUMBER = '+1234567890'
            
            with patch('app.services.whatsapp_service.sib_api_v3_sdk'):
                service = WhatsAppService()
                assert service.is_available() is True
        
        # Test with no provider
        service_no_provider = WhatsAppService()
        service_no_provider.provider = None
        assert service_no_provider.is_available() is False


class TestOTPServiceWhatsAppIntegration:
    """Test OTP service with WhatsApp integration"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock database session"""
        return Mock()
    
    @pytest.fixture
    def otp_service(self, mock_db):
        """Create OTP service instance"""
        return OTPService(mock_db)
    
    def test_generate_and_send_otp_whatsapp_success(self, otp_service, mock_db):
        """Test OTP generation and WhatsApp sending success"""
        with patch('app.services.otp_service.whatsapp_service') as mock_wa_service:
            with patch('app.services.otp_service.email_service') as mock_email_service:
                mock_wa_service.is_available.return_value = True
                mock_wa_service.send_otp.return_value = (True, None)
                
                success = otp_service.generate_and_send_otp(
                    email='test@example.com',
                    phone_number='+919876543210',
                    delivery_method='whatsapp'
                )
                
                assert success is True
                mock_wa_service.send_otp.assert_called_once()
                mock_email_service.send_otp_email.assert_not_called()
    
    def test_generate_and_send_otp_whatsapp_fallback_to_email(self, otp_service, mock_db):
        """Test OTP fallback to email when WhatsApp fails"""
        with patch('app.services.otp_service.whatsapp_service') as mock_wa_service:
            with patch('app.services.otp_service.email_service') as mock_email_service:
                mock_wa_service.is_available.return_value = True
                mock_wa_service.send_otp.return_value = (False, 'WhatsApp failed')
                mock_email_service.send_otp_email.return_value = True
                
                success = otp_service.generate_and_send_otp(
                    email='test@example.com',
                    phone_number='+919876543210',
                    delivery_method='auto'
                )
                
                assert success is True
                mock_wa_service.send_otp.assert_called_once()
                mock_email_service.send_otp_email.assert_called_once()
    
    def test_generate_and_send_otp_email_only(self, otp_service, mock_db):
        """Test OTP generation with email only"""
        with patch('app.services.otp_service.whatsapp_service') as mock_wa_service:
            with patch('app.services.otp_service.email_service') as mock_email_service:
                mock_email_service.send_otp_email.return_value = True
                
                success = otp_service.generate_and_send_otp(
                    email='test@example.com',
                    delivery_method='email'
                )
                
                assert success is True
                mock_wa_service.send_otp.assert_not_called()
                mock_email_service.send_otp_email.assert_called_once()
    
    def test_generate_and_send_otp_both_methods_fail(self, otp_service, mock_db):
        """Test OTP generation when both methods fail"""
        with patch('app.services.otp_service.whatsapp_service') as mock_wa_service:
            with patch('app.services.otp_service.email_service') as mock_email_service:
                mock_wa_service.is_available.return_value = True
                mock_wa_service.send_otp.return_value = (False, 'WhatsApp failed')
                mock_email_service.send_otp_email.return_value = False
                mock_db.rollback = Mock()
                
                success = otp_service.generate_and_send_otp(
                    email='test@example.com',
                    phone_number='+919876543210',
                    delivery_method='auto'
                )
                
                assert success is False
                mock_db.rollback.assert_called_once()


if __name__ == '__main__':
    pytest.main([__file__])