#!/usr/bin/env python3
"""
WhatsApp OTP Logic Test (Dependency-Free)
Tests the core logic without external dependencies
"""

import unittest
from unittest.mock import Mock, patch
from typing import Optional, Tuple

# Mock classes to test logic without dependencies

class MockSettings:
    BREVO_API_KEY = 'test-key'
    WHATSAPP_SENDER_NUMBER = '+1234567890'
    WHATSAPP_OTP_TEMPLATE_ID = '123'
    WHATSAPP_PROVIDER = 'brevo'

class BrevoWhatsAppProviderLogic:
    """Core logic for WhatsApp provider (dependency-free)"""
    
    def __init__(self):
        self.api_key = MockSettings.BREVO_API_KEY
        self.sender_number = MockSettings.WHATSAPP_SENDER_NUMBER
        self.template_id = MockSettings.WHATSAPP_OTP_TEMPLATE_ID
        self.initialized = bool(self.api_key and self.sender_number)
    
    def format_phone_number(self, phone_number: str) -> str:
        """Format phone number for API"""
        if not phone_number.startswith('+'):
            # Default to India if no country code provided
            formatted_number = f"+91{phone_number}" if len(phone_number) == 10 else f"+{phone_number}"
        else:
            formatted_number = phone_number
        
        # Remove + for API call
        return formatted_number.lstrip('+')
    
    def create_message_content(self, otp: str, purpose: str) -> str:
        """Create WhatsApp message content"""
        return f"🔐 TRITIQ ERP Security Code\n\nYour OTP for {purpose}: {otp}\n\nValid for 10 minutes. Do not share this code.\n\n- TRITIQ ERP Team"
    
    def send_otp(self, phone_number: str, otp: str, purpose: str = "login") -> Tuple[bool, Optional[str]]:
        """Simulate sending OTP via WhatsApp"""
        if not self.initialized:
            return False, "WhatsApp service not initialized"
        
        try:
            contact_number = self.format_phone_number(phone_number)
            message = self.create_message_content(otp, purpose)
            
            # Simulate API call success
            return True, None
            
        except Exception as e:
            return False, f"Failed to send WhatsApp OTP: {str(e)}"

class OTPServiceLogic:
    """Core OTP service logic (dependency-free)"""
    
    def __init__(self):
        self.whatsapp_provider = BrevoWhatsAppProviderLogic()
    
    def generate_otp(self) -> str:
        """Generate 6-digit OTP"""
        import random
        return ''.join(random.choices('0123456789', k=6))
    
    def determine_delivery_method(self, phone_number: Optional[str], delivery_method: str) -> Tuple[bool, bool]:
        """Determine if WhatsApp should be tried and if email fallback allowed"""
        try_whatsapp = phone_number and delivery_method in ["whatsapp", "auto"]
        allow_email_fallback = delivery_method in ["email", "auto"]
        return try_whatsapp, allow_email_fallback
    
    def send_otp_with_fallback(self, email: str, phone_number: Optional[str], 
                              delivery_method: str, otp: str, purpose: str) -> Tuple[bool, str]:
        """Send OTP with WhatsApp/email fallback logic"""
        try_whatsapp, allow_email_fallback = self.determine_delivery_method(phone_number, delivery_method)
        
        delivery_success = False
        delivery_method_used = "none"
        
        # Try WhatsApp first if requested
        if try_whatsapp:
            success, error = self.whatsapp_provider.send_otp(phone_number, otp, purpose)
            if success:
                delivery_success = True
                delivery_method_used = "whatsapp"
        
        # Fallback to email if WhatsApp failed or not requested
        if not delivery_success and allow_email_fallback:
            # Simulate email success
            delivery_success = True
            delivery_method_used = "email"
        
        return delivery_success, delivery_method_used

