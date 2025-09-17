# app/core/config.py

import os
from typing import Any, Dict, Optional, List
from dotenv import load_dotenv  # Explicitly load .env (optional, as BaseSettings handles it)
import logging

logger = logging.getLogger(__name__)

# Explicitly load .env file from project root (optional, but kept for consistency)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
env_path = os.path.join(project_root, '.env')

# Debug prints
print(f"DEBUG: Calculated project_root: {project_root}")
print(f"DEBUG: Calculated env_path: {env_path}")
print(f"DEBUG: .env exists: {os.path.exists(env_path)}")

load_dotenv(env_path)
logger.info(f"Loaded .env from: {env_path}")

def assemble_cors_origins(v: str | List[str]) -> List[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, (list, str)):
        return v
    raise ValueError(v)

class Settings:
    # App Settings
    PROJECT_NAME: str = "TRITIQ ERP API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "FastAPI migration of PySide6 ERP application"
    API_V1_STR: str = "/api"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    # JWT Token Expiry: minimum 120 minutes (2 hours), maximum 300 minutes (5 hours)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "180"))  # Default 3 hours, within required range
    REFRESH_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES", "1440"))  # Default 24 hours
    
    @classmethod
    def validate_token_expiry(cls, v: int) -> int:
        """Validate JWT token expiry is within required range (120-300 minutes)"""
        if not isinstance(v, int):
            try:
                v = int(v)
            except (TypeError, ValueError):
                raise ValueError("ACCESS_TOKEN_EXPIRE_MINUTES must be an integer")
        
        if v < 120:
            raise ValueError("ACCESS_TOKEN_EXPIRE_MINUTES must be at least 120 minutes (2 hours)")
        if v > 300:
            raise ValueError("ACCESS_TOKEN_EXPIRE_MINUTES must not exceed 300 minutes (5 hours)")
        
        return v
    
    # Database (Supabase PostgreSQL)
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")
    SESSION_DATABASE_URL: Optional[str] = os.getenv("SESSION_DATABASE_URL", DATABASE_URL)  # Fallback to DATABASE_URL
    SUPABASE_URL: Optional[str] = os.getenv("SUPABASE_URL")
    SUPABASE_KEY: Optional[str] = os.getenv("SUPABASE_KEY")
    SUPABASE_SERVICE_KEY: Optional[str] = os.getenv("SUPABASE_SERVICE_KEY")
    SUPABASE_JWT_SECRET: Optional[str] = os.getenv("SUPABASE_JWT_SECRET")
    
    # Email Settings (SMTP)
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: Optional[str] = os.getenv("SMTP_USERNAME")
    SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD")
    EMAILS_FROM_EMAIL: Optional[str] = os.getenv("EMAILS_FROM_EMAIL")
    EMAILS_FROM_NAME: str = os.getenv("EMAILS_FROM_NAME", "TRITIQ ERP")
    
    # SendGrid (Alternative email service)
    SENDGRID_API_KEY: Optional[str] = os.getenv("SENDGRID_API_KEY")

    # Brevo (Sendinblue) Email Service - Primary
    BREVO_API_KEY: Optional[str] = os.getenv("BREVO_API_KEY")
    BREVO_FROM_EMAIL: Optional[str] = os.getenv("BREVO_FROM_EMAIL")
    BREVO_FROM_NAME: str = os.getenv("BREVO_FROM_NAME", "TRITIQ ERP")
    
    # WhatsApp OTP Configuration
    WHATSAPP_PROVIDER: Optional[str] = os.getenv("WHATSAPP_PROVIDER", "brevo")
    WHATSAPP_SENDER_NUMBER: Optional[str] = os.getenv("WHATSAPP_SENDER_NUMBER")
    WHATSAPP_OTP_TEMPLATE_ID: Optional[str] = os.getenv("WHATSAPP_OTP_TEMPLATE_ID")
    
    # OAuth2 Configuration
    # Google OAuth2
    GOOGLE_CLIENT_ID: Optional[str] = os.getenv("GOOGLE_CLIENT_ID") or ""
    GOOGLE_CLIENT_SECRET: Optional[str] = os.getenv("GOOGLE_CLIENT_SECRET") or ""
    
    # Microsoft OAuth2
    MICROSOFT_CLIENT_ID: Optional[str] = os.getenv("MICROSOFT_CLIENT_ID") or ""
    MICROSOFT_CLIENT_SECRET: Optional[str] = os.getenv("MICROSOFT_CLIENT_SECRET") or ""
    MICROSOFT_TENANT_ID: Optional[str] = os.getenv("MICROSOFT_TENANT_ID", "common")
    
    # OAuth2 Redirect URIs
    OAUTH_REDIRECT_URI: str = os.getenv("OAUTH_REDIRECT_URI", "http://localhost:3000/auth/callback")
    
    # Redis (for caching and task queue)
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # File Storage
    UPLOAD_FOLDER: str = os.getenv("UPLOAD_FOLDER", "uploads")
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB
    
    # Cors
    BACKEND_CORS_ORIGINS: List[str] = assemble_cors_origins(os.getenv("BACKEND_CORS_ORIGINS", "http://localhost:3000,http://localhost:8080,http://127.0.0.1:3000,http://127.0.0.1:8000,http://127.0.0.1:8080"))
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    
    # wkhtmltopdf path (dynamic for local Windows vs. deployment Linux)
    WKHTMLTOPDF_PATH: str = os.getenv("WKHTMLTOPDF_PATH", "/usr/bin/wkhtmltopdf")
    
    # FastGST API URL (for HSN/GST lookup)
    FASTGST_API_URL: str = os.getenv("FASTGST_API_URL", "https://api.fastgst.in")
    
    @property
    def jwt_secret(self) -> str:
        """
        Get JWT secret for token operations.
        Uses SUPABASE_JWT_SECRET if available, otherwise falls back to SECRET_KEY.
        """
        value = self.SUPABASE_JWT_SECRET or self.SECRET_KEY
        print(f"DEBUG: Loaded jwt_secret = {value}")  # Debug print for troubleshooting
        return value

settings = Settings()