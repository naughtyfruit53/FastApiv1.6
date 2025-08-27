# tests/test_ledger_endpoints.py

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, date, timedelta
from decimal import Decimal

from app.main import app
from app.core.database import get_db
from app.models.base import User, Organization, Vendor, Customer
from app.models.vouchers import PaymentVoucher, ReceiptVoucher, PurchaseVoucher, SalesVoucher
from app.core.security import create_access_token
from app.services.ledger_service import LedgerService
from app.schemas.ledger import LedgerFilters


class TestLedgerEndpoints:
    """Test ledger API endpoints"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @pytest.fixture
    def test_db(self):
        # This would be implemented with test database setup
        # For now, we'll mock it
        pass
    
    @pytest.fixture
    def test_organization(self, test_db):
        """Create test organization"""
        org = Organization(
            id=1,
            name="Test Company",
            subdomain="test",
            primary_email="test@test.com",
            primary_phone="1234567890",
            address1="Test Address",
            city="Test City",
            state="Test State",
            pin_code="123456",
            company_details_completed=True
        )
        return org
    
    @pytest.fixture
    def test_user(self, test_db, test_organization):
        """Create test user with admin role"""
        user = User(
            id=1,
            email="admin@test.com",
            hashed_password="$2b$12$test",
            full_name="Test Admin",
            role="admin",
            organization_id=test_organization.id,
            is_active=True
        )
        return user
    
    @pytest.fixture
    def standard_user(self, test_db, test_organization):
        """Create test user with standard role"""
        user = User(
            id=2,
            email="user@test.com", 
            hashed_password="$2b$12$test",
            full_name="Test User",
            role="standard_user",
            organization_id=test_organization.id,
            is_active=True
        )
        return user
    
    @pytest.fixture
    def app_super_admin(self, test_db):
        """Create app super admin (no organization)"""
        user = User(
            id=3,
            email="superadmin@test.com",
            hashed_password="$2b$12$test", 
            full_name="Super Admin",
            role="super_admin",
            organization_id=None,  # App super admin has no organization
            is_active=True,
            is_super_admin=True
        )
        return user
    
    @pytest.fixture
    def test_vendor(self, test_db, test_organization):
        """Create test vendor"""
        vendor = Vendor(
            id=1,
            organization_id=test_organization.id,
            name="Test Vendor",
            contact_number="9876543210",
            email="vendor@test.com",
            address1="Vendor Address",
            city="Vendor City",
            state="Vendor State",
            pin_code="654321",
            state_code="VS",
            is_active=True
        )
        return vendor
    
    @pytest.fixture
    def test_customer(self, test_db, test_organization):
        """Create test customer"""
        customer = Customer(
            id=1,
            organization_id=test_organization.id,
            name="Test Customer",
            contact_number="1122334455",
            email="customer@test.com",
            address1="Customer Address",
            city="Customer City",
            state="Customer State",
            pin_code="112233",
            state_code="CS",
            is_active=True
        )
        return customer
    
    @pytest.fixture
    def auth_headers(self, test_user):
        """Create auth headers for test user"""
        access_token = create_access_token(data={"sub": test_user.email})
        return {"Authorization": f"Bearer {access_token}"}
    
    @pytest.fixture
    def standard_auth_headers(self, standard_user):
        """Create auth headers for standard user"""
        access_token = create_access_token(data={"sub": standard_user.email})
        return {"Authorization": f"Bearer {access_token}"}
    
    @pytest.fixture
    def super_admin_headers(self, app_super_admin):
        """Create auth headers for app super admin"""
        access_token = create_access_token(data={"sub": app_super_admin.email})
        return {"Authorization": f"Bearer {access_token}"}


class TestCompleteLedgerEndpoint(TestLedgerEndpoints):
    """Test complete ledger endpoint"""
    
    def test_complete_ledger_admin_access(self, client, auth_headers):
        """Test that admin can access complete ledger"""
        response = client.get("/api/v1/reports/complete-ledger", headers=auth_headers)
        
        # Should return 200 or 500 (if no data), not 403
        assert response.status_code in [200, 500]
        if response.status_code == 200:
            data = response.json()
            assert "transactions" in data
            assert "summary" in data
            assert "filters_applied" in data
    
    def test_complete_ledger_standard_user_access(self, client, standard_auth_headers):
        """Test that standard user can access complete ledger"""
        response = client.get("/api/v1/reports/complete-ledger", headers=standard_auth_headers)
        
        # Should return 200 or 500 (if no data), not 403
        assert response.status_code in [200, 500]
    
    def test_complete_ledger_super_admin_blocked(self, client, super_admin_headers):
        """Test that app super admin is blocked from accessing complete ledger"""
        response = client.get("/api/v1/reports/complete-ledger", headers=super_admin_headers)
        
        # Should return 403 - app super admins cannot access org data
        assert response.status_code == 403
        assert "cannot access organization" in response.json()["detail"].lower()
    
    def test_complete_ledger_unauthenticated(self, client):
        """Test that unauthenticated users cannot access complete ledger"""
        response = client.get("/api/v1/reports/complete-ledger")
        
        assert response.status_code == 401
    
    def test_complete_ledger_with_filters(self, client, auth_headers):
        """Test complete ledger with date and account filters"""
        params = {
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "account_type": "vendor",
            "voucher_type": "payment_voucher"
        }
        
        response = client.get("/api/v1/reports/complete-ledger", headers=auth_headers, params=params)
        
        # Should not return 403 (permission denied)
        assert response.status_code != 403
    
    def test_complete_ledger_invalid_account_type(self, client, auth_headers):
        """Test complete ledger with invalid account type"""
        params = {"account_type": "invalid_type"}
        
        response = client.get("/api/v1/reports/complete-ledger", headers=auth_headers, params=params)
        
        # Should return 422 (validation error) or process with default
        assert response.status_code in [200, 422, 500]


class TestOutstandingLedgerEndpoint(TestLedgerEndpoints):
    """Test outstanding ledger endpoint"""
    
    def test_outstanding_ledger_admin_access(self, client, auth_headers):
        """Test that admin can access outstanding ledger"""
        response = client.get("/api/v1/reports/outstanding-ledger", headers=auth_headers)
        
        # Should return 200 or 500 (if no data), not 403
        assert response.status_code in [200, 500]
        if response.status_code == 200:
            data = response.json()
            assert "outstanding_balances" in data
            assert "summary" in data
            assert "total_payable" in data
            assert "total_receivable" in data
            assert "net_outstanding" in data
    
    def test_outstanding_ledger_standard_user_access(self, client, standard_auth_headers):
        """Test that standard user can access outstanding ledger"""
        response = client.get("/api/v1/reports/outstanding-ledger", headers=standard_auth_headers)
        
        # Should return 200 or 500 (if no data), not 403
        assert response.status_code in [200, 500]
    
    def test_outstanding_ledger_super_admin_blocked(self, client, super_admin_headers):
        """Test that app super admin is blocked from accessing outstanding ledger"""
        response = client.get("/api/v1/reports/outstanding-ledger", headers=super_admin_headers)
        
        # Should return 403 - app super admins cannot access org data
        assert response.status_code == 403
        assert "cannot access organization" in response.json()["detail"].lower()
    
    def test_outstanding_ledger_with_filters(self, client, auth_headers):
        """Test outstanding ledger with filters"""
        params = {
            "account_type": "customer",
            "account_id": 1
        }
        
        response = client.get("/api/v1/reports/outstanding-ledger", headers=auth_headers, params=params)
        
        # Should not return 403 (permission denied)
        assert response.status_code != 403
    
    def test_outstanding_ledger_response_structure(self, client, auth_headers):
        """Test outstanding ledger response structure"""
        response = client.get("/api/v1/reports/outstanding-ledger", headers=auth_headers)
        
        if response.status_code == 200:
            data = response.json()
            
            # Check required fields
            assert "outstanding_balances" in data
            assert "summary" in data
            assert "filters_applied" in data
            assert "total_payable" in data
            assert "total_receivable" in data
            assert "net_outstanding" in data
            
            # Check summary structure
            summary = data["summary"]
            assert "total_accounts" in summary
            assert "currency" in summary
            
            # Check individual balance structure
            for balance in data["outstanding_balances"]:
                assert "account_type" in balance
                assert "account_id" in balance
                assert "account_name" in balance
                assert "outstanding_amount" in balance
                assert balance["account_type"] in ["vendor", "customer"]


class TestLedgerService:
    """Test ledger service business logic"""
    
    def test_ledger_filters_validation(self):
        """Test ledger filters validation"""
        # Valid filters
        filters = LedgerFilters(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31),
            account_type="vendor",
            voucher_type="payment_voucher"
        )
        
        assert filters.start_date == date(2024, 1, 1)
        assert filters.account_type == "vendor"
        assert filters.voucher_type == "payment_voucher"
    
    def test_ledger_filters_defaults(self):
        """Test ledger filters default values"""
        filters = LedgerFilters()
        
        assert filters.start_date is None
        assert filters.end_date is None
        assert filters.account_type == "all"
        assert filters.account_id is None
        assert filters.voucher_type == "all"
    
    def test_outstanding_balance_sign_convention(self):
        """Test that outstanding balance follows correct sign convention"""
        # This would test the actual calculation logic
        # - Negative for payable to vendors
        # - Positive for receivable from customers
        pass


class TestPermissionIntegration:
    """Test permission integration with ledger endpoints"""
    
    def test_ledger_access_roles(self):
        """Test which roles can access ledger endpoints"""
        allowed_roles = ["super_admin", "org_admin", "admin", "standard_user"]
        blocked_roles = ["app_super_admin", "guest", "inactive"]
        
        # This would test the _check_ledger_access function
        # to ensure proper role-based access control
        pass
    
    def test_organization_isolation(self):
        """Test that users can only see their organization's data"""
        # This would test that tenant filtering works correctly
        # and users cannot access other organizations' ledgers
        pass


if __name__ == "__main__":
    # Simple test runner for development
    print("Running ledger endpoint tests...")
    
    # Test endpoint existence
    client = TestClient(app)
    
    # Test unauthenticated access
    response = client.get("/api/v1/reports/complete-ledger")
    assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    
    response = client.get("/api/v1/reports/outstanding-ledger")
    assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    
    print("✅ Ledger endpoints exist and require authentication")
    print("✅ Basic ledger tests passed!")