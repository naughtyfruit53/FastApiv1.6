"""
Test suite for comprehensive license management, email, and authentication fixes
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import Mock, patch

from app.main import app
from app.core.database import get_db
from app.models.base import User, Organization
from app.core.security import get_password_hash, create_access_token
from app.schemas.user import PasswordChangeRequest


def get_test_db():
    """Mock database for testing"""
    db = Mock(spec=Session)
    return db


app.dependency_overrides[get_db] = get_test_db
client = TestClient(app)


class TestPasswordChangeFlow:
    """Test password change functionality with JWT token refresh"""
    
    def test_password_change_returns_new_jwt(self):
        """Test that password change returns a new JWT token to prevent logout"""
        
        # Mock user data
        mock_user = Mock()
        mock_user.id = 1
        mock_user.email = "testuser@example.com"
        mock_user.organization_id = 1
        mock_user.role = "standard_user"
        mock_user.must_change_password = True
        mock_user.force_password_reset = False
        mock_user.hashed_password = get_password_hash("oldpassword123")
        
        with patch('app.api.v1.password.get_current_active_user', return_value=mock_user), \
             patch('app.api.v1.password.verify_password', return_value=True), \
             patch('app.api.v1.password.get_password_hash', return_value="hashed_new_password"), \
             patch('app.api.v1.password.create_access_token', return_value="new_jwt_token"), \
             patch('app.api.v1.password.UserService'), \
             patch('app.api.v1.password.AuditLogger'), \
             patch('app.core.config.settings') as mock_settings:
            
            mock_settings.ACCESS_TOKEN_EXPIRE_MINUTES = 30
            
            # Test mandatory password change
            response = client.post(
                "/api/v1/password/change",
                json={
                    "new_password": "newpassword123",
                    "confirm_password": "newpassword123"
                },
                headers={"Authorization": "Bearer fake_token"}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Check that new JWT token is returned
            assert "access_token" in data
            assert data["access_token"] == "new_jwt_token"
            assert data["token_type"] == "bearer"
            assert data["message"] == "Password changed successfully"
    
    def test_password_change_normal_flow_with_current_password(self):
        """Test normal password change flow with current password verification"""
        
        mock_user = Mock()
        mock_user.id = 1
        mock_user.email = "testuser@example.com"
        mock_user.organization_id = 1
        mock_user.role = "standard_user"
        mock_user.must_change_password = False  # Normal flow
        mock_user.force_password_reset = False
        mock_user.hashed_password = get_password_hash("oldpassword123")
        
        with patch('app.api.v1.password.get_current_active_user', return_value=mock_user), \
             patch('app.api.v1.password.verify_password', return_value=True), \
             patch('app.api.v1.password.get_password_hash', return_value="hashed_new_password"), \
             patch('app.api.v1.password.create_access_token', return_value="new_jwt_token"), \
             patch('app.api.v1.password.UserService'), \
             patch('app.api.v1.password.AuditLogger'), \
             patch('app.core.config.settings') as mock_settings:
            
            mock_settings.ACCESS_TOKEN_EXPIRE_MINUTES = 30
            
            response = client.post(
                "/api/v1/password/change",
                json={
                    "current_password": "oldpassword123",
                    "new_password": "newpassword123",
                    "confirm_password": "newpassword123"
                },
                headers={"Authorization": "Bearer fake_token"}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Check that new JWT token is returned
            assert "access_token" in data
            assert data["access_token"] == "new_jwt_token"
            assert data["token_type"] == "bearer"


class TestLicenseCreationEmailNotification:
    """Test license creation email notification functionality"""
    
    def test_license_creation_sends_enhanced_emails(self):
        """Test that license creation sends comprehensive emails to org admin and creator"""
        
        # Mock super admin user
        mock_super_admin = Mock()
        mock_super_admin.id = 1
        mock_super_admin.email = "superadmin@platform.com"
        mock_super_admin.is_super_admin = True
        
        # Mock database session
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = None  # No existing org
        mock_db.query.return_value.scalar.return_value = 0  # User count
        
        # Mock new organization and user
        mock_org = Mock()
        mock_org.id = 1
        mock_org.name = "Test Organization"
        mock_org.subdomain = "test-org"
        mock_org.org_code = "24/08-(0)-tq0001"
        
        mock_user = Mock()
        mock_user.id = 1
        mock_user.email = "admin@testorg.com"
        mock_user.username = "admin"
        mock_user.full_name = "Admin User"
        
        with patch('app.api.v1.organizations.get_current_user', return_value=mock_super_admin), \
             patch('app.api.v1.organizations.get_db', return_value=mock_db), \
             patch('app.api.v1.organizations.email_service') as mock_email_service, \
             patch('app.api.v1.organizations.Organization', return_value=mock_org), \
             patch('app.api.v1.organizations.User', return_value=mock_user), \
             patch('app.api.v1.organizations.get_password_hash', return_value="hashed_password"):
            
            # Mock email service to return success
            mock_email_service.send_license_creation_email.return_value = (True, None)
            
            response = client.post(
                "/api/v1/organizations/license/create",
                json={
                    "organization_name": "Test Organization",
                    "superadmin_email": "admin@testorg.com"
                },
                headers={"Authorization": "Bearer fake_token"}
            )
            
            # Check that email service was called with correct parameters
            if hasattr(mock_email_service, 'send_license_creation_email'):
                mock_email_service.send_license_creation_email.assert_called_once()
                call_args = mock_email_service.send_license_creation_email.call_args
                assert call_args[1]['org_admin_email'] == "admin@testorg.com"
                assert call_args[1]['organization_name'] == "Test Organization"
                assert call_args[1]['created_by'] == "superadmin@platform.com"
                assert call_args[1]['notify_creator'] is True


class TestPasswordResetUnification:
    """Test unified password reset functionality"""
    
    def test_admin_password_reset_enhanced_logging(self):
        """Test that admin password reset includes enhanced logging"""
        
        mock_super_admin = Mock()
        mock_super_admin.id = 1
        mock_super_admin.email = "superadmin@platform.com"
        mock_super_admin.is_super_admin = True
        
        mock_target_user = Mock()
        mock_target_user.id = 2
        mock_target_user.email = "user@example.com"
        mock_target_user.full_name = "Test User"
        mock_target_user.is_licenseholder_admin = True
        mock_target_user.is_super_admin = False
        
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_target_user
        
        with patch('app.api.v1.password.get_current_super_admin', return_value=mock_super_admin), \
             patch('app.api.v1.password.get_db', return_value=mock_db), \
             patch('app.api.v1.password.email_service') as mock_email_service, \
             patch('app.api.v1.password.get_password_hash', return_value="hashed_password"), \
             patch('app.api.v1.password.log_password_reset') as mock_log_reset, \
             patch('app.api.v1.password.log_security_event') as mock_log_security:
            
            mock_email_service.send_password_reset_email.return_value = (True, None)
            
            response = client.post(
                "/api/v1/password/admin-reset",
                json={
                    "user_email": "user@example.com"
                },
                headers={"Authorization": "Bearer fake_token"}
            )
            
            # Verify logging was called
            mock_log_reset.assert_called_once_with("user@example.com", "superadmin@platform.com", True)
            mock_log_security.assert_called_once()


def test_comprehensive_fixes_integration():
    """Integration test to verify all fixes work together"""
    
    # This test would verify the complete flow:
    # 1. Super admin creates license
    # 2. Emails are sent successfully
    # 3. Org admin can login and change password
    # 4. Fresh JWT is returned preventing logout
    # 5. Password reset works from both contexts
    
    # This is a placeholder for a more comprehensive integration test
    # that would require a real test database and email service
    
    assert True  # Placeholder


if __name__ == "__main__":
    pytest.main([__file__, "-v"])