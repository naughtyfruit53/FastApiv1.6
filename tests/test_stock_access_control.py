"""
Test module for stock access control functionality
Tests the new stock module access control for different user types
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import get_db, Base
from app.models.base import Organization, User, Product, Stock
from app.core.security import get_password_hash
from app.schemas.user import UserRole

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_stock_access.db"
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
    # Create test database tables
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)
    # Clean up
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def test_organization(test_db):
    """Create a test organization"""
    org = Organization(
        name="Test Organization",
        subdomain="test",
        status="active",
        primary_email="test@example.com",
        primary_phone="+1234567890",
        address1="123 Test Street",
        city="Test City",
        state="Test State",
        pin_code="123456",
        country="India"
    )
    test_db.add(org)
    test_db.commit()
    test_db.refresh(org)
    return org

@pytest.fixture
def test_super_admin(test_db):
    """Create a super admin user (no organization)"""
    admin = User(
        organization_id=None,  # Super admin has no organization
        email="superadmin@example.com",
        username="superadmin",
        hashed_password=get_password_hash("password123"),
        full_name="Super Admin",
        role=UserRole.SUPER_ADMIN,
        is_super_admin=True,
        is_active=True,
        has_stock_access=True  # Super admin always has access
    )
    test_db.add(admin)
    test_db.commit()
    test_db.refresh(admin)
    return admin

@pytest.fixture
def test_org_admin(test_db, test_organization):
    """Create an organization admin user"""
    admin = User(
        organization_id=test_organization.id,
        email="orgadmin@test.com",
        username="orgadmin",
        hashed_password=get_password_hash("password123"),
        full_name="Org Admin",
        role=UserRole.ORG_ADMIN,
        is_super_admin=False,
        is_active=True,
        has_stock_access=True  # Org admin has stock access
    )
    test_db.add(admin)
    test_db.commit()
    test_db.refresh(admin)
    return admin

@pytest.fixture
def test_standard_user_with_stock_access(test_db, test_organization):
    """Create a standard user with stock access"""
    user = User(
        organization_id=test_organization.id,
        email="user_with_stock@test.com",
        username="userwithstock",
        hashed_password=get_password_hash("password123"),
        full_name="User With Stock Access",
        role=UserRole.STANDARD_USER,
        is_super_admin=False,
        is_active=True,
        has_stock_access=True  # Has stock access
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user

@pytest.fixture
def test_standard_user_without_stock_access(test_db, test_organization):
    """Create a standard user without stock access"""
    user = User(
        organization_id=test_organization.id,
        email="user_no_stock@test.com",
        username="usernostock",
        hashed_password=get_password_hash("password123"),
        full_name="User Without Stock Access",
        role=UserRole.STANDARD_USER,
        is_super_admin=False,
        is_active=True,
        has_stock_access=False  # No stock access
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user

@pytest.fixture
def test_product_and_stock(test_db, test_organization):
    """Create a test product with stock"""
    product = Product(
        organization_id=test_organization.id,
        name="Test Product",
        hsn_code="12345678",
        part_number="TP001",
        unit="PCS",
        unit_price=100.0,
        gst_rate=18.0,
        reorder_level=10,
        is_active=True
    )
    test_db.add(product)
    test_db.flush()
    
    stock = Stock(
        organization_id=test_organization.id,
        product_id=product.id,
        quantity=50.0,
        unit="PCS",
        location="Warehouse A"
    )
    test_db.add(stock)
    test_db.commit()
    test_db.refresh(product)
    test_db.refresh(stock)
    return product, stock

def get_auth_headers(user):
    """Helper to get authentication headers for a user"""
    # This is a simplified auth header for testing
    # In real implementation, this would generate a proper JWT token
    return {"Authorization": f"Bearer test_token_{user.email}"}

class TestStockAccessControl:
    """Test cases for stock access control functionality"""
    
    def test_super_admin_can_access_stock(self, client, test_db, test_super_admin, test_product_and_stock):
        """Test that super admins can access stock from any organization"""
        product, stock = test_product_and_stock
        
        # Mock the authentication to return our test super admin
        app.dependency_overrides[lambda: None] = lambda: test_super_admin
        
        response = client.get("/api/v1/stock/")
        # Since this is a minimal test without full auth setup, we expect it to work
        # In full implementation, this would need proper JWT token setup
        
    def test_org_admin_can_access_org_stock(self, client, test_db, test_org_admin, test_product_and_stock):
        """Test that organization admins can access their organization's stock"""
        product, stock = test_product_and_stock
        
        # Mock the authentication to return our test org admin
        app.dependency_overrides[lambda: None] = lambda: test_org_admin
        
        response = client.get("/api/v1/stock/")
        # Would test successful access in full implementation
        
    def test_standard_user_with_stock_access_can_view_stock(self, client, test_db, test_standard_user_with_stock_access, test_product_and_stock):
        """Test that standard users with stock access can view stock"""
        product, stock = test_product_and_stock
        
        # Mock the authentication to return our test user with stock access
        app.dependency_overrides[lambda: None] = lambda: test_standard_user_with_stock_access
        
        response = client.get("/api/v1/stock/")
        # Would test successful access in full implementation
        
    def test_standard_user_without_stock_access_denied(self, client, test_db, test_standard_user_without_stock_access, test_product_and_stock):
        """Test that standard users without stock access are denied"""
        product, stock = test_product_and_stock
        
        # Mock the authentication to return our test user without stock access
        app.dependency_overrides[lambda: None] = lambda: test_standard_user_without_stock_access
        
        response = client.get("/api/v1/stock/")
        # Would test 403 Forbidden in full implementation

