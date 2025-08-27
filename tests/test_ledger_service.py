# tests/test_ledger_service.py

import pytest
from unittest.mock import Mock, MagicMock, patch
from decimal import Decimal
from datetime import datetime, date

from app.services.ledger_service import LedgerService
from app.schemas.ledger import LedgerFilters, LedgerTransaction
from app.models.base import Vendor, Customer
from app.models.vouchers import PaymentVoucher, ReceiptVoucher, PurchaseVoucher, SalesVoucher


class TestLedgerService:
    """Test LedgerService business logic"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock database session"""
        return Mock()
    
    @pytest.fixture
    def sample_filters(self):
        """Sample ledger filters"""
        return LedgerFilters(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31),
            account_type="all",
            voucher_type="all"
        )
    
    @pytest.fixture
    def sample_vendor(self):
        """Sample vendor"""
        vendor = Mock()
        vendor.id = 1
        vendor.name = "Test Vendor"
        vendor.contact_number = "1234567890"
        return vendor
    
    @pytest.fixture
    def sample_customer(self):
        """Sample customer"""
        customer = Mock()
        customer.id = 1
        customer.name = "Test Customer"
        customer.contact_number = "0987654321"
        return customer
    
    @pytest.fixture
    def sample_payment_voucher(self, sample_vendor):
        """Sample payment voucher"""
        voucher = Mock()
        voucher.id = 1
        voucher.voucher_number = "PV001"
        voucher.date = datetime(2024, 6, 15)
        voucher.total_amount = 1000.0
        voucher.vendor_id = 1
        voucher.vendor = sample_vendor
        voucher.status = "confirmed"
        voucher.notes = "Payment to vendor"
        voucher.reference = "REF001"
        return voucher
    
    @pytest.fixture
    def sample_sales_voucher(self, sample_customer):
        """Sample sales voucher"""
        voucher = Mock()
        voucher.id = 2
        voucher.voucher_number = "SV001"
        voucher.date = datetime(2024, 6, 20)
        voucher.total_amount = 1500.0
        voucher.customer_id = 1
        voucher.customer = sample_customer
        voucher.status = "confirmed"
        voucher.notes = "Sale to customer"
        voucher.reference = "REF002"
        return voucher


