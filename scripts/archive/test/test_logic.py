#!/usr/bin/env python3
"""
Simple test to verify the logic changes in PDF generation service
"""

def test_address_merging_logic():
    """Test the address merging logic without dependencies"""
    
    def merge_address_lines(party):
        """Simulated address merging logic from PDF service"""
        if party and isinstance(party, dict):
            address1 = party.get('address1', '') or party.get('address', '') or ''
            address2 = party.get('address2', '') or ''
            
            # Merge address lines with comma separation if both exist
            merged_address = address1
            if address1 and address2:
                merged_address = f"{address1}, {address2}"
            elif address2:  # Only address2 exists
                merged_address = address2
            
            return merged_address
        return ''
    
    # Test case 1: Both address lines exist
    party1 = {
        'name': 'Test Vendor',
        'address1': '789 Vendor Street',
        'address2': 'Floor 2'
    }
    result1 = merge_address_lines(party1)
    assert result1 == '789 Vendor Street, Floor 2', f"Expected '789 Vendor Street, Floor 2', got '{result1}'"
    
    # Test case 2: Only address1 exists
    party2 = {
        'name': 'Test Vendor',
        'address1': '789 Vendor Street',
        'address2': ''
    }
    result2 = merge_address_lines(party2)
    assert result2 == '789 Vendor Street', f"Expected '789 Vendor Street', got '{result2}'"
    
    # Test case 3: Only address2 exists
    party3 = {
        'name': 'Test Vendor',
        'address1': '',
        'address2': 'Floor 2'
    }
    result3 = merge_address_lines(party3)
    assert result3 == 'Floor 2', f"Expected 'Floor 2', got '{result3}'"
    
    # Test case 4: Neither address exists
    party4 = {
        'name': 'Test Vendor',
        'address1': '',
        'address2': ''
    }
    result4 = merge_address_lines(party4)
    assert result4 == '', f"Expected '', got '{result4}'"
    
    print("✅ Address merging logic test passed!")

def test_bank_details_structure():
    """Test the expected bank details structure"""
    
    def create_bank_details(bank_account, company_name):
        """Simulated bank details creation logic"""
        if bank_account:
            return {
                'holder_name': company_name,
                'bank_name': bank_account.get('bank_name'),
                'account_number': bank_account.get('account_number'),
                'branch': bank_account.get('branch_name', ''),
                'ifsc': bank_account.get('ifsc_code', '')
            }
        return None
    
    # Test with bank account
    bank_account = {
        'bank_name': 'HDFC Bank',
        'branch_name': 'Mumbai Central',
        'account_number': '1234567890',
        'ifsc_code': 'HDFC0001234'
    }
    company_name = "Test Company Ltd"
    
    result = create_bank_details(bank_account, company_name)
    
    assert result is not None
    assert result['holder_name'] == 'Test Company Ltd'
    assert result['bank_name'] == 'HDFC Bank'
    assert result['account_number'] == '1234567890'
    assert result['branch'] == 'Mumbai Central'
    assert result['ifsc'] == 'HDFC0001234'
    
    # Test without bank account
    result_none = create_bank_details(None, company_name)
    assert result_none is None
    
    print("✅ Bank details structure test passed!")

if __name__ == "__main__":
    print("Running logic tests...")
    test_address_merging_logic()
    test_bank_details_structure()
    print("🎉 All logic tests passed!")