# app/schemas/user.py

"""
User schemas for authentication and user management
"""
from pydantic import BaseModel, EmailStr, field_validator, Field, ConfigDict
from typing import Optional, Union, TypeAlias, Dict
from datetime import datetime
from enum import Enum
# Removed import of check_password_strength from security to break circular import


class UserRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    APP_ADMIN = "app_admin"
    ORG_ADMIN = "org_admin"
    ADMIN = "admin"
    STANDARD_USER = "standard_user"

class EmailLogin(BaseModel):
    email: EmailStr
    password: str

class PlatformUserRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    PLATFORM_ADMIN = "platform_admin"


# User schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    role: UserRole = UserRole.STANDARD_USER
    department: Optional[str] = None
    designation: Optional[str] = None
    employee_id: Optional[str] = None
    phone: Optional[str] = None
    is_active: bool = True
    has_stock_access: bool = True  # Module access for stock functionality
    assigned_modules: Optional[Dict[str, bool]] = None  # Module access control


class UserCreate(UserBase):
    password: str
    organization_id: Optional[int] = None  # Optional for creation by super admin
    
    @field_validator('password')
    def validate_password(cls, v):
        is_strong, msg = cls.check_password_strength(v)
        if not is_strong:
            raise ValueError(msg)
        return v
    
    @staticmethod
    def check_password_strength(password: str) -> tuple[bool, str]:
        """Check password strength and return validation result"""
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"

        if not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"

        if not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"

        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one digit"

        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(c in special_chars for c in password):
            return False, "Password must contain at least one special character"

        return True, "Password is strong"


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    employee_id: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None
    must_change_password: Optional[bool] = None
    has_stock_access: Optional[bool] = None  # Module access for stock functionality
    assigned_modules: Optional[Dict[str, bool]] = None  # Module access control


class UserInDB(UserBase):
    id: int
    organization_id: Optional[int] = None  # Optional to allow None for platform users
    supabase_uuid: Optional[str] = None  # Supabase user UUID for auth integration
    is_super_admin: bool = False
    must_change_password: bool = False
    force_password_reset: bool = False
    failed_login_attempts: int = 0
    locked_until: Optional[datetime] = None
    avatar_path: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    has_stock_access: bool = True  # Module access for stock functionality
    user_settings: Optional[Dict] = None  # Add user_settings here
    assigned_modules: Optional[Dict[str, bool]] = None  # Module access control
    
    model_config = ConfigDict(from_attributes = True, use_enum_values=True)  # Added use_enum_values=True


class UserLogin(BaseModel):
    email: EmailStr
    password: str
    subdomain: Optional[str] = None  # For tenant-specific login


class Token(BaseModel):
    access_token: str
    token_type: str
    organization_id: Optional[int] = None
    organization_name: Optional[str] = None
    user_role: Optional[str] = None
    must_change_password: bool = False
    force_password_reset: bool = False
    is_first_login: bool = False
    company_details_completed: bool = True
    model_config = ConfigDict(use_enum_values=True)  # Added for enum serialization


class TokenData(BaseModel):
    email: Optional[str] = None
    organization_id: Optional[int] = None
    user_role: Optional[str] = None
    user_type: Optional[str] = None


# Platform User schemas - for SaaS platform-level users
class PlatformUserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    role: PlatformUserRole = PlatformUserRole.PLATFORM_ADMIN
    is_active: bool = True


class PlatformUserCreate(PlatformUserBase):
    password: str
    
    @field_validator('password')
    def validate_password(cls, v):
        is_strong, msg = cls.check_password_strength(v)
        if not is_strong:
            raise ValueError(msg)
        return v
    
    @staticmethod
    def check_password_strength(password: str) -> tuple[bool, str]:
        """Check password strength and return validation result"""
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"

        if not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"

        if not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"

        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one digit"

        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(c in special_chars for c in password):
            return False, "Password must contain at least one special character"

        return True, "Password is strong"


class PlatformUserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[PlatformUserRole] = None
    is_active: Optional[bool] = None


class PlatformUserInDB(PlatformUserBase):
    id: int
    force_password_reset: bool = False
    failed_login_attempts: int = 0
    locked_until: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes = True, use_enum_values=True)


