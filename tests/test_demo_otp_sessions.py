# tests/test_demo_otp_sessions.py
"""
Unit tests for Demo OTP Users (Ephemeral Sessions)
Tests OTP generation, verification, session management, and data purge functionality.
"""

import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime, timedelta

# Import the service and utilities
from app.services.demo_user_service import (
    DemoUserService,
    DEMO_SESSION_DURATION_MINUTES,
    DEMO_ORG_ID,
    DEMO_USER_PREFIX,
    _demo_sessions
)


class TestDemoUserService:
    """Tests for the DemoUserService class"""

    @pytest.fixture
    def mock_db(self):
        """Mock database session"""
        return AsyncMock()

    @pytest.fixture
    def demo_service(self, mock_db):
        """Create a demo service instance"""
        return DemoUserService(mock_db)

    def test_generate_demo_email(self):
        """Test demo email generation format"""
        email = DemoUserService.generate_demo_email()
        
        assert email.startswith(DEMO_USER_PREFIX)
        assert email.endswith("@demo.local")
        assert len(email) > len(DEMO_USER_PREFIX) + 11  # prefix + 8 chars + @demo.local

    def test_generate_demo_email_uniqueness(self):
        """Test that generated emails are unique"""
        emails = [DemoUserService.generate_demo_email() for _ in range(100)]
        assert len(set(emails)) == 100  # All should be unique

    def test_is_demo_user_valid(self):
        """Test demo user email validation"""
        valid_email = f"{DEMO_USER_PREFIX}abc12345@demo.local"
        assert DemoUserService.is_demo_user(valid_email) is True

    def test_is_demo_user_invalid(self):
        """Test non-demo user email validation"""
        regular_email = "user@company.com"
        assert DemoUserService.is_demo_user(regular_email) is False
        
        # Wrong prefix
        wrong_prefix = "other_user_abc12345@demo.local"
        assert DemoUserService.is_demo_user(wrong_prefix) is False
        
        # Wrong domain
        wrong_domain = f"{DEMO_USER_PREFIX}abc12345@other.com"
        assert DemoUserService.is_demo_user(wrong_domain) is False

    def test_demo_session_duration(self):
        """Test that demo session duration is 30 minutes"""
        assert DEMO_SESSION_DURATION_MINUTES == 30

    def test_demo_org_id(self):
        """Test that demo org ID is -1 (pseudo org)"""
        assert DEMO_ORG_ID == -1

    @pytest.mark.asyncio
    async def test_initiate_demo_session_success(self, demo_service, mock_db):
        """Test successful demo session initiation"""
        # Mock OTP service
        with patch.object(demo_service, 'otp_service') as mock_otp:
            mock_otp.generate_and_send_otp = AsyncMock(return_value=(True, "123456"))
            
            success, message, demo_email = await demo_service.initiate_demo_session()
            
            assert success is True
            assert demo_email is not None
            assert DemoUserService.is_demo_user(demo_email)
            assert "OTP sent" in message

    @pytest.mark.asyncio
    async def test_initiate_demo_session_failure(self, demo_service, mock_db):
        """Test demo session initiation failure"""
        # Mock OTP service to fail
        with patch.object(demo_service, 'otp_service') as mock_otp:
            mock_otp.generate_and_send_otp = AsyncMock(return_value=(False, None))
            
            success, message, demo_email = await demo_service.initiate_demo_session()
            
            assert success is False
            assert demo_email is None
            assert "Failed" in message

    @pytest.mark.asyncio
    async def test_verify_demo_otp_success(self, demo_service, mock_db):
        """Test successful OTP verification"""
        demo_email = f"{DEMO_USER_PREFIX}test1234@demo.local"
        
        # Mock OTP service
        with patch.object(demo_service, 'otp_service') as mock_otp:
            mock_otp.verify_otp = AsyncMock(return_value=(True, "OTP verified"))
            
            # Mock create_access_token
            with patch('app.services.demo_user_service.create_access_token') as mock_token:
                mock_token.return_value = "test_access_token"
                
                success, message, session_data = await demo_service.verify_demo_otp(
                    demo_email, "123456"
                )
                
                assert success is True
                assert session_data is not None
                assert session_data["access_token"] == "test_access_token"
                assert session_data["is_demo"] is True

    @pytest.mark.asyncio
    async def test_verify_demo_otp_invalid(self, demo_service, mock_db):
        """Test invalid OTP verification"""
        demo_email = f"{DEMO_USER_PREFIX}test1234@demo.local"
        
        # Mock OTP service to fail
        with patch.object(demo_service, 'otp_service') as mock_otp:
            mock_otp.verify_otp = AsyncMock(return_value=(False, "Invalid OTP"))
            
            success, message, session_data = await demo_service.verify_demo_otp(
                demo_email, "wrong_otp"
            )
            
            assert success is False
            assert session_data is None
            assert "Invalid" in message

    def test_get_demo_session_active(self, demo_service):
        """Test getting active demo session"""
        demo_email = f"{DEMO_USER_PREFIX}active123@demo.local"
        
        # Manually add a session
        _demo_sessions[demo_email] = {
            "status": "active",
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(minutes=30),
            "access_token": "test_token",
            "temp_data": {}
        }
        
        session = demo_service.get_demo_session(demo_email)
        
        assert session is not None
        assert session["status"] == "active"
        
        # Cleanup
        del _demo_sessions[demo_email]

    def test_get_demo_session_expired(self, demo_service):
        """Test getting expired demo session"""
        demo_email = f"{DEMO_USER_PREFIX}expired123@demo.local"
        
        # Manually add an expired session
        _demo_sessions[demo_email] = {
            "status": "active",
            "created_at": datetime.utcnow() - timedelta(hours=1),
            "expires_at": datetime.utcnow() - timedelta(minutes=30),
            "access_token": "test_token",
            "temp_data": {}
        }
        
        session = demo_service.get_demo_session(demo_email)
        
        # Session should be cleaned up and return None
        assert session is None
        assert demo_email not in _demo_sessions

    def test_get_session_time_remaining(self, demo_service):
        """Test getting session time remaining"""
        demo_email = f"{DEMO_USER_PREFIX}time123@demo.local"
        
        # Add session with 15 minutes remaining
        _demo_sessions[demo_email] = {
            "status": "active",
            "created_at": datetime.utcnow() - timedelta(minutes=15),
            "expires_at": datetime.utcnow() + timedelta(minutes=15),
            "temp_data": {}
        }
        
        remaining = demo_service.get_session_time_remaining(demo_email)
        
        assert remaining is not None
        # Should be approximately 15 minutes (900 seconds) with some tolerance
        assert 850 < remaining < 950
        
        # Cleanup
        del _demo_sessions[demo_email]

    @pytest.mark.asyncio
    async def test_store_temp_data(self, demo_service):
        """Test storing temporary data in demo session"""
        demo_email = f"{DEMO_USER_PREFIX}temp123@demo.local"
        
        # Add session
        _demo_sessions[demo_email] = {
            "status": "active",
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(minutes=30),
            "temp_data": {}
        }
        
        result = await demo_service.store_temp_data(demo_email, "test_key", "test_value")
        
        assert result is True
        assert _demo_sessions[demo_email]["temp_data"]["test_key"] == "test_value"
        
        # Cleanup
        del _demo_sessions[demo_email]

    def test_get_temp_data(self, demo_service):
        """Test getting temporary data from demo session"""
        demo_email = f"{DEMO_USER_PREFIX}gettemp123@demo.local"
        
        # Add session with data
        _demo_sessions[demo_email] = {
            "status": "active",
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(minutes=30),
            "temp_data": {"stored_key": "stored_value"}
        }
        
        value = demo_service.get_temp_data(demo_email, "stored_key")
        
        assert value == "stored_value"
        
        # Cleanup
        del _demo_sessions[demo_email]

    @pytest.mark.asyncio
    async def test_end_demo_session(self, demo_service):
        """Test ending demo session and purging data"""
        demo_email = f"{DEMO_USER_PREFIX}end123@demo.local"
        
        # Add session with data
        _demo_sessions[demo_email] = {
            "status": "active",
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(minutes=30),
            "access_token": "test_token",
            "temp_data": {"key1": "value1", "key2": "value2"}
        }
        
        success, message = await demo_service.end_demo_session(demo_email)
        
        assert success is True
        assert "purged" in message.lower()
        assert demo_email not in _demo_sessions

    @pytest.mark.asyncio
    async def test_end_nonexistent_session(self, demo_service):
        """Test ending a session that doesn't exist"""
        demo_email = f"{DEMO_USER_PREFIX}nonexistent@demo.local"
        
        success, message = await demo_service.end_demo_session(demo_email)
        
        # Should succeed gracefully
        assert success is True

    def test_cleanup_expired_sessions(self):
        """Test cleanup of expired demo sessions"""
        # Add some sessions
        active_email = f"{DEMO_USER_PREFIX}active@demo.local"
        expired_email1 = f"{DEMO_USER_PREFIX}expired1@demo.local"
        expired_email2 = f"{DEMO_USER_PREFIX}expired2@demo.local"
        
        _demo_sessions[active_email] = {
            "status": "active",
            "expires_at": datetime.utcnow() + timedelta(minutes=15)
        }
        _demo_sessions[expired_email1] = {
            "status": "active",
            "expires_at": datetime.utcnow() - timedelta(minutes=10)
        }
        _demo_sessions[expired_email2] = {
            "status": "active",
            "expires_at": datetime.utcnow() - timedelta(minutes=30)
        }
        
        cleaned = DemoUserService.cleanup_expired_sessions()
        
        assert cleaned == 2
        assert active_email in _demo_sessions
        assert expired_email1 not in _demo_sessions
        assert expired_email2 not in _demo_sessions
        
        # Cleanup
        del _demo_sessions[active_email]

    def test_get_active_demo_session_count(self):
        """Test counting active demo sessions"""
        # Clear any existing sessions
        _demo_sessions.clear()
        
        # Add some sessions
        for i in range(3):
            _demo_sessions[f"{DEMO_USER_PREFIX}active{i}@demo.local"] = {
                "status": "active",
                "expires_at": datetime.utcnow() + timedelta(minutes=15)
            }
        
        # Add expired session
        _demo_sessions[f"{DEMO_USER_PREFIX}expired@demo.local"] = {
            "status": "active",
            "expires_at": datetime.utcnow() - timedelta(minutes=10)
        }
        
        count = DemoUserService.get_active_demo_session_count()
        
        assert count == 3
        
        # Cleanup
        _demo_sessions.clear()


class TestDemoSessionDataPurge:
    """Tests specifically for data purge functionality"""

    def test_session_cleanup_removes_all_temp_data(self):
        """Test that cleanup removes all temporary data"""
        demo_email = f"{DEMO_USER_PREFIX}purge123@demo.local"
        
        # Add session with various temp data
        _demo_sessions[demo_email] = {
            "status": "active",
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(minutes=30),
            "access_token": "sensitive_token",
            "temp_data": {
                "customers": [1, 2, 3],
                "invoices": [100, 101, 102],
                "products": {"a": 1, "b": 2}
            }
        }
        
        # Verify data exists
        assert demo_email in _demo_sessions
        assert len(_demo_sessions[demo_email]["temp_data"]) == 3
        
        # Cleanup
        DemoUserService(AsyncMock())._cleanup_demo_session(demo_email)
        
        # Verify all data is removed
        assert demo_email not in _demo_sessions


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
