"""
OAuth2 and Email Token Management Models
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone, timedelta
from enum import Enum as PyEnum

from app.core.database import Base
from app.utils.crypto_aes_gcm import encrypt_aes_gcm, decrypt_aes_gcm, EncryptionKeysAESGCM


class OAuthProvider(PyEnum):
    GOOGLE = "GOOGLE"
    MICROSOFT = "MICROSOFT"
    OUTLOOK = "OUTLOOK"
    GMAIL = "GMAIL"


class TokenStatus(PyEnum):
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"
    REFRESH_FAILED = "REFRESH_FAILED"


class UserEmailToken(Base):
    """
    Encrypted storage for OAuth2 email tokens with automatic refresh capability
    """
    __tablename__ = "user_email_tokens"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    
    # User and organization associations
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True, index=True)
    
    # OAuth provider and account info
    provider = Column(Enum(OAuthProvider), nullable=False)
    email_address = Column(String(255), nullable=False, index=True)
    display_name = Column(String(255), nullable=True)
    
    # Encrypted OAuth tokens
    access_token_encrypted = Column(Text, nullable=False)
    refresh_token_encrypted = Column(Text, nullable=True)
    id_token_encrypted = Column(Text, nullable=True)
    
    # Token metadata
    scope = Column(Text, nullable=True)  # Space-separated list of granted scopes
    token_type = Column(String(50), default="Bearer", nullable=False)
    expires_at = Column(DateTime, nullable=True)
    status = Column(Enum(TokenStatus), default=TokenStatus.ACTIVE, nullable=False)
    
    # Provider-specific metadata
    provider_metadata = Column(JSON, nullable=True)  # Store provider-specific data
    
    # Sync settings
    sync_enabled = Column(Boolean, default=True, nullable=False)
    sync_folders = Column(JSON, nullable=True)  # Array of folder names to sync
    last_sync_at = Column(DateTime, nullable=True)
    last_sync_status = Column(String(50), nullable=True)
    last_sync_error = Column(Text, nullable=True)
    
    # Incremental sync tracking (restored from working commit c2fadf02)
    # These enable efficient delta/history-based sync instead of full sync every time
    last_history_id = Column(String(255), nullable=True, index=True)  # Gmail history API
    last_delta_token = Column(Text, nullable=True)  # Microsoft Graph delta queries
    
    # Security and audit
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_used_at = Column(DateTime, nullable=True)
    refresh_count = Column(Integer, default=0, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="email_tokens")
    organization = relationship("Organization", back_populates="email_tokens")
    
    # Properties for transparent access to encrypted tokens
    @property
    def access_token(self) -> str:
        """Get decrypted access token"""
        return decrypt_aes_gcm(self.access_token_encrypted, EncryptionKeysAESGCM.OAUTH) or ""
    
    @access_token.setter
    def access_token(self, value: str):
        """Set encrypted access token"""
        self.access_token_encrypted = encrypt_aes_gcm(value, EncryptionKeysAESGCM.OAUTH) if value else None
    
    @property
    def refresh_token(self) -> str:
        """Get decrypted refresh token"""
        return decrypt_aes_gcm(self.refresh_token_encrypted, EncryptionKeysAESGCM.OAUTH) or ""
    
    @refresh_token.setter
    def refresh_token(self, value: str):
        """Set encrypted refresh token"""
        self.refresh_token_encrypted = encrypt_aes_gcm(value, EncryptionKeysAESGCM.OAUTH) if value else None
    
    @property
    def id_token(self) -> str:
        """Get decrypted ID token"""
        return decrypt_aes_gcm(self.id_token_encrypted, EncryptionKeysAESGCM.OAUTH) or ""
    
    @id_token.setter
    def id_token(self, value: str):
        """Set encrypted ID token"""
        self.id_token_encrypted = encrypt_aes_gcm(value, EncryptionKeysAESGCM.OAUTH) if value else None
    
    def is_expired(self) -> bool:
        """Check if token is expired"""
        if not self.expires_at:
            return False
        # Use naive UTC comparison to match how expires_at is stored
        return datetime.utcnow() >= self.expires_at
    
    def is_active(self) -> bool:
        """Check if token is active and usable"""
        return (
            self.status == TokenStatus.ACTIVE and
            not self.is_expired() and
            bool(self.access_token)
        )


class OAuthState(Base):
    """
    Temporary storage for OAuth2 state during authorization flow
    """
    __tablename__ = "oauth_states"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    
    # State tracking
    state = Column(String(255), unique=True, nullable=False, index=True)
    provider = Column(Enum(OAuthProvider), nullable=False)
    
    # User context
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True, index=True)
    
    # Flow metadata
    redirect_uri = Column(String(500), nullable=True)
    scope = Column(Text, nullable=True)
    code_verifier = Column(String(255), nullable=True)  # For PKCE
    nonce = Column(String(255), nullable=True)  # For OpenID Connect
    
    # Expiry
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User")
    organization = relationship("Organization")
    
    def is_expired(self) -> bool:
        """Check if state is expired"""
        return datetime.utcnow() >= self.expires_at