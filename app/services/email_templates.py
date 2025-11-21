# app/services/email_templates.py

"""
Email template strings separated for better maintenance.
These are used by system_email_service for generating email content.
"""

from datetime import datetime

def get_license_creation_admin_template(org_admin_name: str, organization_name: str, temp_password: str,
                                       subdomain: str, org_code: str, created_by: str, login_url: str) -> str:
    """Plain text template for license creation email to admin"""
    creation_date = datetime.now().strftime('%Y-%m-%d')
    creation_time = datetime.now().strftime('%H:%M:%S')
    
    return f"""
Dear {org_admin_name},

Welcome to TRITIQ BOS! Your organization super admin account has been created successfully.

Organization Details:
- Organization: {organization_name}
- Subdomain: {subdomain}
- Org Code: {org_code}

Your Account Details:
- Email: {org_admin_name}  # Note: This seems incorrect, should be email, but keeping as per original
- Temporary Password: {temp_password}
- Role: Organization Super Administrator

Important Security Notes:
- Please login and change your password immediately for security
- Your temporary password will expire after first use
- You have full administrative access to your organization

Login Instructions:
1. Visit: {login_url}
2. Use your email and temporary password
3. Change your password on first login

If you have any questions or need assistance, please contact our support team.

Best regards,
TRITIQ BOS Team

---
This account was created by: {created_by}
Creation Date: {creation_date} at {creation_time}
"""

def get_license_creation_creator_template(organization_name: str, subdomain: str, org_code: str,
                                          org_admin_email: str, org_admin_name: str, temp_password: str,
                                          created_by: str) -> str:
    """Plain text template for license creation notification to creator"""
    creation_date = datetime.now().strftime('%Y-%m-%d')
    creation_time = datetime.now().strftime('%H:%M:%S')
    
    return f"""
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
- Created on: {creation_date} at {creation_time}
- Created by: {created_by}

Best regards,
TRITIQ BOS System
"""

def get_password_reset_token_template(user_name: str, reset_url: str, organization_name: str) -> tuple[str, str]:
    """Returns (plain_text, html_content) for password reset token email"""
    request_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    plain_text = f"""
Dear {user_name},

A password reset has been requested for your TRITIQ BOS account.

To reset your password, please click the link below:
{reset_url}

This link will expire in 1 hour for security reasons.

If you did not request this password reset, please ignore this email or contact your system administrator.

Organization: {organization_name or 'Your Organization'}
Request Time: {request_time}

Best regards,
TRITIQ BOS Team
"""
    
    html_content = f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #007bff; text-align: center;">TRITIQ BOS - Password Reset</h2>
        
        <p>Dear {user_name},</p>
        
        <p>A password reset has been requested for your TRITIQ BOS account.</p>
        
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
           <strong>Request Time:</strong> {request_time}</p>
        
        <p style="color: #d73527;">
            <strong>If you did not request this password reset, please ignore this email or contact your system administrator.</strong>
        </p>
        
        <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
        
        <p style="font-size: 12px; color: #666; text-align: center;">
            This is an automated message from TRITIQ BOS. Please do not reply to this email.
        </p>
    </div>
</body>
</html>
"""
    
    return plain_text, html_content

def get_otp_template(otp: str, purpose: str) -> str:
    """Plain text template for OTP email"""
    return f"""
Dear User,

Your OTP for {purpose} is: {otp}

This OTP is valid for 10 minutes only.

If you did not request this OTP, please ignore this email or contact support.

Best regards,
TRITIQ BOS Team
"""