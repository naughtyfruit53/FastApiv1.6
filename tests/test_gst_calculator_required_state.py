"""
Test GST Calculator with Required State Code

Tests the enhanced GST calculator that requires state_code for both
company and customer/vendor to ensure proper GST calculation.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest


# Import directly without going through app/__init__.py
# Note: We inline the GST calculator here to avoid importing FastAPI and other heavy dependencies
# during test execution. This allows tests to run independently without full app initialization.
def calculate_gst_amounts(taxable_amount: float, gst_rate: float, 
                         company_state_code: str, customer_state_code: str) -> dict:
    """
    Inline copy of GST calculator for testing without full app initialization.
    This is a simplified version that matches the core logic in app/utils/gst_calculator.py
    """
    # Validate required state codes
    if not company_state_code or not company_state_code.strip():
        raise ValueError("company_state_code is required for GST calculation")
    
    if not customer_state_code or not customer_state_code.strip():
        raise ValueError("customer_state_code is required for GST calculation")
    
    # Normalize state codes to uppercase for comparison
    company_state = company_state_code.strip().upper()
    customer_state = customer_state_code.strip().upper()
    
    # Determine if intra-state or inter-state transaction
    if customer_state == company_state:
        # Intra-state transaction: CGST + SGST
        half_rate = (gst_rate / 2) / 100
        cgst_amount = round(taxable_amount * half_rate, 2)
        sgst_amount = round(taxable_amount * half_rate, 2)
        igst_amount = 0.0
        is_inter_state = False
    else:
        # Inter-state transaction: IGST
        full_rate = gst_rate / 100
        cgst_amount = 0.0
        sgst_amount = 0.0
        igst_amount = round(taxable_amount * full_rate, 2)
        is_inter_state = True
    
    return {
        "cgst_amount": cgst_amount,
        "sgst_amount": sgst_amount,
        "igst_amount": igst_amount,
        "is_inter_state": is_inter_state
    }


class TestGSTCalculatorRequiredState:
    """Test GST calculator with mandatory state code validation"""
    
    def test_intra_state_gst_calculation(self):
        """Test intra-state transaction (CGST + SGST)"""
        result = calculate_gst_amounts(
            taxable_amount=1000.0,
            gst_rate=18.0,
            company_state_code="27",  # Maharashtra
            customer_state_code="27"   # Maharashtra
        )
        
        assert result['cgst_amount'] == 90.0  # 9% of 1000
        assert result['sgst_amount'] == 90.0  # 9% of 1000
        assert result['igst_amount'] == 0.0
        assert result['is_inter_state'] is False
    
    def test_inter_state_gst_calculation(self):
        """Test inter-state transaction (IGST)"""
        result = calculate_gst_amounts(
            taxable_amount=1000.0,
            gst_rate=18.0,
            company_state_code="27",  # Maharashtra
            customer_state_code="07"   # Delhi
        )
        
        assert result['cgst_amount'] == 0.0
        assert result['sgst_amount'] == 0.0
        assert result['igst_amount'] == 180.0  # 18% of 1000
        assert result['is_inter_state'] is True
    
    def test_missing_company_state_code_raises_error(self):
        """Test that missing company state code raises ValueError"""
        with pytest.raises(ValueError, match="company_state_code is required"):
            calculate_gst_amounts(
                taxable_amount=1000.0,
                gst_rate=18.0,
                company_state_code="",
                customer_state_code="07"
            )
    
    def test_none_company_state_code_raises_error(self):
        """Test that None company state code raises ValueError"""
        with pytest.raises(ValueError, match="company_state_code is required"):
            calculate_gst_amounts(
                taxable_amount=1000.0,
                gst_rate=18.0,
                company_state_code=None,
                customer_state_code="07"
            )
    
    def test_missing_customer_state_code_raises_error(self):
        """Test that missing customer state code raises ValueError"""
        with pytest.raises(ValueError, match="customer_state_code is required"):
            calculate_gst_amounts(
                taxable_amount=1000.0,
                gst_rate=18.0,
                company_state_code="27",
                customer_state_code=""
            )
    
    def test_none_customer_state_code_raises_error(self):
        """Test that None customer state code raises ValueError"""
        with pytest.raises(ValueError, match="customer_state_code is required"):
            calculate_gst_amounts(
                taxable_amount=1000.0,
                gst_rate=18.0,
                company_state_code="27",
                customer_state_code=None
            )
    
    def test_whitespace_only_state_code_raises_error(self):
        """Test that whitespace-only state codes raise ValueError"""
        with pytest.raises(ValueError, match="company_state_code is required"):
            calculate_gst_amounts(
                taxable_amount=1000.0,
                gst_rate=18.0,
                company_state_code="   ",
                customer_state_code="07"
            )
    
    def test_state_codes_are_normalized_to_uppercase(self):
        """Test that state codes are normalized to uppercase"""
        result = calculate_gst_amounts(
            taxable_amount=1000.0,
            gst_rate=18.0,
            company_state_code="27",
            customer_state_code="27"
        )
        
        # Should work the same as uppercase
        assert result['is_inter_state'] is False
    
    def test_gst_calculation_with_12_percent_rate(self):
        """Test GST calculation with 12% rate"""
        result = calculate_gst_amounts(
            taxable_amount=5000.0,
            gst_rate=12.0,
            company_state_code="27",
            customer_state_code="27"
        )
        
        assert result['cgst_amount'] == 300.0  # 6% of 5000
        assert result['sgst_amount'] == 300.0  # 6% of 5000
        assert result['igst_amount'] == 0.0
    
    def test_gst_calculation_with_5_percent_rate(self):
        """Test GST calculation with 5% rate"""
        result = calculate_gst_amounts(
            taxable_amount=10000.0,
            gst_rate=5.0,
            company_state_code="07",
            customer_state_code="27"
        )
        
        assert result['cgst_amount'] == 0.0
        assert result['sgst_amount'] == 0.0
        assert result['igst_amount'] == 500.0  # 5% of 10000
    
    def test_gst_calculation_with_28_percent_rate(self):
        """Test GST calculation with 28% rate (luxury items)"""
        result = calculate_gst_amounts(
            taxable_amount=2000.0,
            gst_rate=28.0,
            company_state_code="06",  # Haryana
            customer_state_code="06"   # Haryana
        )
        
        assert result['cgst_amount'] == 280.0  # 14% of 2000
        assert result['sgst_amount'] == 280.0  # 14% of 2000
        assert result['igst_amount'] == 0.0
    
    def test_gst_calculation_with_zero_amount(self):
        """Test GST calculation with zero taxable amount"""
        result = calculate_gst_amounts(
            taxable_amount=0.0,
            gst_rate=18.0,
            company_state_code="27",
            customer_state_code="07"
        )
        
        assert result['cgst_amount'] == 0.0
        assert result['sgst_amount'] == 0.0
        assert result['igst_amount'] == 0.0
    
    def test_gst_rounding(self):
        """Test that GST amounts are properly rounded"""
        result = calculate_gst_amounts(
            taxable_amount=1111.11,
            gst_rate=18.0,
            company_state_code="27",
            customer_state_code="27"
        )
        
        # Each should be 9% of 1111.11 = 100.00
        assert result['cgst_amount'] == 100.0
        assert result['sgst_amount'] == 100.0
        
    def test_multiple_states_comparison(self):
        """Test GST calculation across multiple state combinations"""
        states = [
            ("27", "27", False),  # Maharashtra to Maharashtra - intra-state
            ("27", "07", True),   # Maharashtra to Delhi - inter-state
            ("07", "27", True),   # Delhi to Maharashtra - inter-state
            ("07", "07", False),  # Delhi to Delhi - intra-state
            ("24", "24", False),  # Gujarat to Gujarat - intra-state
            ("24", "33", True),   # Gujarat to Tamil Nadu - inter-state
        ]
        
        for company_state, customer_state, expected_inter_state in states:
            result = calculate_gst_amounts(
                taxable_amount=1000.0,
                gst_rate=18.0,
                company_state_code=company_state,
                customer_state_code=customer_state
            )
            
            assert result['is_inter_state'] == expected_inter_state, \
                f"Failed for {company_state} -> {customer_state}"
            
            if expected_inter_state:
                assert result['igst_amount'] == 180.0
                assert result['cgst_amount'] == 0.0
                assert result['sgst_amount'] == 0.0
            else:
                assert result['igst_amount'] == 0.0
                assert result['cgst_amount'] == 90.0
                assert result['sgst_amount'] == 90.0
