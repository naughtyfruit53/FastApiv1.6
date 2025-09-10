#!/usr/bin/env python3
"""
Email Service Setup Script for Organization Role Restructuring

This script configures and validates the email service for:
- Role change notifications
- Approval workflow emails
- Management report scheduling
- User migration notifications
"""

import os
import sys
import logging
from typing import Dict, Optional
from pathlib import Path

# Add app to path for imports
sys.path.append(str(Path(__file__).parent.parent))

try:
    from app.services.email_service import EmailService
    from app.core.config import settings
    from app.core.logging import setup_logging
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure you're running from the project root and dependencies are installed.")
    sys.exit(1)

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

class EmailServiceSetup:
    """Setup and validate email service configuration"""
    
    def __init__(self):
        self.email_service = None
        self.config_valid = False
        
    def validate_environment(self) -> Dict[str, bool]:
        """Validate email-related environment variables"""
        required_vars = [
            'SMTP_HOST',
            'SMTP_PORT', 
            'SMTP_USERNAME',
            'SMTP_PASSWORD',
            'EMAILS_FROM_EMAIL',
            'EMAILS_FROM_NAME'
        ]
        
        optional_vars = [
            'BREVO_API_KEY',
            'SENDGRID_API_KEY',
            'WHATSAPP_PROVIDER'
        ]
        
        validation_results = {}
        
        print("📧 Email Service Configuration Validation")
        print("=" * 50)
        
        # Check required variables
        print("\n✅ Required Configuration:")
        for var in required_vars:
            value = getattr(settings, var, None)
            is_set = value is not None and value != ""
            validation_results[var] = is_set
            status = "✅" if is_set else "❌"
            print(f"  {status} {var}: {'SET' if is_set else 'NOT SET'}")
            
        # Check optional variables
        print("\n🔧 Optional Configuration:")
        for var in optional_vars:
            value = getattr(settings, var, None)
            is_set = value is not None and value != ""
            validation_results[f"optional_{var}"] = is_set
            status = "✅" if is_set else "⚠️"
            print(f"  {status} {var}: {'SET' if is_set else 'NOT SET'}")
            
        return validation_results
    
    def setup_email_service(self) -> bool:
        """Initialize and test email service"""
        try:
            print("\n🔌 Initializing Email Service...")
            self.email_service = EmailService()
            print("✅ Email service initialized successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize email service: {e}")
            return False
    
    def test_email_functionality(self) -> bool:
        """Test basic email functionality"""
        if not self.email_service:
            print("❌ Email service not initialized")
            return False
            
        try:
            print("\n📧 Testing Email Functionality...")
            
            # Test email template generation
            test_template_data = {
                'user_name': 'Test User',
                'organization_name': 'Test Organization',
                'role_name': 'Admin',
                'approval_status': 'approved'
            }
            
            # Test role change notification template
            role_change_html = self.email_service.generate_role_change_notification(
                **test_template_data
            )
            
            if role_change_html:
                print("✅ Role change notification template generated")
            else:
                print("❌ Failed to generate role change notification template")
                return False
                
            # Test approval workflow template
            approval_html = self.email_service.generate_approval_workflow_notification(
                **test_template_data
            )
            
            if approval_html:
                print("✅ Approval workflow notification template generated")
            else:
                print("❌ Failed to generate approval workflow notification template")
                return False
                
            print("✅ All email functionality tests passed")
            return True
            
        except Exception as e:
            print(f"❌ Email functionality test failed: {e}")
            return False
    
    def create_sample_configuration(self):
        """Create sample email configuration file"""
        sample_config = """# Email Service Configuration for Organization Role Restructuring

# SMTP Configuration (Required)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAILS_FROM_EMAIL=your-email@gmail.com
EMAILS_FROM_NAME=TRITIQ ERP - Role Management

# Alternative Email Services (Optional)
BREVO_API_KEY=your-brevo-api-key
BREVO_FROM_EMAIL=your-email@domain.com
SENDGRID_API_KEY=your-sendgrid-api-key

# Role Management Email Templates
ROLE_CHANGE_TEMPLATE=role_change_notification.html
APPROVAL_WORKFLOW_TEMPLATE=approval_workflow_notification.html
MANAGEMENT_REPORT_TEMPLATE=management_report_scheduled.html

# Email Service Features
EMAIL_RATE_LIMIT=100
EMAIL_RETRY_ATTEMPTS=3
EMAIL_QUEUE_ENABLED=true
EMAIL_ASYNC_SENDING=true
"""
        
        config_file = Path(__file__).parent.parent / '.env.email'
        with open(config_file, 'w') as f:
            f.write(sample_config)
            
        print(f"\n📁 Sample email configuration created: {config_file}")
        print("   Please update the values and merge with your .env file")
    
    def validate_role_management_integration(self) -> bool:
        """Validate integration with role management system"""
        try:
            print("\n🔐 Validating Role Management Integration...")
            
            # Check if role management services are available
            from app.services.role_management_service import RoleManagementService
            from app.services.rbac_enhanced import EnhancedRBACService
            
            print("✅ Role Management Service available")
            print("✅ Enhanced RBAC Service available")
            
            # Check if email templates for role management exist
            template_dir = Path(__file__).parent.parent / 'app' / 'templates' / 'emails'
            required_templates = [
                'role_change_notification.html',
                'approval_workflow_notification.html',
                'user_migration_notification.html',
                'management_report_scheduled.html'
            ]
            
            missing_templates = []
            for template in required_templates:
                template_path = template_dir / template
                if template_path.exists():
                    print(f"✅ Email template found: {template}")
                else:
                    print(f"⚠️ Email template missing: {template}")
                    missing_templates.append(template)
            
            if missing_templates:
                print(f"\n📝 Creating missing email templates...")
                self.create_missing_templates(template_dir, missing_templates)
            
            return True
            
        except ImportError as e:
            print(f"❌ Role management services not available: {e}")
            return False
        except Exception as e:
            print(f"❌ Role management integration validation failed: {e}")
            return False
    
    def create_missing_templates(self, template_dir: Path, missing_templates: list):
        """Create missing email templates"""
        template_dir.mkdir(parents=True, exist_ok=True)
        
        templates = {
            'role_change_notification.html': '''
<!DOCTYPE html>
<html>
<head>
    <title>Role Change Notification</title>
</head>
<body>
    <h2>Role Change Notification</h2>
    <p>Dear {{ user_name }},</p>
    <p>Your role in {{ organization_name }} has been updated to: <strong>{{ role_name }}</strong></p>
    <p>This change is effective immediately.</p>
    <p>Best regards,<br>{{ organization_name }} Admin Team</p>
</body>
</html>''',
            'approval_workflow_notification.html': '''
<!DOCTYPE html>
<html>
<head>
    <title>Approval Workflow Notification</title>
</head>
<body>
    <h2>Approval Request</h2>
    <p>Dear {{ user_name }},</p>
    <p>You have a pending approval request in {{ organization_name }}.</p>
    <p>Status: <strong>{{ approval_status }}</strong></p>
    <p>Please log in to review and process this request.</p>
    <p>Best regards,<br>{{ organization_name }} System</p>
</body>
</html>''',
            'user_migration_notification.html': '''
<!DOCTYPE html>
<html>
<head>
    <title>User Migration Notification</title>
</head>
<body>
    <h2>Account Migration Complete</h2>
    <p>Dear {{ user_name }},</p>
    <p>Your account has been successfully migrated to the new role structure in {{ organization_name }}.</p>
    <p>Your new role: <strong>{{ role_name }}</strong></p>
    <p>No action is required on your part.</p>
    <p>Best regards,<br>{{ organization_name }} Admin Team</p>
</body>
</html>''',
            'management_report_scheduled.html': '''
<!DOCTYPE html>
<html>
<head>
    <title>Scheduled Management Report</title>
</head>
<body>
    <h2>{{ organization_name }} - Management Report</h2>
    <p>Dear {{ user_name }},</p>
    <p>Please find attached your scheduled management report for {{ report_period }}.</p>
    <p>Report Type: <strong>{{ report_type }}</strong></p>
    <p>Generated on: {{ generation_date }}</p>
    <p>Best regards,<br>{{ organization_name }} Reporting System</p>
</body>
</html>'''
        }
        
        for template_name in missing_templates:
            if template_name in templates:
                template_path = template_dir / template_name
                with open(template_path, 'w') as f:
                    f.write(templates[template_name].strip())
                print(f"✅ Created email template: {template_name}")
    
    def run_complete_setup(self):
        """Run complete email service setup and validation"""
        print("🚀 Organization Role Restructuring - Email Service Setup")
        print("=" * 60)
        
        # Step 1: Validate environment
        validation_results = self.validate_environment()
        required_config_valid = all(
            validation_results.get(var, False) 
            for var in ['SMTP_HOST', 'SMTP_PORT', 'SMTP_USERNAME', 'SMTP_PASSWORD', 'EMAILS_FROM_EMAIL']
        )
        
        if not required_config_valid:
            print("\n❌ Required email configuration is incomplete")
            print("📝 Creating sample configuration file...")
            self.create_sample_configuration()
            return False
        
        # Step 2: Setup email service
        if not self.setup_email_service():
            return False
            
        # Step 3: Test functionality
        if not self.test_email_functionality():
            return False
            
        # Step 4: Validate role management integration
        if not self.validate_role_management_integration():
            return False
            
        print("\n🎉 Email Service Setup Complete!")
        print("✅ Email service is ready for Organization Role Restructuring")
        print("✅ All templates are in place")
        print("✅ Integration with role management validated")
        
        return True

def main():
    """Main setup function"""
    setup = EmailServiceSetup()
    success = setup.run_complete_setup()
    
    if success:
        print("\n📧 Email Service Status: READY")
        return 0
    else:
        print("\n❌ Email Service Status: NEEDS CONFIGURATION")
        return 1

if __name__ == "__main__":
    sys.exit(main())