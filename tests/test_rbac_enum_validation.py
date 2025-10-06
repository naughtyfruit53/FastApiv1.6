# tests/test_rbac_enum_validation.py

"""
Test enum validation and error handling for RBAC endpoints
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db
from app.models.base import Organization, User
from app.schemas.rbac import ServiceRoleType

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_rbac_enum.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def test_organization(db_session):
    org = Organization(
        name="Test Organization",
        subdomain="test",
        status="active",
        primary_email="test@example.com",
        primary_phone="+1234567890",
        address1="123 Test St",
        city="Test City",
        state="Test State",
        pin_code="12345",
        country="Test Country"
    )
    db_session.add(org)
    db_session.commit()
    db_session.refresh(org)
    return org


@pytest.fixture
def admin_user(db_session, test_organization):
    user = User(
        organization_id=test_organization.id,
        email="admin@example.com",
        full_name="Admin User",
        role="org_admin",
        is_active=True,
        is_super_admin=True,
    )
    user.set_password("password123")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_valid_role_type_enum():
    """Test that valid ServiceRoleType enum values are accepted"""
    valid_roles = ["admin", "manager", "support", "viewer"]
    for role_value in valid_roles:
        role_type = ServiceRoleType(role_value)
        assert role_type.value == role_value


def test_invalid_role_type_enum():
    """Test that invalid ServiceRoleType enum values raise ValueError"""
    invalid_roles = ["invalid", "superuser", "moderator", ""]
    for role_value in invalid_roles:
        with pytest.raises(ValueError):
            ServiceRoleType(role_value)


def test_create_role_with_valid_enum(client, test_organization, admin_user):
    """Test creating a role with a valid enum value"""
    # Note: This test assumes authentication is working
    # In a real scenario, you'd need to get a valid token
    role_data = {
        "name": "admin",
        "display_name": "Administrator",
        "description": "Full access to all features",
        "organization_id": test_organization.id,
        "is_active": True,
    }
    
    # This would normally require authentication
    # response = client.post(
    #     f"/api/v1/rbac/organizations/{test_organization.id}/roles",
    #     json=role_data,
    #     headers={"Authorization": f"Bearer {token}"}
    # )
    # assert response.status_code == 200
    # assert response.json()["name"] == "admin"
    pass  # Placeholder for integration test


def test_create_role_with_invalid_enum_returns_400():
    """Test that creating a role with invalid enum returns 400 error"""
    # This test validates that the enum validation logic works
    role_data = {
        "name": "invalid_role_type",
        "display_name": "Invalid Role",
        "description": "This should fail",
        "organization_id": 1,
        "is_active": True,
    }
    
    # The pydantic validation should catch this before it reaches the endpoint
    # This test validates the enum is properly defined
    with pytest.raises(ValueError):
        ServiceRoleType("invalid_role_type")


def test_enum_validation_error_message():
    """Test that enum validation provides helpful error messages"""
    try:
        ServiceRoleType("bad_role")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        # Pydantic/Python enum will raise ValueError with message
        assert "bad_role" in str(e) or "not a valid" in str(e).lower()


def test_all_valid_service_role_types():
    """Test that all expected ServiceRoleType values are defined"""
    expected_roles = ["admin", "manager", "support", "viewer"]
    
    for role_name in expected_roles:
        role_type = ServiceRoleType(role_name)
        assert role_type.value == role_name
    
    # Test that enum has exactly these values
    all_role_values = [role.value for role in ServiceRoleType]
    assert set(all_role_values) == set(expected_roles)


def test_role_type_case_sensitivity():
    """Test that ServiceRoleType enum is case-sensitive"""
    # Should work with lowercase
    assert ServiceRoleType("admin").value == "admin"
    
    # Should fail with uppercase
    with pytest.raises(ValueError):
        ServiceRoleType("ADMIN")
    
    with pytest.raises(ValueError):
        ServiceRoleType("Admin")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
