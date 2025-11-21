#!/usr/bin/env python3
"""
WhatsApp OTP Demo Script
Demonstrates the new authentication flow without full dependencies
"""

import json
from typing import Optional, Dict, Any

class MockSettings:
    """Mock settings for demonstration"""
    BREVO_API_KEY = "demo-api-key" 
    WHATSAPP_SENDER_NUMBER = "+1234567890"
    WHATSAPP_OTP_TEMPLATE_ID = "123"
    WHATSAPP_PROVIDER = "brevo"

class MockWhatsAppProvider:
    """Mock WhatsApp provider for demonstration"""
    
    def __init__(self):
        self.api_key = MockSettings.BREVO_API_KEY
        self.sender_number = MockSettings.WHATSAPP_SENDER_NUMBER
        self.template_id = MockSettings.WHATSAPP_OTP_TEMPLATE_ID
        print(f"✅ Mock WhatsApp Provider initialized")
        print(f"   Sender: {self.sender_number}")
        print(f"   Template ID: {self.template_id}")
    
    def send_otp(self, phone_number: str, otp: str, purpose: str = "login") -> tuple[bool, Optional[str]]:
        """Simulate sending OTP via WhatsApp"""
        print(f"\n📱 Sending WhatsApp OTP:")
        print(f"   To: {phone_number}")
        print(f"   OTP: {otp}")
        print(f"   Purpose: {purpose}")
        
        # Format phone number
        if not phone_number.startswith('+'):
            formatted_number = f"+91{phone_number}" if len(phone_number) == 10 else f"+{phone_number}"
        else:
            formatted_number = phone_number
        
        contact_number = formatted_number.lstrip('+')
        
        # Simulate message content
        message = f"🔐 TRITIQ BOS Security Code\n\nYour OTP for {purpose}: {otp}\n\nValid for 10 minutes. Do not share this code.\n\n- TRITIQ BOS Team"
        
        print(f"   Formatted Number: {contact_number}")
        print(f"   Message Content:")
        for line in message.split('\n'):
            print(f"     {line}")
        
        # Simulate success
        print("✅ WhatsApp OTP sent successfully!")
        return True, None

class MockEmailService:
    """Mock email service for demonstration"""
    
    def send_otp_email(self, email: str, otp: str, purpose: str, template: str = "otp.html") -> bool:
        """Simulate sending OTP via email"""
        print(f"\n📧 Sending Email OTP:")
        print(f"   To: {email}")
        print(f"   OTP: {otp}")
        print(f"   Purpose: {purpose}")
        print(f"   Template: {template}")
        print("✅ Email OTP sent successfully!")
        return True

class MockOTPService:
    """Mock OTP service demonstrating the new functionality"""
    
    def __init__(self):
        self.whatsapp_provider = MockWhatsAppProvider()
        self.email_service = MockEmailService()
    
    def generate_otp(self) -> str:
        """Generate a 6-digit OTP"""
        import random
        return ''.join(random.choices('0123456789', k=6))
    
    def generate_and_send_otp(self, email: str, purpose: str = "login", 
                            phone_number: Optional[str] = None, 
                            delivery_method: str = "email") -> bool:
        """Generate OTP and send via specified method with fallback"""
        
        print(f"\n🔐 Generating OTP for {email}")
        print(f"   Purpose: {purpose}")
        print(f"   Phone: {phone_number or 'Not provided'}")
        print(f"   Delivery Method: {delivery_method}")
        
        # Generate OTP
        otp = self.generate_otp()
        print(f"   Generated OTP: {otp}")
        
        delivery_success = False
        delivery_method_used = "none"
        
        # Try WhatsApp first if phone number provided and method allows
        if phone_number and delivery_method in ["whatsapp", "auto"]:
            print(f"\n📱 Attempting WhatsApp delivery...")
            success, error = self.whatsapp_provider.send_otp(phone_number, otp, purpose)
            if success:
                delivery_success = True
                delivery_method_used = "whatsapp"
            else:
                print(f"❌ WhatsApp delivery failed: {error}")
        
        # Fallback to email if WhatsApp failed or not requested
        if not delivery_success:
            print(f"\n📧 Using email fallback...")
            success = self.email_service.send_otp_email(email, otp, purpose)
            if success:
                delivery_success = True
                delivery_method_used = "email"
        
        print(f"\n📊 Delivery Result:")
        print(f"   Success: {delivery_success}")
        print(f"   Method Used: {delivery_method_used}")
        
        return delivery_success