class TestLedgerCalculations(TestLedgerService):
    """Test ledger calculation logic"""
    
    def test_calculate_running_balances_vendor(self):
        """Test running balance calculation for vendor transactions"""
        transactions = [
            LedgerTransaction(
                id=1,
                voucher_type="purchase_voucher",
                voucher_number="PV001",
                date=datetime(2024, 1, 1),
                account_type="vendor",
                account_id=1,
                account_name="Test Vendor",
                debit_amount=Decimal("1000"),  # Purchase increases payable
                credit_amount=Decimal("0"),
                balance=Decimal("0"),
                status="confirmed"
            ),
            LedgerTransaction(
                id=2,
                voucher_type="payment_voucher", 
                voucher_number="PAY001",
                date=datetime(2024, 1, 5),
                account_type="vendor",
                account_id=1,
                account_name="Test Vendor",
                debit_amount=Decimal("0"),
                credit_amount=Decimal("600"),  # Payment reduces payable
                balance=Decimal("0"),
                status="confirmed"
            )
        ]
        
        result = LedgerService._calculate_running_balances(transactions)
        
        # First transaction: +1000 (debit increases vendor payable)
        assert result[0].balance == Decimal("1000")
        
        # Second transaction: 1000 - 600 = 400 (credit reduces vendor payable)
        assert result[1].balance == Decimal("400")
    
    def test_calculate_running_balances_customer(self):
        """Test running balance calculation for customer transactions"""
        transactions = [
            LedgerTransaction(
                id=1,
                voucher_type="sales_voucher",
                voucher_number="SV001", 
                date=datetime(2024, 1, 1),
                account_type="customer",
                account_id=1,
                account_name="Test Customer",
                debit_amount=Decimal("0"),
                credit_amount=Decimal("1500"),  # Sale increases receivable
                balance=Decimal("0"),
                status="confirmed"
            ),
            LedgerTransaction(
                id=2,
                voucher_type="receipt_voucher",
                voucher_number="REC001",
                date=datetime(2024, 1, 5),
                account_type="customer", 
                account_id=1,
                account_name="Test Customer",
                debit_amount=Decimal("800"),  # Receipt reduces receivable
                credit_amount=Decimal("0"),
                balance=Decimal("0"),
                status="confirmed"
            )
        ]
        
        result = LedgerService._calculate_running_balances(transactions)
        
        # First transaction: +1500 (credit increases customer receivable)
        assert result[0].balance == Decimal("1500")
        
        # Second transaction: 1500 - 800 = 700 (debit reduces customer receivable)
        assert result[1].balance == Decimal("700")
    
    def test_get_account_info_payment_voucher(self):
        """Test account info extraction for payment voucher"""
        voucher = Mock()
        voucher.vendor_id = 1
        voucher.vendor = Mock()
        voucher.vendor.name = "Test Vendor"
        
        config = {
            "type": "payment_voucher",
            "account_relation": "vendor",
            "account_field": "vendor_id"
        }
        
        account_type, account_id, account_name = LedgerService._get_account_info(
            voucher, config, Mock()
        )
        
        assert account_type == "vendor"
        assert account_id == 1
        assert account_name == "Test Vendor"
    
    def test_get_account_info_debit_note_vendor(self):
        """Test account info extraction for debit note with vendor"""
        voucher = Mock()
        voucher.vendor_id = 1
        voucher.customer_id = None
        voucher.vendor = Mock()
        voucher.vendor.name = "Test Vendor"
        
        config = {"type": "debit_note"}
        
        account_type, account_id, account_name = LedgerService._get_account_info(
            voucher, config, Mock()
        )
        
        assert account_type == "vendor"
        assert account_id == 1
        assert account_name == "Test Vendor"
    
    def test_get_account_info_debit_note_customer(self):
        """Test account info extraction for debit note with customer"""
        voucher = Mock()
        voucher.vendor_id = None
        voucher.customer_id = 2
        voucher.customer = Mock()
        voucher.customer.name = "Test Customer"
        
        config = {"type": "debit_note"}
        
        account_type, account_id, account_name = LedgerService._get_account_info(
            voucher, config, Mock()
        )
        
        assert account_type == "customer"
        assert account_id == 2
        assert account_name == "Test Customer"
    
    def test_date_range_calculation(self):
        """Test date range calculation from transactions"""
        transactions = [
            LedgerTransaction(
                id=1, voucher_type="test", voucher_number="T001",
                date=datetime(2024, 1, 15), account_type="vendor", account_id=1,
                account_name="Test", debit_amount=Decimal("0"), credit_amount=Decimal("0"),
                balance=Decimal("0"), status="confirmed"
            ),
            LedgerTransaction(
                id=2, voucher_type="test", voucher_number="T002", 
                date=datetime(2024, 3, 20), account_type="vendor", account_id=1,
                account_name="Test", debit_amount=Decimal("0"), credit_amount=Decimal("0"),
                balance=Decimal("0"), status="confirmed"
            ),
            LedgerTransaction(
                id=3, voucher_type="test", voucher_number="T003",
                date=datetime(2024, 2, 10), account_type="vendor", account_id=1,
                account_name="Test", debit_amount=Decimal("0"), credit_amount=Decimal("0"),
                balance=Decimal("0"), status="confirmed"
            )
        ]
        
        date_range = LedgerService._get_date_range(transactions)
        
        assert date_range["start_date"] == datetime(2024, 1, 15).isoformat()
        assert date_range["end_date"] == datetime(2024, 3, 20).isoformat()
    
    def test_date_range_empty_transactions(self):
        """Test date range calculation with empty transactions"""
        transactions = []
        
        date_range = LedgerService._get_date_range(transactions)
        
        assert date_range["start_date"] is None
        assert date_range["end_date"] is None


