# app/services/email_service.py

"""
Enhanced Email service using Brevo API with SMTP fallback, audit logging and retry logic
"""

import secrets
import string
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.core.security import get_password_hash, verify_password
from app.core.logging import log_email_operation
from app.models import User, OTPVerification, EmailSend, EmailProvider, EmailStatus, EmailType
from app.models.vouchers import PurchaseVoucher, SalesVoucher, PurchaseOrder, SalesOrder
from app.services.role_hierarchy_service import RoleHierarchyService
import logging

# Brevo (Sendinblue) import
import brevo_python as sib_api_v3_sdk
from brevo_python.rest import ApiException

# SMTP imports for fallback
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Assuming engine is defined in database.py; adjust if needed
from app.core.database import sync_engine, SessionLocal

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        # Brevo api config
        self.brevo_api_api_key = getattr(settings, 'BREVO_API_KEY', None)
        self.from_email = getattr(settings, 'BREVO_FROM_EMAIL', None) or getattr(settings, 'EMAILS_FROM_EMAIL', 'naughtyfruit53@gmail.com')
        self.from_name = getattr(settings, 'BREVO_FROM_NAME', None) or getattr(settings, 'EMAILS_FROM_NAME', 'TritIQ Business Suite')
        
        # Feature flags
        self.enable_brevo = getattr(settings, 'ENABLE_BREVO_EMAIL', True)
        self.fallback_enabled = getattr(settings, 'EMAIL_FALLBACK_ENABLED', True)
        self.max_retry_attempts = getattr(settings, 'EMAIL_RETRY_ATTEMPTS', 3)
        self.retry_delay = getattr(settings, 'EMAIL_RETRY_DELAY_SECONDS', 5)
        
        if self.brevo_api_api_key and self.enable_brevo:
            try:
                configuration = sib_api_v3_sdk.Configuration()
                configuration.api_key['api-key'] = self.brevo_api_api_key
                self.api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
                logger.info("Brevo email service initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Brevo API client: {e}")
                self.api_instance = None
        else:
            logger.warning("Brevo API key not configured or disabled - falling back to SMTP")
            self.api_instance = None
        
        # SMTP fallback config
        self.smtp_host = getattr(settings, 'SMTP_HOST', None)
        self.smtp_port = getattr(settings, 'SMTP_PORT', None)
        self.smtp_username = getattr(settings, 'SMTP_USERNAME', None)
        self.smtp_password = getattr(settings, 'SMTP_PASSWORD', None)
        self.emails_from_email = getattr(settings, 'EMAILS_FROM_EMAIL', None)
        
        if not all([self.smtp_host, self.smtp_port, self.smtp_username, self.smtp_password, self.emails_from_email]):
            logger.warning("SMTP configuration incomplete - email sending may be disabled")
        
        # Initialize role hierarchy service for BCC functionality
        self.role_hierarchy_service = RoleHierarchyService()
    
    def _create_email_audit_record(self, 
                                 db: Session, 
                                 to_email: str, 
                                 subject: str, 
                                 email_type: EmailType,
                                 organization_id: Optional[int] = None,
                                 user_id: Optional[int] = None) -> EmailSend:
        """Create initial record for email send"""
        email_send = EmailSend(
            to_email=to_email,
            from_email=self.from_email,
            subject=subject,
            email_type=email_type,
            provider_used=EmailProvider.BREVO,  # Will be updated if fallback is used
            status=EmailStatus.PENDING,
            organization_id=organization_id,
            user_id=user_id,
            is_brevo_enabled=self.enable_brevo,
            retry_count=0,
            max_retries=self.max_retry_attempts
        )
        db.add(email_send)
        db.flush()  # Get the ID without committing
        return email_send
    
    def _update_email_audit_record(self, 
                                 db: Session, 
                                 email_send: EmailSend,
                                 status: EmailStatus,
                                 provider_used: Optional[EmailProvider] = None,
                                 provider_response: Optional[dict] = None,
                                 provider_message_id: Optional[str] = None,
                                 error_message: Optional[str] = None,
                                 increment_retry: bool = False) -> None:
        """Update email audit record with results"""
        email_send.status = status
        if provider_used:
            email_send.provider_used = provider_used
        if provider_response:
            # Redact sensitive information from response
            redacted_response = self._redact_sensitive_data(provider_response)
            email_send.provider_response = redacted_response
        if provider_message_id:
            email_send.provider_message_id = provider_message_id
        if error_message:
            email_send.error_message = error_message
        if increment_retry:
            email_send.retry_count += 1
            
        # Set status timestamps
        now = datetime.utcnow()
        if status == EmailStatus.SENT:
            email_send.sent_at = now
        elif status == EmailStatus.DELIVERED:
            email_send.delivered_at = now
        elif status == EmailStatus.FAILED:
            email_send.failed_at = now
            
        email_send.updated_at = now
    
    def _redact_sensitive_data(self, data: dict) -> dict:
        """Redact sensitive information from provider response for audit log"""
        if not isinstance(data, dict):
            return data
            
        redacted = data.copy()
        sensitive_keys = ['api_key', 'password', 'token', 'secret', 'authorization', 'auth']
        
        for key in redacted:
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                redacted[key] = "[REDACTED]"
        return redacted
    
    def _validate_email_config(self) -> tuple[bool, str]:
        """Validate email configuration"""
        if self.brevo_api_api_key and self.enable_brevo:
            return True, "Brevo configuration is valid"
        elif self.fallback_enabled and all([self.smtp_host, self.smtp_port, self.smtp_username, self.smtp_password, self.emails_from_email]):
            return True, "SMTP fallback configuration is valid"
        return False, "No valid email configuration found"
    
    def _send_email_brevo(self, 
                        to_email: str, 
                        subject: str, 
                        body: str, 
                        html_body: Optional[str] = None, 
                        bcc_emails: Optional[list] = None,
                        email_send: Optional[EmailSend] = None) -> tuple[bool, Optional[str], Optional[str]]:
        """Send email via Brevo with enhanced error handling and BCC support"""
        logger.debug(f"Attempting to send email via Brevo to {to_email} with BCC: {bcc_emails}")
        try:
            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                to=[{"email": to_email}],
                sender={"name": self.from_name, "email": self.from_email},
                subject=subject,
                text_content=body
            )
            if html_body:
                send_smtp_email.html_content = html_body
            
            # Add BCC recipients if provided
            if bcc_emails:
                send_smtp_email.bcc = [{"email": bcc_email} for bcc_email in bcc_emails if bcc_email]
                logger.info(f"Adding BCC recipients: {bcc_emails}")
            
            response = self.api_instance.send_transac_email(send_smtp_email)
            
            # Extract message ID from response
            message_id = None
            if hasattr(response, 'message_id'):
                message_id = response.message_id
            elif isinstance(response, dict) and 'messageId' in response:
                message_id = response['messageId']
            
            logger.info(f"Email sent successfully via Brevo to {to_email}. Response: {response}")
            log_email_operation("send", to_email, True)
            
            return True, None, message_id
            
        except ApiException as e:
            error_msg = f"Brevo API error: {str(e)} - Body: {e.body if hasattr(e, 'body') else 'No body'}"
            logger.error(error_msg)
            log_email_operation("send", to_email, False, error_msg)
            return False, error_msg, None
            
        except Exception as e:
            error_msg = f"Failed to send email via Brevo: {str(e)}"
            logger.error(error_msg)
            log_email_operation("send", to_email, False, error_msg)
            return False, error_msg, None
    
    def _send_email_smtp(self, 
                       to_email: str, 
                       subject: str, 
                       body: str, 
                       html_body: Optional[str] = None,
                       email_send: Optional[EmailSend] = None) -> tuple[bool, Optional[str], Optional[str]]:
        """Send email via SMTP fallback with enhanced error handling"""
        logger.debug(f"Attempting to send email via SMTP to {to_email}")
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.emails_from_email
            msg['To'] = to_email
            
            # Generate a simple message ID for tracking
            message_id = f"{int(time.time())}.{secrets.token_hex(8)}@{self.smtp_host}"
            msg['Message-ID'] = message_id
            
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
            return True, None, message_id
            
        except smtplib.SMTPException as e:
            error_msg = f"SMTP error: {str(e)}"
            logger.error(error_msg)
            log_email_operation("send", to_email, False, error_msg)
            return False, error_msg, None
            
        except Exception as e:
            error_msg = f"Failed to send email via SMTP: {str(e)}"
            logger.error(error_msg)
            log_email_operation("send", to_email, False, error_msg)
            return False, error_msg, None
    
    def _send_email(self, 
                  to_email: str, 
                  subject: str, 
                  body: str, 
                  html_body: Optional[str] = None,
                  email_type: EmailType = EmailType.TRANSACTIONAL,
                  organization_id: Optional[int] = None,
                  user_id: Optional[int] = None,
                  db: Optional[Session] = None) -> tuple[bool, Optional[str]]:
        """
        Enhanced internal method to send an email with retry, fallback, and audit logging.
        Returns tuple of (success: bool, error_message: Optional[str])
        """
        logger.debug(f"Starting enhanced email send process to {to_email} with subject: {subject}")
        
        # Use provided session or create new one
        close_db = False
        if db is None:
            db = SessionLocal()
            close_db = True
            
        try:
            # Validate configuration
            is_valid, error_msg = self._validate_email_config()
            if not is_valid:
                logger.warning(f"Email configuration invalid: {error_msg}")
                return False, error_msg
            
            # Create audit record
            email_send = self._create_email_audit_record(
                db, to_email, subject, email_type, organization_id, user_id
            )
            
            # Try sending with retry logic
            last_error = None
            attempt = 0
            
            while attempt <= self.max_retry_attempts:
                attempt += 1
                logger.debug(f"Email send attempt {attempt}/{self.max_retry_attempts + 1} to {to_email}")
                
                # Try Brevo first if available and enabled
                if self.api_instance and self.enable_brevo:
                    logger.debug("Trying Brevo")
                    success, error, message_id = self._send_email_brevo(to_email, subject, body, html_body, email_send)
                    
                    if success:
                        self._update_email_audit_record(
                            db, email_send, EmailStatus.SENT, EmailProvider.BREVO, 
                            provider_message_id=message_id
                        )
                        db.commit()
                        logger.info(f"✅ Email sent successfully via Brevo to {to_email} (attempt {attempt})")
                        return True, None
                    else:
                        last_error = error
                        self._update_email_audit_record(
                            db, email_send, EmailStatus.RETRY, EmailProvider.BREVO,
                            error_message=error, increment_retry=True
                        )
                        logger.warning(f"❌ Brevo failed on attempt {attempt}: {error}")
                
                # Try SMTP fallback if enabled and Brevo failed
                if self.fallback_enabled and all([self.smtp_host, self.smtp_port, self.smtp_username, self.smtp_password, self.emails_from_email]):
                    logger.debug("Trying SMTP fallback")
                    success, error, message_id = self._send_email_smtp(to_email, subject, body, html_body, email_send)
                    
                    if success:
                        self._update_email_audit_record(
                            db, email_send, EmailStatus.SENT, EmailProvider.SMTP,
                            provider_message_id=message_id
                        )
                        db.commit()
                        logger.info(f"✅ Email sent successfully via SMTP to {to_email} (attempt {attempt})")
                        return True, None
                    else:
                        last_error = error
                        self._update_email_audit_record(
                            db, email_send, EmailStatus.RETRY, EmailProvider.SMTP,
                            error_message=error, increment_retry=True
                        )
                        logger.warning(f"❌ SMTP failed on attempt {attempt}: {error}")
                
                # Wait before retry (except on last attempt)
                if attempt <= self.max_retry_attempts:
                    retry_delay = self.retry_delay * (2 ** (attempt - 1))  # Exponential backoff
                    logger.debug(f"Waiting {retry_delay} seconds before retry...")
                    time.sleep(retry_delay)
            
            # All attempts failed
            self._update_email_audit_record(
                db, email_send, EmailStatus.FAILED,
                error_message=f"All attempts failed. Last error: {last_error}"
            )
            db.commit()
            
            final_error = f"Failed to send email after {self.max_retry_attempts + 1} attempts. Last error: {last_error}"
            logger.error(f"💀 {final_error}")
            return False, final_error
            
        except Exception as e:
            error_msg = f"Unexpected error in email send process: {str(e)}"
            logger.error(error_msg)
            if 'email_send' in locals():
                self._update_email_audit_record(
                    db, email_send, EmailStatus.FAILED, error_message=error_msg
                )
                db.commit()
            return False, error_msg
        finally:
            if close_db:
                db.close()
    
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
    <p><strong>Reset by:</strong> {reset_by}<strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
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
            
            admin_success, admin_error = self._send_email(
                to_email=org_admin_email,
                subject=admin_subject,
                body=admin_body,
                email_type=EmailType.USER_INVITE,
                organization_id=None,  # This is org creation, so no org_id yet
                user_id=None  # New user not yet created
            )
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
                
                creator_success, creator_error = self._send_email(
                    to_email=created_by,
                    subject=creator_subject,
                    body=creator_body,
                    email_type=EmailType.NOTIFICATION,
                    organization_id=None,  # This is org creation notification
                    user_id=None
                )
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

    def send_password_reset_token_email(self,
                                      user_email: str,
                                      user_name: str,
                                      reset_url: str,
                                      organization_name: Optional[str] = None,
                                      organization_id: Optional[int] = None,
                                      user_id: Optional[int] = None,
                                      db: Optional[Session] = None) -> tuple[bool, Optional[str]]:
        """Send password reset email with secure token URL"""
        try:
            subject = "TRITIQ ERP - Password Reset Request"
            
            # Create email content
            plain_text = f"""
Dear {user_name},

A password reset has been requested for your TRITIQ ERP account.

To reset your password, please click the link below:
{reset_url}

This link will expire in 1 hour for security reasons.

If you did not request this password reset, please ignore this email or contact your system administrator.

Organization: {organization_name or 'Your Organization'}
Request Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Best regards,
TRITIQ ERP Team
"""
            
            html_content = f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #007bff; text-align: center;">TRITIQ ERP - Password Reset</h2>
        
        <p>Dear {user_name},</p>
        
        <p>A password reset has been requested for your TRITIQ ERP account.</p>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{reset_url}" 
               style="background-color: #007bff; color: white; padding: 12px 24px; 
                      text-decoration: none; border-radius: 5px; display: inline-block;">
                Reset Your Password
            </a>
        </div>
        
        <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; margin: 20px 0; border-radius: 5px;">
            <strong>⚠️ Security Notice:</strong> This link will expire in 1 hour for security reasons.
        </div>
        
        <p><strong>Organization:</strong> {organization_name or 'Your Organization'}<br>
           <strong>Request Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <p style="color: #d73527;">
            <strong>If you did not request this password reset, please ignore this email or contact your system administrator.</strong>
        </p>
        
        <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
        
        <p style="font-size: 12px; color: #666; text-align: center;">
            This is an automated message from TRITIQ ERP. Please do not reply to this email.
        </p>
    </div>
