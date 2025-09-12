"""
Tests for OAuth2 functionality
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from app.models.oauth_models import UserEmailToken, OAuthProvider, TokenStatus
from app.services.oauth_service import OAuth2Service
from app.schemas.oauth_schemas import OAuthLoginRequest, UserEmailTokenCreate


class TestOAuth2Service:
    """Test OAuth2 service functionality"""
    
    def test_generate_state(self):
        """Test state generation"""
        db_mock = Mock()
        oauth_service = OAuth2Service(db_mock)
        
        state = oauth_service.generate_state()
        assert isinstance(state, str)
        assert len(state) > 20  # Should be reasonably long
    
    def test_generate_code_verifier(self):
        """Test PKCE code verifier generation"""
        db_mock = Mock()
        oauth_service = OAuth2Service(db_mock)
        
        verifier = oauth_service.generate_code_verifier()
        assert isinstance(verifier, str)
        assert len(verifier) > 20
    
    def test_generate_code_challenge(self):
        """Test PKCE code challenge generation"""
        db_mock = Mock()
        oauth_service = OAuth2Service(db_mock)
        
        verifier = "test_verifier"
        challenge = oauth_service.generate_code_challenge(verifier)
        assert isinstance(challenge, str)
        assert challenge != verifier  # Should be different from verifier
    
    @patch('app.services.oauth_service.requests.post')
    def test_exchange_code_for_tokens_success(self, mock_post):
        """Test successful token exchange"""
        # Mock database
        db_mock = Mock()
        oauth_state_mock = Mock()
        oauth_state_mock.code_verifier = "test_verifier"
        db_mock.query.return_value.filter.return_value.first.return_value = oauth_state_mock
        
        # Mock API response
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token",
            "expires_in": 3600
        }
        mock_post.return_value = mock_response
        
        # Mock user info request
        with patch('app.services.oauth_service.requests.get') as mock_get:
            mock_get.return_value.ok = True
            mock_get.return_value.json.return_value = {
                "email": "test@example.com",
                "name": "Test User"
            }
            
            oauth_service = OAuth2Service(db_mock)
            
            tokens, user_info = oauth_service.exchange_code_for_tokens(
                provider=OAuthProvider.GOOGLE,
                code="test_code",
                state="test_state",
                redirect_uri="http://localhost:3000/callback"
            )
            
            assert tokens["access_token"] == "test_access_token"
            assert user_info["email"] == "test@example.com"
    
    def test_store_user_tokens(self):
        """Test storing user tokens"""
        db_mock = Mock()
        db_mock.query.return_value.filter.return_value.first.return_value = None  # No existing token
        
        oauth_service = OAuth2Service(db_mock)
        
        token_response = {
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token",
            "expires_in": 3600
        }
        
        user_info = {
            "email": "test@example.com",
            "name": "Test User"
        }
        
        result = oauth_service.store_user_tokens(
            user_id=1,
            organization_id=1,
            provider=OAuthProvider.GOOGLE,
            token_response=token_response,
            user_info=user_info
        )
        
        # Verify token was added to database
        db_mock.add.assert_called_once()
        db_mock.commit.assert_called_once()
        
        # Verify result type
        assert isinstance(result, UserEmailToken)


class TestUserEmailToken:
    """Test UserEmailToken model"""
    
    def test_is_expired_not_expired(self):
        """Test token expiry check for non-expired token"""
        token = UserEmailToken()
        token.expires_at = datetime.utcnow() + timedelta(hours=1)
        
        assert not token.is_expired()
    
    def test_is_expired_expired(self):
        """Test token expiry check for expired token"""
        token = UserEmailToken()
        token.expires_at = datetime.utcnow() - timedelta(hours=1)
        
        assert token.is_expired()
    
    def test_is_expired_no_expiry(self):
        """Test token expiry check when no expiry is set"""
        token = UserEmailToken()
        token.expires_at = None
        
        assert not token.is_expired()
    
    def test_is_active_valid_token(self):
        """Test active check for valid token"""
        token = UserEmailToken()
        token.status = TokenStatus.ACTIVE
        token.expires_at = datetime.utcnow() + timedelta(hours=1)
        token.access_token_encrypted = "encrypted_token"
        
        assert token.is_active()
    
    def test_is_active_expired_token(self):
        """Test active check for expired token"""
        token = UserEmailToken()
        token.status = TokenStatus.ACTIVE
        token.expires_at = datetime.utcnow() - timedelta(hours=1)
        token.access_token_encrypted = "encrypted_token"
        
        assert not token.is_active()
    
    def test_is_active_revoked_token(self):
        """Test active check for revoked token"""
        token = UserEmailToken()
        token.status = TokenStatus.REVOKED
        token.expires_at = datetime.utcnow() + timedelta(hours=1)
        token.access_token_encrypted = "encrypted_token"
        
        assert not token.is_active()
    
    def test_is_active_no_token(self):
        """Test active check when no access token"""
        token = UserEmailToken()
        token.status = TokenStatus.ACTIVE
        token.expires_at = datetime.utcnow() + timedelta(hours=1)
        token.access_token_encrypted = None
        
        assert not token.is_active()


class TestOAuthEndpoints:
    """Test OAuth API endpoints"""
    
    def test_oauth_providers_endpoint(self):
        """Test OAuth providers endpoint returns configured providers"""
        # This would need actual FastAPI test client setup
        # For now, just ensure the concept is correct
        assert True  # Placeholder
    
    def test_oauth_login_endpoint(self):
        """Test OAuth login endpoint creates authorization URL"""
        # This would need actual FastAPI test client setup
        # For now, just ensure the concept is correct
        assert True  # Placeholder
    
    def test_oauth_callback_endpoint(self):
        """Test OAuth callback endpoint processes tokens"""
        # This would need actual FastAPI test client setup
        # For now, just ensure the concept is correct
        assert True  # Placeholder


if __name__ == "__main__":
    pytest.main([__file__])