"""
AES-GCM encryption utilities for OAuth tokens and sensitive data
Provides stronger encryption than Fernet with authenticated encryption
"""
import os
import base64
import logging
from typing import Optional
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2

logger = logging.getLogger(__name__)


class AESGCMEncryption:
    """
    AES-GCM authenticated encryption for sensitive data
    Provides confidentiality and integrity protection
    """
    
    def __init__(self, key_id: str = "oauth"):
        """
        Initialize AES-GCM encryption with key from environment
        """
        self.key_id = key_id
        self._cipher = None
        self._load_key()
    
    def _load_key(self):
        """
        Load encryption key from environment variables
        """
        key_env_var = f"ENCRYPTION_KEY_{self.key_id.upper()}_AES_GCM"
        key_b64 = os.getenv(key_env_var)
        
        if not key_b64:
            # For development - generate a key if none exists
            if os.getenv("ENVIRONMENT") == "development":
                logger.warning(f"No AES-GCM encryption key found for {self.key_id}. Generating development key.")
                # Generate 256-bit key
                key = AESGCM.generate_key(bit_length=256)
                key_b64 = base64.b64encode(key).decode()
                os.environ[key_env_var] = key_b64
                logger.warning(f"Set {key_env_var} environment variable: {key_b64}")
            else:
                raise ValueError(f"AES-GCM encryption key not found for {self.key_id}. Set {key_env_var} environment variable.")
        
        try:
            key = base64.b64decode(key_b64.encode())
            if len(key) not in [16, 24, 32]:  # 128, 192, or 256 bits
                raise ValueError(f"Invalid key length: {len(key)} bytes. Must be 16, 24, or 32 bytes.")
            self._cipher = AESGCM(key)
        except Exception as e:
            raise ValueError(f"Invalid AES-GCM encryption key for {self.key_id}: {e}")
    
    def encrypt(self, plaintext: str, associated_data: Optional[str] = None) -> str:
        """
        Encrypt a string value with AES-GCM
        
        Args:
            plaintext: String to encrypt
            associated_data: Optional additional authenticated data (AAD)
        
        Returns:
            Base64-encoded encrypted data (nonce + ciphertext + tag)
        """
        if not plaintext:
            return ""
        
        try:
            # Generate a random 96-bit nonce (12 bytes is recommended for GCM)
            nonce = os.urandom(12)
            
            # Convert to bytes
            plaintext_bytes = plaintext.encode('utf-8')
            aad = associated_data.encode('utf-8') if associated_data else None
            
            # Encrypt
            ciphertext = self._cipher.encrypt(nonce, plaintext_bytes, aad)
            
            # Combine nonce + ciphertext (ciphertext already includes auth tag)
            encrypted_data = nonce + ciphertext
            
            # Return base64 encoded
            return base64.b64encode(encrypted_data).decode('utf-8')
        except Exception as e:
            logger.error(f"AES-GCM encryption failed for key_id {self.key_id}: {e}")
            raise ValueError(f"Encryption failed: {e}")
    
    def decrypt(self, ciphertext: str, associated_data: Optional[str] = None) -> str:
        """
        Decrypt a string value encrypted with AES-GCM
        
        Args:
            ciphertext: Base64-encoded encrypted data
            associated_data: Optional additional authenticated data (must match encryption)
        
        Returns:
            Decrypted plaintext string
        """
        if not ciphertext:
            return ""
        
        try:
            # Decode from base64
            encrypted_data = base64.b64decode(ciphertext.encode('utf-8'))
            
            # Extract nonce (first 12 bytes) and ciphertext (rest)
            nonce = encrypted_data[:12]
            ciphertext_bytes = encrypted_data[12:]
            
            # Convert AAD to bytes if provided
            aad = associated_data.encode('utf-8') if associated_data else None
            
            # Decrypt and verify
            plaintext_bytes = self._cipher.decrypt(nonce, ciphertext_bytes, aad)
            
            return plaintext_bytes.decode('utf-8')
        except Exception as e:
            logger.error(f"AES-GCM decryption failed for key_id {self.key_id}: {e}")
            raise ValueError(f"Decryption failed: {e}")
    
    def encrypt_bytes(self, plain_bytes: bytes, associated_data: Optional[bytes] = None) -> bytes:
        """
        Encrypt binary data with AES-GCM
        
        Args:
            plain_bytes: Bytes to encrypt
            associated_data: Optional additional authenticated data (AAD)
        
        Returns:
            Encrypted data (nonce + ciphertext + tag)
        """
        if not plain_bytes:
            return b""
        
        try:
            # Generate a random 96-bit nonce
            nonce = os.urandom(12)
            
            # Encrypt
            ciphertext = self._cipher.encrypt(nonce, plain_bytes, associated_data)
            
            # Combine nonce + ciphertext
            return nonce + ciphertext
        except Exception as e:
            logger.error(f"AES-GCM binary encryption failed for key_id {self.key_id}: {e}")
            raise ValueError(f"Binary encryption failed: {e}")
    
    def decrypt_bytes(self, encrypted_bytes: bytes, associated_data: Optional[bytes] = None) -> bytes:
        """
        Decrypt binary data encrypted with AES-GCM
        
        Args:
            encrypted_bytes: Encrypted data
            associated_data: Optional additional authenticated data (must match encryption)
        
        Returns:
            Decrypted bytes
        """
        if not encrypted_bytes:
            return b""
        
        try:
            # Extract nonce (first 12 bytes) and ciphertext (rest)
            nonce = encrypted_bytes[:12]
            ciphertext = encrypted_bytes[12:]
            
            # Decrypt and verify
            return self._cipher.decrypt(nonce, ciphertext, associated_data)
        except Exception as e:
            logger.error(f"AES-GCM binary decryption failed for key_id {self.key_id}: {e}")
            raise ValueError(f"Binary decryption failed: {e}")


