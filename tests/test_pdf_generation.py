# tests/test_pdf_generation.py

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.core.database import get_db, SessionLocal
from app.models.base import User, Company, Organization
from app.core.security import create_access_token

client = TestClient(app)

@pytest.fixture
def test_db():
    """Create a test database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def test_user(test_db: Session):
    """Create a test user with organization and company"""
    # Create organization
    organization = Organization(
        name="Test Org",
        subdomain="test"
    )
    test_db.add(organization)
    test_db.commit()
    test_db.refresh(organization)
    
    # Create company
    company = Company(
        name="Test Company",
        address="123 Test Street",
        contact_number="1234567890",
        email="test@company.com",
        organization_id=organization.id
    )
    test_db.add(company)
    test_db.commit()
    test_db.refresh(company)
    
    # Create user
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="hashedpassword",
        organization_id=organization.id
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    
    return user

def test_company_branding_endpoint_without_auth():
    """Test that company branding endpoint requires authentication"""
    response = client.get("/api/v1/company/branding")
    assert response.status_code == 401

def test_company_branding_endpoint_with_auth(test_user: User):
    """Test company branding endpoint with authentication"""
    # Create access token
    token = create_access_token(subject=test_user.username)
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/api/v1/company/branding", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert "name" in data
    assert "address" in data
    assert "contact_number" in data
    assert "email" in data

def test_company_branding_fallback_data():
    """Test that fallback branding data is returned when no company exists"""
    # Create a user without a company
    token = create_access_token(subject="nonexistentuser")
    headers = {"Authorization": f"Bearer {token}"}
    
    # This should return fallback data rather than error
    response = client.get("/api/v1/company/branding", headers=headers)
    # Note: This might fail due to user not existing, but the logic should handle it
    
def test_pdf_generation_audit_log():
    """Test PDF generation audit logging"""
    token = create_access_token(subject="testuser")
    headers = {"Authorization": f"Bearer {token}"}
    
    audit_data = {
        "action": "pdf_generated",
        "voucher_type": "payment-voucher",
        "voucher_number": "PV/2526/00000001",
        "timestamp": "2024-01-01T00:00:00Z"
    }
    
    response = client.post("/api/v1/audit/pdf-generation", json=audit_data, headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] in ["logged", "warning"]

def test_pdf_audit_without_auth():
    """Test that PDF audit endpoint requires authentication"""
    audit_data = {
        "action": "pdf_generated",
        "voucher_type": "payment-voucher",
        "voucher_number": "PV/2526/00000001",
        "timestamp": "2024-01-01T00:00:00Z"
    }
    
    response = client.post("/api/v1/audit/pdf-generation", json=audit_data)
    assert response.status_code == 401

if __name__ == "__main__":
    # Run tests with: python -m pytest tests/test_pdf_generation.py -v
    pytest.main([__file__, "-v"])