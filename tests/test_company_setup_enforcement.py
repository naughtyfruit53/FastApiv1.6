"""
Test company setup enforcement for inventory operations
"""
import pytest
import io
import pandas as pd
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import get_db, Base
from app.models.base import Organization, User, Product, Stock, Company
from app.core.security import get_password_hash

# Test database URL (use SQLite for testing)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_company_setup.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    """Create test client"""
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def test_organization_without_company(test_db):
    """Create test organization without company setup"""
    org = Organization(
        name="Test Organization No Company",
        subdomain="testnocompany",
        status="active",
        primary_email="test@example.com",
        primary_phone="+1234567890",
        address1="123 Test Street",
        city="Test City",
        state="Test State",
        pin_code="12345",
        country="India",
        company_details_completed=False  # Key: company setup not completed
    )
    test_db.add(org)
    test_db.commit()
    test_db.refresh(org)
    return org

@pytest.fixture
def test_organization_with_company(test_db):
    """Create test organization with company setup completed"""
    org = Organization(
        name="Test Organization With Company",
        subdomain="testwithcompany",
        status="active",
        primary_email="test@example.com",
        primary_phone="+1234567890",
        address1="123 Test Street",
        city="Test City",
        state="Test State",
        pin_code="12345",
        country="India",
        company_details_completed=True  # Key: company setup completed
    )
    test_db.add(org)
    test_db.commit()
    test_db.refresh(org)
    
    # Create actual company record
    company = Company(
        organization_id=org.id,
        name="Test Company",
        business_type="Manufacturing",
        industry="Technology",
        primary_email="company@example.com",
        primary_phone="+1234567890",
        address1="123 Company Street",
        city="Company City",
        state="Company State",
        pin_code="12345",
        country="India"
    )
    test_db.add(company)
    test_db.commit()
    test_db.refresh(company)
    
    return org

