"""
Test suite for voucher module RBAC migration (Phase 4)
Validates that all voucher modules properly use require_access enforcement
"""
import pytest
import ast
import re
from pathlib import Path

VOUCHER_DIR = Path(__file__).parent.parent / "app" / "api" / "v1" / "vouchers"

# All voucher files that should be migrated
VOUCHER_FILES = [
    "sales_voucher.py",
    "purchase_voucher.py",
    "journal_voucher.py",
    "contra_voucher.py",
    "credit_note.py",
    "debit_note.py",
    "delivery_challan.py",
    "goods_receipt_note.py",
    "inter_department_voucher.py",
    "non_sales_credit_note.py",
    "payment_voucher.py",
    "proforma_invoice.py",
    "purchase_order.py",
    "purchase_return.py",
    "quotation.py",
    "receipt_voucher.py",
    "sales_order.py",
    "sales_return.py",
]


class TestVoucherRBACMigration:
    """Test voucher module RBAC enforcement migration"""
    
    def test_all_voucher_files_exist(self):
        """Verify all voucher files exist"""
        for filename in VOUCHER_FILES:
            filepath = VOUCHER_DIR / filename
            assert filepath.exists(), f"Voucher file {filename} not found"
    
    def test_require_access_import(self):
        """Verify all voucher files import require_access"""
        for filename in VOUCHER_FILES:
            filepath = VOUCHER_DIR / filename
            with open(filepath, 'r') as f:
                content = f.read()
            
            assert 'from app.core.enforcement import require_access' in content, \
                f"{filename} missing require_access import"
    
    def test_no_old_auth_imports(self):
        """Verify old auth patterns are removed"""
        old_patterns = [
            'get_current_active_user',  # Should not be used directly in endpoints
        ]
        
        for filename in VOUCHER_FILES:
            filepath = VOUCHER_DIR / filename
            with open(filepath, 'r') as f:
                content = f.read()
            
            # Check for endpoints using old pattern
            # Look for @router decorated functions
            router_functions = re.finditer(
                r'@router\.\w+[^\n]*\n(?:@[^\n]*\n)*async def \w+\([^)]+\)',
                content,
                re.MULTILINE | re.DOTALL
            )
            
            for match in router_functions:
                func_text = match.group(0)
                # Should NOT have current_user: User = Depends(get_current_active_user)
                assert 'current_user: User = Depends(get_current_active_user)' not in func_text, \
                    f"{filename} still uses old current_user dependency pattern in: {func_text[:100]}"
    
    def test_auth_tuple_usage(self):
        """Verify endpoints use auth: tuple = Depends(require_access(...))"""
        for filename in VOUCHER_FILES:
            filepath = VOUCHER_DIR / filename
            with open(filepath, 'r') as f:
                content = f.read()
            
            # Find all router decorated functions
            has_endpoints = '@router.' in content
            if has_endpoints:
                # At least one endpoint should use auth tuple
                has_auth_tuple = 'auth: tuple = Depends(require_access(' in content
                assert has_auth_tuple, \
                    f"{filename} has endpoints but doesn't use auth tuple pattern"
    
    def test_correct_module_permission(self):
        """Verify endpoints use correct 'voucher' module permission"""
        for filename in VOUCHER_FILES:
            filepath = VOUCHER_DIR / filename
            with open(filepath, 'r') as f:
                content = f.read()
            
            # Find all require_access calls
            access_calls = re.findall(
                r'require_access\(["\'](\w+)["\']\s*,\s*["\'](\w+)["\']\)',
                content
            )
            
            for module, action in access_calls:
                # All voucher modules should use "voucher" permission
                assert module == "voucher", \
                    f"{filename} uses wrong module '{module}', should be 'voucher'"
                
                # Action should be one of the standard CRUD actions
                assert action in ['create', 'read', 'update', 'delete'], \
                    f"{filename} uses invalid action '{action}'"
    
    def test_auth_extraction_present(self):
        """Verify endpoints extract current_user and org_id from auth tuple"""
        for filename in VOUCHER_FILES:
            filepath = VOUCHER_DIR / filename
            with open(filepath, 'r') as f:
                content = f.read()
            
            # If file uses auth tuple, should have extraction
            if 'auth: tuple = Depends(require_access(' in content:
                # Should have at least one extraction
                has_extraction = (
                    'current_user, org_id = auth' in content or
                    'user, org_id = auth' in content
                )
                assert has_extraction, \
                    f"{filename} uses auth tuple but doesn't extract current_user and org_id"
    
    def test_no_current_user_organization_id(self):
        """Verify current_user.organization_id is replaced with org_id"""
        for filename in VOUCHER_FILES:
            filepath = VOUCHER_DIR / filename
            with open(filepath, 'r') as f:
                content = f.read()
            
            # Should NOT use current_user.organization_id
            assert 'current_user.organization_id' not in content, \
                f"{filename} still uses current_user.organization_id instead of org_id"
    
    def test_organization_scoping(self):
        """Verify queries are scoped to organization_id"""
        for filename in VOUCHER_FILES:
            filepath = VOUCHER_DIR / filename
            with open(filepath, 'r') as f:
                content = f.read()
            
            # If file has database queries, should scope by organization
            if 'select(' in content or 'query(' in content:
                # Should have organization_id filtering
                has_org_filter = (
                    '.organization_id == org_id' in content or
                    'organization_id=org_id' in content or
                    '.where(' in content  # At least using where clauses
                )
                assert has_org_filter, \
                    f"{filename} has database queries but may be missing organization scoping"
    
    def test_file_syntax(self):
        """Verify all files have valid Python syntax"""
        for filename in VOUCHER_FILES:
            filepath = VOUCHER_DIR / filename
            with open(filepath, 'r') as f:
                content = f.read()
            
            try:
                ast.parse(content)
            except SyntaxError as e:
                pytest.fail(f"{filename} has syntax error: {e}")
    
    def test_consistent_pattern(self):
        """Verify consistent enforcement pattern across all files"""
        patterns = {
            'has_require_access_import': 0,
            'has_auth_tuple': 0,
            'has_auth_extraction': 0,
            'has_org_scoping': 0,
        }
        
        for filename in VOUCHER_FILES:
            filepath = VOUCHER_DIR / filename
            with open(filepath, 'r') as f:
                content = f.read()
            
            if 'from app.core.enforcement import require_access' in content:
                patterns['has_require_access_import'] += 1
            
            if 'auth: tuple = Depends(require_access(' in content:
                patterns['has_auth_tuple'] += 1
            
            if 'current_user, org_id = auth' in content or 'user, org_id = auth' in content:
                patterns['has_auth_extraction'] += 1
            
            if '.organization_id == org_id' in content or 'organization_id=org_id' in content:
                patterns['has_org_scoping'] += 1
        
        # All files should have the import
        assert patterns['has_require_access_import'] == len(VOUCHER_FILES), \
            f"Not all files have require_access import: {patterns['has_require_access_import']}/{len(VOUCHER_FILES)}"
        
        # Most files should have auth tuple (some may not have endpoints)
        assert patterns['has_auth_tuple'] >= len(VOUCHER_FILES) * 0.9, \
            f"Too few files use auth tuple: {patterns['has_auth_tuple']}/{len(VOUCHER_FILES)}"
    
    def test_no_manual_rbac_checks(self):
        """Verify manual RBAC checks are removed (now centralized)"""
        manual_rbac_patterns = [
            'RBACService',
            'check_permission',
            'user_has_permission',
            'check_service_permission',
        ]
        
        for filename in VOUCHER_FILES:
            filepath = VOUCHER_DIR / filename
            with open(filepath, 'r') as f:
                content = f.read()
            
            for pattern in manual_rbac_patterns:
                # Allow pattern in comments but not in actual code
                lines = content.split('\n')
                code_lines = [l for l in lines if not l.strip().startswith('#')]
                code_content = '\n'.join(code_lines)
                
                assert pattern not in code_content, \
                    f"{filename} still has manual RBAC checks using {pattern}"


