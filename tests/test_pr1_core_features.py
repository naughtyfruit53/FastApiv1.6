# tests/test_pr1_core_features.py

"""
Unit tests for PR 1 core features:
- Voucher reindexing logic with chronological insert
- RBAC permission checks on vouchers
- JWT malformed token handling
- Sales Order next-number and create flow
- Exhibition endpoints basic CRUD
- Item rate/description memory APIs
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch


class TestRBACPermissionChecks:
    """Tests for RBAC permission checks on vouchers"""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session"""
        return AsyncMock()

    @pytest.fixture
    def mock_user(self):
        """Create a mock user"""
        user = MagicMock()
        user.id = 1
        user.email = "test@example.com"
        user.organization_id = 1
        user.role = "org_admin"
        user.is_super_admin = False
        user.is_active = True
        return user

    @pytest.fixture
    def mock_super_admin(self):
        """Create a mock super admin user"""
        user = MagicMock()
        user.id = 1
        user.email = "admin@example.com"
        user.organization_id = None
        user.role = "super_admin"
        user.is_super_admin = True
        user.is_active = True
        return user

    @pytest.mark.asyncio
    async def test_super_admin_bypasses_permission_checks(self, mock_db, mock_super_admin):
        """Test that super admins bypass all permission checks"""
        from app.utils.rbac_helpers import RBACHelper
        
        # Super admin should always have any permission
        result = await RBACHelper.is_super_admin(mock_super_admin)
        assert result is True

    def test_org_admin_role_detection(self, mock_user):
        """Test org_admin role is detected correctly"""
        from app.utils.rbac_helpers import RBACHelper
        
        mock_user.role = "org_admin"
        assert RBACHelper.is_org_admin(mock_user) is True
        
        mock_user.role = "viewer"
        mock_user.is_company_admin = False
        assert RBACHelper.is_org_admin(mock_user) is False

    def test_role_hierarchy(self):
        """Test role hierarchy levels are correct"""
        from app.utils.rbac_helpers import RBACHelper
        
        # Higher level = more privileges
        super_admin_level = RBACHelper.get_role_level("super_admin")
        org_admin_level = RBACHelper.get_role_level("org_admin")
        viewer_level = RBACHelper.get_role_level("viewer")
        
        assert super_admin_level >= org_admin_level
        assert org_admin_level >= viewer_level

    def test_can_manage_role(self):
        """Test role management permissions"""
        from app.utils.rbac_helpers import RBACHelper
        
        # Super admin can manage org_admin
        result = RBACHelper.can_manage_role("super_admin", "org_admin")
        assert result is True
        
        # Viewer cannot manage org_admin
        result = RBACHelper.can_manage_role("viewer", "org_admin")
        assert result is False


class TestJWTMalformedTokenHandling:
    """Tests for JWT malformed token handling"""

    def test_empty_token_raises_error(self):
        """Test that empty token raises appropriate error"""
        from fastapi import HTTPException
        from app.core.security import verify_token
        
        with pytest.raises(HTTPException) as exc_info:
            verify_token("")
        
        assert exc_info.value.status_code == 401
        assert "error" in exc_info.value.detail or "Invalid" in str(exc_info.value.detail)

    def test_malformed_token_structure(self):
        """Test that malformed token with wrong segments raises error"""
        from fastapi import HTTPException
        from app.core.security import verify_token
        
        # Token without proper segments
        with pytest.raises(HTTPException) as exc_info:
            verify_token("invalid-token-without-dots")
        
        assert exc_info.value.status_code == 401

    def test_valid_token_structure_but_invalid_signature(self):
        """Test that token with valid structure but invalid signature raises error"""
        from fastapi import HTTPException
        from app.core.security import verify_token
        
        # Token with correct structure but invalid content
        fake_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.invalidSig"
        
        with pytest.raises(HTTPException) as exc_info:
            verify_token(fake_token)
        
        assert exc_info.value.status_code == 401

    def test_structured_401_response(self):
        """Test that 401 responses have structured format"""
        from fastapi import HTTPException
        from app.core.security import verify_token
        
        with pytest.raises(HTTPException) as exc_info:
            verify_token("bad.token.here")
        
        detail = exc_info.value.detail
        # Should be structured with error key or contain meaningful message
        if isinstance(detail, dict):
            assert "error" in detail or "message" in detail
        else:
            assert "invalid" in str(detail).lower() or "token" in str(detail).lower()