</body>
</html>
"""
            
            success, error = self._send_email(
                to_email=user_email,
                subject=subject,
                body=plain_text,
                html_body=html_content,
                email_type=EmailType.PASSWORD_RESET,
                organization_id=organization_id,
                user_id=user_id,
                db=db
            )
            
            if success:
                logger.info(f"Password reset token email sent successfully to {user_email}")
            else:
                logger.error(f"Failed to send password reset token email to {user_email}: {error}")
            return success, error
            
        except Exception as e:
            error_msg = f"Error preparing password reset token email for {user_email}: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    def send_password_reset_email(self, 
                                  user_email: str, 
                                  user_name: str, 
                                  new_password: str, 
                                  reset_by: str,
                                  organization_name: Optional[str] = None,
                                  organization_id: Optional[int] = None,
                                  user_id: Optional[int] = None,
                                  db: Optional[Session] = None) -> tuple[bool, Optional[str]]:
        """Send password reset email with enhanced audit logging"""
        try:
            logger.debug(f"Preparing password reset email for {user_email}")
            template_vars = {
                'user_name': user_name,
                'user_email': user_email,
                'new_password': new_password,
                'reset_by': reset_by,
                'organization_name': organization_name or 'Your Organization',
                'reset_date': datetime.now().strftime('%Y-%m-%d'),
                'reset_time': datetime.now().strftime('%H:%M:%S')
            }
            
            plain_text, html_content = self.load_email_template('password_reset', **template_vars)
            
            subject = "TRITIQ ERP - Password Reset Notification"
            
            success, error = self._send_email(
                to_email=user_email,
                subject=subject, 
                body=plain_text, 
                html_body=html_content,
                email_type=EmailType.PASSWORD_RESET,
                organization_id=organization_id,
                user_id=user_id,
                db=db
            )
            if success:
                logger.info(f"Password reset email sent successfully to {user_email}")
            else:
                logger.error(f"Failed to send password reset email to {user_email}: {error}")
            return success, error
            
        except Exception as e:
            error_msg = f"Error preparing password reset email for {user_email}: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    def send_user_creation_email(self,
                                 user_email: str,
                                 user_name: str,
                                 temp_password: str,
                                 organization_name: str,
                                 login_url: str = "https://fast-apiv1-6.vercel.app/",
                                 organization_id: Optional[int] = None,
                                 user_id: Optional[int] = None,
                                 db: Optional[Session] = None) -> tuple[bool, Optional[str]]:
        """Send user creation welcome email with enhanced audit logging"""
        try:
            logger.debug(f"Preparing user creation email for {user_email}")
            template_vars = {
                'user_name': user_name,
                'user_email': user_email,
                'temp_password': temp_password,
                'organization_name': organization_name,
                'creation_date': datetime.now().strftime('%Y-%m-%d'),
                'creation_time': datetime.now().strftime('%H:%M:%S'),
                'login_url': login_url
            }
            
            plain_text, html_content = self.load_email_template('user_creation', **template_vars)
            
            subject = "Welcome to TRITIQ ERP - Your Account Has Been Created"
            
            success, error = self._send_email(
                to_email=user_email,
                subject=subject, 
                body=plain_text, 
                html_body=html_content,
                email_type=EmailType.USER_CREATION,
                organization_id=organization_id,
                user_id=user_id,
                db=db
            )
            if success:
                logger.info(f"User creation email sent successfully to {user_email}")
            else:
                logger.error(f"Failed to send user creation email to {user_email}: {error}")
            return success, error
            
        except Exception as e:
            error_msg = f"Error preparing user creation email for {user_email}: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    def generate_otp(self, length: int = 6) -> str:
        """Generate a secure random OTP"""
        return ''.join(secrets.choice(string.digits) for i in range(length))
    
    def send_otp_email(self, 
                     to_email: str, 
                     otp: str, 
                     purpose: str = "login", 
                     template: Optional[str] = None,
                     organization_id: Optional[int] = None,
                     user_id: Optional[int] = None,
                     db: Optional[Session] = None) -> tuple[bool, Optional[str]]:
        """Send OTP via email with enhanced audit logging"""
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
            
            success, error = self._send_email(
                to_email=to_email,
                subject=subject,
                body=body,
                email_type=EmailType.OTP,
                organization_id=organization_id,
                user_id=user_id,
                db=db
            )
            return success, error
            
        except Exception as e:
            error_msg = f"Error sending OTP email: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def create_otp_verification(self, db: Session, email: str, purpose: str = "login", 
                              organization_id: Optional[int] = None, user_id: Optional[int] = None) -> tuple[Optional[str], Optional[str]]:
        """
        Create OTP verification entry with enhanced error handling and audit logging.
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
            
            # Send OTP email with audit logging
            success, error = self.send_otp_email(
                to_email=email, 
                otp=otp, 
                purpose=purpose,
                organization_id=organization_id,
                user_id=user_id,
                db=db
            )
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
    
    def send_email_with_role_bcc(self,
                                db: Session,
                                to_email: str,
                                subject: str,
                                body: str,
                                html_body: Optional[str] = None,
                                sender_user: Optional[User] = None,
                                email_type: EmailType = EmailType.TRANSACTIONAL,
                                organization_id: Optional[int] = None,
                                user_id: Optional[int] = None) -> tuple[bool, Optional[str]]:
        """
        Enhanced email sending with automatic role-based BCC functionality.
        
        Args:
            db: Database session
            to_email: Primary recipient email
            subject: Email subject
            body: Plain text body
            html_body: HTML body (optional)
            sender_user: User sending the email (for BCC logic)
            email_type: Type of email being sent
            organization_id: Organization ID for audit
            user_id: User ID for audit
            
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        try:
            # Get BCC recipients based on sender's role and organization settings
            bcc_emails = []
            if sender_user:
                bcc_emails = self.role_hierarchy_service.get_bcc_recipients_for_user(db, sender_user)
                organization_id = organization_id or sender_user.organization_id
                user_id = user_id or sender_user.id
            
            # Create audit record
            email_send = self._create_email_audit_record(
                db=db,
                to_email=to_email,
                subject=subject,
                email_type=email_type,
                organization_id=organization_id,
                user_id=user_id
            )
            
            # Try Brevo first
            if self.api_instance and self.enable_brevo:
                success, error_msg, message_id = self._send_email_brevo(
                    to_email=to_email,
                    subject=subject,
                    body=body,
                    html_body=html_body,
                    bcc_emails=bcc_emails,
                    email_send=email_send
                )
                
                if success:
                    self._update_email_audit_record(
                        db=db,
                        email_send=email_send,
                        status=EmailStatus.SENT,
                        provider_used=EmailProvider.BREVO,
                        provider_message_id=message_id
                    )
                    db.commit()
                    
                    log_msg = f"Email sent successfully to {to_email}"
                    if bcc_emails:
                        log_msg += f" with BCC: {bcc_emails}"
                    logger.info(log_msg)
                    
                    return True, None
                else:
                    # Log the failure and try fallback if enabled
                    self._update_email_audit_record(
                        db=db,
                        email_send=email_send,
                        status=EmailStatus.FAILED,
                        provider_used=EmailProvider.BREVO,
                        error_message=error_msg
                    )
                    
                    if self.fallback_enabled:
                        logger.warning(f"Brevo failed for {to_email}, trying SMTP fallback")
                        # Note: SMTP fallback doesn't support BCC in current implementation
                        # This could be enhanced if needed
                        fallback_success, fallback_error, fallback_message_id = self._send_email_smtp(to_email, subject, body, html_body, email_send)
                        if fallback_success:
                            self._update_email_audit_record(
                                db=db,
                                email_send=email_send,
                                status=EmailStatus.SENT,
                                provider_used=EmailProvider.SMTP,
                                provider_message_id=fallback_message_id
                            )
                            db.commit()
                            logger.warning(f"Email sent via SMTP fallback to {to_email} (BCC not supported in fallback)")
                            return True, None
                        else:
                            self._update_email_audit_record(
                                db=db,
                                email_send=email_send,
                                status=EmailStatus.FAILED,
                                provider_used=EmailProvider.SMTP,
                                error_message=fallback_error
                            )
                    
                    db.commit()
                    return False, error_msg
            else:
                # No Brevo, try SMTP fallback
                if self.fallback_enabled:
                    logger.info(f"Using SMTP for {to_email} (BCC not supported)")
                    success, error_msg, message_id = self._send_email_smtp(to_email, subject, body, html_body, email_send)
                    
                    status = EmailStatus.SENT if success else EmailStatus.FAILED
                    self._update_email_audit_record(
                        db=db,
                        email_send=email_send,
                        status=status,
                        provider_used=EmailProvider.SMTP,
                        provider_message_id=message_id if success else None,
                        error_message=error_msg if not success else None
                    )
                    db.commit()
                    
                    return success, error_msg
                else:
                    error_msg = "No email service configured"
                    self._update_email_audit_record(
                        db=db,
                        email_send=email_send,
                        status=EmailStatus.FAILED,
                        error_message=error_msg
                    )
                    db.commit()
                    return False, error_msg
                    
        except Exception as e:
            error_msg = f"Failed to send email with role BCC: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

# Global instance
email_service = EmailService()

# Import email sync capabilities
from .email_sync_service import EmailSyncService

class EmailManagementService:
    """
    Comprehensive email management service combining sending and syncing
    """
    
    def __init__(self):
        self.email_service = email_service
        self.sync_service = EmailSyncService()
    
    def sync_all_accounts(self, organization_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Sync all active email accounts for an organization
        """
        from app.models.email import MailAccount, EmailSyncStatus
        
        db = SessionLocal()
        try:
            # Get all active accounts
            query = db.query(MailAccount).filter(
                MailAccount.sync_enabled == True,
                MailAccount.sync_status == EmailSyncStatus.ACTIVE
            )
            
            if organization_id:
                query = query.filter(MailAccount.organization_id == organization_id)
            
            accounts = query.all()
            
            results = {
                'total_accounts': len(accounts),
                'successful_syncs': 0,
                'failed_syncs': 0,
                'errors': []
            }
            
            for account in accounts:
                try:
                    success = self.sync_service.sync_account(account.id)
                    if success:
                        results['successful_syncs'] += 1
                    else:
                        results['failed_syncs'] += 1
                except Exception as e:
                    results['failed_syncs'] += 1
                    results['errors'].append(f"Account {account.id}: {str(e)}")
            
            return results
            
        finally:
            db.close()
    
    def get_account_status(self, account_id: int) -> Optional[Dict[str, Any]]:
        """
        Get detailed status of an email account
        """
        from app.models.email import MailAccount, EmailSyncLog
        
        db = SessionLocal()
        try:
            account = db.query(MailAccount).filter(MailAccount.id == account_id).first()
            if not account:
                return None
            
            # Get latest sync log
            latest_sync = db.query(EmailSyncLog).filter(
                EmailSyncLog.account_id == account_id
            ).order_by(EmailSyncLog.started_at.desc()).first()
            
            return {
                'account_id': account.id,
                'email_address': account.email_address,
                'sync_enabled': account.sync_enabled,
                'sync_status': account.sync_status.value,
                'last_sync_at': account.last_sync_at,
                'last_sync_error': account.last_sync_error,
                'total_messages_synced': account.total_messages_synced,
                'full_sync_completed': account.full_sync_completed,
                'latest_sync': {
                    'status': latest_sync.status if latest_sync else None,
                    'messages_new': latest_sync.messages_new if latest_sync else 0,
                    'messages_updated': latest_sync.messages_updated if latest_sync else 0,
                    'duration_seconds': latest_sync.duration_seconds if latest_sync else None,
                    'started_at': latest_sync.started_at if latest_sync else None,
                    'error_message': latest_sync.error_message if latest_sync else None
                }
            }
            
        finally:
            db.close()
    
    def fetch_emails(self, account_id: int, folder: str = 'INBOX', limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """
        Fetch emails from database for a specific account
        """
        from app.models.email import Email, EmailThread
        
        db = SessionLocal()
        try:
            # Get emails
            emails_query = db.query(Email).filter(
                Email.account_id == account_id,
                Email.folder == folder
            ).order_by(Email.received_at.desc())
            
            total_count = emails_query.count()
            emails = emails_query.offset(offset).limit(limit).all()
            
            # Convert to dict format
            email_list = []
            for email in emails:
                email_dict = {
                    'id': email.id,
                    'message_id': email.message_id,
                    'subject': email.subject,
                    'from_address': email.from_address,
                    'from_name': email.from_name,
                    'to_addresses': email.to_addresses,
                    'body_text': email.body_text[:500] + '...' if email.body_text and len(email.body_text) > 500 else email.body_text,
                    'status': email.status.value,
                    'priority': email.priority.value,
                    'has_attachments': email.has_attachments,
                    'sent_at': email.sent_at,
                    'received_at': email.received_at,
                    'folder': email.folder,
                    'customer_id': email.customer_id,
                    'vendor_id': email.vendor_id,
                    'thread_id': email.thread_id
                }
                email_list.append(email_dict)
            
            return {
                'emails': email_list,
                'total_count': total_count,
                'offset': offset,
                'limit': limit,
                'has_more': offset + limit < total_count
            }
            
        finally:
            db.close()
    
    def get_email_detail(self, email_id: int, include_attachments: bool = True) -> Optional[Dict[str, Any]]:
        """
        Get detailed email information including full body and attachments
        """
        from app.models.email import Email, EmailAttachment
        
        db = SessionLocal()
        try:
            email = db.query(Email).filter(Email.id == email_id).first()
            if not email:
                return None
            
            email_dict = {
                'id': email.id,
                'message_id': email.message_id,
                'subject': email.subject,
                'from_address': email.from_address,
                'from_name': email.from_name,
                'reply_to': email.reply_to,
                'to_addresses': email.to_addresses,
                'cc_addresses': email.cc_addresses,
                'bcc_addresses': email.bcc_addresses,
                'body_text': email.body_text,
                'body_html': email.body_html,
                'status': email.status.value,
                'priority': email.priority.value,
                'is_flagged': email.is_flagged,
                'is_important': email.is_important,
                'has_attachments': email.has_attachments,
                'sent_at': email.sent_at,
                'received_at': email.received_at,
                'folder': email.folder,
                'labels': email.labels,
                'size_bytes': email.size_bytes,
                'customer_id': email.customer_id,
                'vendor_id': email.vendor_id,
                'thread_id': email.thread_id,
                'created_at': email.created_at,
                'updated_at': email.updated_at
            }
            
            # Add attachments if requested
            if include_attachments and email.has_attachments:
                attachments = db.query(EmailAttachment).filter(
                    EmailAttachment.email_id == email_id
                ).all()
                
                attachment_list = []
                for attachment in attachments:
                    attachment_dict = {
                        'id': attachment.id,
                        'filename': attachment.filename,
                        'original_filename': attachment.original_filename,
                        'content_type': attachment.content_type,
                        'size_bytes': attachment.size_bytes,
                        'is_inline': attachment.is_inline,
                        'is_safe': attachment.is_safe,
                        'download_count': attachment.download_count,
                        'created_at': attachment.created_at
                    }
                    attachment_list.append(attachment_dict)
                
                email_dict['attachments'] = attachment_list
            
            return email_dict
            
        finally:
            db.close()

# Global email management instance
email_management_service = EmailManagementService()

def send_voucher_email(voucher_type: str, voucher_id: int, recipient_email: str, recipient_name: str,
                      organization_id: Optional[int] = None, user_id: Optional[int] = None) -> tuple[bool, Optional[str]]:
    """
    Send email for a voucher with enhanced audit logging.
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
        
        success, error = email_service._send_email(
            to_email=recipient_email,
            subject=subject,
            body=body,
            email_type=EmailType.NOTIFICATION,
            organization_id=organization_id,
            user_id=user_id,
            db=db
        )
        return success, error
        
    except Exception as e:
        error_msg = f"Failed to send voucher email for {voucher_type} #{voucher_id}: {str(e)}"
        logger.error(error_msg)
        return False, error_msg
    finally:
        db.close()


def link_email_to_customer_vendor(email_id: int, customer_id: Optional[int] = None, 
                                vendor_id: Optional[int] = None, user_id: Optional[int] = None) -> tuple[bool, Optional[str]]:
    """
    Link an email to a customer or vendor for ERP integration
    
    Args:
        email_id: ID of the email to link
        customer_id: Optional customer ID to link to
        vendor_id: Optional vendor ID to link to  
        user_id: ID of user performing the action
        
    Returns:
        Tuple of (success: bool, error_message: Optional[str])
    """
    db = SessionLocal()
    try:
        email = db.query(Email).filter(Email.id == email_id).first()
        if not email:
            return False, f"Email not found: {email_id}"
        
        # Update email with customer/vendor link
        if customer_id:
            email.customer_id = customer_id
        if vendor_id:
            email.vendor_id = vendor_id
            
        email.updated_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Email {email_id} linked to customer_id={customer_id}, vendor_id={vendor_id} by user {user_id}")
        return True, None
        
    except Exception as e:
        db.rollback()
        error_msg = f"Failed to link email {email_id} to customer/vendor: {str(e)}"
        logger.error(error_msg)
        return False, error_msg
    finally:
        db.close()


def auto_link_emails_by_sender(organization_id: int, limit: int = 100) -> Dict[str, Any]:
    """
    Automatically link emails to customers/vendors based on sender email addresses
    
    Args:
        organization_id: Organization ID for multi-tenant filtering
        limit: Maximum number of emails to process in one batch
        
    Returns:
        Dict containing processing results
    """
    db = SessionLocal()
    try:
        from app.models.base import Customer, Vendor
        
        # Get unlinked emails
        unlinked_emails = db.query(Email).filter(
            Email.organization_id == organization_id,
            Email.customer_id.is_(None),
            Email.vendor_id.is_(None)
        ).limit(limit).all()
        
        linked_count = 0
        processed_count = 0
        
        for email in unlinked_emails:
            processed_count += 1
            sender_email = email.sender_email
            
            if not sender_email:
                continue
                
            # Try to match with customer
            customer = db.query(Customer).filter(
                Customer.organization_id == organization_id,
                Customer.email == sender_email
            ).first()
            
            if customer:
                email.customer_id = customer.id
                linked_count += 1
                continue
            
            # Try to match with vendor
            vendor = db.query(Vendor).filter(
                Vendor.organization_id == organization_id,
                Vendor.email == sender_email
            ).first()
            
            if vendor:
                email.vendor_id = vendor.id
                linked_count += 1
        
        db.commit()
        
        return {
            "success": True,
            "processed_emails": processed_count,
            "linked_emails": linked_count,
            "organization_id": organization_id
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error auto-linking emails: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "processed_emails": 0,
            "linked_emails": 0
        }
    finally:
        db.close()