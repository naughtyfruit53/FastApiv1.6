#!/usr/bin/env python3
"""
Auth and CRM API Validation Script

This script validates:
1. Authentication endpoints
2. CRM API endpoints
3. Token management
4. Organization context
"""

import requests
import sys
import json
from typing import Dict, Optional

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"
TEST_USER_EMAIL = "admin@example.com"  # Update with your test credentials
TEST_USER_PASSWORD = "admin"  # Update with your test credentials


class APIValidator:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.headers: Dict[str, str] = {"Content-Type": "application/json"}
        
    def log(self, message: str, status: str = "INFO"):
        """Log a message with status"""
        symbols = {
            "INFO": "ℹ️",
            "SUCCESS": "✅",
            "ERROR": "❌",
            "WARNING": "⚠️"
        }
        print(f"{symbols.get(status, 'ℹ️')} [{status}] {message}")
    
    def test_login(self, email: str, password: str) -> bool:
        """Test login endpoint"""
        self.log("Testing login endpoint...", "INFO")
        
        try:
            # FastAPI OAuth2 expects form data
            data = {
                "username": email,
                "password": password
            }
            
            response = requests.post(
                f"{self.base_url}/auth/login",
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                self.refresh_token = data.get("refresh_token")
                
                if self.access_token:
                    self.headers["Authorization"] = f"Bearer {self.access_token}"
                    self.log(f"Login successful! Token: {self.access_token[:20]}...", "SUCCESS")
                    return True
                else:
                    self.log("Login response missing access_token", "ERROR")
                    return False
            else:
                self.log(f"Login failed with status {response.status_code}: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Login exception: {str(e)}", "ERROR")
            return False
    
    def test_current_user(self) -> bool:
        """Test /users/me endpoint"""
        self.log("Testing /users/me endpoint...", "INFO")
        
        try:
            response = requests.get(
                f"{self.base_url}/users/me",
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"Current user: {data.get('email')} (Role: {data.get('role')})", "SUCCESS")
                return True
            else:
                self.log(f"Get current user failed: {response.status_code} - {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Get current user exception: {str(e)}", "ERROR")
            return False
    
    def test_organization_current(self) -> bool:
        """Test /organizations/current endpoint"""
        self.log("Testing /organizations/current endpoint...", "INFO")
        
        try:
            response = requests.get(
                f"{self.base_url}/organizations/current",
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"Organization: {data.get('name')} (ID: {data.get('id')})", "SUCCESS")
                return True
            elif response.status_code == 404:
                self.log("No organization configured (this may be expected for super admin)", "WARNING")
                return True
            else:
                self.log(f"Get organization failed: {response.status_code} - {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Get organization exception: {str(e)}", "ERROR")
            return False
    
    def test_crm_leads(self) -> bool:
        """Test /crm/leads endpoint"""
        self.log("Testing /crm/leads endpoint...", "INFO")
        
        try:
            response = requests.get(
                f"{self.base_url}/crm/leads",
                headers=self.headers,
                params={"skip": 0, "limit": 10}
            )
            
            if response.status_code == 200:
                data = response.json()
                lead_count = len(data) if isinstance(data, list) else 0
                self.log(f"Successfully fetched {lead_count} leads", "SUCCESS")
                return True
            else:
                self.log(f"Get leads failed: {response.status_code} - {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Get leads exception: {str(e)}", "ERROR")
            return False
    
    def test_crm_opportunities(self) -> bool:
        """Test /crm/opportunities endpoint"""
        self.log("Testing /crm/opportunities endpoint...", "INFO")
        
        try:
            response = requests.get(
                f"{self.base_url}/crm/opportunities",
                headers=self.headers,
                params={"skip": 0, "limit": 10}
            )
            
            if response.status_code == 200:
                data = response.json()
                opp_count = len(data) if isinstance(data, list) else 0
                self.log(f"Successfully fetched {opp_count} opportunities", "SUCCESS")
                return True
            else:
                self.log(f"Get opportunities failed: {response.status_code} - {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Get opportunities exception: {str(e)}", "ERROR")
            return False
    
    def test_crm_analytics(self) -> bool:
        """Test /crm/analytics endpoint"""
        self.log("Testing /crm/analytics endpoint...", "INFO")
        
        try:
            response = requests.get(
                f"{self.base_url}/crm/analytics",
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"Analytics: {json.dumps(data, indent=2)}", "SUCCESS")
                return True
            else:
                self.log(f"Get analytics failed: {response.status_code} - {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Get analytics exception: {str(e)}", "ERROR")
            return False
    
    def run_all_tests(self, email: str, password: str) -> bool:
        """Run all validation tests"""
        self.log("=" * 60, "INFO")
        self.log("Starting API Validation Tests", "INFO")
        self.log("=" * 60, "INFO")
        
        tests = [
            ("Login", lambda: self.test_login(email, password)),
            ("Current User", self.test_current_user),
            ("Organization Current", self.test_organization_current),
            ("CRM Leads", self.test_crm_leads),
            ("CRM Opportunities", self.test_crm_opportunities),
            ("CRM Analytics", self.test_crm_analytics),
        ]
        
        results = []
        for test_name, test_func in tests:
            self.log(f"\n--- Testing: {test_name} ---", "INFO")
            result = test_func()
            results.append((test_name, result))
        
        # Summary
        self.log("\n" + "=" * 60, "INFO")
        self.log("Test Results Summary", "INFO")
        self.log("=" * 60, "INFO")
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "SUCCESS" if result else "ERROR"
            self.log(f"{test_name}: {'PASSED' if result else 'FAILED'}", status)
        
        self.log(f"\nTotal: {passed}/{total} tests passed", "SUCCESS" if passed == total else "WARNING")
        
        return passed == total


def main():
    """Main entry point"""
    validator = APIValidator(API_BASE_URL)
    
    # You can override credentials via command line arguments
    email = sys.argv[1] if len(sys.argv) > 1 else TEST_USER_EMAIL
    password = sys.argv[2] if len(sys.argv) > 2 else TEST_USER_PASSWORD
    
    success = validator.run_all_tests(email, password)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
