# app/services/system_email_service.py

"""
System Email service using Brevo API with SMTP fallback, audit logging and retry logic
This is separated from user email sending logic as per requirements.
Handles only system-generated emails like password resets, user creation, etc.
"""

import secrets
import string
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from pathlib import Path
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.security import get_password_hash, verify_password
from app.core.logging import log_email_operation
from app.models import User, OTPVerification, EmailSend, EmailProvider, EmailStatus, EmailType
from app.models.email import MailAccount
from app.models.vouchers import PurchaseVoucher, SalesVoucher, PurchaseOrder, SalesOrder
from app.services.role_hierarchy_service import RoleHierarchyService
import logging
import asyncio

# Brevo (Sendinblue) import
import brevo_python as sib_api_v3_sdk
from brevo_python.rest import ApiException

# Assuming engine is defined in database.py; adjust if needed
from app.core.database import sync_engine, SessionLocal, AsyncSessionLocal
from app.services.user_email_service import user_email_service

logger = logging.getLogger(__name__)

class SystemEmailService:
    def __init__(self):
        # Brevo api config
        self.brevo_api_api_key = getattr(settings, 'BREVO_API_KEY', None)
        self.from_email = getattr(settings, 'BREVO_FROM_EMAIL', None) or getattr(settings, 'EMAILS_FROM_EMAIL', 'naughtyfruit53@gmail.com')
        self.from_name = getattr(settings, 'BREVO_FROM_NAME', None) or getattr(settings, 'EMAILS_FROM_NAME', 'TritIQ Business Suite')
        
        # Feature flags
        self.enable_brevo = getattr(settings, 'ENABLE_BREVO_EMAIL', True)
        self.fallback_enabled = getattr(settings, 'EMAIL_FALLBACK_ENABLED', True)  # ADDED: Default to True for SMTP fallback if needed
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
            logger.warning("Brevo API key not configured or disabled")
            self.api_instance = None
        
        # Initialize role hierarchy service for BCC functionality
        self.role_hierarchy_service = RoleHierarchyService()
    
    async def _create_email_audit_record(self, 
                                 db: AsyncSession, 
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
        await db.flush()  # Get the ID without committing
        return email_send
    
    async def _update_email_audit_record(self, 
                                 db: AsyncSession, 
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
        return False, "No valid email configuration found"
    
    def _send_email_brevo(self, 
                        to_email: str, 
                        subject: str, 
                        body: str, 
                        html_body: Optional[str] = None, 
                        bcc_emails: Optional[list] = None) -> tuple[bool, Optional[str], Optional[str]]:
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
            
            # Detailed logging for debug
            logger.debug(f"Brevo full response: status_code={getattr(response, 'status_code', 'N/A')}, body={getattr(response, 'body', 'N/A')}")
            
            # Extract message ID from response
            message_id = None
            if hasattr(response, 'message_id'):
                message_id = response.message_id
            elif isinstance(response, dict) and 'messageId' in response:
                message_id = response['messageId']
            
            if message_id:
                logger.info(f"✅ Email queued via Brevo to {to_email} (Message ID: {message_id})")
            else:
                logger.warning(f"⚠️ Email queued via Brevo to {to_email} but no Message ID returned")
            
            log_email_operation("send", to_email, True)
            
            return True, None, message_id
            
        except ApiException as e:
            error_msg = f"Brevo API error (code {e.status}): {str(e)} - Body: {getattr(e, 'body', 'No body')}"
            logger.error(error_msg)
            log_email_operation("send", to_email, False, error_msg)
            return False, error_msg, None
            
        except Exception as e:
            error_msg = f"Failed to send email via Brevo: {str(e)}"
            logger.error(error_msg)
            log_email_operation("send", to_email, False, error_msg)
            return False, error_msg, None
    
    async def _send_email(self, 
                  to_email: str, 
                  subject: str, 
                  body: str, 
                  html_body: Optional[str] = None,
                  email_type: EmailType = EmailType.TRANSACTIONAL,
                  organization_id: Optional[int] = None,
                  user_id: Optional[int] = None,
                  db: Optional[AsyncSession] = None) -> tuple[bool, Optional[str]]:
        """
        Enhanced internal method to send an email with retry, fallback, and audit logging.
        Returns tuple of (success: bool, error_message: Optional[str])
        """
        logger.debug(f"Starting enhanced email send process to {to_email} with subject: {subject}")
        
        # Use provided session or create new one
        close_db = False
        if db is None:
            db = AsyncSessionLocal()
            close_db = True
            
        try:
            # Validate configuration
            is_valid, error_msg = self._validate_email_config()
            if not is_valid:
                logger.warning(f"Email configuration invalid: {error_msg}")
                return False, error_msg
            
            # Create audit record
            email_send = await self._create_email_audit_record(
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
                    loop = asyncio.get_event_loop()
                    success, error, message_id = await loop.run_in_executor(
                        None,
                        self._send_email_brevo,
                        to_email,
                        subject,
                        body,
                        html_body,
                        None  # bcc_emails is None here, adjust if needed
                    )
                    
                    if success:
                        await self._update_email_audit_record(
                            db, email_send, EmailStatus.SENT, EmailProvider.BREVO, 
                            provider_message_id=message_id
                        )
                        await db.commit()
                        logger.info(f"✅ Email sent successfully via Brevo to {to_email} (attempt {attempt})")
                        return True, None
                    else:
                        last_error = error
                        await self._update_email_audit_record(
                            db, email_send, EmailStatus.RETRY, EmailProvider.BREVO,
                            error_message=error, increment_retry=True
                        )
                        logger.warning(f"❌ Brevo failed on attempt {attempt}: {error}")
                
                # Wait before retry (except on last attempt) - FIXED: Use async sleep
                if attempt <= self.max_retry_attempts:
                    retry_delay = self.retry_delay * (2 ** (attempt - 1))  # Exponential backoff
                    logger.debug(f"Waiting {retry_delay} seconds before retry...")
                    await asyncio.sleep(retry_delay)
            
            # All attempts failed
            await self._update_email_audit_record(
                db, email_send, EmailStatus.FAILED,
                error_message=f"All attempts failed. Last error: {last_error}"
            )
            await db.commit()
            
            final_error = f"Failed to send email after {self.max_retry_attempts + 1} attempts. Last error: {last_error}"
            logger.error(f"💀 {final_error}")
            return False, final_error
            
        except Exception as e:
            error_msg = f"Unexpected error in email send process: {str(e)}"
            logger.error(error_msg)
            if 'email_send' in locals():
                await self._update_email_audit_record(
                    db, email_send, EmailStatus.FAILED, error_message=error_msg
                )
                await db.commit()
            return False, error_msg
        finally:
            if close_db:
                await db.close()
    
    def load_email_template(self, template_name: str, **kwargs) -> tuple[str, str]:
        """
        Load and render email template with variables.
        Returns tuple of (plain_text, html_content)
        """
        try:
            template_path = Path(__file__).parent.parent / "templates" / "email" / f"{template_name}.html"
            
            logger.debug(f"Loading template from: {template_path} with vars: {kwargs}")
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
            
            logger.debug(f"Rendered template {template_name}: plain length={len(plain_text)}, html length={len(html_content)}")
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
        # Load fallback template with provided kwargs
        return self.load_email_template('fallback_email', **kwargs)
    
    async def send_license_creation_email(self,
                                   org_admin_email: str,
                                   org_admin_name: str,
                                   organization_name: str,
                                   temp_password: str,
                                   subdomain: str,
                                   org_code: str,
                                   created_by: str,
                                   notify_creator: bool = True,
                                   login_url: str = "https://app.tritiq.com") -> tuple[bool, Optional[str]]:
        """Send license creation notification email to organization admin and optionally the creator"""
        success_count = 0
        errors = []
        
        try:
            # Log template vars for debug
            admin_vars = {
                'org_admin_name': org_admin_name,
                'organization_name': organization_name,
                'temp_password': temp_password,
                'subdomain': subdomain,
                'org_code': org_code,
                'created_by': created_by,
                'login_url': login_url
            }
            logger.debug(f"License admin email vars: {admin_vars}")
            
            # Email to new organization admin
            admin_subject = f"Welcome to {organization_name} - Org Super Admin Account Created"
            admin_plain, admin_html = self.load_email_template(
                'license_creation_admin',
                **admin_vars
            )
            
            admin_success, admin_error = await self._send_email(
                to_email=org_admin_email,
                subject=admin_subject,
                body=admin_plain,
                html_body=admin_html,
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
                creator_vars = {
                    'organization_name': organization_name,
                    'subdomain': subdomain,
                    'org_code': org_code,
                    'org_admin_email': org_admin_email,
                    'org_admin_name': org_admin_name,
                    'temp_password': temp_password,
                    'created_by': created_by
                }
                logger.debug(f"License creator email vars: {creator_vars}")
                
                creator_subject = f"Organization License Created: {organization_name}"
                creator_plain, creator_html = self.load_email_template(
                    'license_creation_creator',
                    **creator_vars
                )
                
                creator_success, creator_error = await self._send_email(
                    to_email=created_by,
                    subject=creator_subject,
                    body=creator_plain,
                    html_body=creator_html,
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

    async def send_password_reset_token_email(self,
                                      user_email: str,
                                      user_name: str,
                                      reset_url: str,
                                      organization_name: Optional[str] = None,
                                      organization_id: Optional[int] = None,
                                      user_id: Optional[int] = None,
                                      db: Optional[AsyncSession] = None) -> tuple[bool, Optional[str]]:
        """Send password reset email with secure token URL"""
        try:
            subject = "TRITIQ ERP - Password Reset Request"
            
            plain_text, html_content = self.load_email_template(
                'password_reset_token',
                user_name=user_name,
                reset_url=reset_url,
                organization_name=organization_name or 'Your Organization'
            )
            
            success, error = await self._send_email(
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

    async def send_password_reset_email(self, 
                                  user_email: str, 
                                  user_name: str, 
                                  new_password: str, 
                                  reset_by: str,
                                  organization_name: Optional[str] = None,
                                  organization_id: Optional[int] = None,
                                  user_id: Optional[int] = None,
                                  db: Optional[AsyncSession] = None) -> tuple[bool, Optional[str]]:
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
            
            plain_text, html_content = self.load_email_template('password_reset_notification', **template_vars)
            
            subject = "TRITIQ ERP - Password Reset Notification"
            
            success, error = await self._send_email(
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

    async def send_user_creation_email(self,
                                 user_email: str,
                                 user_name: str,
                                 temp_password: str,
                                 organization_name: str,
                                 login_url: str = "https://fast-apiv1-6.vercel.app/",
                                 organization_id: Optional[int] = None,
                                 user_id: Optional[int] = None,
                                 db: Optional[AsyncSession] = None) -> tuple[bool, Optional[str]]:
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
            
            success, error = await self._send_email(
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
    
    async def send_otp_email(self, 
                     to_email: str, 
                     otp: str, 
                     purpose: str = "login", 
                     template: Optional[str] = None,
                     organization_id: Optional[int] = None,
                     user_id: Optional[int] = None,
                     db: Optional[AsyncSession] = None) -> tuple[bool, Optional[str]]:
        """Send OTP via email with enhanced audit logging"""
        try:
            subject = f"TRITIQ ERP - OTP for {purpose.title()}"
            plain_text, html_content = self.load_email_template('otp_email', otp=otp, purpose=purpose)
            
            success, error = await self._send_email(
                to_email=to_email,
                subject=subject,
                body=plain_text,
                html_body=html_content,
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
    
    async def create_otp_verification(self, db: AsyncSession, email: str, purpose: str = "login", 
                              organization_id: Optional[int] = None, user_id: Optional[int] = None) -> tuple[Optional[str], Optional[str]]:
        """
        Create OTP verification entry with enhanced error handling and audit logging.
        Returns tuple of (otp: Optional[str], error_message: Optional[str])
        """
        try:
            otp = self.generate_otp()
            
            # Remove any existing OTP for this email and purpose
            stmt = select(OTPVerification).filter(
                OTPVerification.email == email,
                OTPVerification.purpose == purpose
            )
            result = await db.execute(stmt)
            existing = result.scalars().all()
            for ex in existing:
                await db.delete(ex)
            
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
            await db.commit()
            
            # Send OTP email with audit logging
            success, error = await self.send_otp_email(
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
                await db.rollback()
                return None, error
                
        except Exception as e:
            error_msg = f"Failed to create OTP verification for {email}: {str(e)}"
            logger.error(error_msg)
            await db.rollback()
            return None, error_msg
    
    async def verify_otp(self, db: AsyncSession, email: str, otp: str, purpose: str = "login") -> tuple[bool, Optional[str]]:
        """
        Verify OTP with enhanced error handling.
        Returns tuple of (success: bool, error_message: Optional[str])
        """
        try:
            # Find valid OTP
            stmt = select(OTPVerification).filter(
                OTPVerification.email == email,
                OTPVerification.purpose == purpose,
                OTPVerification.expires_at > datetime.utcnow(),
                OTPVerification.is_used == False
            )
            result = await db.execute(stmt)
            otp_verification = result.scalars().first()
            
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
                await db.commit()
                return True, None
            else:
                await db.commit()  # Save the incremented attempts
                return False, "Invalid OTP"
            
        except Exception as e:
            error_msg = f"Failed to verify OTP for {email}: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    async def send_email_with_role_bcc(self,
                                db: AsyncSession,
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
                bcc_emails = await self.role_hierarchy_service.get_bcc_recipient_for_user(db, sender_user)
                organization_id = organization_id or sender_user.organization_id
                user_id = user_id or sender_user.id
            
            # Create audit record
            email_send = await self._create_email_audit_record(
                db=db,
                to_email=to_email,
                subject=subject,
                email_type=email_type,
                organization_id=organization_id,
                user_id=user_id
            )
            
            # Try Brevo first
            if self.api_instance and self.enable_brevo:
                logger.debug("Trying Brevo")
                
                loop = asyncio.get_event_loop()
                success, error, message_id = await loop.run_in_executor(
                    None,
                    self._send_email_brevo,
                    to_email,
                    subject,
                    body,
                    html_body,
                    bcc_emails
                )
                
                if success:
                    await self._update_email_audit_record(
                        db=db,
                        email_send=email_send,
                        status=EmailStatus.SENT,
                        provider_used=EmailProvider.BREVO, 
                        provider_message_id=message_id
                    )
                    await db.commit()
                    
                    log_msg = f"Email sent successfully to {to_email}"
                    if bcc_emails:
                        log_msg += f" with BCC: {bcc_emails}"
                    logger.info(log_msg)
                    
                    return True, None
                else:
                    # Log the failure and try fallback if enabled
                    await self._update_email_audit_record(
                        db=db,
                        email_send=email_send,
                        status=EmailStatus.FAILED,
                        provider_used=EmailProvider.BREVO,
                        error_message=error
                    )
                    
                    if self.fallback_enabled:
                        logger.warning(f"Brevo failed for {to_email}, trying SMTP fallback")
                        # Note: SMTP fallback doesn't support BCC in current implementation
                        # This could be enhanced if needed
                        fallback_success, fallback_error, fallback_message_id = self._send_email_smtp(to_email, subject, body, html_body, email_send)
                        if fallback_success:
                            await self._update_email_audit_record(
                                db=db,
                                email_send=email_send,
                                status=EmailStatus.SENT,
                                provider_used=EmailProvider.SMTP,
                                provider_message_id=fallback_message_id
                            )
                            await db.commit()
                            logger.warning(f"Email sent via SMTP fallback to {to_email} (BCC not supported in fallback)")
                            return True, None
                        else:
                            await self._update_email_audit_record(
                                db=db,
                                email_send=email_send,
                                status=EmailStatus.FAILED,
                                provider_used=EmailProvider.SMTP,
                                error_message=fallback_error
                            )
                    
                    await db.commit()
                    return False, error
            else:
                # No Brevo, try SMTP fallback
                if self.fallback_enabled:
                    if self.fallback_enabled:
                        logger.info(f"Using SMTP for {to_email} (BCC not supported)")
                        success, error_msg, message_id = self._send_email_smtp(to_email, subject, body, html_body, email_send)
                        
                        status = EmailStatus.SENT if success else EmailStatus.FAILED
                        await self._update_email_audit_record(
                            db=db,
                            email_send=email_send,
                            status=status,
                            provider_used=EmailProvider.SMTP,
                            provider_message_id=message_id if success else None,
                            error_message=error_msg if not success else None
                        )
                        await db.commit()
                        
                        return success, error_msg
                else:
                    error_msg = "No email service configured"
                    await self._update_email_audit_record(
                        db=db,
                        email_send=email_send,
                        status=EmailStatus.FAILED,
                        error_message=error_msg
                    )
                    await db.commit()
                    return False, error_msg
                    
        except Exception as e:
            error_msg = f"Failed to send email with role BCC: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

# Global instance
system_email_service = SystemEmailService()

async def send_voucher_email(voucher_type: str, voucher_id: int, recipient_email: str, recipient_name: str,
                      organization_id: Optional[int] = None, created_by_id: int = None) -> tuple[bool, Optional[str]]:
    """
    Send email for a voucher using user_email_service only (privacy requirement).
    NO FALLBACK to system email - fails if user email account is not available.
    Returns tuple of (success: bool, error_message: Optional[str])
    """
    db = AsyncSessionLocal()
    try:
        voucher = None
        details = ""
        
        stmt = None
        if voucher_type == "purchase_voucher":
            stmt = select(PurchaseVoucher).filter(PurchaseVoucher.id == voucher_id)
        elif voucher_type == "sales_voucher":
            stmt = select(SalesVoucher).filter(SalesVoucher.id == voucher_id)
        elif voucher_type == "purchase_order":
            stmt = select(PurchaseOrder).filter(PurchaseOrder.id == voucher_id)
        elif voucher_type == "sales_order":
            stmt = select(SalesOrder).filter(SalesOrder.id == voucher_id)
        
        if stmt:
            result = await db.execute(stmt)
            voucher = result.scalars().first()
        
        if not voucher:
            error_msg = f"Voucher not found: {voucher_type} #{voucher_id}"
            logger.error(error_msg)
            return False, error_msg
        
        # Get creator ID from voucher
        if not created_by_id:
            created_by_id = voucher.created_by_id if hasattr(voucher, 'created_by_id') else None
        
        if not created_by_id:
            error_msg = "Creator ID is required for sending voucher emails"
            logger.error(error_msg)
            return False, error_msg
        
        # Generate details string; adjust based on actual model fields
        details = (
            f"Voucher Number: {voucher.voucher_number}\n"
            f"Date: {voucher.voucher_date if hasattr(voucher, 'voucher_date') else voucher.date}\n"
            f"Total Amount: {voucher.total_amount}\n"
            f"Status: {voucher.status}\n"
        )
        
        template_vars = {
            'recipient_name': recipient_name,
            'voucher_type': voucher_type.replace('_', ' '),
            'details': details
        }
        
        plain_text, html_content = system_email_service.load_email_template('voucher_notification', **template_vars)
        
        subject = f"TRITIQ ERP - {voucher_type.replace('_', ' ').title()} #{voucher.voucher_number}"
        
        # Fetch creator
        stmt = select(User).filter(User.id == created_by_id)
        result = await db.execute(stmt)
        creator = result.scalars().first()
        
        if not creator:
            error_msg = f"Creator user not found: {created_by_id}"
            logger.error(error_msg)
            return False, error_msg
        
        # Find creator's mail account (assume first active one)
        stmt = select(MailAccount).filter(
            MailAccount.user_id == created_by_id,
            MailAccount.is_active == True,
            MailAccount.sync_enabled == True
        ).limit(1)
        result = await db.execute(stmt)
        account = result.scalars().first()
        
        if not account:
            error_msg = f"No active email account found for user {created_by_id}. Please connect an email account to send vouchers."
            logger.error(error_msg)
            return False, error_msg
        
        # Send using user_email_service ONLY - no fallback
        success, err = await user_email_service.send_email(
            db=db,
            account_id=account.id,
            to_email=recipient_email,
            subject=subject,
            body=plain_text,
            html_body=html_content
        )
        
        if success:
            logger.info(f"Voucher email sent from user {created_by_id}'s account to {recipient_email}")
        else:
            logger.error(f"Failed to send voucher email from user account: {err}")
        
        return success, err
        
    except Exception as e:
        error_msg = f"Failed to send voucher email for {voucher_type} #{voucher_id}: {str(e)}"
        logger.error(error_msg)
        return False, error_msg
    finally:
        await db.close()


async def link_email_to_customer_vendor(email_id: int, customer_id: Optional[int] = None, 
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
    db = AsyncSessionLocal()
    try:
        stmt = select(Email).filter(Email.id == email_id)
        result = await db.execute(stmt)
        email = result.scalars().first()
        if not email:
            return False, f"Email not found: {email_id}"
        
        # Update email with customer/vendor link
        if customer_id:
            email.customer_id = customer_id
        if vendor_id:
            email.vendor_id = vendor_id
            
        email.updated_at = datetime.utcnow()
        await db.commit()
        
        logger.info(f"Email {email_id} linked to customer_id={customer_id}, vendor_id={vendor_id} by user {user_id}")
        return True, None
        
    except Exception as e:
        await db.rollback()
        error_msg = f"Failed to link email {email_id} to customer/vendor: {str(e)}"
        logger.error(error_msg)
        return False, error_msg
    finally:
        await db.close()


async def auto_link_emails_by_sender(organization_id: int, limit: int = 100) -> Dict[str, Any]:
    """
    Automatically link emails to customers/vendors based on sender email addresses
    
    Args:
        organization_id: Organization ID for multi-tenant filtering
        limit: Maximum number of emails to process in one batch
        
    Returns:
        Dict containing processing results
    """
    db = AsyncSessionLocal()
    try:
        from app.models.base import Customer, Vendor
        
        # Get unlinked emails
        stmt = select(Email).filter(
            Email.organization_id == organization_id,
            Email.customer_id.is_(None),
            Email.vendor_id.is_(None)
        ).limit(limit)
        result = await db.execute(stmt)
        unlinked_emails = result.scalars().all()
        
        linked_count = 0
        processed_count = 0
        
        for email in unlinked_emails:
            processed_count += 1
            sender_email = email.sender_email
            
            if not sender_email:
                continue
                
            # Try to match with customer
            stmt = select(Customer).filter(
                Customer.organization_id == organization_id,
                Customer.email == sender_email
            )
            result = await db.execute(stmt)
            customer = result.scalars().first()
            
            if customer:
                email.customer_id = customer.id
                linked_count += 1
                continue
            
            # Try to match with vendor
            stmt = select(Vendor).filter(
                Vendor.organization_id == organization_id,
                Vendor.email == sender_email
            )
            result = await db.execute(stmt)
            vendor = result.scalars().first()
            
            if vendor:
                email.vendor_id = vendor.id
                linked_count += 1
        
        await db.commit()
        
        return {
            "success": True,
            "processed_emails": processed_count,
            "linked_emails": linked_count,
            "organization_id": organization_id
        }
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error auto-linking emails: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "processed_emails": 0,
            "linked_emails": 0
        }
    finally:
        await db.close()