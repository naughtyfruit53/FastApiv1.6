#!/usr/bin/env python3
"""
Test script to verify PDF generation with bank details and address merging
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.pdf_generation_service import VoucherPDFGenerator
from app.models.erp_models import BankAccount
from app.models.system_models import Company
from sqlalchemy.orm import Session
from unittest.mock import MagicMock, patch

def test_bank_details_integration():
    """Test that bank details are properly included in company branding"""
    
    # Mock database session
    db = MagicMock(spec=Session)
    
    # Mock company
    mock_company = MagicMock(spec=Company)
    mock_company.name = "Test Company Ltd"
    mock_company.address1 = "123 Test Street"
    mock_company.address2 = "Suite 456"
    mock_company.city = "Mumbai"
    mock_company.state = "Maharashtra"
    mock_company.pin_code = "400001"
    mock_company.state_code = "27"
    mock_company.gst_number = "27ABCDE1234F1Z5"
    mock_company.pan_number = "ABCDE1234F"
    mock_company.contact_number = "+91-9876543210"
    mock_company.email = "test@company.com"
    mock_company.website = "www.testcompany.com"
    
    # Mock bank account
    mock_bank_account = MagicMock(spec=BankAccount)
    mock_bank_account.bank_name = "HDFC Bank"
    mock_bank_account.branch_name = "Mumbai Central"
    mock_bank_account.account_number = "1234567890"
    mock_bank_account.ifsc_code = "HDFC0001234"
    
    # Setup query mocks
    db.query.return_value.filter.return_value.first.side_effect = [
        mock_company,  # First call for company
        mock_bank_account,  # Second call for bank account (default)
    ]
    
    # Test the PDF generator
    generator = VoucherPDFGenerator()
    company_branding = generator._get_company_branding(db, 1)
    
    # Verify bank details are included
    assert company_branding is not None
    assert company_branding['name'] == "Test Company Ltd"
    assert company_branding['bank_details'] is not None
    assert company_branding['bank_details']['bank_name'] == "HDFC Bank"
    assert company_branding['bank_details']['account_number'] == "1234567890"
    assert company_branding['bank_details']['ifsc'] == "HDFC0001234"
    assert company_branding['bank_details']['holder_name'] == "Test Company Ltd"
    
    print("✅ Bank details integration test passed!")

def test_address_merging():
    """Test that vendor/customer addresses are properly merged"""
    
    # Mock database session
    db = MagicMock(spec=Session)
    
    # Mock company (minimal for testing)
    mock_company = MagicMock(spec=Company)
    mock_company.name = "Test Company"
    mock_company.state_code = "27"
    
    db.query.return_value.filter.return_value.first.side_effect = [
        mock_company,  # First call for company
        None,  # No bank account
    ]
    
    # Test data with vendor having address1 and address2
    voucher_data = {
        'vendor': {
            'name': 'Test Vendor',
            'address1': '789 Vendor Street',
            'address2': 'Floor 2',
            'city': 'Delhi',
            'state': 'Delhi',
            'pin_code': '110001',
            'state_code': '07'
        },
        'items': []
    }
    
    generator = VoucherPDFGenerator()
    
    # Mock the _get_company_branding method to avoid file system operations
    with patch.object(generator, '_get_company_branding') as mock_branding:
        mock_branding.return_value = {
            'name': 'Test Company',
            'state_code': '27',
            'bank_details': None
        }
        
        prepared_data = generator._prepare_voucher_data("purchase_voucher", voucher_data, db, 1)
    
    # Verify address merging
    vendor = prepared_data['vendor']
    assert vendor['address'] == '789 Vendor Street, Floor 2'
    
    print("✅ Address merging test passed!")

def test_address_merging_single_line():
    """Test address merging when only one address line exists"""
    
    # Mock database session
    db = MagicMock(spec=Session)
    
    # Test data with vendor having only address1
    voucher_data = {
        'vendor': {
            'name': 'Test Vendor',
            'address1': '789 Vendor Street',
            'address2': '',  # Empty address2
            'city': 'Delhi',
            'state': 'Delhi',
            'pin_code': '110001',
            'state_code': '07'
        },
        'items': []
    }
    
    generator = VoucherPDFGenerator()
    
    # Mock the _get_company_branding method
    with patch.object(generator, '_get_company_branding') as mock_branding:
        mock_branding.return_value = {
            'name': 'Test Company',
            'state_code': '27',
            'bank_details': None
        }
        
        prepared_data = generator._prepare_voucher_data("purchase_voucher", voucher_data, db, 1)
    
    # Verify address merging with single line
    vendor = prepared_data['vendor']
    assert vendor['address'] == '789 Vendor Street'
    
    print("✅ Single address line test passed!")

if __name__ == "__main__":
    print("Running PDF generation tests...")
    test_bank_details_integration()
    test_address_merging()
    test_address_merging_single_line()
    print("🎉 All tests passed!")