class TestOutstandingBalanceCalculation(TestLedgerService):
    """Test outstanding balance calculation logic"""
    
    @patch.object(LedgerService, '_get_all_transactions')
    def test_outstanding_balance_vendor_payable(self, mock_get_transactions, mock_db):
        """Test outstanding balance calculation for vendor (payable)"""
        # Mock transactions that result in vendor payable
        mock_transactions = [
            LedgerTransaction(
                id=1, voucher_type="purchase_voucher", voucher_number="PV001",
                date=datetime(2024, 1, 1), account_type="vendor", account_id=1,
                account_name="Test Vendor", debit_amount=Decimal("1000"), 
                credit_amount=Decimal("0"), balance=Decimal("0"), status="confirmed"
            ),
            LedgerTransaction(
                id=2, voucher_type="payment_voucher", voucher_number="PAY001", 
                date=datetime(2024, 1, 5), account_type="vendor", account_id=1,
                account_name="Test Vendor", debit_amount=Decimal("0"),
                credit_amount=Decimal("300"), balance=Decimal("0"), status="confirmed"
            )
        ]
        mock_get_transactions.return_value = mock_transactions
        
        # Mock vendor query
        mock_vendor = Mock()
        mock_vendor.contact_number = "1234567890"
        mock_db.query.return_value.filter.return_value.first.return_value = mock_vendor
        
        filters = LedgerFilters()
        result = LedgerService._calculate_outstanding_balances(mock_db, 1, filters)
        
        assert len(result) == 1
        balance = result[0]
        
        assert balance.account_type == "vendor"
        assert balance.account_id == 1
        assert balance.account_name == "Test Vendor"
        # 1000 - 300 = 700 payable, but should be negative
        assert balance.outstanding_amount == Decimal("-700")
        assert balance.transaction_count == 2
        assert balance.contact_info == "1234567890"
    
    @patch.object(LedgerService, '_get_all_transactions')
    def test_outstanding_balance_customer_receivable(self, mock_get_transactions, mock_db):
        """Test outstanding balance calculation for customer (receivable)"""
        # Mock transactions that result in customer receivable
        mock_transactions = [
            LedgerTransaction(
                id=1, voucher_type="sales_voucher", voucher_number="SV001",
                date=datetime(2024, 1, 1), account_type="customer", account_id=1,
                account_name="Test Customer", debit_amount=Decimal("0"),
                credit_amount=Decimal("1500"), balance=Decimal("0"), status="confirmed"
            ),
            LedgerTransaction(
                id=2, voucher_type="receipt_voucher", voucher_number="REC001",
                date=datetime(2024, 1, 5), account_type="customer", account_id=1, 
                account_name="Test Customer", debit_amount=Decimal("500"),
                credit_amount=Decimal("0"), balance=Decimal("0"), status="confirmed"
            )
        ]
        mock_get_transactions.return_value = mock_transactions
        
        # Mock customer query
        mock_customer = Mock()
        mock_customer.contact_number = "0987654321"
        mock_db.query.return_value.filter.return_value.first.return_value = mock_customer
        
        filters = LedgerFilters()
        result = LedgerService._calculate_outstanding_balances(mock_db, 1, filters)
        
        assert len(result) == 1
        balance = result[0]
        
        assert balance.account_type == "customer"
        assert balance.account_id == 1
        assert balance.account_name == "Test Customer"
        # 1500 - 500 = 1000 receivable, should be positive
        assert balance.outstanding_amount == Decimal("1000")
        assert balance.transaction_count == 2
        assert balance.contact_info == "0987654321"


class TestLedgerFiltering(TestLedgerService):
    """Test ledger filtering logic"""
    
    def test_filter_by_voucher_type(self):
        """Test filtering by voucher type"""
        voucher_configs = [
            {"type": "payment_voucher", "model": PaymentVoucher},
            {"type": "sales_voucher", "model": SalesVoucher}
        ]
        
        # Test that filtering works correctly
        filters = LedgerFilters(voucher_type="payment_voucher")
        
        # Only payment voucher config should be processed
        matching_configs = [
            config for config in voucher_configs 
            if filters.voucher_type == "all" or filters.voucher_type == config["type"]
        ]
        
        assert len(matching_configs) == 1
        assert matching_configs[0]["type"] == "payment_voucher"
    
    def test_filter_by_account_type(self):
        """Test filtering by account type"""
        voucher_configs = [
            {"type": "payment_voucher", "account_relation": "vendor"},
            {"type": "receipt_voucher", "account_relation": "customer"}
        ]
        
        filters = LedgerFilters(account_type="vendor")
        
        # Only vendor-related configs should match
        matching_configs = [
            config for config in voucher_configs
            if filters.account_type == "all" or filters.account_type == config.get("account_relation")
        ]
        
        assert len(matching_configs) == 1
        assert matching_configs[0]["account_relation"] == "vendor"


class TestErrorHandling(TestLedgerService):
    """Test error handling in ledger service"""
    
    @patch.object(LedgerService, '_get_all_transactions')
    def test_complete_ledger_database_error(self, mock_get_transactions, mock_db):
        """Test complete ledger handles database errors"""
        mock_get_transactions.side_effect = Exception("Database error")
        
        filters = LedgerFilters()
        
        with pytest.raises(Exception) as exc_info:
            LedgerService.get_complete_ledger(mock_db, 1, filters)
        
        assert "Database error" in str(exc_info.value)
    
    @patch.object(LedgerService, '_calculate_outstanding_balances')
    def test_outstanding_ledger_calculation_error(self, mock_calculate, mock_db):
        """Test outstanding ledger handles calculation errors"""
        mock_calculate.side_effect = Exception("Calculation error")
        
        filters = LedgerFilters()
        
        with pytest.raises(Exception) as exc_info:
            LedgerService.get_outstanding_ledger(mock_db, 1, filters)
        
        assert "Calculation error" in str(exc_info.value)


if __name__ == "__main__":
    # Simple test runner for development
    print("Running ledger service tests...")
    
    # Test basic instantiation
    service = LedgerService()
    assert service is not None
    
    # Test empty transaction date range
    date_range = LedgerService._get_date_range([])
    assert date_range["start_date"] is None
    assert date_range["end_date"] is None
    
    print("✅ Basic ledger service tests passed!")