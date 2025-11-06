#!/usr/bin/env python3
"""
Automated End-to-End Testing Script for TRITIQ ERP System

This script performs comprehensive testing of all main application features
including authentication, master data management, voucher operations,
inventory management, and reporting functionality.

Usage:
    python complete_app_test.py [--base-url BASE_URL] [--verbose] [--report-file REPORT_FILE]

Requirements:
    pip install requests pytest pandas openpyxl
"""

import requests
import json
import time
import argparse
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import logging
from dataclasses import dataclass
import pandas as pd
import io
import tempfile


@dataclass
class TestResult:
    """Data class for storing test results"""
    test_name: str
    status: str  # 'PASS', 'FAIL', 'SKIP'
    duration_ms: int
    error_message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


@dataclass
class TestReport:
    """Data class for comprehensive test reporting"""
    total_tests: int
    passed_tests: int
    failed_tests: int
    skipped_tests: int
    total_duration_ms: int
    test_results: List[TestResult]
    environment_info: Dict[str, Any]
    timestamp: datetime


class ERPTestClient:
    """Client for testing ERP system endpoints"""
    
    def __init__(self, base_url: str, verbose: bool = False):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.verbose = verbose
        self.logger = self._setup_logger()
        self.auth_token = None
        self.test_org_id = None
        
    def _setup_logger(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger('erp_test')
        level = logging.DEBUG if self.verbose else logging.INFO
        logger.setLevel(level)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make HTTP request with authentication"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        headers = kwargs.pop('headers', {})
        if self.auth_token:
            headers['Authorization'] = f"Bearer {self.auth_token}"
        
        self.logger.debug(f"{method.upper()} {url}")
        
        response = self.session.request(method, url, headers=headers, **kwargs)
        
        if self.verbose:
            self.logger.debug(f"Response: {response.status_code} - {response.text[:200]}...")
        
        return response
    
    def login(self, email: str, password: str) -> bool:
        """Authenticate user and store token"""
        try:
            response = self._make_request(
                'POST', 
                '/api/v1/auth/login',
                json={
                    'email': email,
                    'password': password
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get('access_token')
                user_info = data.get('user', {})
                self.test_org_id = user_info.get('organization_id')
                self.logger.info(f"Successfully logged in as {email}")
                return True
            else:
                self.logger.error(f"Login failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Login error: {str(e)}")
            return False


class ERPAutomatedTester:
    """Main class for automated ERP testing"""
    
    def __init__(self, base_url: str, verbose: bool = False):
        self.client = ERPTestClient(base_url, verbose)
        self.verbose = verbose
        self.test_results: List[TestResult] = []
        self.start_time = datetime.now()
        
        # Test data for creating entities
        self.test_data = {
            'vendor': {
                'name': f'Test Vendor {int(time.time())}',
                'address1': '123 Test Street',
                'city': 'Test City',
                'state': 'Test State',
                'pin_code': '123456',
                'contact_number': '+91 9876543210',
                'email': 'vendor@test.com',
                'gst_number': '29ABCDE1234F1Z5'
            },
            'customer': {
                'name': f'Test Customer {int(time.time())}',
                'address1': '456 Customer Lane',
                'city': 'Customer City',
                'state': 'Customer State',
                'pin_code': '654321',
                'contact_number': '+91 9876543211',
                'email': 'customer@test.com',
                'gst_number': '29ABCDE1234F1Z6'
            },
            'product': {
                'name': f'Test Product {int(time.time())}',
                'hsn_code': '12345678',
                'unit': 'PCS',
                'unit_price': 100.0,
                'gst_rate': 18.0,
                'reorder_level': 10
            }
        }
        
        # Store created entity IDs for cleanup
        self.created_entities = {
            'vendors': [],
            'customers': [],
            'products': [],
            'vouchers': []
        }
    
    def run_test(self, test_name: str, test_func, *args, **kwargs) -> TestResult:
        """Run a single test and record the result"""
        start_time = time.time()
        
        try:
            print(f"Running test: {test_name}...")
            
            result = test_func(*args, **kwargs)
            
            duration_ms = int((time.time() - start_time) * 1000)
            
            if result is True:
                test_result = TestResult(test_name, 'PASS', duration_ms)
                print(f"✅ {test_name} - PASSED ({duration_ms}ms)")
            elif isinstance(result, tuple) and result[0] is True:
                test_result = TestResult(test_name, 'PASS', duration_ms, details=result[1])
                print(f"✅ {test_name} - PASSED ({duration_ms}ms)")
            else:
                error_msg = str(result) if result else "Test returned False"
                test_result = TestResult(test_name, 'FAIL', duration_ms, error_msg)
                print(f"❌ {test_name} - FAILED ({duration_ms}ms): {error_msg}")
                
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            test_result = TestResult(test_name, 'FAIL', duration_ms, str(e))
            print(f"❌ {test_name} - FAILED ({duration_ms}ms): {str(e)}")
        
        self.test_results.append(test_result)
        return test_result
    
    def test_authentication(self) -> bool:
        """Test user authentication"""
        # Try to login with test credentials
        # For demo purposes, using a default test user
        return self.client.login('test@example.com', 'password123')
    
    def test_vendor_crud(self) -> bool:
        """Test vendor CRUD operations"""
        try:
            # Create vendor
            response = self.client._make_request(
                'POST',
                '/api/v1/vendors',
                json=self.test_data['vendor']
            )
            
            if response.status_code not in [200, 201]:
                return f"Failed to create vendor: {response.text}"
            
            vendor_data = response.json()
            vendor_id = vendor_data.get('id')
            if not vendor_id:
                return "No vendor ID returned from create"
            
            self.created_entities['vendors'].append(vendor_id)
            
            # Read vendor
            response = self.client._make_request('GET', f'/api/v1/vendors/{vendor_id}')
            if response.status_code != 200:
                return f"Failed to read vendor: {response.text}"
            
            # Update vendor
            update_data = {'name': f'Updated {self.test_data["vendor"]["name"]}'}
            response = self.client._make_request(
                'PUT', 
                f'/api/v1/vendors/{vendor_id}',
                json=update_data
            )
            if response.status_code not in [200, 204]:
                return f"Failed to update vendor: {response.text}"
            
            # List vendors
            response = self.client._make_request('GET', '/api/v1/vendors')
            if response.status_code != 200:
                return f"Failed to list vendors: {response.text}"
            
            return True
            
        except Exception as e:
            return f"Vendor CRUD test error: {str(e)}"
    
    def test_customer_crud(self) -> bool:
        """Test customer CRUD operations"""
        try:
            # Create customer
            response = self.client._make_request(
                'POST',
                '/api/v1/customers',
                json=self.test_data['customer']
            )
            
            if response.status_code not in [200, 201]:
                return f"Failed to create customer: {response.text}"
            
            customer_data = response.json()
            customer_id = customer_data.get('id')
            if not customer_id:
                return "No customer ID returned from create"
            
            self.created_entities['customers'].append(customer_id)
            
            # Read customer
            response = self.client._make_request('GET', f'/api/v1/customers/{customer_id}')
            if response.status_code != 200:
                return f"Failed to read customer: {response.text}"
            
            return True
            
        except Exception as e:
            return f"Customer CRUD test error: {str(e)}"
    
    def test_product_crud(self) -> bool:
        """Test product CRUD operations"""
        try:
            # Create product
            response = self.client._make_request(
                'POST',
                '/api/v1/products',
                json=self.test_data['product']
            )
            
            if response.status_code not in [200, 201]:
                return f"Failed to create product: {response.text}"
            
            product_data = response.json()
            product_id = product_data.get('id')
            if not product_id:
                return "No product ID returned from create"
            
            self.created_entities['products'].append(product_id)
            
            # Read product
            response = self.client._make_request('GET', f'/api/v1/products/{product_id}')
            if response.status_code != 200:
                return f"Failed to read product: {response.text}"
            
            return True
            
        except Exception as e:
            return f"Product CRUD test error: {str(e)}"
    
    def test_excel_import_export(self) -> bool:
        """Test Excel import and export functionality"""
        try:
            # Test template download
            response = self.client._make_request('GET', '/api/v1/stock/template')
            if response.status_code != 200:
                return f"Failed to download template: {response.text}"
            
            # Create a simple test Excel file
            test_data = pd.DataFrame([
                {
                    'Product Name': f'Excel Test Product {int(time.time())}',
                    'Quantity': 100,
                    'Unit': 'PCS',
                    'HSN Code': '12345678',
                    'Unit Price': 50.0,
                    'GST Rate': 18.0
                }
            ])
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
                test_data.to_excel(tmp_file.name, index=False)
                tmp_file_path = tmp_file.name
            
            try:
                # Test import
                with open(tmp_file_path, 'rb') as f:
                    files = {'file': ('test_import.xlsx', f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
                    response = self.client._make_request('POST', '/api/v1/stock/import', files=files)
                
                if response.status_code not in [200, 201]:
                    return f"Failed to import Excel: {response.text}"
                
                # Test export
                response = self.client._make_request('GET', '/api/v1/stock/export')
                if response.status_code != 200:
                    return f"Failed to export Excel: {response.text}"
                
                return True
                
            finally:
                # Clean up temporary file
                if os.path.exists(tmp_file_path):
                    os.unlink(tmp_file_path)
            
        except Exception as e:
            return f"Excel import/export test error: {str(e)}"
    
    def test_voucher_creation(self) -> bool:
        """Test voucher creation functionality"""
        try:
            # Need at least one vendor and product for voucher creation
            if not self.created_entities['vendors'] or not self.created_entities['products']:
                return "Skipping voucher test - no vendors or products available"
            
            vendor_id = self.created_entities['vendors'][0]
            product_id = self.created_entities['products'][0]
            
            # Create a purchase order
            po_data = {
                'vendor_id': vendor_id,
                'voucher_date': datetime.now().isoformat(),
                'items': [
                    {
                        'product_id': product_id,
                        'quantity': 10,
                        'unit_price': 100.0
                    }
                ]
            }
            
            response = self.client._make_request(
                'POST',
                '/api/v1/vouchers/purchase-orders',
                json=po_data
            )
            
            if response.status_code not in [200, 201]:
                return f"Failed to create purchase order: {response.text}"
            
            voucher_data = response.json()
            voucher_id = voucher_data.get('id')
            if voucher_id:
                self.created_entities['vouchers'].append(voucher_id)
            
            return True
            
        except Exception as e:
            return f"Voucher creation test error: {str(e)}"
    
    def test_inventory_management(self) -> bool:
        """Test inventory/stock management"""
        try:
            # Test stock listing
            response = self.client._make_request('GET', '/api/v1/stock')
            if response.status_code != 200:
                return f"Failed to list stock: {response.text}"
            
            # Test low stock report
            response = self.client._make_request('GET', '/api/v1/stock/low-stock')
            if response.status_code != 200:
                return f"Failed to get low stock report: {response.text}"
            
            return True
            
        except Exception as e:
            return f"Inventory management test error: {str(e)}"
    
    def test_reporting_apis(self) -> bool:
        """Test reporting functionality"""
        try:
            # Test dashboard stats
            response = self.client._make_request('GET', '/api/v1/reports/dashboard-stats')
            if response.status_code != 200:
                return f"Failed to get dashboard stats: {response.text}"
            
            # Test organization statistics
            response = self.client._make_request('GET', '/api/v1/organizations/app-statistics')
            if response.status_code != 200:
                return f"Failed to get app statistics: {response.text}"
            
            return True
            
        except Exception as e:
            return f"Reporting test error: {str(e)}"
    
    def test_bom_functionality(self) -> bool:
        """Test Bill of Materials functionality"""
        try:
            if not self.created_entities['products']:
                return "Skipping BOM test - no products available"
            
            product_id = self.created_entities['products'][0]
            
            # Create a BOM
            bom_data = {
                'bom_name': f'Test BOM {int(time.time())}',
                'output_item_id': product_id,
                'output_quantity': 1.0,
                'components': [
                    {
                        'component_item_id': product_id,
                        'quantity_required': 2.0,
                        'unit': 'PCS',
                        'unit_cost': 50.0
                    }
                ]
            }
            
            response = self.client._make_request('POST', '/api/v1/bom', json=bom_data)
            if response.status_code not in [200, 201]:
                return f"Failed to create BOM: {response.text}"
            
            # List BOMs
            response = self.client._make_request('GET', '/api/v1/bom')
            if response.status_code != 200:
                return f"Failed to list BOMs: {response.text}"
            
            return True
            
        except Exception as e:
            return f"BOM functionality test error: {str(e)}"
    
    def test_organization_management(self) -> bool:
        """Test organization management (if accessible)"""
        try:
            # Test listing organizations (may require super admin)
            response = self.client._make_request('GET', '/api/v1/organizations')
            
            # If forbidden, that's expected for non-super-admin users
            if response.status_code == 403:
                return True  # This is expected behavior
            
            if response.status_code != 200:
                return f"Unexpected error listing organizations: {response.text}"
            
            return True
            
        except Exception as e:
            return f"Organization management test error: {str(e)}"
    
    def cleanup_test_data(self) -> None:
        """Clean up created test data"""
        print("\nCleaning up test data...")
        
        # Delete created entities in reverse order
        for voucher_id in self.created_entities['vouchers']:
            try:
                self.client._make_request('DELETE', f'/api/v1/vouchers/{voucher_id}')
            except:
                pass
        
        for product_id in self.created_entities['products']:
            try:
                self.client._make_request('DELETE', f'/api/v1/products/{product_id}')
            except:
                pass
        
        for customer_id in self.created_entities['customers']:
            try:
                self.client._make_request('DELETE', f'/api/v1/customers/{customer_id}')
            except:
                pass
        
        for vendor_id in self.created_entities['vendors']:
            try:
                self.client._make_request('DELETE', f'/api/v1/vendors/{vendor_id}')
            except:
                pass
    
    def run_all_tests(self) -> TestReport:
        """Run all tests and return comprehensive report"""
        print("🚀 Starting TRITIQ ERP Automated Testing")
        print("=" * 50)
        
        # Authentication test
        auth_result = self.run_test("Authentication", self.test_authentication)
        if auth_result.status != 'PASS':
            print("❌ Authentication failed - skipping remaining tests")
            return self._generate_report()
        
        # Core functionality tests
        self.run_test("Vendor CRUD Operations", self.test_vendor_crud)
        self.run_test("Customer CRUD Operations", self.test_customer_crud)
        self.run_test("Product CRUD Operations", self.test_product_crud)
        self.run_test("Excel Import/Export", self.test_excel_import_export)
        self.run_test("Voucher Creation", self.test_voucher_creation)
        self.run_test("Inventory Management", self.test_inventory_management)
        self.run_test("BOM Functionality", self.test_bom_functionality)
        self.run_test("Reporting APIs", self.test_reporting_apis)
        self.run_test("Organization Management", self.test_organization_management)
        
        # Cleanup
        try:
            self.cleanup_test_data()
        except Exception as e:
            print(f"Warning: Cleanup failed: {str(e)}")
        
        return self._generate_report()
    
    def _generate_report(self) -> TestReport:
        """Generate comprehensive test report"""
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r.status == 'PASS'])
        failed_tests = len([r for r in self.test_results if r.status == 'FAIL'])
        skipped_tests = len([r for r in self.test_results if r.status == 'SKIP'])
        
        total_duration = sum(r.duration_ms for r in self.test_results)
        
        environment_info = {
            'base_url': self.client.base_url,
            'test_start_time': self.start_time.isoformat(),
            'python_version': sys.version,
            'os_info': os.name
        }
        
        return TestReport(
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            skipped_tests=skipped_tests,
            total_duration_ms=total_duration,
            test_results=self.test_results,
            environment_info=environment_info,
            timestamp=datetime.now()
        )


def print_report(report: TestReport) -> None:
    """Print formatted test report"""
    print("\n" + "=" * 60)
    print("📊 TEST EXECUTION REPORT")
    print("=" * 60)
    
    print(f"📅 Timestamp: {report.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⏱️  Total Duration: {report.total_duration_ms:,}ms ({report.total_duration_ms/1000:.2f}s)")
    print(f"🌐 Base URL: {report.environment_info['base_url']}")
    
    print(f"\n📈 SUMMARY:")
    print(f"   Total Tests: {report.total_tests}")
    print(f"   ✅ Passed: {report.passed_tests}")
    print(f"   ❌ Failed: {report.failed_tests}")
    print(f"   ⏭️  Skipped: {report.skipped_tests}")
    
    success_rate = (report.passed_tests / report.total_tests * 100) if report.total_tests > 0 else 0
    print(f"   📊 Success Rate: {success_rate:.1f}%")
    
    print(f"\n📋 DETAILED RESULTS:")
    for result in report.test_results:
        status_icon = "✅" if result.status == "PASS" else "❌" if result.status == "FAIL" else "⏭️"
        print(f"   {status_icon} {result.test_name:<25} {result.duration_ms:>6}ms")
        if result.error_message:
            print(f"      Error: {result.error_message}")
    
    if report.failed_tests > 0:
        print(f"\n🔍 FAILED TESTS ANALYSIS:")
        failed_results = [r for r in report.test_results if r.status == 'FAIL']
        for result in failed_results:
            print(f"   ❌ {result.test_name}")
            print(f"      Error: {result.error_message}")
            if result.details:
                print(f"      Details: {result.details}")


def save_report_to_file(report: TestReport, filename: str) -> None:
    """Save test report to JSON file"""
    report_data = {
        'summary': {
            'total_tests': report.total_tests,
            'passed_tests': report.passed_tests,
            'failed_tests': report.failed_tests,
            'skipped_tests': report.skipped_tests,
            'total_duration_ms': report.total_duration_ms,
            'success_rate': (report.passed_tests / report.total_tests * 100) if report.total_tests > 0 else 0,
            'timestamp': report.timestamp.isoformat()
        },
        'environment_info': report.environment_info,
        'test_results': [
            {
                'test_name': r.test_name,
                'status': r.status,
                'duration_ms': r.duration_ms,
                'error_message': r.error_message,
                'details': r.details
            }
            for r in report.test_results
        ]
    }
    
    with open(filename, 'w') as f:
        json.dump(report_data, f, indent=2)
    
    print(f"\n💾 Test report saved to: {filename}")


def main():
    """Main function for running the automated test suite"""
    parser = argparse.ArgumentParser(description='TRITIQ ERP Automated Test Suite')
    parser.add_argument('--base-url', default='http://localhost:8000', help='Base URL of the ERP system')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    parser.add_argument('--report-file', help='File to save test report (JSON format)')
    parser.add_argument('--skip-cleanup', action='store_true', help='Skip cleanup of test data')
    
    args = parser.parse_args()
    
    # Create tester instance
    tester = ERPAutomatedTester(args.base_url, args.verbose)
    
    try:
        # Run all tests
        report = tester.run_all_tests()
        
        # Print report
        print_report(report)
        
        # Save report to file if requested
        if args.report_file:
            save_report_to_file(report, args.report_file)
        
        # Exit with appropriate code
        sys.exit(0 if report.failed_tests == 0 else 1)
        
    except KeyboardInterrupt:
        print("\n⚠️ Test execution interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Unexpected error during test execution: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()