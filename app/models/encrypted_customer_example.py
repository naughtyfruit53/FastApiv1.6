"""
Example model demonstrating field-level encryption for sensitive customer data
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.core.database import Base
from app.models.encrypted_fields import EncryptedCustomerData, EncryptedPII, EncryptedFinancial
from typing import Optional
from datetime import datetime


class EncryptedCustomerProfile(Base):
    """
    Example model showing how to use field-level encryption for sensitive customer data
    This demonstrates best practices for data privacy and compliance
    """
    __tablename__ = "encrypted_customer_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Non-encrypted business data (safe to store in plaintext)
    customer_id: Mapped[str] = mapped_column(String, nullable=False, index=True)  # Business identifier
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    customer_type: Mapped[str] = mapped_column(String, nullable=False, default="individual")  # individual, business
    
    # Encrypted PII data (Personal Identifiable Information)
    name_encrypted: Mapped[str] = mapped_column(EncryptedPII(), nullable=False)
    email_encrypted: Mapped[Optional[str]] = mapped_column(EncryptedPII(), nullable=True)
    phone_encrypted: Mapped[str] = mapped_column(EncryptedPII(), nullable=False)
    
    # Encrypted address information
    address_line1_encrypted: Mapped[str] = mapped_column(EncryptedCustomerData(), nullable=False)
    address_line2_encrypted: Mapped[Optional[str]] = mapped_column(EncryptedCustomerData(), nullable=True)
    city_encrypted: Mapped[str] = mapped_column(EncryptedCustomerData(), nullable=False)
    state_encrypted: Mapped[str] = mapped_column(EncryptedCustomerData(), nullable=False)
    zip_code_encrypted: Mapped[str] = mapped_column(EncryptedCustomerData(), nullable=False)
    
    # Encrypted financial information
    payment_terms_encrypted: Mapped[Optional[str]] = mapped_column(EncryptedFinancial(), nullable=True)
    credit_limit_encrypted: Mapped[Optional[str]] = mapped_column(EncryptedFinancial(), nullable=True)
    tax_id_encrypted: Mapped[Optional[str]] = mapped_column(EncryptedFinancial(), nullable=True)
    bank_details_encrypted: Mapped[Optional[str]] = mapped_column(EncryptedFinancial(), nullable=True)  # JSON string
    
    # Privacy and compliance metadata
    consent_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    data_retention_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    gdpr_consent: Mapped[bool] = mapped_column(Boolean, default=False)
    marketing_consent: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Audit fields
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    last_accessed: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Properties for transparent encryption/decryption
    @property
    def name(self) -> str:
        """Get decrypted customer name"""
        return self.name_encrypted or ""
    
    @name.setter 
    def name(self, value: str):
        """Set encrypted customer name"""
        self.name_encrypted = value
    
    @property
    def email(self) -> Optional[str]:
        """Get decrypted email"""
        return self.email_encrypted
    
    @email.setter
    def email(self, value: Optional[str]):
        """Set encrypted email"""
        self.email_encrypted = value
    
    @property 
    def phone(self) -> str:
        """Get decrypted phone"""
        return self.phone_encrypted or ""
    
    @phone.setter
    def phone(self, value: str):
        """Set encrypted phone"""
        self.phone_encrypted = value
    
    @property
    def address(self) -> dict:
        """Get decrypted address as dictionary"""
        return {
            "line1": self.address_line1_encrypted or "",
            "line2": self.address_line2_encrypted or "",
            "city": self.city_encrypted or "",
            "state": self.state_encrypted or "",
            "zip_code": self.zip_code_encrypted or ""
        }
    
    @address.setter
    def address(self, value: dict):
        """Set encrypted address from dictionary"""
        self.address_line1_encrypted = value.get("line1", "")
        self.address_line2_encrypted = value.get("line2")
        self.city_encrypted = value.get("city", "")
        self.state_encrypted = value.get("state", "")
        self.zip_code_encrypted = value.get("zip_code", "")
    
    def update_last_accessed(self):
        """Update last accessed timestamp for compliance tracking"""
        self.last_accessed = datetime.utcnow()
    
    def can_be_deleted(self) -> bool:
        """Check if customer data can be deleted based on retention policy"""
        if not self.data_retention_until:
            return False
        return datetime.utcnow() >= self.data_retention_until
    
    def anonymize_data(self):
        """Anonymize customer data for GDPR compliance"""
        self.name_encrypted = "[ANONYMIZED]"
        self.email_encrypted = "[ANONYMIZED]"
        self.phone_encrypted = "[ANONYMIZED]"
        self.address_line1_encrypted = "[ANONYMIZED]"
        self.address_line2_encrypted = "[ANONYMIZED]"
        self.city_encrypted = "[ANONYMIZED]" 
        self.state_encrypted = "[ANONYMIZED]"
        self.zip_code_encrypted = "[ANONYMIZED]"
        self.payment_terms_encrypted = "[ANONYMIZED]"
        self.credit_limit_encrypted = "[ANONYMIZED]"
        self.tax_id_encrypted = "[ANONYMIZED]"
        self.bank_details_encrypted = "[ANONYMIZED]"