# Global encryption instances
_aes_gcm_instances = {}


def get_aes_gcm_instance(key_id: str = "oauth") -> AESGCMEncryption:
    """
    Get or create AES-GCM encryption instance for a specific key ID
    """
    if key_id not in _aes_gcm_instances:
        _aes_gcm_instances[key_id] = AESGCMEncryption(key_id)
    return _aes_gcm_instances[key_id]


def encrypt_aes_gcm(value: str, key_id: str = "oauth", aad: Optional[str] = None) -> str:
    """
    Encrypt a field value using AES-GCM
    """
    return get_aes_gcm_instance(key_id).encrypt(value, aad)


def decrypt_aes_gcm(value: str, key_id: str = "oauth", aad: Optional[str] = None) -> str:
    """
    Decrypt a field value using AES-GCM
    """
    return get_aes_gcm_instance(key_id).decrypt(value, aad)


def encrypt_bytes_aes_gcm(plain_bytes: bytes, key_id: str = "oauth", aad: Optional[bytes] = None) -> bytes:
    """
    Encrypt binary data using AES-GCM
    """
    return get_aes_gcm_instance(key_id).encrypt_bytes(plain_bytes, aad)


def decrypt_bytes_aes_gcm(encrypted_bytes: bytes, key_id: str = "oauth", aad: Optional[bytes] = None) -> bytes:
    """
    Decrypt binary data using AES-GCM
    """
    return get_aes_gcm_instance(key_id).decrypt_bytes(encrypted_bytes, aad)


class EncryptionKeysAESGCM:
    """
    Predefined AES-GCM encryption key IDs for different data types
    """
    OAUTH = "oauth"          # OAuth tokens
    OAUTH_REFRESH = "oauth_refresh"  # Refresh tokens (separate key)
    API_KEYS = "api_keys"    # API keys and secrets
    DEFAULT = "oauth"        # Default encryption key