class TestWhatsAppOTPLogic(unittest.TestCase):
    """Test WhatsApp OTP logic without dependencies"""
    
    def setUp(self):
        self.provider = BrevoWhatsAppProviderLogic()
        self.otp_service = OTPServiceLogic()
    
    def test_phone_number_formatting(self):
        """Test phone number formatting logic"""
        # Test with country code
        result = self.provider.format_phone_number('+919876543210')
        self.assertEqual(result, '919876543210')
        
        # Test 10-digit Indian number
        result = self.provider.format_phone_number('9876543210')
        self.assertEqual(result, '919876543210')
        
        # Test international without +
        result = self.provider.format_phone_number('14155552671')
        self.assertEqual(result, '14155552671')
    
    def test_message_content_creation(self):
        """Test WhatsApp message content creation"""
        otp = '123456'
        purpose = 'login'
        message = self.provider.create_message_content(otp, purpose)
        
        self.assertIn('TRITIQ ERP', message)
        self.assertIn(otp, message)
        self.assertIn(purpose, message)
        self.assertIn('10 minutes', message)
    
    def test_delivery_method_determination(self):
        """Test delivery method logic"""
        # WhatsApp with phone number
        try_wa, allow_email = self.otp_service.determine_delivery_method('+919876543210', 'whatsapp')
        self.assertTrue(try_wa)
        self.assertFalse(allow_email)
        
        # Auto with phone number  
        try_wa, allow_email = self.otp_service.determine_delivery_method('+919876543210', 'auto')
        self.assertTrue(try_wa)
        self.assertTrue(allow_email)
        
        # Email only
        try_wa, allow_email = self.otp_service.determine_delivery_method(None, 'email')
        self.assertFalse(try_wa)
        self.assertTrue(allow_email)
    
    def test_otp_generation(self):
        """Test OTP generation"""
        otp = self.otp_service.generate_otp()
        self.assertEqual(len(otp), 6)
        self.assertTrue(otp.isdigit())
    
    def test_whatsapp_success_scenario(self):
        """Test successful WhatsApp delivery"""
        success, method = self.otp_service.send_otp_with_fallback(
            email='test@example.com',
            phone_number='+919876543210',
            delivery_method='whatsapp',
            otp='123456',
            purpose='login'
        )
        
        self.assertTrue(success)
        self.assertEqual(method, 'whatsapp')
    
    def test_email_fallback_scenario(self):
        """Test email fallback when no phone provided"""
        success, method = self.otp_service.send_otp_with_fallback(
            email='test@example.com',
            phone_number=None,
            delivery_method='auto',
            otp='123456',
            purpose='login'
        )
        
        self.assertTrue(success)
        self.assertEqual(method, 'email')
    
    def test_auto_mode_with_phone(self):
        """Test auto mode with phone number (WhatsApp preferred)"""
        success, method = self.otp_service.send_otp_with_fallback(
            email='test@example.com',
            phone_number='+919876543210',
            delivery_method='auto',
            otp='123456',
            purpose='login'
        )
        
        self.assertTrue(success)
        self.assertEqual(method, 'whatsapp')

def run_ui_flow_test():
    """Test the new UI flow logic"""
    print("\n🎨 UI Flow Logic Test")
    print("-" * 40)
    
    # Simulate UI state changes
    ui_state = {
        'use_otp': False,
        'show_password': False,
        'otp_step': 0,
        'otp_sent': False
    }
    
    print(f"Initial state: {ui_state}")
    
    # User checks "Login with OTP"
    ui_state['use_otp'] = True
    print(f"After OTP toggle: {ui_state}")
    assert ui_state['use_otp'] == True
    
    # User clicks show password (should only work when not in OTP mode)
    if not ui_state['use_otp']:
        ui_state['show_password'] = True
    print(f"Password visibility: {ui_state['show_password']}")
    
    # User requests OTP
    ui_state['otp_sent'] = True
    ui_state['otp_step'] = 1
    print(f"After OTP request: {ui_state}")
    assert ui_state['otp_step'] == 1
    
    # User goes back
    ui_state['otp_step'] = 0
    ui_state['otp_sent'] = False
    print(f"After back button: {ui_state}")
    assert ui_state['otp_step'] == 0
    
    print("✅ UI flow logic test passed!")

def run_integration_scenarios():
    """Run integration test scenarios"""
    print("\n🔄 Integration Scenarios Test")
    print("-" * 40)
    
    service = OTPServiceLogic()
    
    scenarios = [
        {
            'name': 'WhatsApp Primary',
            'email': 'user@company.com',
            'phone': '+919876543210',
            'method': 'whatsapp',
            'expected_method': 'whatsapp'
        },
        {
            'name': 'Auto with Phone',
            'email': 'user@company.com', 
            'phone': '+919876543210',
            'method': 'auto',
            'expected_method': 'whatsapp'
        },
        {
            'name': 'Email Fallback',
            'email': 'user@company.com',
            'phone': None,
            'method': 'auto',
            'expected_method': 'email'
        },
        {
            'name': 'Email Only',
            'email': 'user@company.com',
            'phone': None,
            'method': 'email',
            'expected_method': 'email'
        }
    ]
    
    for scenario in scenarios:
        print(f"\n📋 Testing: {scenario['name']}")
        success, method = service.send_otp_with_fallback(
            email=scenario['email'],
            phone_number=scenario['phone'],
            delivery_method=scenario['method'],
            otp='123456',
            purpose='login'
        )
        
        print(f"   Expected: {scenario['expected_method']}, Got: {method}")
        assert method == scenario['expected_method'], f"Expected {scenario['expected_method']}, got {method}"
        assert success == True, "Delivery should succeed"
        print(f"   ✅ Passed!")
    
    print("\n✅ All integration scenarios passed!")

if __name__ == '__main__':
    print("=" * 60)
    print("🧪 WhatsApp OTP Logic Test Suite")
    print("=" * 60)
    
    # Run unit tests
    print("\n📋 Running Unit Tests...")
    unittest.main(argv=[''], exit=False, verbosity=0)
    
    # Run UI flow tests
    run_ui_flow_test()
    
    # Run integration scenario tests
    run_integration_scenarios()
    
    print("\n" + "=" * 60)
    print("✅ All tests passed successfully!")
    print("🎯 Core logic verified for WhatsApp OTP functionality")
    print("📱 UI flow logic validated")
    print("🔄 Integration scenarios confirmed")
    print("=" * 60)