#!/usr/bin/env python3
"""
Automated RBAC Enforcement Migration Script

This script migrates API endpoint files to use centralized RBAC and tenant
isolation enforcement via app.core.enforcement.require_access.

Usage:
    python scripts/migrate_to_rbac_enforcement.py --file app/api/vendors.py --module vendor
    python scripts/migrate_to_rbac_enforcement.py --all --dry-run
    
Author: GitHub Copilot
Date: 2025-10-28
"""

import re
import argparse
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Map of file paths to module names
MODULE_MAPPINGS = {
    'app/api/vendors.py': 'vendor',
    'app/api/products.py': 'product',
    'app/api/companies.py': 'company',
    'app/api/customer_analytics.py': 'customer_analytics',
    'app/api/management_reports.py': 'report',
    'app/api/settings.py': 'settings',
    'app/api/platform.py': 'platform',
    'app/api/routes/admin.py': 'admin',
    'app/api/v1/accounts.py': 'account',
    'app/api/v1/chart_of_accounts.py': 'chart_of_accounts',
    'app/api/v1/ledger.py': 'ledger',
    'app/api/v1/expense_account.py': 'expense_account',
    'app/api/v1/gst.py': 'gst',
    'app/api/v1/contacts.py': 'contact',
    'app/api/v1/assets.py': 'asset',
    'app/api/v1/transport.py': 'transport',
    'app/api/v1/calendar.py': 'calendar',
    'app/api/v1/tasks.py': 'task',
    'app/api/v1/project_management.py': 'project',
    'app/api/v1/workflow_approval.py': 'workflow',
    'app/api/v1/audit_log.py': 'audit',
    'app/api/v1/feedback.py': 'feedback',
    'app/api/v1/company_branding.py': 'branding',
    'app/api/pincode.py': 'pincode',
    'app/api/v1/seo.py': 'seo',
    'app/api/v1/marketing.py': 'marketing',
    'app/api/v1/ab_testing.py': 'ab_testing',
    'app/api/v1/plugin.py': 'plugin',
    'app/api/v1/tally.py': 'tally',
    'app/api/v1/oauth.py': 'oauth',
    'app/api/v1/email.py': 'email',
    'app/api/v1/mail.py': 'mail',
    'app/api/v1/ai.py': 'ai',
    'app/api/v1/ai_agents.py': 'ai_agent',
    'app/api/v1/chatbot.py': 'chatbot',
    'app/api/v1/forecasting.py': 'forecasting',
    'app/api/v1/financial_modeling.py': 'financial_modeling',
    'app/api/v1/ml_algorithms.py': 'ml_algorithm',
    'app/api/v1/automl.py': 'automl',
    'app/api/v1/user.py': 'user',
    'app/api/v1/reporting_hub.py': 'reporting',
    'app/api/v1/service_analytics.py': 'service_analytics',
    'app/api/v1/streaming_analytics.py': 'streaming_analytics',
    'app/api/v1/ai_analytics.py': 'ai_analytics',
    'app/api/v1/ml_analytics.py': 'ml_analytics',
}


def update_imports(content: str) -> str:
    """Update imports to use centralized enforcement."""
    
    # Remove old auth imports
    content = re.sub(
        r'from app\.api\.v1\.auth import get_current_active_user.*?\n',
        '',
        content
    )
    
    content = re.sub(
        r'from app\.api\.v1\.auth import get_current_admin_user.*?\n',
        '',
        content
    )
    
    content = re.sub(
        r'from app\.api\.v1\.auth import \([^)]*\)\n',
        '',
        content,
        flags=re.DOTALL
    )
    
    # Remove tenant and org imports
    content = re.sub(
        r'from app\.core\.tenant import.*?\n',
        '',
        content
    )
    
    content = re.sub(
        r'from app\.core\.org_restrictions import.*?\n',
        '',
        content
    )
    
    content = re.sub(
        r'from app\.core\.rbac_dependencies import.*?\n',
        '',
        content
    )
    
    # Add new enforcement import if not present
    if 'from app.core.enforcement import require_access' not in content:
        content = content.replace(
            'from app.core.database import get_db',
            'from app.core.database import get_db\nfrom app.core.enforcement import require_access'
        )
    
    return content


def infer_action_from_function(func_name: str, method: str) -> str:
    """Infer CRUD action from function name and HTTP method."""
    func_lower = func_name.lower()
    
    if 'delete' in func_lower or 'remove' in func_lower:
        return 'delete'
    elif 'create' in func_lower or 'add' in func_lower or method == 'POST':
        return 'create'
    elif 'update' in func_lower or 'edit' in func_lower or method in ['PUT', 'PATCH']:
        return 'update'
    else:
        return 'read'


