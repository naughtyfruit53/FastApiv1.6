# app/services/email_service.py

"""
Email service using Brevo API with SMTP fallback
"""

import secrets
import string
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.security import get_password_hash, verify_password
from app.core.logging import log_email_operation
from app.models import User, OTPVerification
from app.models.vouchers import PurchaseVoucher, SalesVoucher, PurchaseOrder, SalesOrder
import logging

# Brevo (Sendinblue) import
import brevo_python as sib_api_v3_sdk
from brevo_python.rest import ApiException

# SMTP imports for fallback
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Assuming engine is defined in database.py; adjust if needed
from app.core.database import engine
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        # Brevo config
        self.brevo_api_key = getattr(settings, 'BREVO_API_KEY', None)
        self.from_email = getattr(settings, 'BREVO_FROM_EMAIL', None) or getattr(settings, 'EMAILS_FROM_EMAIL', 'naughtyfruit53@gmail.com')
        self.from_name = getattr(settings, 'BREVO_FROM_NAME', 'TritIQ Business Suite')
        
        if self.brevo_api_key:
            try:
                configuration = sib_api_v3_sdk.Configuration()
                configuration.api_key['api-key'] = self.brevo_api_key
                self.api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
                logger.info("Brevo email service initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Brevo API client: {e}")
                self.api_instance = None
        else:
            logger.warning("Brevo API key not configured - falling back to SMTP")
            self.api_instance = None
        
        # SMTP fallback config
        self.smtp_host = getattr(settings, 'SMTP_HOST', None)
        self.smtp_port = getattr(settings, 'SMTP_PORT', None)
        self.smtp_username = getattr(settings, 'SMTP_USERNAME', None)
        self.smtp_password = getattr(settings, 'SMTP_PASSWORD', None)
        self.emails_from_email = getattr(settings, 'EMAILS_FROM_EMAIL', None)
        
        if not all([self.smtp_host, self.smtp_port, self.smtp_username, self.smtp_password, self.emails_from_email]):
            logger.warning("SMTP configuration incomplete - email sending may be disabled")
    
    def _validate_email_config(self) -> tuple[bool, str]:
        """Validate email configuration"""
        if self.brevo_api_key:
            return True, "Brevo configuration is valid"
        elif all([self.smtp_host, self.smtp_port, self.smtp_username, self.smtp_password, self.emails_from_email]):
            return True, "SMTP configuration is valid"
        return False, "No valid email configuration found"
    
    def _send_email_brevo(self, to_email: str, subject: str, body: str, html_body: Optional[str] = None) -> tuple[bool, Optional[str]]:
        """Send email via Brevo"""
        logger.debug(f"Attempting to send email via Brevo to {to_email}")
        try:
            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                to=[{"email": to_email}],
                sender={"name": self.from_name, "email": self.from_email},
                subject=subject,
                text_content=body
            )
            if html_body:
                send_smtp_email.html_content = html_body
            
            response = self.api_instance.send_transac_email(send_smtp_email)
            logger.info(f"Email sent successfully via Brevo to {to_email}. Response: {response}")
            log_email_operation("send", to_email, True)
            return True, None
            
        except ApiException as e:
            error_msg = f"Brevo API error: {str(e)} - Body: {e.body if hasattr(e, 'body') else 'No body'}"
            logger.error(error_msg)
            log_email_operation("send", to_email, False, error_msg)
            return False, error_msg
            
        except Exception as e:
            error_msg = f"Failed to send email via Brevo: {str(e)}"
            logger.error(error_msg)
            log_email_operation("send", to_email, False, error_msg)
            return False, error_msg
    
    def _send_email_smtp(self, to_email: str, subject: str, body: str, html_body: Optional[str] = None) -> tuple[bool, Optional[str]]:
        """Send email via SMTP fallback"""
        logger.debug(f"Attempting to send email via SMTP to {to_email}")
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.emails_from_email
            msg['To'] = to_email
            
            # Plain text part
            text_part = MIMEText(body, 'plain')
            msg.attach(text_part)
            
            # HTML part if available
            if html_body:
                html_part = MIMEText(html_body, 'html')
                msg.attach(html_part)
            
            # Connect to SMTP server
            logger.debug(f"Connecting to SMTP server: {self.smtp_host}:{self.smtp_port}")
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                logger.debug("Starting TLS")
                server.starttls()
                logger.debug(f"Logging in as {self.smtp_username}")
                server.login(self.smtp_username, self.smtp_password)
                logger.debug("Sending message")
                server.send_message(msg)
            
            logger.info(f"Email sent successfully via SMTP to {to_email}")
            log_email_operation("send", to_email, True)
            return True, None
            
        except smtplib.SMTPException as e:
            error_msg = f"SMTP error: {str(e)}"
            logger.error(error_msg)
            log_email_operation("send", to_email, False, error_msg)
            return False, error_msg
            
        except Exception as e:
            error_msg = f"Failed to send email via SMTP: {str(e)}"
            logger.error(error_msg)
            log_email_operation("send", to_email, False, error_msg)
            return False, error_msg
    
    def _send_email(self, to_email: str, subject: str, body: str, html_body: Optional[str] = None) -> tuple[bool, Optional[str]]:
        """
        Internal method to send an email, trying Brevo first then SMTP fallback.
        Returns tuple of (success: bool, error_message: Optional[str])
        """
        logger.debug(f"Starting email send process to {to_email} with subject: {subject}")
        is_valid, error_msg = self._validate_email_config()
        if not is_valid:
            logger.warning(f"Email configuration invalid: {error_msg}")
            log_email_operation("send", to_email, False, error_msg)
            return False, error_msg
        
        # Try Brevo first if available
        if self.api_instance:
            logger.debug("Trying Brevo")
            success, error = self._send_email_brevo(to_email, subject, body, html_body)
            if success:
                return True, None
            logger.warning(f"Brevo failed, falling back to SMTP: {error}")
        
        # Fallback to SMTP
        logger.debug("Trying SMTP fallback")
        return self._send_email_smtp(to_email, subject, body, html_body)
    
    def load_email_template(self, template_name: str, **kwargs) -> tuple[str, str]:
        """
        Load and render email template with variables.
        Returns tuple of (plain_text, html_content)
        """
        try:
            template_path = Path(__file__).parent.parent / "templates" / "email" / f"{template_name}.html"
            
            logger.debug(f"Loading template from: {template_path}")
            if not template_path.exists():
                logger.warning(f"Email template not found: {template_path}")
                return self._generate_fallback_content(**kwargs)
            
            with open(template_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Simple template variable replacement
            for key, value in kwargs.items():
                placeholder = f"{{{{{key}}}}}"
                html_content = html_content.replace(placeholder, str(value) if value is not None else "")
            
            # Generate plain text version from HTML (simplified)
            plain_text = self._html_to_plain(html_content, **kwargs)
            
            return plain_text, html_content
            
        except Exception as e:
            logger.error(f"Error loading email template {template_name}: {e}")
            return self._generate_fallback_content(**kwargs)
    
    def _html_to_plain(self, html_content: str, **kwargs) -> str:
        """Convert HTML to plain text (simplified version)"""
        import re
        
        # Remove HTML tags
        plain = re.sub('<[^<]+?>', '', html_content)
        
        # Clean up whitespace
        plain = re.sub(r'\s+', ' ', plain).strip()
        
        return plain
    
    def _generate_fallback_content(self, **kwargs) -> tuple[str, str]:
        """Generate fallback email content when template is not available"""
        user_name = kwargs.get('user_name', 'User')
        new_password = kwargs.get('new_password', '[PASSWORD]')
        reset_by = kwargs.get('reset_by', 'Administrator')
        
        plain_text = f"""
Dear {user_name},

Your password has been reset by a system administrator.

New Password: {new_password}

For security reasons, you will be required to change this password on your next login.

Reset by: {reset_by}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}

If you did not request this password reset, please contact your system administrator immediately.

Best regards,
TRITIQ ERP Team
"""
        
        html_content = f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <h2 style="color: #007bff;">TRITIQ ERP - Password Reset</h2>
    <p>Dear {user_name},</p>
    <p>Your password has been reset by a system administrator.</p>
    <div style="background-color: #f8f9fa; border: 2px solid #007bff; padding: 15px; margin: 20px 0; text-align: center;">
        <strong>New Password: <span style="font-family: monospace; color: #007bff;">{new_password}</span></strong>
    </div>
    <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; margin: 20px 0;">
        <strong>⚠️ Important:</strong> You will be required to change this password on your next login.
    </div>
    <p><strong>Reset by:</strong> {reset_by}<br>
       <strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
    <p style="color: #d73527;"><strong>If you did not request this password reset, please contact your system administrator immediately.</strong></p>
    <p>Best regards,<br>TRITIQ ERP Team</p>
</body>
</html>
"""
        
        return plain_text, html_content
    
    def send_license_creation_email(self,
                                   org_admin_email: str,
                                   org_admin_name: str,
                                   organization_name: str,
                                   temp_password: str,
                                   subdomain: str,
                                   org_code: str,
                                   created_by: str,
                                   notify_creator: bool = True) -> tuple[bool, Optional[str]]:
        """Send license creation notification email to organization admin and optionally the creator"""
        success_count = 0
        errors = []
        
        try:
            # Email to new organization admin
            admin_template_vars = {
                'admin_name': org_admin_name,
                'admin_email': org_admin_email,
                'organization_name': organization_name,
                'temp_password': temp_password,
                'subdomain': subdomain,
                'org_code': org_code,
                'created_by': created_by,
                'creation_date': datetime.now().strftime('%Y-%m-%d'),
                'creation_time': datetime.now().strftime('%H:%M:%S'),
                'login_url': f"https://{subdomain}.tritiq.com" if subdomain else "https://app.tritiq.com"
            }
            
            admin_subject = f"Welcome to {organization_name} - Org Super Admin Account Created"
            admin_body = f"""
Dear {org_admin_name},

Welcome to TRITIQ ERP! Your organization super admin account has been created successfully.

Organization Details:
- Organization: {organization_name}
- Subdomain: {subdomain}
- Org Code: {org_code}

Your Account Details:
- Email: {org_admin_email}
- Temporary Password: {temp_password}
- Role: Organization Super Administrator

Important Security Notes:
- Please login and change your password immediately for security
- Your temporary password will expire after first use
- You have full administrative access to your organization

Login Instructions:
1. Visit: {admin_template_vars['login_url']}
2. Use your email and temporary password
3. Change your password on first login

If you have any questions or need assistance, please contact our support team.

Best regards,
TRITIQ ERP Team

---
This account was created by: {created_by}
Creation Date: {admin_template_vars['creation_date']} at {admin_template_vars['creation_time']}
"""
            
            admin_success, admin_error = self._send_email(org_admin_email, admin_subject, admin_body)
            if admin_success:
                success_count += 1
                logger.info(f"✅ License creation email sent successfully to org admin: {org_admin_email}")
            else:
                errors.append(f"Failed to send email to org admin {org_admin_email}: {admin_error}")
                logger.error(f"❌ Failed to send license creation email to org admin {org_admin_email}: {admin_error}")
            
            # Email to super admin who created the license (if requested)
            if notify_creator and created_by != org_admin_email:
                creator_subject = f"Organization License Created: {organization_name}"
                creator_body = f"""
Dear Super Administrator,

You have successfully created a new organization license with the following details:

Organization Details:
- Name: {organization_name}
- Subdomain: {subdomain}
- Org Code: {org_code}

Admin Account Created:
- Email: {org_admin_email}
- Name: {org_admin_name}
- Role: Organization Super Administrator
- Temporary Password: {temp_password}

The organization admin has been notified via email with their login credentials.

Creation Summary:
- Created on: {admin_template_vars['creation_date']} at {admin_template_vars['creation_time']}
- Created by: {created_by}

Best regards,
TRITIQ ERP System
"""
                
                creator_success, creator_error = self._send_email(created_by, creator_subject, creator_body)
                if creator_success:
                    success_count += 1
                    logger.info(f"✅ License creation notification sent successfully to creator: {created_by}")
                else:
                    errors.append(f"Failed to send notification to creator {created_by}: {creator_error}")
                    logger.error(f"❌ Failed to send license creation notification to creator {created_by}: {creator_error}")
            
            # Return success if at least one email was sent
            if success_count > 0:
                return True, None if not errors else f"Partial success: {'; '.join(errors)}"
            else:
                return False, f"All emails failed: {'; '.join(errors)}"
                
        except Exception as e:
            error_msg = f"Error in license creation email process: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    def send_password_reset_email(self, 
                                  user_email: str, 
                                  user_name: str, 
                                  new_password: str, 
                                  reset_by: str,
                                  organization_name: Optional[str] = None) -> tuple[bool, Optional[str]]:
        """Send password reset email with template"""
        try:
            logger.debug(f"Preparing password reset email for {user_email}")
            template_vars = {
                'user_name': user_name,
                'user_email': user_email,
                'new_password': new_password,
                'reset_by': reset_by,
                'organization_name': organization_name or 'Your Organization',
                'reset_date': datetime.now().strftime('%Y-%m-%d'),
                'reset_time': datetime.now().strftime('%H:%M:%S'),
                'sent_date': datetime.now().strftime('%Y-%m-%d'),
                'sent_time': datetime.now().strftime('%H:%M:%S'),
                'admin_contact': self.from_email
            }
            
            plain_text, html_content = self.load_email_template('password_reset', **template_vars)
            
            subject = "TRITIQ ERP - Password Reset Notification"
            
            success, error = self._send_email(user_email, subject, plain_text, html_content)
            if success:
                logger.info(f"Password reset email sent successfully to {user_email}")
            else:
                logger.error(f"Failed to send password reset email to {user_email}: {error}")
            return success, error
            
        except Exception as e:
            error_msg = f"Error preparing password reset email for {user_email}: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    def generate_otp(self, length: int = 6) -> str:
        """Generate a secure random OTP"""
        return ''.join(secrets.choice(string.digits) for i in range(length))
    
    def send_otp_email(self, to_email: str, otp: str, purpose: str = "login") -> tuple[bool, Optional[str]]:
        """Send OTP via email with error handling"""
        try:
            subject = f"TRITIQ ERP - OTP for {purpose.title()}"
            body = f"""
Dear User,

Your OTP for {purpose} is: {otp}

This OTP is valid for 10 minutes only.

If you did not request this OTP, please ignore this email or contact support.

Best regards,
TRITIQ ERP Team
"""
            
            return self._send_email(to_email, subject, body)
            
        except Exception as e:
            error_msg = f"Error sending OTP email: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def create_otp_verification(self, db: Session, email: str, purpose: str = "login") -> tuple[Optional[str], Optional[str]]:
        """
        Create OTP verification entry with enhanced error handling.
        Returns tuple of (otp: Optional[str], error_message: Optional[str])
        """
        try:
            otp = self.generate_otp()
            
            # Remove any existing OTP for this email and purpose
            db.query(OTPVerification).filter(
                OTPVerification.email == email,
                OTPVerification.purpose == purpose
            ).delete()
            
            # Create new OTP verification
            otp_verification = OTPVerification(
                email=email,
                otp_hash=get_password_hash(otp),  # Hash the OTP for security
                purpose=purpose,
                expires_at=datetime.utcnow() + timedelta(minutes=10),
                is_used=False,
                used_at=None
            )
            
            db.add(otp_verification)
            db.commit()
            
            # Send OTP email
            success, error = self.send_otp_email(email, otp, purpose)
            if success:
                return otp, None
            else:
                # Rollback if email failed
                db.rollback()
                return None, error
                
        except Exception as e:
            error_msg = f"Failed to create OTP verification for {email}: {str(e)}"
            logger.error(error_msg)
            db.rollback()
            return None, error_msg
    
    def verify_otp(self, db: Session, email: str, otp: str, purpose: str = "login") -> tuple[bool, Optional[str]]:
        """
        Verify OTP with enhanced error handling.
        Returns tuple of (success: bool, error_message: Optional[str])
        """
        try:
            # Find valid OTP
            otp_verification = db.query(OTPVerification).filter(
                OTPVerification.email == email,
                OTPVerification.purpose == purpose,
                OTPVerification.expires_at > datetime.utcnow(),
                OTPVerification.is_used == False
            ).first()
            
            if not otp_verification:
                return False, "Invalid or expired OTP"
            
            # Check attempts
            if otp_verification.attempts >= otp_verification.max_attempts:
                return False, "Maximum OTP attempts exceeded"
            
            # Increment attempts
            otp_verification.attempts += 1
            
            # Verify OTP
            if verify_password(otp, otp_verification.otp_hash):
                # Mark as used
                otp_verification.is_used = True
                otp_verification.used_at = datetime.utcnow()
                db.commit()
                return True, None
            else:
                db.commit()  # Save the incremented attempts
                return False, "Invalid OTP"
            
        except Exception as e:
            error_msg = f"Failed to verify OTP for {email}: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

# Global instance
email_service = EmailService()

def send_voucher_email(voucher_type: str, voucher_id: int, recipient_email: str, recipient_name: str) -> tuple[bool, Optional[str]]:
    """
    Send email for a voucher, fetching details from the database.
    Returns tuple of (success: bool, error_message: Optional[str])
    """
    db = SessionLocal()
    try:
        voucher = None
        details = ""
        
        if voucher_type == "purchase_voucher":
            voucher = db.query(PurchaseVoucher).filter(PurchaseVoucher.id == voucher_id).first()
        elif voucher_type == "sales_voucher":
            voucher = db.query(SalesVoucher).filter(SalesVoucher.id == voucher_id).first()
        elif voucher_type == "purchase_order":
            voucher = db.query(PurchaseOrder).filter(PurchaseOrder.id == voucher_id).first()
        elif voucher_type == "sales_order":
            voucher = db.query(SalesOrder).filter(SalesOrder.id == voucher_id).first()
        
        if not voucher:
            error_msg = f"Voucher not found: {voucher_type} #{voucher_id}"
            logger.error(error_msg)
            return False, error_msg
        
        # Generate details string; adjust based on actual model fields
        details = (
            f"Voucher Number: {voucher.voucher_number}\n"
            f"Date: {voucher.voucher_date if hasattr(voucher, 'voucher_date') else voucher.date}\n"
            f"Total Amount: {voucher.total_amount}\n"
            f"Status: {voucher.status}\n"
        )
        
        subject = f"TRITIQ ERP - {voucher_type.replace('_', ' ').title()} #{voucher.voucher_number}"
        body = f"""
Dear {recipient_name},

A {voucher_type.replace('_', ' ')} has been created/updated.

Details:
{details}

Please login to your TRITIQ ERP account to view the complete details.

Best regards,
TRITIQ ERP Team
"""
        
        success, error = email_service._send_email(recipient_email, subject, body)
        return success, error
        
    except Exception as e:
        error_msg = f"Failed to send voucher email for {voucher_type} #{voucher_id}: {str(e)}"
        logger.error(error_msg)
        return False, error_msg
    finally:
        db.close()