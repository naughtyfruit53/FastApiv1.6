# app/core/config.py

"""
Application configuration
"""

import os
from typing import Any, Dict, Optional, List
from dotenv import load_dotenv
import logging
import platform

logger = logging.getLogger(__name__)

# Ensure .env file is loaded
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
env_path = os.path.join(project_root, '.env')

logger.debug(f"Calculated project_root: {project_root}")
logger.debug(f"Calculated env_path: {env_path}")
logger.debug(f".env exists: {os.path.exists(env_path)}")

load_dotenv(env_path)
logger.info(f"Loaded .env from: {env_path}")

def assemble_cors_origins(v: str | List[str]) -> List[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, (list, str)):
        return v
    raise ValueError(v)

class Settings:
    PROJECT_NAME: str = "TRITIQ BOS API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "FastAPI migration of PySide6 ERP application"
    API_V1_STR: str = "/api"
    
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 1440
    
    @classmethod
    def validate_token_expiry(cls, v: int) -> int:
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
    
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")
    SESSION_DATABASE_URL: Optional[str] = os.getenv("SESSION_DATABASE_URL", DATABASE_URL)
    SUPABASE_URL: Optional[str] = os.getenv("SUPABASE_URL")
    SUPABASE_KEY: Optional[str] = os.getenv("SUPABASE_KEY")
    SUPABASE_SERVICE_KEY: Optional[str] = os.getenv("SUPABASE_SERVICE_KEY")
    SUPABASE_JWT_SECRET: Optional[str] = os.getenv("SUPABASE_JWT_SECRET")
    
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: Optional[str] = os.getenv("SMTP_USERNAME")
    SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD")
    EMAILS_FROM_EMAIL: Optional[str] = os.getenv("EMAILS_FROM_EMAIL")
    EMAILS_FROM_NAME: str = os.getenv("EMAILS_FROM_NAME", "TRITIQ BOS")
    
    SENDGRID_API_KEY: Optional[str] = os.getenv("SENDGRID_API_KEY")

    BREVO_API_KEY: Optional[str] = os.getenv("BREVO_API_KEY")
    BREVO_FROM_EMAIL: Optional[str] = os.getenv("BREVO_FROM_EMAIL")
    BREVO_FROM_NAME: str = os.getenv("BREVO_FROM_NAME", "TRITIQ BOS")
    
    WHATSAPP_ENABLED: bool = os.getenv("WHATSAPP_ENABLED", "false").lower() == "true"
    WHATSAPP_PROVIDER: str = os.getenv("WHATSAPP_PROVIDER", "none") if os.getenv("WHATSAPP_ENABLED", "false").lower() == "true" else "none"
    WHATSAPP_SENDER_NUMBER: Optional[str] = os.getenv("WHATSAPP_SENDER_NUMBER") if os.getenv("WHATSAPP_ENABLED", "false").lower() == "true" else None
    WHATSAPP_OTP_TEMPLATE_ID: Optional[str] = os.getenv("WHATSAPP_OTP_TEMPLATE_ID") if os.getenv("WHATSAPP_ENABLED", "false").lower() == "true" else None
    
    @property
    def is_brevo_whatsapp_configured(self) -> bool:
        if not self.WHATSAPP_ENABLED:
            logger.debug("WhatsApp integration is disabled (WHATSAPP_ENABLED=false)")
            return False
        if self.WHATSAPP_PROVIDER != "brevo":
            logger.debug(f"WhatsApp provider is set to {self.WHATSAPP_PROVIDER}, skipping Brevo configuration check")
            return False
        configured = all([self.BREVO_API_KEY, self.WHATSAPP_SENDER_NUMBER, self.WHATSAPP_OTP_TEMPLATE_ID])
        if not configured:
            logger.warning("Brevo WhatsApp configuration incomplete: Missing one or more of BREVO_API_KEY, WHATSAPP_SENDER_NUMBER, WHATSAPP_OTP_TEMPLATE_ID. WhatsApp features disabled.")
            return False
        logger.info("Brevo WhatsApp configuration validated successfully")
        return True
    
    GOOGLE_CLIENT_ID: Optional[str] = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: Optional[str] = os.getenv("GOOGLE_CLIENT_SECRET", "")
    
    MICROSOFT_CLIENT_ID: Optional[str] = os.getenv("MICROSOFT_CLIENT_ID", "")
    MICROSOFT_CLIENT_SECRET: Optional[str] = os.getenv("MICROSOFT_CLIENT_SECRET", "")
    MICROSOFT_TENANT_ID: Optional[str] = os.getenv("MICROSOFT_TENANT_ID", "common")
    
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    OAUTH_REDIRECT_URI: str = os.getenv("OAUTH_REDIRECT_URI", "https://naughtyfruit.in/auth/callback" if ENVIRONMENT == "production" else "http://localhost:3000/auth/callback")
    
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    UPLOAD_FOLDER: str = os.getenv("UPLOAD_FOLDER", "uploads")
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "5242880"))  # 5MB to match pdf_extraction.py
    
    BACKEND_CORS_ORIGINS: List[str] = assemble_cors_origins(os.getenv("BACKEND_CORS_ORIGINS", "https://tritiqbusinesssuite.vercel.app,https://www.naughtyfruit.in,https://naughtyfruit.in,http://localhost:3000,http://127.0.0.1:3000"))
    
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    
    # Auth transport options for development
    # When enabled, auth can return tokens in cookies (Secure=False, SameSite=Lax)
    # Production always uses Secure=True, SameSite=None over HTTPS
    AUTH_COOKIE_DEV: bool = os.getenv("AUTH_COOKIE_DEV", "false").lower() == "true"
    
    WKHTMLTOPDF_PATH: str = os.getenv("WKHTMLTOPDF_PATH", "/usr/bin/wkhtmltopdf")
    logger.info(f"wkhtmltopdf path configured: {WKHTMLTOPDF_PATH} (exists: {os.path.exists(WKHTMLTOPDF_PATH)})")
    
    FASTGST_API_URL: str = os.getenv("FASTGST_API_URL", "https://api.fastgst.in")
    
    # SNAPPYMAIL_URL removed - SnappyMail integration discontinued
    
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "https://naughtyfruit.in")
    
    RAPIDAPI_KEY: Optional[str] = os.getenv("RAPIDAPI_KEY")
    
    SCHEMA_CACHE_DIR: str = os.getenv("SCHEMA_CACHE_DIR", "./cache")
    
    @property
    def jwt_secret(self) -> str:
        value = self.SUPABASE_JWT_SECRET or self.SECRET_KEY
        logger.debug(f"Loaded jwt_secret = {value}")
        return value

# Ensure settings is initialized
try:
    settings = Settings()
except Exception as e:
    logger.error(f"Failed to initialize settings: {str(e)}")
    raise