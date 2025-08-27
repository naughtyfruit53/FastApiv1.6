#!/usr/bin/env python3
"""
Test suite for enhanced organization management endpoints
"""

import os
import sys
import pytest
import tempfile
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add app to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.core.database import get_db, Base
from app.models.base import Organization, User
from app.core.security import get_password_hash, create_access_token
from app.schemas.user import UserRole

class TestOrganizationManagement:
    """Test enhanced organization management functionality"""
    
    @pytest.fixture
    def temp_db_url(self):
        """Create a temporary database for testing"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_url = f"sqlite:///{tmp.name}"
            yield db_url
            # Cleanup
            try:
                os.unlink(tmp.name)
            except:
                pass
    
    @pytest.fixture
    def test_db(self, temp_db_url):
        """Create test database session"""
        # Set required env vars
        os.environ['SMTP_USERNAME'] = 'test@example.com'
        os.environ['SMTP_PASSWORD'] = 'testpass'
        os.environ['EMAILS_FROM_EMAIL'] = 'test@example.com'
        
        engine = create_engine(temp_db_url, connect_args={"check_same_thread": False})
        Base.metadata.create_all(bind=engine)
        
        TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        def override_get_db():
            try:
                db = TestingSessionLocal()
                yield db
            finally:
                db.close()
        
        app.dependency_overrides[get_db] = override_get_db
        yield TestingSessionLocal()
        
        # Cleanup
        app.dependency_overrides.clear()
    
    @pytest.fixture
    def test_data(self, test_db):
        """Create test data"""
        # Create organizations
        org1 = Organization(
            name="Test Org 1",
            subdomain="test1",
            primary_email="admin@test1.com",
            primary_phone="1234567890",
            address1="123 Test St",
            city="Test City",
            state="Test State",
            pin_code="123456",
            state_code="01",
            status="active"
        )
        
        org2 = Organization(
            name="Test Org 2", 
            subdomain="test2",
            primary_email="admin@test2.com",
            primary_phone="0987654321",
            address1="456 Test Ave",
            city="Test City 2",
            state="Test State 2",
            pin_code="654321",
            state_code="02",
            status="active"
        )
        
        test_db.add(org1)
        test_db.add(org2)
        test_db.flush()
        
        # Create users
        super_admin = User(
            email="superadmin@test.com",
            username="superadmin",
            hashed_password=get_password_hash("password123"),
            full_name="Super Admin",
            role=UserRole.SUPER_ADMIN.value,
            is_super_admin=True,
            is_active=True,
            organization_id=None  # Super admins have no fixed organization
        )
        
        org1_admin = User(
            organization_id=org1.id,
            email="admin@test1.com",
            username="org1admin",
            hashed_password=get_password_hash("password123"),
            full_name="Org 1 Admin",
            role=UserRole.ORG_ADMIN.value,
            is_active=True
        )
        
        org2_user = User(
            organization_id=org2.id,
            email="user@test2.com",
            username="org2user",
            hashed_password=get_password_hash("password123"),
            full_name="Org 2 User",
            role=UserRole.STANDARD_USER.value,
            is_active=True
        )
        
        test_db.add(super_admin)
        test_db.add(org1_admin)
        test_db.add(org2_user)
        test_db.commit()
        
        return {
            'org1': org1,
            'org2': org2,
            'super_admin': super_admin,
            'org1_admin': org1_admin,
            'org2_user': org2_user
        }
    
    def get_auth_headers(self, email: str, user_type: str = "org", organization_id: int = None):
        """Generate auth headers for test requests"""
        token = create_access_token(
            data={
                "sub": email,
                "organization_id": organization_id,
                "user_role": "super_admin" if user_type == "platform" else "standard_user",
                "user_type": user_type
            }
        )
        return {"Authorization": f"Bearer {token}"}
    
    def test_create_organization_by_super_admin(self, test_data):
        """Test organization creation by super admin"""
        client = TestClient(app)
        
        org_data = {
            "name": "New Test Org",
            "subdomain": "newtest",
            "primary_email": "admin@newtest.com",
            "primary_phone": "1111111111",
            "address1": "789 New St",
            "city": "New City",
            "state": "New State",
            "pin_code": "111111",
            "state_code": "03",
            "business_type": "Manufacturing",
            "industry": "Technology"
        }
        
        headers = self.get_auth_headers("superadmin@test.com", user_type="platform")
        response = client.post("/api/v1/organizations/", json=org_data, headers=headers)
        
        assert response.status_code == 201
        assert response.json()["name"] == "New Test Org"
        assert response.json()["subdomain"] == "newtest"
    
    def test_create_organization_by_regular_user_fails(self, test_data):
        """Test that regular users cannot create organizations"""
        client = TestClient(app)
        
        org_data = {
            "name": "Unauthorized Org",
            "subdomain": "unauthorized",
            "primary_email": "test@unauthorized.com"
        }
        
        headers = self.get_auth_headers("user@test2.com", organization_id=test_data['org2'].id)
        response = client.post("/api/v1/organizations/", json=org_data, headers=headers)
        
        assert response.status_code == 403
    
    def test_join_organization_by_super_admin(self, test_data):
        """Test super admin joining an organization"""
        client = TestClient(app)
        
        headers = self.get_auth_headers("superadmin@test.com", user_type="platform")
        response = client.post(f"/api/v1/organizations/{test_data['org1'].id}/join", headers=headers)
        
        assert response.status_code == 200
        assert "Successfully joined organization" in response.json()["message"]
    
    def test_join_organization_by_regular_user_fails(self, test_data):
        """Test that regular users cannot join organizations without invitation"""
        client = TestClient(app)
        
        headers = self.get_auth_headers("user@test2.com", organization_id=test_data['org2'].id)
        response = client.post(f"/api/v1/organizations/{test_data['org1'].id}/join", headers=headers)
        
        assert response.status_code == 403
    
    def test_get_organization_members(self, test_data):
        """Test getting organization members"""
        client = TestClient(app)
        
        # Org admin can get members of their own organization
        headers = self.get_auth_headers("admin@test1.com", organization_id=test_data['org1'].id)
        response = client.get(f"/api/v1/organizations/{test_data['org1'].id}/members", headers=headers)
        
        assert response.status_code == 200
        members = response.json()
        assert len(members) == 1
        assert members[0]["email"] == "admin@test1.com"
    
    def test_get_organization_members_access_denied(self, test_data):
        """Test that users cannot access members of other organizations"""
        client = TestClient(app)
        
        headers = self.get_auth_headers("user@test2.com", organization_id=test_data['org2'].id)
        response = client.get(f"/api/v1/organizations/{test_data['org1'].id}/members", headers=headers)
        
        assert response.status_code == 403
    
    def test_invite_user_to_organization(self, test_data):
        """Test inviting a user to an organization"""
        client = TestClient(app)
        
        user_data = {
            "email": "newuser@test1.com",
            "username": "newuser",
            "full_name": "New User",
            "password": "password123",
            "role": "standard_user"
        }
        
        headers = self.get_auth_headers("admin@test1.com", organization_id=test_data['org1'].id)
        response = client.post(f"/api/v1/organizations/{test_data['org1'].id}/invite", 
                              json=user_data, headers=headers)
        
        assert response.status_code == 200
        assert "successfully invited" in response.json()["message"]
    
    def test_invite_user_insufficient_permissions(self, test_data):
        """Test that regular users cannot invite other users"""
        client = TestClient(app)
        
        user_data = {
            "email": "newuser@test2.com",
            "username": "newuser2",
            "full_name": "New User 2",
            "password": "password123"
        }
        
        headers = self.get_auth_headers("user@test2.com", organization_id=test_data['org2'].id)
        response = client.post(f"/api/v1/organizations/{test_data['org2'].id}/invite", 
                              json=user_data, headers=headers)
        
        assert response.status_code == 403
    
    def test_get_user_organizations(self, test_data):
        """Test getting user's accessible organizations"""
        client = TestClient(app)
        
        # Super admin should see all organizations
        headers = self.get_auth_headers("superadmin@test.com", user_type="platform")
        response = client.get("/api/v1/users/me/organizations", headers=headers)
        
        assert response.status_code == 200
        orgs = response.json()
        assert len(orgs) == 2  # Should see both test organizations
        
        # Regular user should see only their organization
        headers = self.get_auth_headers("admin@test1.com", organization_id=test_data['org1'].id)
        response = client.get("/api/v1/users/me/organizations", headers=headers)
        
        assert response.status_code == 200
        orgs = response.json()
        assert len(orgs) == 1
        assert orgs[0]["name"] == "Test Org 1"
    
    def test_switch_organization_super_admin(self, test_data):
        """Test super admin switching between organizations"""
        client = TestClient(app)
        
        headers = self.get_auth_headers("superadmin@test.com", user_type="platform")
        response = client.put("/api/v1/users/me/organization", 
                             json={"organization_id": test_data['org1'].id}, 
                             headers=headers)
        
        assert response.status_code == 200
        assert response.json()["organization_id"] == test_data['org1'].id
    
    def test_switch_organization_regular_user_fails(self, test_data):
        """Test that regular users cannot switch organizations"""
        client = TestClient(app)
        
        headers = self.get_auth_headers("user@test2.com", organization_id=test_data['org2'].id)
        response = client.put("/api/v1/users/me/organization", 
                             json={"organization_id": test_data['org1'].id}, 
                             headers=headers)
        
        assert response.status_code == 403
    
    def test_organization_scoping_enforcement(self, test_data):
        """Test that organization scoping is properly enforced"""
        client = TestClient(app)
        
        # User from org1 should not be able to access org2 details
        headers = self.get_auth_headers("admin@test1.com", organization_id=test_data['org1'].id)
        response = client.get(f"/api/v1/organizations/{test_data['org2'].id}", headers=headers)
        
        assert response.status_code == 403
        
        # But should be able to access their own org
        response = client.get(f"/api/v1/organizations/{test_data['org1'].id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["name"] == "Test Org 1"
    
    def test_update_organization_permissions(self, test_data):
        """Test organization update permissions"""
        client = TestClient(app)
        
        update_data = {"name": "Updated Test Org 1"}
        
        # Org admin should be able to update their own organization
        headers = self.get_auth_headers("admin@test1.com", organization_id=test_data['org1'].id)
        response = client.put(f"/api/v1/organizations/{test_data['org1'].id}", 
                             json=update_data, headers=headers)
        
        assert response.status_code == 200
        assert response.json()["name"] == "Updated Test Org 1"
        
        # Regular user should not be able to update organization
        headers = self.get_auth_headers("user@test2.com", organization_id=test_data['org2'].id)
        response = client.put(f"/api/v1/organizations/{test_data['org2'].id}", 
                             json=update_data, headers=headers)
        
        assert response.status_code == 403