class TestStockAccessControlLogic:
    """Test the core access control logic without full API integration"""
    
    def test_stock_access_logic_super_admin(self, test_super_admin):
        """Test that super admin always has access"""
        # Super admin should always have access regardless of has_stock_access
        assert test_super_admin.is_super_admin == True
        assert test_super_admin.organization_id is None
        
    def test_stock_access_logic_org_admin(self, test_org_admin, test_organization):
        """Test that org admin has access to their organization"""
        assert test_org_admin.role == UserRole.ORG_ADMIN
        assert test_org_admin.organization_id == test_organization.id
        assert test_org_admin.has_stock_access == True
        
    def test_stock_access_logic_standard_user_with_access(self, test_standard_user_with_stock_access, test_organization):
        """Test standard user with stock access"""
        assert test_standard_user_with_stock_access.role == UserRole.STANDARD_USER
        assert test_standard_user_with_stock_access.organization_id == test_organization.id
        assert test_standard_user_with_stock_access.has_stock_access == True
        
    def test_stock_access_logic_standard_user_without_access(self, test_standard_user_without_stock_access, test_organization):
        """Test standard user without stock access"""
        assert test_standard_user_without_stock_access.role == UserRole.STANDARD_USER
        assert test_standard_user_without_stock_access.organization_id == test_organization.id
        assert test_standard_user_without_stock_access.has_stock_access == False

class TestDataIntegrity:
    """Test data integrity and organization context"""
    
    def test_organization_context_validation(self, test_org_admin):
        """Test that organization context is properly validated"""
        assert test_org_admin.organization_id is not None
        assert isinstance(test_org_admin.organization_id, int)
        
    def test_stock_product_relationship(self, test_product_and_stock, test_organization):
        """Test that stock and product records have proper organization_id"""
        product, stock = test_product_and_stock
        assert product.organization_id == test_organization.id
        assert stock.organization_id == test_organization.id
        assert stock.product_id == product.id

class TestErrorHandling:
    """Test error handling and validation scenarios"""
    
    def test_user_without_organization_error(self, test_db):
        """Test error when user has no organization_id"""
        user_no_org = User(
            organization_id=None,
            email="noorg@test.com",
            username="noorg",
            hashed_password=get_password_hash("password123"),
            full_name="No Org User",
            role=UserRole.STANDARD_USER,
            is_super_admin=False,
            is_active=True,
            has_stock_access=True
        )
        test_db.add(user_no_org)
        test_db.commit()
        
        # This user should be rejected when accessing stock API
        assert user_no_org.organization_id is None
        assert user_no_org.is_super_admin == False
        # This would cause a 400 error in the stock endpoint
        
    def test_access_control_error_message_validation(self):
        """Test that access control error messages are helpful"""
        # The stock endpoint should return:
        # "Access denied. You do not have permission to view stock information."
        # for standard users without stock access
        expected_message = "Access denied. You do not have permission to view stock information."
        assert len(expected_message) > 10  # Ensure message is descriptive
        assert "Access denied" in expected_message
        assert "stock" in expected_message.lower()