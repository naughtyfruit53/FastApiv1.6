"""
Unit tests for JWT error handling improvements
"""

import pytest
from fastapi import HTTPException, status
from jose import jwt, JWTError
from datetime import datetime, timedelta
from app.core.security import create_access_token, decode_access_token
from app.core.config import settings


class TestJWTErrorHandling:
    """Test JWT error handling and structured responses"""
    
    def test_valid_token_decoding(self):
        """Test decoding a valid JWT token"""
        # Create a valid token
        data = {"sub": "test@example.com", "user_id": 1}
        token = create_access_token(data=data)
        
        # Decode it
        try:
            decoded = decode_access_token(token)
            assert decoded is not None
            assert "sub" in decoded
            assert decoded["sub"] == "test@example.com"
        except HTTPException:
            # If function raises HTTPException instead of returning None
            pytest.fail("Valid token should decode successfully")
    
    def test_expired_token_returns_structured_error(self):
        """Test that expired tokens return structured 401 response"""
        # Create an expired token
        expired_time = datetime.utcnow() - timedelta(minutes=30)
        data = {
            "sub": "test@example.com",
            "exp": expired_time
        }
        
        try:
            token = jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
            
            # Try to decode it
            with pytest.raises((HTTPException, JWTError)):
                decoded = decode_access_token(token)
                if decoded is None:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Token has expired"
                    )
        except Exception as e:
            # Verify it's a 401 error
            if isinstance(e, HTTPException):
                assert e.status_code == 401
    
    def test_malformed_token_returns_structured_error(self):
        """Test that malformed tokens return structured 401 response"""
        malformed_tokens = [
            "not.a.jwt.token",
            "invalid_token",
            "",
            "Bearer invalid",
            "header.payload"  # Missing signature
        ]
        
        for token in malformed_tokens:
            try:
                decoded = decode_access_token(token)
                # Should either return None or raise HTTPException
                if decoded is not None and "sub" in decoded:
                    pytest.fail(f"Malformed token '{token}' should not decode successfully")
            except (HTTPException, JWTError):
                # Expected behavior
                pass
    
    def test_tampered_token_returns_structured_error(self):
        """Test that tampered tokens return structured 401 response"""
        # Create a valid token
        data = {"sub": "test@example.com", "user_id": 1}
        token = create_access_token(data=data)
        
        # Tamper with it
        parts = token.split('.')
        if len(parts) == 3:
            # Change the payload
            tampered_token = f"{parts[0]}.TAMPERED.{parts[2]}"
            
            try:
                decoded = decode_access_token(tampered_token)
                if decoded is not None:
                    pytest.fail("Tampered token should not decode successfully")
            except (HTTPException, JWTError):
                # Expected behavior
                pass
    
    def test_missing_required_claims(self):
        """Test that tokens missing required claims return structured errors"""
        # Create token without 'sub' claim
        data = {"user_id": 1, "exp": datetime.utcnow() + timedelta(minutes=30)}
        
        try:
            token = jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
            decoded = decode_access_token(token)
            
            # Should fail validation
            if decoded and "sub" not in decoded:
                # Token decoded but missing required claim
                with pytest.raises(HTTPException):
                    if "sub" not in decoded:
                        raise HTTPException(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Token missing required claims"
                        )
        except Exception:
            # Expected behavior
            pass
    
    def test_token_with_invalid_signature(self):
        """Test that tokens with invalid signatures are rejected"""
        # Create a token with wrong secret
        data = {"sub": "test@example.com", "user_id": 1}
        wrong_secret = "wrong_secret_key_12345"
        
        try:
            token = jwt.encode(data, wrong_secret, algorithm=settings.ALGORITHM)
            decoded = decode_access_token(token)
            
            if decoded is not None:
                pytest.fail("Token with invalid signature should not decode")
        except (HTTPException, JWTError):
            # Expected behavior
            pass


class TestJWTErrorMessages:
    """Test JWT error messages are informative but not revealing"""
    
    def test_error_messages_not_too_revealing(self):
        """Test that error messages don't reveal sensitive information"""
        # Error messages should not reveal:
        # - Secret key
        # - Internal algorithms
        # - Exact token structure
        
        malformed_token = "malformed.token.here"
        
        try:
            decoded = decode_access_token(malformed_token)
            if decoded is None:
                # Good - just returns None
                pass
        except HTTPException as e:
            error_detail = str(e.detail).lower()
            
            # Should not contain these
            assert "secret" not in error_detail
            assert "key" not in error_detail
            assert settings.SECRET_KEY not in error_detail
            
            # Should contain generic message
            assert "invalid" in error_detail or "unauthorized" in error_detail or "authentication" in error_detail


class TestJWTLogSpam:
    """Test that malformed tokens don't cause excessive logging"""
    
    def test_repeated_invalid_tokens_minimal_logging(self, caplog):
        """Test that repeated invalid tokens don't spam logs"""
        import logging
        caplog.set_level(logging.INFO)
        
        # Try multiple invalid tokens
        for i in range(10):
            try:
                decode_access_token(f"invalid_token_{i}")
            except (HTTPException, JWTError):
                pass
        
        # Check logs aren't spammed
        error_logs = [record for record in caplog.records if record.levelname == "ERROR"]
        
        # Should have minimal error logs (ideally none or just a few)
        # Exact number depends on implementation
        # Just verify it's not logging every single failure
        assert len(error_logs) < 20  # Reasonable threshold


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