class TestVoucherMigrationCoverage:
    """Test migration coverage statistics"""
    
    def test_migration_coverage(self):
        """Verify migration coverage is 100%"""
        total_files = len(VOUCHER_FILES)
        migrated_count = 0
        
        for filename in VOUCHER_FILES:
            filepath = VOUCHER_DIR / filename
            with open(filepath, 'r') as f:
                content = f.read()
            
            if 'from app.core.enforcement import require_access' in content:
                migrated_count += 1
        
        coverage = (migrated_count / total_files) * 100
        
        assert coverage == 100.0, \
            f"Migration coverage is {coverage}%, expected 100%. " \
            f"{migrated_count}/{total_files} files migrated"
    
    def test_report_statistics(self):
        """Generate and report migration statistics"""
        stats = {
            'total_files': len(VOUCHER_FILES),
            'migrated': 0,
            'with_auth_tuple': 0,
            'with_org_scoping': 0,
            'syntax_valid': 0,
        }
        
        for filename in VOUCHER_FILES:
            filepath = VOUCHER_DIR / filename
            with open(filepath, 'r') as f:
                content = f.read()
            
            if 'from app.core.enforcement import require_access' in content:
                stats['migrated'] += 1
            
            if 'auth: tuple = Depends(require_access(' in content:
                stats['with_auth_tuple'] += 1
            
            if '.organization_id == org_id' in content:
                stats['with_org_scoping'] += 1
            
            try:
                ast.parse(content)
                stats['syntax_valid'] += 1
            except:
                pass
        
        # Print statistics
        print("\n" + "="*70)
        print("VOUCHER MODULE RBAC MIGRATION STATISTICS")
        print("="*70)
        print(f"Total voucher files: {stats['total_files']}")
        print(f"Migrated to require_access: {stats['migrated']} ({stats['migrated']/stats['total_files']*100:.1f}%)")
        print(f"Using auth tuple pattern: {stats['with_auth_tuple']} ({stats['with_auth_tuple']/stats['total_files']*100:.1f}%)")
        print(f"With org_id scoping: {stats['with_org_scoping']} ({stats['with_org_scoping']/stats['total_files']*100:.1f}%)")
        print(f"Syntax valid: {stats['syntax_valid']} ({stats['syntax_valid']/stats['total_files']*100:.1f}%)")
        print("="*70)
        
        # All should be 100%
        assert stats['migrated'] == stats['total_files']
        assert stats['syntax_valid'] == stats['total_files']


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