# Password management schemas
class PasswordChangeRequest(BaseModel):
    current_password: Optional[str] = Field(None, description="Current password for verification")
    new_password: str = Field(..., description="New password to set")
    confirm_password: Optional[str] = Field(None, description="Confirm new password")
    
    @field_validator('new_password')
    def validate_password(cls, v):
        is_strong, msg = cls.check_password_strength(v)
        if not is_strong:
            raise ValueError(msg)
        return v
    
    @staticmethod
    def check_password_strength(password: str) -> tuple[bool, str]:
        """Check password strength and return validation result"""
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"

        if not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"

        if not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"

        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one digit"

        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(c in special_chars for c in password):
            return False, "Password must contain at least one special character"

        return True, "Password is strong"
    
    @field_validator('confirm_password')
    def validate_password_match(cls, v, info):
        if 'new_password' in info.data and v != info.data['new_password']:
            raise ValueError('Passwords do not match')
        return v
    
    model_config = ConfigDict(populate_by_name = True)


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class PasswordResetRequest(BaseModel):
    email: EmailStr
    otp: str
    new_password: str
    
    @field_validator('new_password')
    def validate_password(cls, v):
        is_strong, msg = cls.check_password_strength(v)
        if not is_strong:
            raise ValueError(msg)
        return v
    
    @staticmethod
    def check_password_strength(password: str) -> tuple[bool, str]:
        """Check password strength and return validation result"""
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"

        if not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"

        if not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"

        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one digit"

        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(c in special_chars for c in password):
            return False, "Password must contain at least one special character"

        return True, "Password is strong"


class PasswordChangeResponse(BaseModel):
    message: str
    access_token: Optional[str] = None  # New JWT token after password change
    token_type: str = "bearer"
    
    model_config = ConfigDict(from_attributes = True)


# Admin password reset schemas
class AdminPasswordResetRequest(BaseModel):
    user_email: EmailStr


class AdminPasswordResetResponse(BaseModel):
    message: str
    target_email: str
    new_password: str  # New password to display
    email_sent: bool
    email_error: Optional[str] = None
    must_change_password: bool = True


class BulkPasswordResetRequest(BaseModel):
    organization_id: Optional[int] = None  # None for all organizations


class BulkPasswordResetResponse(BaseModel):
    message: str
    total_users_reset: int
    organizations_affected: list
    failed_resets: list = []


# Temporary password schemas
class TemporaryPasswordRequest(BaseModel):
    target_email: EmailStr
    expires_hours: int = 24
    
    @field_validator('expires_hours')
    def validate_expires_hours(cls, v):
        if v < 1 or v > 168:  # Max 1 week
            raise ValueError('expires_hours must be between 1 and 168 (1 week)')
        return v


class TemporaryPasswordResponse(BaseModel):
    message: str
    target_email: str
    temporary_password: str
    expires_at: str
    force_password_reset: bool = True
    

# OTP schemas
class OTPRequest(BaseModel):
    email: EmailStr
    purpose: str = "login"  # login, password_reset
    phone_number: Optional[str] = None  # For WhatsApp OTP
    delivery_method: str = "auto"  # "auto" (WhatsApp preferred), "email", "whatsapp"


class OTPVerifyRequest(BaseModel):
    email: EmailStr
    otp: str
    purpose: str = "login"


class OTPResponse(BaseModel):
    message: str
    email: str
    delivery_method: Optional[str] = None  # Which method was actually used


# Master password schemas
class MasterPasswordLoginRequest(BaseModel):
    email: EmailStr
    master_password: str


class MasterPasswordLoginResponse(BaseModel):
    message: str
    access_token: str
    token_type: str = "bearer"
    force_password_reset: bool = True
    organization_id: Optional[int] = None
    user_role: str

class UserResponse(BaseModel):
    id: int
    organization_id: Optional[int]
    email: str
    full_name: Optional[str]
    role: str
    department: Optional[str]
    designation: Optional[str]
    employee_id: Optional[str]
    is_active: bool
    is_super_admin: bool
    phone: Optional[str]
    avatar_path: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    last_login: Optional[datetime]
    has_stock_access: bool
    assigned_modules: Optional[Dict[str, bool]] = None  # Module access control

    class Config:
        from_attributes = True

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    organization_id: Optional[int] = None
    organization_name: Optional[str] = None
    user_role: Optional[str] = None
    must_change_password: bool = False
    force_password_reset: bool = False
    is_first_login: bool = False
    company_details_completed: bool = True
    user: Union[UserResponse, PlatformUserInDB]

CurrentUser: TypeAlias = Union[UserInDB, PlatformUserInDB]