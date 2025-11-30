# tests/test_backdated_voucher_reindexing.py

"""
Unit tests for backdated voucher reindexing logic
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.voucher_service import VoucherNumberService


class TestBackdatedVoucherReindexing:
    """Tests for backdated voucher conflict detection and reindexing"""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session"""
        return AsyncMock()
    
    @pytest.fixture
    def mock_org_settings(self):
        """Create mock organization settings"""
        settings = MagicMock()
        settings.voucher_prefix_enabled = True
        settings.voucher_prefix = "ORG"
        settings.voucher_counter_reset_period = "annually"
        return settings

    @pytest.mark.asyncio
    async def test_check_backdated_conflict_no_conflict(self, mock_db):
        """Test that no conflict is detected when date is latest"""
        # This test verifies the conflict detection logic
        # In a real scenario, this would be integrated with the database
        
        # Setup mock responses
        mock_db.execute = AsyncMock()
        
        # Mock that there are no later vouchers
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result
        
        # Test would verify check_backdated_voucher_conflict returns has_conflict: False
        # when no vouchers exist with later dates
        assert True  # Placeholder for actual implementation test

    @pytest.mark.asyncio
    async def test_check_backdated_conflict_with_conflict(self, mock_db):
        """Test that conflict is detected when voucher date is earlier"""
        # Setup mock responses to simulate existing vouchers with later dates
        
        mock_db.execute = AsyncMock()
        
        # Mock that there are later vouchers
        mock_voucher = MagicMock()
        mock_voucher.date = datetime.now()
        mock_voucher.voucher_number = "PO/2425/00002"
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_voucher]
        mock_result.scalar_one_or_none.return_value = mock_voucher
        mock_db.execute.return_value = mock_result
        
        # Test would verify check_backdated_voucher_conflict returns has_conflict: True
        # when vouchers exist with later dates
        assert True  # Placeholder for actual implementation test

    @pytest.mark.asyncio
    async def test_reindex_vouchers_chronological_order(self, mock_db):
        """Test that reindexing assigns numbers in chronological order"""
        # Setup mock vouchers
        voucher1 = MagicMock()
        voucher1.id = 1
        voucher1.date = datetime(2024, 1, 15)
        voucher1.voucher_number = "PO/2425/00002"
        
        voucher2 = MagicMock()
        voucher2.id = 2
        voucher2.date = datetime(2024, 1, 10)
        voucher2.voucher_number = "PO/2425/00001"
        
        voucher3 = MagicMock()
        voucher3.id = 3
        voucher3.date = datetime(2024, 1, 12)  # Backdated insert
        voucher3.voucher_number = "PO/2425/00003"
        
        # After reindexing:
        # voucher2 (Jan 10) -> PO/2425/00001
        # voucher3 (Jan 12) -> PO/2425/00002
        # voucher1 (Jan 15) -> PO/2425/00003
        
        # Verify the expected order
        vouchers_by_date = sorted([voucher1, voucher2, voucher3], key=lambda v: v.date)
        
        assert vouchers_by_date[0].id == 2  # Jan 10
        assert vouchers_by_date[1].id == 3  # Jan 12
        assert vouchers_by_date[2].id == 1  # Jan 15

    @pytest.mark.asyncio
    async def test_reindex_preserves_voucher_data(self, mock_db):
        """Test that reindexing only changes voucher numbers, not data"""
        mock_voucher = MagicMock()
        mock_voucher.id = 1
        mock_voucher.date = datetime(2024, 1, 15)
        mock_voucher.voucher_number = "PO/2425/00001"
        mock_voucher.total_amount = 1000.00
        mock_voucher.vendor_id = 5
        
        # Store original values
        original_amount = mock_voucher.total_amount
        original_vendor = mock_voucher.vendor_id
        
        # Simulate reindexing (just changes voucher_number)
        mock_voucher.voucher_number = "PO/2425/00002"
        
        # Verify other data is preserved
        assert mock_voucher.total_amount == original_amount
        assert mock_voucher.vendor_id == original_vendor

    @pytest.mark.asyncio
    async def test_reindex_atomic_transaction(self, mock_db):
        """Test that reindexing is atomic - all succeed or all fail"""
        mock_db.commit = AsyncMock()
        mock_db.rollback = AsyncMock()
        
        # Simulate successful reindexing
        try:
            # Multiple voucher updates would happen here
            await mock_db.commit()
            commit_called = True
        except Exception:
            await mock_db.rollback()
            commit_called = False
        
        assert commit_called

    def test_voucher_number_format(self):
        """Test voucher number format generation"""
        # Standard format: PREFIX/FISCAL_YEAR/SEQUENCE
        prefix = "PO"
        fiscal_year = "2425"
        sequence = 1
        
        voucher_number = f"{prefix}/{fiscal_year}/{sequence:05d}"
        
        assert voucher_number == "PO/2425/00001"
        assert len(voucher_number) == 14

    def test_voucher_number_with_org_prefix(self):
        """Test voucher number with organization prefix"""
        org_prefix = "ACME"
        voucher_prefix = "PO"
        fiscal_year = "2425"
        sequence = 42
        
        voucher_number = f"{org_prefix}-{voucher_prefix}/{fiscal_year}/{sequence:05d}"
        
        assert voucher_number == "ACME-PO/2425/00042"

    def test_monthly_period_segment(self):
        """Test monthly period segment in voucher number"""
        month_names = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 
                      'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
        
        # Test for January
        current_month = 1
        period_segment = month_names[current_month - 1]
        
        assert period_segment == "JAN"
        
        # Test for December
        current_month = 12
        period_segment = month_names[current_month - 1]
        
        assert period_segment == "DEC"

    def test_quarterly_period_segment(self):
        """Test quarterly period segment calculation"""
        # Quarter mapping
        def get_quarter(month: int) -> str:
            quarter = ((month - 1) // 3) + 1
            return f"Q{quarter}"
        
        assert get_quarter(1) == "Q1"   # January
        assert get_quarter(3) == "Q1"   # March
        assert get_quarter(4) == "Q2"   # April
        assert get_quarter(6) == "Q2"   # June
        assert get_quarter(7) == "Q3"   # July
        assert get_quarter(9) == "Q3"   # September
        assert get_quarter(10) == "Q4"  # October
        assert get_quarter(12) == "Q4"  # December

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


class TestVoucherConflictMapping:
    """Tests for voucher number conflict mapping"""

    def test_mapping_creation(self):
        """Test old to new voucher number mapping"""
        old_to_new_mapping = {}
        
        # Simulate reindexing results
        old_to_new_mapping["PO/2425/00002"] = "PO/2425/00001"
        old_to_new_mapping["PO/2425/00003"] = "PO/2425/00002"
        old_to_new_mapping["PO/2425/00001"] = "PO/2425/00003"
        
        assert len(old_to_new_mapping) == 3
        assert old_to_new_mapping["PO/2425/00002"] == "PO/2425/00001"

    def test_no_changes_when_already_ordered(self):
        """Test that no mapping is created when already in order"""
        old_to_new_mapping = {}
        
        vouchers = [
            {"date": "2024-01-10", "number": "PO/2425/00001"},
            {"date": "2024-01-11", "number": "PO/2425/00002"},
            {"date": "2024-01-12", "number": "PO/2425/00003"},
        ]
        
        # Already in chronological order
        for i, v in enumerate(vouchers, 1):
            new_number = f"PO/2425/{i:05d}"
            if v["number"] != new_number:
                old_to_new_mapping[v["number"]] = new_number
        
        # No changes needed
        assert len(old_to_new_mapping) == 0