def demo_login_scenarios():
    """Demonstrate different login scenarios"""
    otp_service = MockOTPService()
    
    print("=" * 60)
    print("🚀 TRITIQ BOS - WhatsApp OTP Authentication Demo")
    print("=" * 60)
    
    scenarios = [
        {
            "name": "WhatsApp OTP with Indian Mobile",
            "email": "user@company.com",
            "phone": "9876543210",  # Will auto-format to +91
            "delivery_method": "auto"
        },
        {
            "name": "WhatsApp OTP with International Number",
            "email": "user@company.com", 
            "phone": "+14155552671",
            "delivery_method": "whatsapp"
        },
        {
            "name": "Email OTP Only",
            "email": "user@company.com",
            "phone": None,
            "delivery_method": "email"
        },
        {
            "name": "Auto Mode with Phone (WhatsApp Preferred)",
            "email": "user@company.com",
            "phone": "+919876543210",
            "delivery_method": "auto"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n📋 Scenario {i}: {scenario['name']}")
        print("-" * 50)
        
        success = otp_service.generate_and_send_otp(
            email=scenario["email"],
            phone_number=scenario["phone"],
            delivery_method=scenario["delivery_method"],
            purpose="login"
        )
        
        if success:
            print("✅ Scenario completed successfully!")
        else:
            print("❌ Scenario failed!")
        
        print()

def demo_api_requests():
    """Demonstrate API request/response format"""
    print("\n" + "=" * 60)
    print("📡 API Request/Response Demo")
    print("=" * 60)
    
    # OTP Request examples
    requests = [
        {
            "name": "WhatsApp OTP Request",
            "payload": {
                "email": "user@company.com",
                "phone_number": "+919876543210", 
                "delivery_method": "auto",
                "purpose": "login"
            }
        },
        {
            "name": "Email OTP Request",
            "payload": {
                "email": "user@company.com",
                "delivery_method": "email",
                "purpose": "login"
            }
        }
    ]
    
    for req in requests:
        print(f"\n📤 {req['name']}:")
        print("POST /auth/otp/request")
        print("Content-Type: application/json")
        print(json.dumps(req['payload'], indent=2))
        
        # Mock response
        response = {
            "message": "OTP sent successfully. Check your WhatsApp or email." if req['payload'].get('phone_number') else "OTP sent successfully to your email address.",
            "email": req['payload']['email'],
            "delivery_method": "whatsapp (preferred)" if req['payload'].get('phone_number') else "email"
        }
        
        print(f"\n📥 Response (200 OK):")
        print(json.dumps(response, indent=2))

def demo_ui_flow():
    """Demonstrate the new UI flow"""
    print("\n" + "=" * 60)
    print("🎨 New Login UI Flow Demo")
    print("=" * 60)
    
    steps = [
        "1. User opens login page - sees unified form",
        "2. Default view: Email + Password fields with 'Show Password' toggle",
        "3. 'Login with OTP' checkbox available below password",
        "4. When OTP checked: Password field hidden, Phone field appears",
        "5. User enters email + optional phone number",
        "6. Click 'Send OTP' - stepper shows progress",
        "7. OTP input field appears with verification step",
        "8. Back button allows return to credentials",
        "9. Resend OTP button available",
        "10. Verify OTP completes login (no mandatory password change)"
    ]
    
    for step in steps:
        print(f"   {step}")
    
    print(f"\n✨ Key Features:")
    print(f"   • No toggle switch - integrated experience")
    print(f"   • Show password functionality")
    print(f"   • Phone number optional (email fallback)")
    print(f"   • WhatsApp preferred, email backup")
    print(f"   • Mobile-friendly stepper UI")
    print(f"   • No forced password change for OTP users")

if __name__ == "__main__":
    demo_login_scenarios()
    demo_api_requests() 
    demo_ui_flow()
    
    print("\n" + "=" * 60)
    print("✅ Demo completed successfully!")
    print("🔧 Ready for production deployment with proper configuration")
    print("📚 See docs/WHATSAPP_OTP_SETUP.md for setup instructions")
    print("=" * 60)