@pytest.fixture
def test_user_no_company(test_db, test_organization_without_company):
    """Create test user in organization without company setup"""
    user = User(
        organization_id=test_organization_without_company.id,
        email="user@nocompany.com",
        username="usernocompany",
        hashed_password=get_password_hash("userpass123"),
        full_name="User No Company",
        role="org_admin",
        is_active=True
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user

@pytest.fixture
def test_user_with_company(test_db, test_organization_with_company):
    """Create test user in organization with company setup"""
    user = User(
        organization_id=test_organization_with_company.id,
        email="user@withcompany.com",
        username="userwithcompany",
        hashed_password=get_password_hash("userpass123"),
        full_name="User With Company",
        role="org_admin",
        is_active=True
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user

def get_auth_token(client: TestClient, email: str, password: str):
    """Get authentication token"""
    response = client.post(
        "/api/v1/auth/login/email",
        json={"email": email, "password": password}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    return None

def create_test_excel_file(data: list) -> io.BytesIO:
    """Create test Excel file"""
    df = pd.DataFrame(data)
    excel_buffer = io.BytesIO()
    df.to_excel(excel_buffer, index=False)
    excel_buffer.seek(0)
    return excel_buffer

class TestCompanySetupEnforcement:
    """Test company setup enforcement for inventory operations"""
    
    def test_stock_import_blocked_without_company_setup(self, client, test_user_no_company, test_db):
        """Test that stock import is blocked when company setup is not completed"""
        token = get_auth_token(client, "user@nocompany.com", "userpass123")
        
        if not token:
            pytest.skip("Could not get authentication token")
        
        # Create test stock data
        test_data = [
            {
                "product_name": "Test Product",
                "unit": "PCS",
                "quantity": 10,
                "location": "Warehouse A"
            }
        ]
        
        excel_file = create_test_excel_file(test_data)
        
        response = client.post(
            "/api/v1/stock/bulk",
            headers={"Authorization": f"Bearer {token}"},
            files={"file": ("test_stock.xlsx", excel_file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response data: {response.json()}")
        
        assert response.status_code == 412  # Precondition Failed
        data = response.json()
        assert "company details" in data["detail"].lower()
        assert "setup" in data["detail"].lower()
    
    def test_stock_import_allowed_with_company_setup(self, client, test_user_with_company, test_db):
        """Test that stock import is allowed when company setup is completed"""
        token = get_auth_token(client, "user@withcompany.com", "userpass123")
        
        if not token:
            pytest.skip("Could not get authentication token")
        
        # Create test stock data
        test_data = [
            {
                "product_name": "Test Product",
                "unit": "PCS",
                "quantity": 10,
                "location": "Warehouse A"
            }
        ]
        
        excel_file = create_test_excel_file(test_data)
        
        response = client.post(
            "/api/v1/stock/bulk",
            headers={"Authorization": f"Bearer {token}"},
            files={"file": ("test_stock.xlsx", excel_file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response data: {response.json()}")
        
        # Should succeed (200) or have validation errors (400), but not 412
        assert response.status_code != 412
    
    def test_product_import_blocked_without_company_setup(self, client, test_user_no_company, test_db):
        """Test that product import is blocked when company setup is not completed"""
        token = get_auth_token(client, "user@nocompany.com", "userpass123")
        
        if not token:
            pytest.skip("Could not get authentication token")
        
        # Create test product data
        test_data = [
            {
                "product_name": "Test Product",
                "hsn_code": "12345678",
                "unit": "PCS",
                "unit_price": 100.0,
                "gst_rate": 18.0
            }
        ]
        
        excel_file = create_test_excel_file(test_data)
        
        response = client.post(
            "/api/products/import/excel",
            headers={"Authorization": f"Bearer {token}"},
            files={"file": ("test_products.xlsx", excel_file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response data: {response.json()}")
        
        assert response.status_code == 412  # Precondition Failed
        data = response.json()
        assert "company details" in data["detail"].lower()
        assert "setup" in data["detail"].lower()
    
    def test_product_import_allowed_with_company_setup(self, client, test_user_with_company, test_db):
        """Test that product import is allowed when company setup is completed"""
        token = get_auth_token(client, "user@withcompany.com", "userpass123")
        
        if not token:
            pytest.skip("Could not get authentication token")
        
        # Create test product data
        test_data = [
            {
                "product_name": "Test Product",
                "hsn_code": "12345678",
                "unit": "PCS",
                "unit_price": 100.0,
                "gst_rate": 18.0
            }
        ]
        
        excel_file = create_test_excel_file(test_data)
        
        response = client.post(
            "/api/products/import/excel",
            headers={"Authorization": f"Bearer {token}"},
            files={"file": ("test_products.xlsx", excel_file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response data: {response.json()}")
        
        # Should succeed (200) or have validation errors (400), but not 412
        assert response.status_code != 412
    
    def test_company_current_endpoint_returns_404_when_no_company(self, client, test_user_no_company, test_db):
        """Test that /companies/current returns 404 when no company exists"""
        token = get_auth_token(client, "user@nocompany.com", "userpass123")
        
        if not token:
            pytest.skip("Could not get authentication token")
        
        response = client.get(
            "/api/companies/current",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "company details not found" in data["detail"].lower()
    
    def test_company_current_endpoint_returns_company_when_exists(self, client, test_user_with_company, test_db):
        """Test that /companies/current returns company data when company exists"""
        token = get_auth_token(client, "user@withcompany.com", "userpass123")
        
        if not token:
            pytest.skip("Could not get authentication token")
        
        response = client.get(
            "/api/companies/current",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Company"
        assert data["business_type"] == "Manufacturing"
    
    def test_specific_error_messages_for_different_scenarios(self, client, test_user_no_company, test_db):
        """Test that specific error messages are returned for different missing company scenarios"""
        token = get_auth_token(client, "user@nocompany.com", "userpass123")
        
        if not token:
            pytest.skip("Could not get authentication token")
        
        # Test stock import error message
        test_data = [{"product_name": "Test", "unit": "PCS", "quantity": 1}]
        excel_file = create_test_excel_file(test_data)
        
        response = client.post(
            "/api/v1/stock/bulk",
            headers={"Authorization": f"Bearer {token}"},
            files={"file": ("test.xlsx", excel_file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        )
        
        assert response.status_code == 412
        data = response.json()
        
        # Verify the error message is specific and actionable
        detail = data["detail"].lower()
        assert "company details" in detail
        assert "completed" in detail or "setup" in detail
        assert "before" in detail
        assert "operation" in detail or "import" in detail or "inventory" in detail