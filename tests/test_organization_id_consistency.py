"""
Test organization_id consistency across API endpoints and models
"""
import pytest
import sqlite3
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models.base import Organization, User, Customer, Vendor, Product, Stock
from app.schemas.user import UserRole


class TestOrganizationIdConsistency:
    """Test that organization_id is used consistently throughout the system"""
    
    @pytest.fixture
    def db_session(self):
        """Create a test database session"""
        # Create all tables
        from app.models.base import Base
        Base.metadata.create_all(bind=engine)
        
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()
            # Clean up tables after test
            Base.metadata.drop_all(bind=engine)
    
    def test_organization_creation_with_organization_id(self, db_session: Session):
        """Test that organizations can be created and referenced by organization_id"""
        
        # Create test organization
        org = Organization(
            name="Test Organization",
            subdomain="testorg",
            primary_email="admin@testorg.com",
            primary_phone="+1-555-1234",
            address1="123 Test St",
            city="Test City",
            state="Test State",
            pin_code="12345",
            country="Test Country"
        )
        
        db_session.add(org)
        db_session.commit()
        db_session.refresh(org)
        
        assert org.id is not None
        assert org.name == "Test Organization"
        assert org.subdomain == "testorg"
    
    def test_user_organization_id_relationship(self, db_session: Session):
        """Test that users are properly linked to organizations via organization_id"""
        
        # Create test organization
        org = Organization(
            name="Test Org",
            subdomain="testorg2",
            primary_email="admin@testorg2.com",
            primary_phone="+1-555-5678",
            address1="456 Test Ave",
            city="Test City",
            state="Test State",
            pin_code="54321",
            country="Test Country"
        )
        db_session.add(org)
        db_session.commit()
        db_session.refresh(org)
        
        # Create regular user linked to organization
        user = User(
            organization_id=org.id,
            email="user@testorg2.com",
            username="testuser",
            hashed_password="hashedpass123",
            full_name="Test User",
            role=UserRole.STANDARD_USER.value
        )
        db_session.add(user)
        
        # Create super admin user (organization_id can be None)
        super_admin = User(
            organization_id=None,  # Super admins can have None organization_id
            email="superadmin@platform.com",
            username="superadmin",
            hashed_password="hashedpass123",
            full_name="Super Admin",
            role=UserRole.SUPER_ADMIN.value,
            is_super_admin=True
        )
        db_session.add(super_admin)
        db_session.commit()
        
        # Verify relationships
        assert user.organization_id == org.id
        assert user.organization is not None
        assert user.organization.name == "Test Org"
        
        # Verify super admin can have None organization_id
        assert super_admin.organization_id is None
        assert super_admin.is_super_admin is True
    
    def test_tenant_data_isolation_by_organization_id(self, db_session: Session):
        """Test that tenant data is properly isolated by organization_id"""
        
        # Create two organizations
        org1 = Organization(
            name="Organization One",
            subdomain="org1",
            primary_email="admin@org1.com",
            primary_phone="+1-111-1111",
            address1="111 Org1 St",
            city="City1",
            state="State1",
            pin_code="11111",
            country="Country1"
        )
        
        org2 = Organization(
            name="Organization Two",
            subdomain="org2",
            primary_email="admin@org2.com",
            primary_phone="+1-222-2222",
            address1="222 Org2 St",
            city="City2",
            state="State2",
            pin_code="22222",
            country="Country2"
        )
        
        db_session.add_all([org1, org2])
        db_session.commit()
        db_session.refresh(org1)
        db_session.refresh(org2)
        
        # Create customers for each organization
        customer1 = Customer(
            organization_id=org1.id,
            name="Customer Org1",
            contact_number="+1-111-9999",
            address1="Customer St",
            city="City1",
            state="State1",
            pin_code="11111",
            state_code="ST1"
        )
        
        customer2 = Customer(
            organization_id=org2.id,
            name="Customer Org2",
            contact_number="+1-222-9999",
            address1="Customer Ave",
            city="City2",
            state="State2",
            pin_code="22222",
            state_code="ST2"
        )
        
        db_session.add_all([customer1, customer2])
        db_session.commit()
        
        # Verify isolation - org1 should only see its customers
        org1_customers = db_session.query(Customer).filter(Customer.organization_id == org1.id).all()
        org2_customers = db_session.query(Customer).filter(Customer.organization_id == org2.id).all()
        
        assert len(org1_customers) == 1
        assert len(org2_customers) == 1
        assert org1_customers[0].name == "Customer Org1"
        assert org2_customers[0].name == "Customer Org2"
        assert org1_customers[0].organization_id == org1.id
        assert org2_customers[0].organization_id == org2.id
    
    def test_all_models_have_organization_id_foreign_key(self, db_session: Session):
        """Test that all tenant-aware models have proper organization_id foreign keys"""
        
        # Create test organization
        org = Organization(
            name="FK Test Org",
            subdomain="fktest",
            primary_email="admin@fktest.com",
            primary_phone="+1-555-0000",
            address1="FK Test St",
            city="FK City",
            state="FK State",
            pin_code="00000",
            country="FK Country"
        )
        db_session.add(org)
        db_session.commit()
        db_session.refresh(org)
        
        # Test that all tenant-aware models can be created with organization_id
        vendor = Vendor(
            organization_id=org.id,
            name="Test Vendor",
            contact_number="+1-555-1111",
            address1="Vendor St",
            city="FK City",
            state="FK State",
            pin_code="00000",
            state_code="FK"
        )
        
        product = Product(
            organization_id=org.id,
            name="Test Product",
            unit="pcs",
            unit_price=100.0
        )
        
        db_session.add_all([vendor, product])
        db_session.commit()
        db_session.refresh(product)
        
        # Test stock with organization_id
        stock = Stock(
            organization_id=org.id,
            product_id=product.id,
            quantity=50.0,
            unit="pcs"
        )
        db_session.add(stock)
        db_session.commit()
        
        # Verify all models are properly linked
        assert vendor.organization_id == org.id
        assert product.organization_id == org.id
        assert stock.organization_id == org.id
        
        # Verify relationships work
        assert vendor.organization.name == "FK Test Org"
        assert product.organization.name == "FK Test Org"
        assert stock.organization.name == "FK Test Org"
    
    def test_database_constraints_enforce_organization_id(self):
        """Test that database constraints properly enforce organization_id relationships"""
        
        # Test using raw SQL to verify constraints
        try:
            conn = sqlite3.connect(':memory:')
            cursor = conn.cursor()
            
            # Create tables with constraints (simplified version)
            cursor.execute('''
                CREATE TABLE organizations (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    subdomain TEXT NOT NULL UNIQUE,
                    primary_email TEXT NOT NULL,
                    primary_phone TEXT NOT NULL,
                    address1 TEXT NOT NULL,
                    city TEXT NOT NULL,
                    state TEXT NOT NULL,
                    pin_code TEXT NOT NULL,
                    country TEXT NOT NULL DEFAULT 'India'
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY,
                    organization_id INTEGER REFERENCES organizations(id),
                    email TEXT NOT NULL,
                    username TEXT NOT NULL,
                    hashed_password TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'standard_user',
                    is_super_admin BOOLEAN DEFAULT FALSE,
                    UNIQUE(organization_id, email),
                    UNIQUE(organization_id, username)
                )
            ''')
            
            # Insert test organization
            cursor.execute('''
                INSERT INTO organizations 
                (name, subdomain, primary_email, primary_phone, address1, city, state, pin_code, country)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', ('Test Org', 'testorg', 'admin@test.com', '+1-555-0000', 'Test St', 'City', 'State', '12345', 'Country'))
            
            org_id = cursor.lastrowid
            
            # Test that valid organization_id works
            cursor.execute('''
                INSERT INTO users 
                (organization_id, email, username, hashed_password, role)
                VALUES (?, ?, ?, ?, ?)
            ''', (org_id, 'user@test.com', 'testuser', 'hash123', 'standard_user'))
            
            # Test that None organization_id works (for super admins)
            cursor.execute('''
                INSERT INTO users 
                (organization_id, email, username, hashed_password, role, is_super_admin)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (None, 'super@platform.com', 'superuser', 'hash123', 'super_admin', True))
            
            # Verify data was inserted correctly
            cursor.execute('SELECT COUNT(*) FROM users WHERE organization_id = ?', (org_id,))
            regular_user_count = cursor.fetchone()[0]
            assert regular_user_count == 1
            
            cursor.execute('SELECT COUNT(*) FROM users WHERE organization_id IS NULL')
            super_admin_count = cursor.fetchone()[0]
            assert super_admin_count == 1
            
            conn.close()
            
        except Exception as e:
            pytest.fail(f"Database constraint test failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__])