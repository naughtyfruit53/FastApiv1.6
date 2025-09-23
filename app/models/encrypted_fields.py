"""
Encrypted field types for SQLAlchemy models
"""
from typing import Optional
from sqlalchemy import TypeDecorator, String
from sqlalchemy.dialects import postgresql
from app.utils.encryption import encrypt_field, decrypt_field, EncryptionKeys
import logging

logger = logging.getLogger(__name__)

class EncryptedString(TypeDecorator):
    """
    SQLAlchemy custom type for encrypted string fields
    """
    impl = String
    cache_ok = True
    
    def __init__(self, key_id: str = EncryptionKeys.DEFAULT, *args, **kwargs):
        self.key_id = key_id
        super().__init__(*args, **kwargs)
    
    def process_bind_param(self, value: Optional[str], dialect) -> Optional[str]:
        """
        Encrypt value before storing in database
        """
        if value is None:
            return None
        if isinstance(value, str) and value.strip():
            return encrypt_field(value, self.key_id)
        return value
    
    def process_result_value(self, value: Optional[str], dialect) -> Optional[str]:
        """
        Decrypt value when reading from database
        """
        if value is None:
            return None
        if isinstance(value, str) and value.strip():
            try:
                return decrypt_field(value, self.key_id)
            except Exception as e:
                # Log decryption failure
                logger.error(f"Decryption failed for key_id {self.key_id}: {str(e)}")
                # Return original value as fallback
                return value
        return value


class EncryptedPII(EncryptedString):
    """
    Encrypted field for Personal Identifiable Information
    """
    def __init__(self, *args, **kwargs):
        super().__init__(key_id=EncryptionKeys.PII, *args, **kwargs)


class EncryptedFinancial(EncryptedString):
    """
    Encrypted field for Financial data
    """
    def __init__(self, *args, **kwargs):
        super().__init__(key_id=EncryptionKeys.FINANCIAL, *args, **kwargs)


class EncryptedCustomerData(EncryptedString):
    """
    Encrypted field for Customer sensitive data
    """
    def __init__(self, *args, **kwargs):
        super().__init__(key_id=EncryptionKeys.CUSTOMER, *args, **kwargs)


class EncryptedEmployeeData(EncryptedString):
    """
    Encrypted field for Employee sensitive data
    """
    def __init__(self, *args, **kwargs):
        super().__init__(key_id=EncryptionKeys.EMPLOYEE, *args, **kwargs)