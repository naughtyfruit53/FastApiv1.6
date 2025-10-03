"""
Tests for AES-GCM encryption utilities
"""
import pytest
import os
from app.utils.crypto_aes_gcm import (
    AESGCMEncryption,
    encrypt_aes_gcm,
    decrypt_aes_gcm,
    encrypt_bytes_aes_gcm,
    decrypt_bytes_aes_gcm,
    EncryptionKeysAESGCM
)


class TestAESGCMEncryption:
    """Test AES-GCM encryption functionality"""
    
    def test_encrypt_decrypt_string(self):
        """Test basic string encryption and decryption"""
        # Set development environment
        os.environ["ENVIRONMENT"] = "development"
        
        # Create encryption instance
        crypto = AESGCMEncryption("test")
        
        # Test data
        plaintext = "This is a test secret"
        
        # Encrypt
        ciphertext = crypto.encrypt(plaintext)
        assert ciphertext != plaintext
        assert len(ciphertext) > 0
        
        # Decrypt
        decrypted = crypto.decrypt(ciphertext)
        assert decrypted == plaintext
    
    def test_encrypt_decrypt_with_aad(self):
        """Test encryption with Additional Authenticated Data (AAD)"""
        os.environ["ENVIRONMENT"] = "development"
        crypto = AESGCMEncryption("test")
        
        plaintext = "Secret data"
        aad = "user_id:123"
        
        # Encrypt with AAD
        ciphertext = crypto.encrypt(plaintext, associated_data=aad)
        
        # Decrypt with correct AAD
        decrypted = crypto.decrypt(ciphertext, associated_data=aad)
        assert decrypted == plaintext
        
        # Decryption with wrong AAD should fail
        with pytest.raises(ValueError):
            crypto.decrypt(ciphertext, associated_data="wrong_aad")
    
    def test_encrypt_empty_string(self):
        """Test encrypting empty string"""
        os.environ["ENVIRONMENT"] = "development"
        crypto = AESGCMEncryption("test")
        
        encrypted = crypto.encrypt("")
        assert encrypted == ""
        
        decrypted = crypto.decrypt("")
        assert decrypted == ""
    
    def test_encrypt_decrypt_bytes(self):
        """Test binary data encryption"""
        os.environ["ENVIRONMENT"] = "development"
        crypto = AESGCMEncryption("test")
        
        plaintext_bytes = b"Binary secret data \x00\x01\x02"
        
        # Encrypt
        encrypted_bytes = crypto.encrypt_bytes(plaintext_bytes)
        assert encrypted_bytes != plaintext_bytes
        assert len(encrypted_bytes) > len(plaintext_bytes)
        
        # Decrypt
        decrypted_bytes = crypto.decrypt_bytes(encrypted_bytes)
        assert decrypted_bytes == plaintext_bytes
    
    def test_encrypt_bytes_with_aad(self):
        """Test binary encryption with AAD"""
        os.environ["ENVIRONMENT"] = "development"
        crypto = AESGCMEncryption("test")
        
        plaintext_bytes = b"Binary secret"
        aad_bytes = b"context_data"
        
        # Encrypt with AAD
        encrypted = crypto.encrypt_bytes(plaintext_bytes, associated_data=aad_bytes)
        
        # Decrypt with correct AAD
        decrypted = crypto.decrypt_bytes(encrypted, associated_data=aad_bytes)
        assert decrypted == plaintext_bytes
        
        # Decryption with wrong AAD should fail
        with pytest.raises(ValueError):
            crypto.decrypt_bytes(encrypted, associated_data=b"wrong_aad")
    
    def test_different_nonces_produce_different_ciphertext(self):
        """Test that same plaintext produces different ciphertext (due to random nonce)"""
        os.environ["ENVIRONMENT"] = "development"
        crypto = AESGCMEncryption("test")
        
        plaintext = "Same secret data"
        
        # Encrypt twice
        ciphertext1 = crypto.encrypt(plaintext)
        ciphertext2 = crypto.encrypt(plaintext)
        
        # Ciphertexts should be different (different nonces)
        assert ciphertext1 != ciphertext2
        
        # But both should decrypt to same plaintext
        assert crypto.decrypt(ciphertext1) == plaintext
        assert crypto.decrypt(ciphertext2) == plaintext
    
    def test_tampered_ciphertext_fails(self):
        """Test that tampered ciphertext is detected"""
        os.environ["ENVIRONMENT"] = "development"
        crypto = AESGCMEncryption("test")
        
        plaintext = "Secret data"
        ciphertext = crypto.encrypt(plaintext)
        
        # Tamper with ciphertext (change one character)
        tampered = ciphertext[:-1] + ('B' if ciphertext[-1] == 'A' else 'A')
        
        # Decryption should fail
        with pytest.raises(ValueError):
            crypto.decrypt(tampered)
    
    def test_helper_functions(self):
        """Test convenience helper functions"""
        os.environ["ENVIRONMENT"] = "development"
        
        plaintext = "Test secret"
        
        # Encrypt using helper
        ciphertext = encrypt_aes_gcm(plaintext, key_id="test")
        assert len(ciphertext) > 0
        
        # Decrypt using helper
        decrypted = decrypt_aes_gcm(ciphertext, key_id="test")
        assert decrypted == plaintext
    
    def test_helper_functions_with_aad(self):
        """Test helper functions with AAD"""
        os.environ["ENVIRONMENT"] = "development"
        
        plaintext = "Test secret"
        aad = "context:user123"
        
        # Encrypt
        ciphertext = encrypt_aes_gcm(plaintext, key_id="test", aad=aad)
        
        # Decrypt
        decrypted = decrypt_aes_gcm(ciphertext, key_id="test", aad=aad)
        assert decrypted == plaintext
    
    def test_binary_helper_functions(self):
        """Test binary data helper functions"""
        os.environ["ENVIRONMENT"] = "development"
        
        plaintext_bytes = b"Binary test data"
        
        # Encrypt
        encrypted = encrypt_bytes_aes_gcm(plaintext_bytes, key_id="test")
        assert len(encrypted) > 0
        
        # Decrypt
        decrypted = decrypt_bytes_aes_gcm(encrypted, key_id="test")
        assert decrypted == plaintext_bytes
    
    def test_encryption_keys_constants(self):
        """Test that encryption key constants are defined"""
        assert EncryptionKeysAESGCM.OAUTH == "oauth"
        assert EncryptionKeysAESGCM.OAUTH_REFRESH == "oauth_refresh"
        assert EncryptionKeysAESGCM.API_KEYS == "api_keys"
        assert EncryptionKeysAESGCM.DEFAULT == "oauth"
    
    def test_oauth_token_encryption_scenario(self):
        """Test realistic OAuth token encryption scenario"""
        os.environ["ENVIRONMENT"] = "development"
        
        # Simulate OAuth access token
        access_token = "ya29.a0AfH6SMBxyz123..."
        user_id = "user:12345"
        
        # Encrypt with user_id as AAD for additional binding
        encrypted_token = encrypt_aes_gcm(
            access_token,
            key_id=EncryptionKeysAESGCM.OAUTH,
            aad=user_id
        )
        
        # Decrypt with correct AAD
        decrypted_token = decrypt_aes_gcm(
            encrypted_token,
            key_id=EncryptionKeysAESGCM.OAUTH,
            aad=user_id
        )
        
        assert decrypted_token == access_token
        
        # Decryption with wrong user_id should fail
        with pytest.raises(ValueError):
            decrypt_aes_gcm(
                encrypted_token,
                key_id=EncryptionKeysAESGCM.OAUTH,
                aad="user:99999"
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
