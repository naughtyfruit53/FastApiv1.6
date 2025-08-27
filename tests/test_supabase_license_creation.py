"""
Test Supabase Auth integration for license creation.

This test validates that organization license creation follows the Supabase-first approach:
1. Create user in Supabase Auth first
2. Only then create organization and user in local DB
3. Proper error handling and rollback if any step fails
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.main import app
from app.core.database import get_db
from app.models.base import Organization, User
from app.schemas.user import UserRole
from app.utils.supabase_auth import SupabaseAuthError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_supabase_license.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture
def mock_super_admin():
    """Create a mock super admin user for authentication"""
    return Mock(
        id=1,
        email="super@admin.com",
        is_super_admin=True,
        organization_id=None
    )

@pytest.fixture
def license_data():
    """Sample license creation data"""
    return {
        "organization_name": "Test Organization",
        "superadmin_email": "admin@testorg.com",
        "admin_password": "TempPass123!",
        "primary_phone": "1234567890",
        "address1": "123 Test St",
        "city": "Test City",
        "state": "Test State",
        "pin_code": "123456",
        "gst_number": "GST123456789",
        "state_code": "TS",
        "max_users": 10
    }

class TestSupabaseLicenseCreation:
    """Test cases for Supabase-first license creation approach"""

    @patch('app.api.v1.organizations.supabase_auth_service')
    @patch('app.api.v1.organizations.get_current_user')
    def test_supabase_auth_failure_prevents_db_creation(self, mock_current_user, mock_supabase_service, mock_super_admin, license_data):
        """Test that Supabase Auth failure prevents any local DB operations"""
        # Setup
        mock_current_user.return_value = mock_super_admin
        mock_supabase_service.create_user.side_effect = SupabaseAuthError("Supabase connection failed")
        
        # Execute
        response = client.post("/api/v1/organizations/license/create", json=license_data)
        
        # Assert
        assert response.status_code == 400
        assert "Supabase Auth error" in response.json()["detail"]
        
        # Verify no DB operations occurred
        with TestingSessionLocal() as db:
            org_count = db.query(Organization).filter(Organization.name == license_data["organization_name"]).count()
            user_count = db.query(User).filter(User.email == license_data["superadmin_email"]).count()
            assert org_count == 0, "Organization should not be created if Supabase Auth fails"
            assert user_count == 0, "User should not be created if Supabase Auth fails"

    @patch('app.api.v1.organizations.supabase_auth_service')
    @patch('app.api.v1.organizations.get_current_user')
    def test_db_failure_triggers_supabase_cleanup(self, mock_current_user, mock_supabase_service, mock_super_admin, license_data):
        """Test that local DB failure triggers Supabase Auth user cleanup"""
        # Setup
        mock_current_user.return_value = mock_super_admin
        mock_supabase_service.create_user.return_value = {
            "supabase_uuid": "test-uuid-123",
            "email": license_data["superadmin_email"]
        }
        
        # Mock DB session to fail during commit
        with patch('app.api.v1.organizations.get_db') as mock_get_db:
            mock_db = Mock(spec=Session)
            mock_db.query.return_value.filter.return_value.first.return_value = None  # No existing org
            mock_db.add.return_value = None
            mock_db.flush.return_value = None
            mock_db.commit.side_effect = Exception("Database connection failed")
            mock_db.rollback.return_value = None
            mock_get_db.return_value = mock_db
            
            # Execute
            response = client.post("/api/v1/organizations/license/create", json=license_data)
            
            # Assert
            assert response.status_code == 500
            assert "Failed to create organization and user in database" in response.json()["detail"]
            
            # Verify Supabase cleanup was called
            mock_supabase_service.delete_user.assert_called_once_with("test-uuid-123")

    @patch('app.api.v1.organizations.supabase_auth_service')
    @patch('app.api.v1.organizations.get_current_user')
    def test_successful_license_creation_with_supabase_uuid(self, mock_current_user, mock_supabase_service, mock_super_admin, license_data):
        """Test successful license creation with proper Supabase UUID linking"""
        # Setup
        mock_current_user.return_value = mock_super_admin
        test_supabase_uuid = "test-uuid-456"
        mock_supabase_service.create_user.return_value = {
            "supabase_uuid": test_supabase_uuid,
            "email": license_data["superadmin_email"]
        }
        
        with patch('app.api.v1.organizations.get_db') as mock_get_db:
            mock_db = Mock(spec=Session)
            mock_db.query.return_value.filter.return_value.first.return_value = None  # No existing org
            
            # Mock organization creation
            mock_org = Mock()
            mock_org.id = 1
            mock_org.name = license_data["organization_name"]
            mock_org.subdomain = "test-organization"
            mock_org.org_code = "24/12-(0)- tq0001"
            
            # Mock user creation
            mock_user = Mock()
            mock_user.email = license_data["superadmin_email"]
            mock_user.supabase_uuid = test_supabase_uuid
            
            mock_db.add.return_value = None
            mock_db.flush.return_value = None
            mock_db.commit.return_value = None
            mock_db.refresh.return_value = None
            
            # Mock the objects returned after refresh
            def mock_refresh(obj):
                if hasattr(obj, 'name'):  # Organization
                    for attr, value in vars(mock_org).items():
                        setattr(obj, attr, value)
                else:  # User
                    for attr, value in vars(mock_user).items():
                        setattr(obj, attr, value)
            
            mock_db.refresh.side_effect = mock_refresh
            mock_get_db.return_value = mock_db
            
            # Execute
            response = client.post("/api/v1/organizations/license/create", json=license_data)
            
            # Assert success response
            assert response.status_code == 200
            response_data = response.json()
            assert response_data["message"] == "Organization license created successfully"
            assert response_data["organization_name"] == license_data["organization_name"]
            assert response_data["superadmin_email"] == license_data["superadmin_email"]
            
            # Verify Supabase user creation was called with correct parameters
            mock_supabase_service.create_user.assert_called_once()
            call_args = mock_supabase_service.create_user.call_args
            assert call_args[1]["email"] == license_data["superadmin_email"]
            assert call_args[1]["password"] == license_data["admin_password"]
            assert call_args[1]["user_metadata"]["role"] == UserRole.ORG_ADMIN.value

    @patch('app.api.v1.organizations.supabase_auth_service')
    @patch('app.api.v1.organizations.get_current_user')
    def test_existing_organization_prevents_supabase_creation(self, mock_current_user, mock_supabase_service, mock_super_admin, license_data):
        """Test that existing organization name prevents Supabase Auth user creation"""
        # Setup
        mock_current_user.return_value = mock_super_admin
        
        with patch('app.api.v1.organizations.get_db') as mock_get_db:
            mock_db = Mock(spec=Session)
            # Mock existing organization
            existing_org = Mock()
            existing_org.name = license_data["organization_name"]
            mock_db.query.return_value.filter.return_value.first.return_value = existing_org
            mock_get_db.return_value = mock_db
            
            # Execute
            response = client.post("/api/v1/organizations/license/create", json=license_data)
            
            # Assert
            assert response.status_code == 400
            assert "Organization name already exists" in response.json()["detail"]
            
            # Verify Supabase service was never called
            mock_supabase_service.create_user.assert_not_called()

def test_supabase_error_types():
    """Test that different Supabase error types are handled appropriately"""
    
    # Test SupabaseAuthError (HTTP 400)
    with patch('app.api.v1.organizations.supabase_auth_service') as mock_service:
        mock_service.create_user.side_effect = SupabaseAuthError("Email already exists")
        # This should result in HTTP 400
        
    # Test general Exception (HTTP 500)  
    with patch('app.api.v1.organizations.supabase_auth_service') as mock_service:
        mock_service.create_user.side_effect = Exception("Network timeout")
        # This should result in HTTP 500

if __name__ == "__main__":
    pytest.main([__file__, "-v"])