def migrate_endpoint_signature(content: str, module_name: str) -> Tuple[str, int]:
    """Migrate endpoint signatures to use require_access."""
    changes = 0
    
    # Find all route decorators and their functions
    pattern = r'@router\.(get|post|put|patch|delete)\([^)]*\)\s*\nasync def (\w+)\([^)]*\):'
    
    def replace_func(match):
        nonlocal changes
        method = match.group(1).upper()
        func_name = match.group(2)
        full_match = match.group(0)
        
        # Infer action
        action = infer_action_from_function(func_name, method)
        
        # Check if already migrated
        if 'require_access' in full_match:
            return full_match
        
        # Replace auth dependencies
        # Pattern 1: current_user before db
        if 'current_user: User = Depends(get_current_active_user)' in full_match:
            new_match = re.sub(
                r'current_user: User = Depends\(get_current_active_user\),?\s*\n\s*db: AsyncSession = Depends\(get_db\)',
                f'auth: tuple = Depends(require_access("{module_name}", "{action}")),\n    db: AsyncSession = Depends(get_db)',
                full_match
            )
            if new_match != full_match:
                changes += 1
                return new_match
        
        # Pattern 2: db before current_user
        if 'db: AsyncSession = Depends(get_db)' in full_match and 'current_user' in full_match:
            new_match = re.sub(
                r'db: AsyncSession = Depends\(get_db\),?\s*\n\s*current_user: User = Depends\(get_current_active_user\)',
                f'auth: tuple = Depends(require_access("{module_name}", "{action}")),\n    db: AsyncSession = Depends(get_db)',
                full_match
            )
            if new_match != full_match:
                changes += 1
                return new_match
        
        return full_match
    
    content = re.sub(pattern, replace_func, content, flags=re.DOTALL)
    return content, changes


def add_auth_unpacking(content: str) -> str:
    """Add 'current_user, org_id = auth' at start of migrated functions."""
    
    # Find functions with auth parameter
    pattern = r'(async def \w+\([^)]*auth: tuple = Depends\(require_access[^)]*\)[^)]*\):)\s*\n(\s+)("""[^"]*""")?'
    
    def replace_func(match):
        func_def = match.group(1)
        indent = match.group(2)
        docstring = match.group(3) or ''
        
        # Add auth unpacking after docstring
        if docstring:
            return f"{func_def}\n{indent}{docstring}\n{indent}\n{indent}current_user, org_id = auth"
        else:
            return f"{func_def}\n{indent}\"\"\"Function docstring\"\"\"\n{indent}\n{indent}current_user, org_id = auth"
    
    content = re.sub(pattern, replace_func, content)
    return content


def replace_org_id_retrieval(content: str) -> str:
    """Replace manual org_id retrieval with auth tuple unpacking."""
    
    # Replace require_current_organization_id calls
    content = re.sub(
        r'target_org_id = require_current_organization_id\(current_user\)',
        '# org_id already extracted from auth tuple',
        content
    )
    
    content = re.sub(
        r'org_id = require_current_organization_id\(current_user\)',
        '# org_id already extracted from auth tuple',
        content
    )
    
    return content


def migrate_file(filepath: str, module_name: str, dry_run: bool = False) -> Dict:
    """Migrate a single file."""
    
    result = {
        'filepath': filepath,
        'module': module_name,
        'success': False,
        'changes': 0,
        'errors': []
    }
    
    try:
        with open(filepath, 'r') as f:
            original_content = f.read()
        
        content = original_content
        
        # Step 1: Update imports
        content = update_imports(content)
        
        # Step 2: Migrate endpoint signatures
        content, sig_changes = migrate_endpoint_signature(content, module_name)
        result['changes'] += sig_changes
        
        # Step 3: Replace org_id retrieval
        content = replace_org_id_retrieval(content)
        
        # Write back if changes were made and not dry run
        if content != original_content:
            if not dry_run:
                with open(filepath, 'w') as f:
                    f.write(content)
                result['success'] = True
            else:
                result['success'] = True
                result['dry_run'] = True
        else:
            result['success'] = True
            result['changes'] = 0
    
    except Exception as e:
        result['errors'].append(str(e))
    
    return result


def main():
    parser = argparse.ArgumentParser(description='Migrate API files to use centralized RBAC enforcement')
    parser.add_argument('--file', help='Specific file to migrate')
    parser.add_argument('--module', help='Module name for the file (required with --file)')
    parser.add_argument('--all', action='store_true', help='Migrate all known files')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without making changes')
    parser.add_argument('--list', action='store_true', help='List all known files and exit')
    
    args = parser.parse_args()
    
    if args.list:
        print("Known files and their module mappings:")
        for filepath, module in sorted(MODULE_MAPPINGS.items()):
            print(f"  {filepath:50s} -> {module}")
        return 0
    
    if args.file:
        if not args.module:
            print("Error: --module is required when using --file")
            return 1
        
        results = [migrate_file(args.file, args.module, args.dry_run)]
    
    elif args.all:
        results = []
        for filepath, module in MODULE_MAPPINGS.items():
            if Path(filepath).exists():
                results.append(migrate_file(filepath, module, args.dry_run))
    
    else:
        parser.print_help()
        return 1
    
    # Print results
    print("\n" + "="*80)
    print("MIGRATION RESULTS")
    print("="*80 + "\n")
    
    successful = 0
    failed = 0
    total_changes = 0
    
    for result in results:
        if result['success']:
            successful += 1
            total_changes += result['changes']
            status = "DRY RUN ✓" if result.get('dry_run') else "SUCCESS ✓"
            print(f"{status:12s} {result['filepath']:50s} ({result['changes']} changes)")
        else:
            failed += 1
            print(f"FAILED ✗     {result['filepath']:50s}")
            for error in result['errors']:
                print(f"             Error: {error}")
    
    print("\n" + "="*80)
    print(f"Total: {successful} successful, {failed} failed, {total_changes} total changes")
    print("="*80 + "\n")
    
    return 0 if failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
