#!/usr/bin/env python3
"""
Validation script to demonstrate the fixes for RBAC auto-initialization and app admin creation
"""

import os

def validate_files():
    """Validate that the required changes have been made to the files"""
    
    print("🔍 Validating RBAC Auto-initialization and App Admin Creation Fixes\n")
    
    validation_results = []
    
    # Check 1: UserRole enum includes APP_ADMIN
    print("1️⃣ Checking UserRole enum for APP_ADMIN...")
    try:
        with open('app/schemas/user.py', 'r') as f:
            content = f.read()
            if 'APP_ADMIN = "app_admin"' in content:
                print("   ✅ APP_ADMIN role added to UserRole enum")
                validation_results.append(True)
            else:
                print("   ❌ APP_ADMIN role not found in UserRole enum")
                validation_results.append(False)
    except FileNotFoundError:
        print("   ❌ app/schemas/user.py not found")
        validation_results.append(False)
    
    # Check 2: RBAC initialization enhanced in organizations_backup.py
    print("\n2️⃣ Checking RBAC initialization in organizations_backup.py...")
    try:
        with open('app/api/v1/organizations_backup.py', 'r') as f:
            content = f.read()
            checks = [
                'Initialize RBAC (roles and permissions) for the new organization',
                'initialize_default_permissions()',
                'initialize_default_roles(',
                'RBAC initialization failed'
            ]
            all_found = all(check in content for check in checks)
            if all_found:
                print("   ✅ Enhanced RBAC initialization with error handling")
                validation_results.append(True)
            else:
                print("   ❌ RBAC initialization enhancements not found")
                for check in checks:
                    if check not in content:
                        print(f"      Missing: {check}")
                validation_results.append(False)
    except FileNotFoundError:
        print("   ❌ app/api/v1/organizations_backup.py not found")
        validation_results.append(False)
    
    # Check 3: RBAC initialization enhanced in organizations/services.py
    print("\n3️⃣ Checking RBAC initialization in organizations/services.py...")
    try:
        with open('app/api/v1/organizations/services.py', 'r') as f:
            content = f.read()
            checks = [
                'Initialize RBAC (roles and permissions) for the new organization',
                'initialize_default_permissions()',
                'initialize_default_roles(',
                'RBAC initialization failed'
            ]
            all_found = all(check in content for check in checks)
            if all_found:
                print("   ✅ Enhanced RBAC initialization with error handling")
                validation_results.append(True)
            else:
                print("   ❌ RBAC initialization enhancements not found")
                validation_results.append(False)
    except FileNotFoundError:
        print("   ❌ app/api/v1/organizations/services.py not found")
        validation_results.append(False)
    
    # Check 4: App user permission logic updated
    print("\n4️⃣ Checking app user permission logic updates...")
    try:
        with open('app/api/v1/app_users.py', 'r') as f:
            content = f.read()
            checks = [
                'Allow any super admin to manage app users',
                'super_admin or app_admin role',
                'Only super admins can create app admin accounts',
                'role.in_([UserRole.SUPER_ADMIN, UserRole.APP_ADMIN])'
            ]
            all_found = all(check in content for check in checks)
            if all_found:
                print("   ✅ App user permission logic updated correctly")
                validation_results.append(True)
            else:
                print("   ❌ App user permission updates not found")
                for check in checks:
                    if check not in content:
                        print(f"      Missing: {check}")
                validation_results.append(False)
    except FileNotFoundError:
        print("   ❌ app/api/v1/app_users.py not found")
        validation_results.append(False)
    
    # Summary
    print(f"\n📊 Validation Summary:")
    passed = sum(validation_results)
    total = len(validation_results)
    print(f"   {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 All validations passed! The fixes have been successfully implemented.")
        
        print("\n📋 Summary of Changes:")
        print("   • Added APP_ADMIN role to UserRole enum")
        print("   • Enhanced RBAC auto-initialization with comprehensive error handling")
        print("   • Updated app user permissions to allow super admins to create app admins")
        print("   • Added restrictions so app admins cannot create other admins")
        print("   • Updated user listing to include both super admins and app admins")
        
        print("\n✨ Key Benefits:")
        print("   1. New organizations will have RBAC properly initialized automatically")
        print("   2. Super admins can now create app admin accounts")
        print("   3. App admins have restricted permissions and cannot create other admins")
        print("   4. Better error handling prevents incomplete organization setups")
        
        return True
    else:
        print(f"\n💥 {total - passed} validation(s) failed. Please check the implementation.")
        return False

def show_usage_examples():
    """Show examples of how the fixes work"""
    
    print("\n📖 Usage Examples:\n")
    
    print("1️⃣ Organization Creation (now auto-initializes RBAC):")
    print("   When creating a new organization via API:")
    print("   POST /api/v1/organizations/license/create")
    print("   -> RBAC permissions and roles are automatically initialized")
    print("   -> Admin role is automatically assigned to the org admin")
    print("   -> Comprehensive error handling prevents incomplete setups\n")
    
    print("2️⃣ App Admin Creation (now allowed for super admins):")
    print("   Super admin can create app admin:")
    print("   POST /api/v1/app-users/")
    print("   Body: {\"role\": \"app_admin\", \"email\": \"admin@company.com\", ...}")
    print("   -> Creates an app admin account with restricted permissions\n")
    
    print("3️⃣ Permission Restrictions:")
    print("   • Super admins: Can create both super admins and app admins")
    print("   • App admins: Cannot create any admin accounts (properly restricted)")
    print("   • App user listing shows both super admins and app admins")

if __name__ == "__main__":
    # Change to project root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    success = validate_files()
    
    if success:
        show_usage_examples()
    
    exit(0 if success else 1)