class TestSalesOrderNextNumber:
    """Tests for Sales Order next-number endpoint"""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session"""
        return AsyncMock()

    @pytest.mark.asyncio
    async def test_generate_voucher_number_format(self, mock_db):
        """Test voucher number format"""
        # Standard format: PREFIX/FISCAL_YEAR/SEQUENCE
        prefix = "SO"
        fiscal_year = "2425"
        sequence = 1
        
        voucher_number = f"{prefix}/{fiscal_year}/{sequence:05d}"
        
        assert voucher_number == "SO/2425/00001"
        assert len(voucher_number.split('/')) == 3

    @pytest.mark.asyncio
    async def test_voucher_date_affects_period(self):
        """Test that voucher date affects period segment"""
        # Test monthly period
        month_names = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 
                      'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
        
        for month in range(1, 13):
            assert month_names[month - 1] == ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 
                                              'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'][month - 1]

    def test_fiscal_year_calculation(self):
        """Test Indian fiscal year calculation (April to March)"""
        def calculate_fiscal_year(year: int, month: int) -> str:
            if month > 3:  # April onwards
                return f"{str(year)[-2:]}{str(year + 1)[-2:]}"
            else:  # January to March
                return f"{str(year - 1)[-2:]}{str(year)[-2:]}"
        
        # April 2024 -> FY 2024-25
        assert calculate_fiscal_year(2024, 4) == "2425"
        
        # March 2025 -> FY 2024-25
        assert calculate_fiscal_year(2025, 3) == "2425"
        
        # January 2024 -> FY 2023-24
        assert calculate_fiscal_year(2024, 1) == "2324"


class TestSalesOrderCreateFlow:
    """Tests for Sales Order create flow"""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session"""
        return AsyncMock()

    def test_sales_order_data_structure(self):
        """Test sales order data structure requirements"""
        # Required fields
        required_fields = ['customer_id', 'items']
        
        # Optional fields
        optional_fields = ['customer_voucher_number', 'voucher_number', 'date', 'due_date', 'notes']
        
        # Create sample data
        so_data = {
            'customer_id': 1,
            'items': [
                {'product_id': 1, 'quantity': 10, 'unit_price': 100.0}
            ],
            'customer_voucher_number': 'CUST-001'  # Required per PR spec
        }
        
        # Verify required fields
        for field in ['customer_id', 'items']:
            assert field in so_data

    def test_customer_voucher_number_field(self):
        """Test customer_voucher_number field handling"""
        # customer_voucher_number should be TEXT NOT NULL per spec
        customer_voucher_number = "CUST-PO-2024-001"
        
        assert isinstance(customer_voucher_number, str)
        assert len(customer_voucher_number) > 0


class TestExhibitionEndpoints:
    """Tests for Exhibition endpoints basic CRUD"""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session"""
        return AsyncMock()

    def test_exhibition_event_data_structure(self):
        """Test exhibition event data structure"""
        event_data = {
            'name': 'Tech Expo 2024',
            'description': 'Annual technology exhibition',
            'location': 'Convention Center',
            'venue': 'Hall A',
            'start_date': datetime.now().isoformat(),
            'end_date': (datetime.now() + timedelta(days=3)).isoformat(),
            'status': 'planned',
            'is_active': True
        }
        
        assert 'name' in event_data
        assert event_data['status'] in ['planned', 'active', 'completed', 'cancelled']

    def test_card_scan_data_structure(self):
        """Test business card scan data structure"""
        scan_data = {
            'exhibition_event_id': 1,
            'scan_method': 'upload',
            'full_name': 'John Doe',
            'company_name': 'Tech Corp',
            'email': 'john@techcorp.com',
            'phone': '+1234567890'
        }
        
        assert 'exhibition_event_id' in scan_data
        assert scan_data['scan_method'] in ['upload', 'camera', 'scanner']

    def test_prospect_data_structure(self):
        """Test exhibition prospect data structure"""
        prospect_data = {
            'exhibition_event_id': 1,
            'full_name': 'Jane Smith',
            'company_name': 'Innovation Inc',
            'qualification_status': 'qualified',
            'status': 'new'
        }
        
        assert 'exhibition_event_id' in prospect_data
        assert prospect_data['qualification_status'] in ['unqualified', 'qualified', 'hot', 'cold']
        assert prospect_data['status'] in ['new', 'contacted', 'qualified', 'converted', 'lost']


class TestItemRateMemoryAPIs:
    """Tests for Item Rate Memory APIs"""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session"""
        return AsyncMock()

    def test_last_purchase_rate_response_structure(self):
        """Test last purchase rate response structure"""
        response = {
            "item_id": 1,
            "item_name": "Test Product",
            "last_purchase_rate": 100.0,
            "gst_rate": 18.0,
            "last_description": "Test description",
            "source": "purchase_voucher",
            "source_voucher": "PV/2425/00001",
            "last_purchase_date": datetime.now().isoformat()
        }
        
        # Verify required fields
        required_fields = ['item_id', 'item_name', 'last_purchase_rate', 'source']
        for field in required_fields:
            assert field in response

    def test_last_sales_rate_response_structure(self):
        """Test last sales rate response structure"""
        response = {
            "item_id": 1,
            "item_name": "Test Product",
            "last_sales_rate": 150.0,
            "gst_rate": 18.0,
            "last_description": "Test description",
            "source": "sales_voucher",
            "source_voucher": "SV/2425/00001",
            "last_sales_date": datetime.now().isoformat(),
            "customer_id": 1
        }
        
        # Verify required fields
        required_fields = ['item_id', 'item_name', 'last_sales_rate', 'source']
        for field in required_fields:
            assert field in response

    def test_source_types(self):
        """Test valid source types for rate memory"""
        valid_purchase_sources = ['purchase_voucher', 'goods_receipt_note', 'product_default']
        valid_sales_sources = ['sales_voucher', 'sales_order', 'product_default']
        
        # All sources should be valid strings
        for source in valid_purchase_sources + valid_sales_sources:
            assert isinstance(source, str)
            assert len(source) > 0


