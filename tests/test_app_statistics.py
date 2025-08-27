"""
Test organization-level statistics endpoint
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import get_db, Base, engine
from app.models.base import User, Organization
from app.core.security import get_password_hash
from app.schemas.user import UserRole
from sqlalchemy.orm import Session

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def test_db():
    # Create test database tables
    Base.metadata.create_all(bind=engine)
    db = next(get_db())
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def super_admin_user(test_db: Session):
    # Create super admin user
    super_admin = User(
        organization_id=None,  # Super admin has no organization
        email="superadmin@test.com",
        username="superadmin",
        hashed_password=get_password_hash("testpass123"),
        full_name="Super Admin User",
        role=UserRole.SUPER_ADMIN,
        is_super_admin=True,
        is_active=True
    )
    test_db.add(super_admin)
    test_db.commit()
    test_db.refresh(super_admin)
    return super_admin

@pytest.fixture
def test_organization(test_db: Session):
    # Create test organization
    org = Organization(
        name="Test Org",
        subdomain="testorg",
        primary_email="admin@example.com",
        primary_phone="+1234567890",
        address1="Test Address",
        city="Test City",
        state="Test State",
        pin_code="123456",
        status="active",
        plan_type="premium"
    )
    test_db.add(org)
    test_db.commit()
    test_db.refresh(org)
    return org

@pytest.fixture
def org_admin_user(test_db: Session, test_organization):
    # Create org admin user
    org_admin = User(
        organization_id=test_organization.id,
        email="orgadmin@test.com",
        username="orgadmin",
        hashed_password=get_password_hash("testpass123"),
        full_name="Org Admin User",
        role=UserRole.ORG_ADMIN,
        is_active=True
    )
    test_db.add(org_admin)
    test_db.commit()
    test_db.refresh(org_admin)
    return org_admin

def test_org_statistics_requires_auth(client: TestClient):
    """Test that org statistics endpoint requires authentication"""
    response = client.get("/api/v1/organizations/org-statistics")
    assert response.status_code == 401

def test_org_statistics_super_admin_access(client: TestClient, test_db: Session, super_admin_user):
    """Test that org statistics endpoint denies super admin access (no org context)"""
    # Login as super admin
    login_data = {"username": "superadmin@test.com", "password": "testpass123"}
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Super admin should get 403
    response = client.get("/api/v1/organizations/org-statistics", headers=headers)
    assert response.status_code == 403

def test_org_statistics_org_admin_access(client: TestClient, test_db: Session, org_admin_user, test_organization):
    """Test that org statistics endpoint works for org admin"""
    # Login as org admin
    login_data = {"username": "orgadmin@test.com", "password": "testpass123"}
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get org statistics
    response = client.get("/api/v1/organizations/org-statistics", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    
    # Check required fields and default values
    assert "total_products" in data
    assert data["total_products"] == 0
    assert "total_customers" in data
    assert data["total_customers"] == 0
    assert "total_vendors" in data
    assert data["total_vendors"] == 0
    assert "active_users" in data
    assert data["active_users"] == 1  # The org admin user
    assert "monthly_sales" in data
    assert data["monthly_sales"] == 0
    assert "inventory_value" in data
    assert data["inventory_value"] == 0
    assert "plan_type" in data
    assert data["plan_type"] == "premium"
    assert "storage_used_gb" in data
    assert "generated_at" in data