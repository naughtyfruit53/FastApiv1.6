"""
Field-level encryption utilities for sensitive data
"""
import os
from typing import Optional, Any
from cryptography.fernet import Fernet
import base64
import logging

logger = logging.getLogger(__name__)


class FieldEncryption:
    """
    Field-level encryption for sensitive data using Fernet symmetric encryption
    """
    
    def __init__(self, key_id: str = "default"):
        """
        Initialize encryption with key from environment or vault
        """
        self.key_id = key_id
        self._cipher = None
        self._load_key()
    
    def _load_key(self):
        """
        Load encryption key from environment variables
        Never store keys in code!
        """
        # Try to get key from environment
        key_env_var = f"ENCRYPTION_KEY_{self.key_id.upper()}"
        key_b64 = os.getenv(key_env_var)
        
        if not key_b64:
            # For development only - generate a key if none exists
            if os.getenv("ENVIRONMENT") == "development":
                logger.warning(f"No encryption key found for {self.key_id}. Generating development key.")
                key = Fernet.generate_key()
                key_b64 = base64.b64encode(key).decode()
                os.environ[key_env_var] = key_b64
                logger.warning(f"Set {key_env_var} environment variable: {key_b64}")
            else:
                raise ValueError(f"Encryption key not found for {self.key_id}. Set {key_env_var} environment variable.")
        
        try:
            key = base64.b64decode(key_b64.encode())
            self._cipher = Fernet(key)
        except Exception as e:
            raise ValueError(f"Invalid encryption key for {self.key_id}: {e}")
    
    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt a string value
        """
        if not plaintext:
            return ""
        
        try:
            encrypted_bytes = self._cipher.encrypt(plaintext.encode('utf-8'))
            return base64.b64encode(encrypted_bytes).decode('utf-8')
        except Exception as e:
            logger.error(f"Encryption failed for key_id {self.key_id}: {e}")
            raise ValueError(f"Encryption failed: {e}")
    
    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt a string value
        """
        if not ciphertext:
            return ""
        
        try:
            encrypted_bytes = base64.b64decode(ciphertext.encode('utf-8'))
            decrypted_bytes = self._cipher.decrypt(encrypted_bytes)
            return decrypted_bytes.decode('utf-8')
        except Exception as e:
            logger.error(f"Decryption failed for key_id {self.key_id}: {e}")
            raise ValueError(f"Decryption failed: {e}")


# Global encryption instances for different data types
_encryption_instances = {}

def get_encryption_instance(key_id: str = "default") -> FieldEncryption:
    """
    Get or create encryption instance for a specific key ID
    """
    if key_id not in _encryption_instances:
        _encryption_instances[key_id] = FieldEncryption(key_id)
    return _encryption_instances[key_id]


def encrypt_field(value: str, key_id: str = "default") -> str:
    """
    Encrypt a field value
    """
    return get_encryption_instance(key_id).encrypt(value)


def decrypt_field(value: str, key_id: str = "default") -> str:
    """
    Decrypt a field value
    """
    return get_encryption_instance(key_id).decrypt(value)


# Predefined key IDs for different types of sensitive data
class EncryptionKeys:
    """
    Predefined encryption key IDs for different data types
    """
    PII = "pii"              # Personal Identifiable Information
    FINANCIAL = "financial"  # Financial data
    CUSTOMER = "customer"    # Customer sensitive data
    EMPLOYEE = "employee"    # Employee sensitive data
    DEFAULT = "default"      # Default encryption key