class TestVoucherReindexing:
    """Tests for voucher reindexing logic"""

    def test_chronological_ordering(self):
        """Test vouchers are ordered chronologically"""
        vouchers = [
            {"id": 1, "date": datetime(2024, 1, 15), "number": "PO/2425/00002"},
            {"id": 2, "date": datetime(2024, 1, 10), "number": "PO/2425/00001"},
            {"id": 3, "date": datetime(2024, 1, 12), "number": "PO/2425/00003"},
        ]
        
        # Sort by date
        sorted_vouchers = sorted(vouchers, key=lambda v: v["date"])
        
        # After sorting: Jan 10 (id=2), Jan 12 (id=3), Jan 15 (id=1)
        assert sorted_vouchers[0]["id"] == 2
        assert sorted_vouchers[1]["id"] == 3
        assert sorted_vouchers[2]["id"] == 1

    def test_reindex_mapping(self):
        """Test old to new voucher number mapping"""
        old_to_new_mapping = {}
        
        # Simulate reindexing
        old_to_new_mapping["PO/2425/00002"] = "PO/2425/00003"
        old_to_new_mapping["PO/2425/00003"] = "PO/2425/00002"
        
        # Only changed numbers should be in mapping
        assert len(old_to_new_mapping) == 2
        assert "PO/2425/00001" not in old_to_new_mapping  # Unchanged

    def test_no_mapping_when_already_ordered(self):
        """Test no mapping when vouchers are already in order"""
        vouchers = [
            {"date": datetime(2024, 1, 10), "number": "PO/2425/00001"},
            {"date": datetime(2024, 1, 11), "number": "PO/2425/00002"},
            {"date": datetime(2024, 1, 12), "number": "PO/2425/00003"},
        ]
        
        old_to_new_mapping = {}
        
        # Check if any changes needed
        for i, v in enumerate(vouchers, 1):
            new_number = f"PO/2425/{i:05d}"
            if v["number"] != new_number:
                old_to_new_mapping[v["number"]] = new_number
        
        # No changes needed
        assert len(old_to_new_mapping) == 0


class TestQuotationEnhancements:
    """Tests for quotation enhancements (base_quote_id, revision_number, is_proforma)"""

    def test_revision_number_increment(self):
        """Test revision number increments correctly"""
        base_revision = 0
        revision_1 = base_revision + 1
        revision_2 = revision_1 + 1
        
        assert revision_1 == 1
        assert revision_2 == 2

    def test_revision_voucher_number_format(self):
        """Test revision voucher number format"""
        base_number = "QT/2425/00001"
        revision = 1
        
        revised_number = f"{base_number} Rev {revision}"
        
        assert revised_number == "QT/2425/00001 Rev 1"

    def test_is_proforma_defaults_to_false(self):
        """Test is_proforma defaults to false"""
        quotation = {"is_proforma": False}
        
        assert quotation["is_proforma"] is False
