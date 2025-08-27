import os
from typing import Any, Dict, Optional, List
from pydantic_settings import BaseSettings, SettingsConfigDict  # Use pydantic-settings for env loading
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

class Settings(BaseSettings):
    # App Settings
    PROJECT_NAME: str = "TRITIQ ERP API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "FastAPI migration of PySide6 ERP application"
    API_V1_STR: str = "/api"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    # JWT Token Expiry: minimum 120 minutes (2 hours), maximum 300 minutes (5 hours)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 180  # Default 3 hours, within required range
    
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
    DATABASE_URL: Optional[str] = None
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None
    SUPABASE_SERVICE_KEY: Optional[str] = None
    SUPABASE_JWT_SECRET: Optional[str] = None
    
    # Email Settings (SMTP)
    SMTP_HOST: str = "smtp.gmail.com"  # Changed back to SMTP_HOST to match .env
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None  # Gmail or SMTP user email
    SMTP_PASSWORD: Optional[str] = None  # Gmail app password or SMTP password  
    EMAILS_FROM_EMAIL: Optional[str] = None  # Sender email (same as SMTP_USERNAME)
    EMAILS_FROM_NAME: str = "TRITIQ ERP"
    
    # SendGrid (Alternative email service)
    SENDGRID_API_KEY: Optional[str] = None

    # Brevo (Sendinblue) Email Service - Primary
    BREVO_API_KEY: Optional[str] = None
    BREVO_FROM_EMAIL: Optional[str] = None
    BREVO_FROM_NAME: str = "TRITIQ ERP"
    
    # Redis (for caching and task queue)
    REDIS_URL: str = "redis://localhost:6379"
    
    # File Storage
    UPLOAD_FOLDER: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # Cors
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:8080"
    ]
    
    # Super Admin Configuration
    SUPER_ADMIN_EMAILS: List[str] = ["admin@tritiq.com", "superadmin@tritiq.com", "naughtyfruit53@gmail.com"]
    
    @classmethod
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    @property
    def jwt_secret(self) -> str:
        """
        Get JWT secret for token operations.
        Uses SUPABASE_JWT_SECRET if available, otherwise falls back to SECRET_KEY.
        """
        value = self.SUPABASE_JWT_SECRET or self.SECRET_KEY
        print(f"DEBUG: Loaded jwt_secret = {value}")  # Debug print for troubleshooting
        return value
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding='utf-8',
        case_sensitive=True,
        extra='ignore'  # Ignore extra fields in .env to prevent validation errors
    )

settings = Settings()