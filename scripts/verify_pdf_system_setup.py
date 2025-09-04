# scripts/verify_pdf_system_setup.py

"""
Verification script for PDF generation system setup
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import inspect, text
from app.core.database import SessionLocal, engine
from app.models import Company, Product, ProductFile

def verify_database_schema():
    """Verify that all required database fields exist"""
    print("🔍 Verifying database schema for PDF generation system...")
    
    inspector = inspect(engine)
    issues = []
    
    # Check Company table for logo_path field
    company_columns = inspector.get_columns('companies')
    company_column_names = [col['name'] for col in company_columns]
    
    if 'logo_path' not in company_column_names:
        issues.append("❌ Missing 'logo_path' field in companies table")
    else:
        print("✅ Company logo_path field exists")
    
    # Check ProductFile table exists
    tables = inspector.get_table_names()
    if 'product_files' not in tables:
        issues.append("❌ Missing 'product_files' table")
    else:
        print("✅ ProductFile table exists")
        
        # Check ProductFile table structure
        product_file_columns = inspector.get_columns('product_files')
        product_file_column_names = [col['name'] for col in product_file_columns]
        
        required_fields = ['id', 'product_id', 'filename', 'original_filename', 'file_path', 'file_size', 'content_type', 'organization_id']
        for field in required_fields:
            if field not in product_file_column_names:
                issues.append(f"❌ Missing '{field}' field in product_files table")
            else:
                print(f"✅ ProductFile.{field} field exists")
    
    return issues

def verify_directory_structure():
    """Verify that all required directories exist"""
    print("\n🗂️  Verifying directory structure...")
    
    directories = [
        'app/templates/pdf',
        'app/static/css',
        'uploads/voucher_pdfs',
        'uploads/company_logos'
    ]
    
    issues = []
    for directory in directories:
        if os.path.exists(directory):
            print(f"✅ Directory exists: {directory}")
        else:
            print(f"⚠️  Creating directory: {directory}")
            os.makedirs(directory, exist_ok=True)
    
    return issues

def verify_templates():
    """Verify that all PDF templates exist"""
    print("\n📄 Verifying PDF templates...")
    
    templates = [
        'app/templates/pdf/base_voucher.html',
        'app/templates/pdf/purchase_voucher.html',
        'app/templates/pdf/sales_voucher.html',
        'app/templates/pdf/presales_voucher.html'
    ]
    
    issues = []
    for template in templates:
        if os.path.exists(template):
            print(f"✅ Template exists: {template}")
        else:
            issues.append(f"❌ Missing template: {template}")
    
    return issues

def verify_css_files():
    """Verify that CSS files exist"""
    print("\n🎨 Verifying CSS files...")
    
    css_files = [
        'app/static/css/voucher_print.css'
    ]
    
    issues = []
    for css_file in css_files:
        if os.path.exists(css_file):
            print(f"✅ CSS file exists: {css_file}")
        else:
            issues.append(f"❌ Missing CSS file: {css_file}")
    
    return issues

def test_database_connection():
    """Test database connection and basic queries"""
    print("\n🔗 Testing database connection...")
    
    try:
        db = SessionLocal()
        
        # Test Company model
        company_count = db.query(Company).count()
        print(f"✅ Company table accessible, {company_count} companies found")
        
        # Test Product model
        product_count = db.query(Product).count()
        print(f"✅ Product table accessible, {product_count} products found")
        
        # Test ProductFile model if table exists
        try:
            file_count = db.query(ProductFile).count()
            print(f"✅ ProductFile table accessible, {file_count} files found")
        except Exception as e:
            print(f"⚠️  ProductFile table issue: {e}")
        
        db.close()
        return []
        
    except Exception as e:
        return [f"❌ Database connection failed: {e}"]

def check_dependencies():
    """Check if required Python packages are installed"""
    print("\n📦 Checking Python dependencies...")
    
    required_packages = [
        'weasyprint',
        'jinja2', 
        'reportlab',
        'num2words'
    ]
    
    issues = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ Package installed: {package}")
        except ImportError:
            issues.append(f"❌ Missing package: {package}")
    
    return issues

def main():
    """Run all verification checks"""
    print("🚀 PDF Generation System Verification")
    print("=" * 50)
    
    all_issues = []
    
    # Run all checks
    all_issues.extend(verify_database_schema())
    all_issues.extend(verify_directory_structure())
    all_issues.extend(verify_templates())
    all_issues.extend(verify_css_files())
    all_issues.extend(test_database_connection())
    all_issues.extend(check_dependencies())
    
    print("\n" + "=" * 50)
    
    if all_issues:
        print("❌ Issues found:")
        for issue in all_issues:
            print(f"   {issue}")
        print(f"\n⚠️  Found {len(all_issues)} issue(s) that need to be resolved.")
        return 1
    else:
        print("✅ All checks passed! PDF generation system is ready.")
        print("\n🎉 You can now:")
        print("   • Generate PDFs for vouchers via API")
        print("   • Upload company logos for branding")
        print("   • Attach files to products")
        print("   • Use the frontend PDF buttons")
        return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)