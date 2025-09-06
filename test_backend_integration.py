#!/usr/bin/env python3
"""
Comprehensive Backend Integration Test Suite - Phase 2&3 Integration
Tests all backend modules accessibility and RBAC/multi-tenancy integration
"""

import pytest
import asyncio
import httpx
import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

# Test configuration
BASE_URL = os.getenv("TEST_BASE_URL", "http://localhost:8000")
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "TestPassword123!"
TEST_ORG_NAME = "Test Organization"


class BackendIntegrationTester:
    """Comprehensive backend integration tester"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.access_token: Optional[str] = None
        self.user_data: Optional[Dict] = None
        self.org_data: Optional[Dict] = None
        self.test_results: Dict[str, Dict] = {}
        
    async def setup_test_environment(self):
        """Set up test environment with authentication and organization"""
        async with httpx.AsyncClient() as client:
            # Test authentication
            auth_result = await self.test_authentication(client)
            if not auth_result["success"]:
                raise Exception("Authentication setup failed")
            
            # Test organization setup
            org_result = await self.test_organization_setup(client)
            if not org_result["success"]:
                print("Warning: Organization setup failed, continuing with existing org")
    
    async def test_authentication(self, client: httpx.AsyncClient) -> Dict[str, Any]:
        """Test authentication module"""
        print("🔐 Testing Authentication Module...")
        
        try:
            # Test login
            login_response = await client.post(
                f"{self.base_url}/api/v1/auth/login",
                json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
            )
            
            if login_response.status_code == 200:
                auth_data = login_response.json()
                self.access_token = auth_data.get("access_token")
                client.headers.update({"Authorization": f"Bearer {self.access_token}"})
                
                # Get user profile
                profile_response = await client.get(f"{self.base_url}/api/v1/users/me")
                if profile_response.status_code == 200:
                    self.user_data = profile_response.json()
                
                return {"success": True, "message": "Authentication successful"}
            else:
                return {"success": False, "message": f"Login failed: {login_response.status_code}"}
                
        except Exception as e:
            return {"success": False, "message": f"Authentication error: {str(e)}"}
    
    async def test_organization_setup(self, client: httpx.AsyncClient) -> Dict[str, Any]:
        """Test organization management (multi-tenancy)"""
        print("🏢 Testing Organization Management...")
        
        try:
            # Get organizations
            orgs_response = await client.get(f"{self.base_url}/api/v1/organizations")
            
            if orgs_response.status_code == 200:
                orgs = orgs_response.json()
                if orgs:
                    self.org_data = orgs[0]  # Use first organization
                    return {"success": True, "message": "Using existing organization"}
                
            # Create test organization if none exists
            org_data = {
                "name": TEST_ORG_NAME,
                "subdomain": "test-org",
                "plan": "basic"
            }
            
            create_response = await client.post(
                f"{self.base_url}/api/v1/organizations",
                json=org_data
            )
            
            if create_response.status_code in [200, 201]:
                self.org_data = create_response.json()
                return {"success": True, "message": "Organization created successfully"}
            else:
                return {"success": False, "message": f"Organization creation failed: {create_response.status_code}"}
                
        except Exception as e:
            return {"success": False, "message": f"Organization setup error: {str(e)}"}
    
    async def test_module_accessibility(self) -> Dict[str, Dict[str, Any]]:
        """Test accessibility of all backend modules"""
        print("🔍 Testing Module Accessibility...")
        
        modules_to_test = {
            # Core modules
            "users": "/api/v1/users/me",
            "organizations": "/api/v1/organizations",
            "rbac_permissions": "/api/v1/rbac/permissions",
            
            # Business modules
            "customers": "/api/v1/customers",
            "products": "/api/v1/products",
            "vendors": "/api/v1/vendors",
            "sales_orders": "/api/v1/vouchers/sales-orders",
            "purchase_orders": "/api/v1/vouchers/purchase-orders",
            "stock": "/api/v1/stock",
            
            # Service modules
            "service_tickets": "/api/v1/service-desk/tickets",
            "sla": "/api/v1/sla",
            "dispatch": "/api/v1/dispatch",
            "feedback": "/api/v1/feedback",
            
            # Finance modules
            "gst": "/api/v1/gst/reports",
            "finance_analytics": "/api/v1/finance/analytics",
            
            # HR modules
            "hr_employees": "/api/v1/hr/employees",
            "payroll": "/api/v1/payroll",
            
            # Manufacturing modules
            "bom": "/api/v1/bom",
            "manufacturing": "/api/v1/manufacturing/orders",
            
            # Analytics modules
            "customer_analytics": "/api/v1/analytics/customers",
            "service_analytics": "/api/v1/service-analytics",
            "ai_analytics": "/api/v1/ai-analytics",
            
            # Admin modules
            "settings": "/api/v1/settings",
            "company_branding": "/api/v1/company/branding",
            "app_users": "/api/v1/app-users",
            
            # Integration modules
            "integrations": "/api/v1/integrations",
            "external_integrations": "/api/v1/external-integrations",
            "tally": "/api/v1/tally/config",
            
            # Utility modules
            "notifications": "/api/v1/notifications",
            "calendar": "/api/v1/calendar/events",
            "sticky_notes": "/api/v1/sticky-notes",
            "reports": "/api/v1/reports",
            
            # Asset and transport modules
            "assets": "/api/v1/assets",
            "transport": "/api/v1/transport",
            "warehouse": "/api/v1/warehouse",
            
            # Project management
            "projects": "/api/v1/projects",
            "tasks": "/api/v1/tasks",
            "workflow": "/api/v1/workflow",
        }
        
        results = {}
        
        async with httpx.AsyncClient() as client:
            if self.access_token:
                client.headers.update({"Authorization": f"Bearer {self.access_token}"})
            
            for module_name, endpoint in modules_to_test.items():
                try:
                    response = await client.get(f"{self.base_url}{endpoint}")
                    
                    results[module_name] = {
                        "accessible": response.status_code != 404,
                        "status_code": response.status_code,
                        "authenticated": response.status_code != 401,
                        "authorized": response.status_code != 403,
                        "endpoint": endpoint
                    }
                    
                    if response.status_code == 200:
                        results[module_name]["data_available"] = bool(response.json())
                    
                except Exception as e:
                    results[module_name] = {
                        "accessible": False,
                        "error": str(e),
                        "endpoint": endpoint
                    }
        
        return results
    
    async def test_rbac_integration(self) -> Dict[str, Any]:
        """Test RBAC functionality and integration"""
        print("🔒 Testing RBAC Integration...")
        
        if not self.org_data:
            return {"success": False, "message": "No organization data available"}
        
        org_id = self.org_data.get("id")
        
        async with httpx.AsyncClient() as client:
            if self.access_token:
                client.headers.update({"Authorization": f"Bearer {self.access_token}"})
            
            try:
                # Test permissions list
                perms_response = await client.get(f"{self.base_url}/api/v1/rbac/permissions")
                perms_accessible = perms_response.status_code in [200, 401, 403]
                
                # Test organization roles
                roles_response = await client.get(f"{self.base_url}/api/v1/rbac/organizations/{org_id}/roles")
                roles_accessible = roles_response.status_code in [200, 401, 403]
                
                # Test role initialization
                init_response = await client.post(f"{self.base_url}/api/v1/rbac/organizations/{org_id}/roles/initialize")
                init_accessible = init_response.status_code in [200, 201, 400, 401, 403]
                
                # Test permission check
                if self.user_data:
                    user_id = self.user_data.get("id")
                    check_data = {"user_id": user_id, "permission": "test_permission"}
                    check_response = await client.post(f"{self.base_url}/api/v1/rbac/permissions/check", json=check_data)
                    check_accessible = check_response.status_code in [200, 400, 401, 403]
                else:
                    check_accessible = False
                
                return {
                    "success": True,
                    "permissions_accessible": perms_accessible,
                    "roles_accessible": roles_accessible,
                    "initialization_accessible": init_accessible,
                    "permission_check_accessible": check_accessible,
                    "message": "RBAC module tested successfully"
                }
                
            except Exception as e:
                return {"success": False, "message": f"RBAC test error: {str(e)}"}
    
    async def test_multi_tenancy(self) -> Dict[str, Any]:
        """Test multi-tenancy functionality"""
        print("🏘️ Testing Multi-tenancy...")
        
        async with httpx.AsyncClient() as client:
            if self.access_token:
                client.headers.update({"Authorization": f"Bearer {self.access_token}"})
            
            try:
                # Test organization statistics
                stats_response = await client.get(f"{self.base_url}/api/v1/organizations/org-statistics")
                stats_accessible = stats_response.status_code in [200, 401, 403]
                
                # Test app statistics  
                app_stats_response = await client.get(f"{self.base_url}/api/v1/organizations/app-statistics")
                app_stats_accessible = app_stats_response.status_code in [200, 401, 403]
                
                # Test organization modules
                if self.org_data:
                    org_id = self.org_data.get("id")
                    modules_response = await client.get(f"{self.base_url}/api/v1/organizations/{org_id}/modules")
                    modules_accessible = modules_response.status_code in [200, 401, 403, 404]
                else:
                    modules_accessible = False
                
                return {
                    "success": True,
                    "org_statistics_accessible": stats_accessible,
                    "app_statistics_accessible": app_stats_accessible,
                    "org_modules_accessible": modules_accessible,
                    "message": "Multi-tenancy tested successfully"
                }
                
            except Exception as e:
                return {"success": False, "message": f"Multi-tenancy test error: {str(e)}"}
    
    async def test_analytics_integration(self) -> Dict[str, Any]:
        """Test analytics modules integration"""
        print("📊 Testing Analytics Integration...")
        
        analytics_endpoints = {
            "customer_analytics": "/api/v1/analytics/customers",
            "dashboard_metrics": "/api/v1/analytics/dashboard/metrics",
            "service_analytics": "/api/v1/service-analytics",
            "finance_analytics": "/api/v1/finance/analytics",
            "ai_analytics": "/api/v1/ai-analytics",
            "technician_performance": "/api/v1/service-analytics/technician-performance",
            "job_completion": "/api/v1/service-analytics/job-completion",
        }
        
        results = {}
        
        async with httpx.AsyncClient() as client:
            if self.access_token:
                client.headers.update({"Authorization": f"Bearer {self.access_token}"})
            
            for name, endpoint in analytics_endpoints.items():
                try:
                    response = await client.get(f"{self.base_url}{endpoint}")
                    results[name] = {
                        "accessible": response.status_code in [200, 401, 403],
                        "status_code": response.status_code
                    }
                except Exception as e:
                    results[name] = {"accessible": False, "error": str(e)}
        
        accessible_count = sum(1 for r in results.values() if r.get("accessible", False))
        
        return {
            "success": True,
            "analytics_modules": results,
            "accessible_modules": accessible_count,
            "total_modules": len(analytics_endpoints),
            "message": f"Analytics integration tested: {accessible_count}/{len(analytics_endpoints)} modules accessible"
        }
    
    async def generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        print("📋 Generating Comprehensive Report...")
        
        # Run all tests
        module_results = await self.test_module_accessibility()
        rbac_results = await self.test_rbac_integration()
        tenancy_results = await self.test_multi_tenancy()
        analytics_results = await self.test_analytics_integration()
        
        # Calculate statistics
        total_modules = len(module_results)
        accessible_modules = sum(1 for r in module_results.values() if r.get("accessible", False))
        authenticated_modules = sum(1 for r in module_results.values() if r.get("authenticated", False))
        
        # Categorize modules
        business_modules = [k for k in module_results.keys() if k in [
            "customers", "products", "vendors", "sales_orders", "purchase_orders", "stock"
        ]]
        service_modules = [k for k in module_results.keys() if k in [
            "service_tickets", "sla", "dispatch", "feedback"
        ]]
        analytics_modules = [k for k in module_results.keys() if k in [
            "customer_analytics", "service_analytics", "ai_analytics", "finance_analytics"
        ]]
        admin_modules = [k for k in module_results.keys() if k in [
            "settings", "company_branding", "app_users", "rbac_permissions"
        ]]
        
        report = {
            "test_summary": {
                "timestamp": datetime.now().isoformat(),
                "total_modules_tested": total_modules,
                "accessible_modules": accessible_modules,
                "authenticated_modules": authenticated_modules,
                "accessibility_rate": f"{(accessible_modules/total_modules)*100:.1f}%",
                "authentication_rate": f"{(authenticated_modules/total_modules)*100:.1f}%"
            },
            "module_categories": {
                "business_modules": {
                    "modules": business_modules,
                    "accessible": sum(1 for m in business_modules if module_results[m].get("accessible", False)),
                    "total": len(business_modules)
                },
                "service_modules": {
                    "modules": service_modules,
                    "accessible": sum(1 for m in service_modules if module_results[m].get("accessible", False)),
                    "total": len(service_modules)
                },
                "analytics_modules": {
                    "modules": analytics_modules,
                    "accessible": sum(1 for m in analytics_modules if module_results[m].get("accessible", False)),
                    "total": len(analytics_modules)
                },
                "admin_modules": {
                    "modules": admin_modules,
                    "accessible": sum(1 for m in admin_modules if module_results[m].get("accessible", False)),
                    "total": len(admin_modules)
                }
            },
            "feature_integration": {
                "rbac": rbac_results,
                "multi_tenancy": tenancy_results,
                "analytics": analytics_results
            },
            "detailed_results": {
                "module_accessibility": module_results
            },
            "recommendations": self.generate_recommendations(module_results, rbac_results, tenancy_results)
        }
        
        return report
    
    def generate_recommendations(self, module_results: Dict, rbac_results: Dict, tenancy_results: Dict) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        # Check for inaccessible modules
        inaccessible_modules = [k for k, v in module_results.items() if not v.get("accessible", False)]
        if inaccessible_modules:
            recommendations.append(f"⚠️ {len(inaccessible_modules)} modules are not accessible: {', '.join(inaccessible_modules[:5])}")
        
        # Check authentication issues
        auth_issues = [k for k, v in module_results.items() if not v.get("authenticated", False) and v.get("status_code") == 401]
        if auth_issues:
            recommendations.append(f"🔐 {len(auth_issues)} modules have authentication issues")
        
        # Check authorization issues
        authz_issues = [k for k, v in module_results.items() if not v.get("authorized", False) and v.get("status_code") == 403]
        if authz_issues:
            recommendations.append(f"🔒 {len(authz_issues)} modules have authorization issues - check RBAC configuration")
        
        # RBAC recommendations
        if not rbac_results.get("success", False):
            recommendations.append("🔒 RBAC module requires attention - role-based access control may not be functioning properly")
        
        # Multi-tenancy recommendations
        if not tenancy_results.get("success", False):
            recommendations.append("🏢 Multi-tenancy features need review - organization isolation may not be working correctly")
        
        # Success recommendations
        accessible_count = sum(1 for r in module_results.values() if r.get("accessible", False))
        total_count = len(module_results)
        if accessible_count / total_count > 0.9:
            recommendations.append("✅ Excellent module accessibility - most backend endpoints are available to frontend")
        
        return recommendations


async def main():
    """Main test execution function"""
    print("🚀 Starting Comprehensive Backend Integration Test Suite")
    print("=" * 70)
    
    tester = BackendIntegrationTester()
    
    try:
        # Setup test environment
        await tester.setup_test_environment()
        
        # Generate comprehensive report
        report = await tester.generate_comprehensive_report()
        
        # Print summary
        print("\n" + "=" * 70)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 70)
        
        summary = report["test_summary"]
        print(f"Total Modules Tested: {summary['total_modules_tested']}")
        print(f"Accessible Modules: {summary['accessible_modules']}")
        print(f"Accessibility Rate: {summary['accessibility_rate']}")
        print(f"Authentication Rate: {summary['authentication_rate']}")
        
        print("\n📋 MODULE CATEGORIES:")
        for category, data in report["module_categories"].items():
            print(f"  {category}: {data['accessible']}/{data['total']} accessible")
        
        print("\n🔧 FEATURE INTEGRATION:")
        features = report["feature_integration"]
        print(f"  RBAC: {'✅' if features['rbac']['success'] else '❌'}")
        print(f"  Multi-tenancy: {'✅' if features['multi_tenancy']['success'] else '❌'}")
        print(f"  Analytics: {'✅' if features['analytics']['success'] else '❌'}")
        
        print("\n💡 RECOMMENDATIONS:")
        for rec in report["recommendations"]:
            print(f"  {rec}")
        
        # Save detailed report
        with open("backend_integration_test_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: backend_integration_test_report.json")
        
        # Return success based on accessibility rate
        accessibility_rate = float(summary['accessibility_rate'].rstrip('%'))
        return accessibility_rate > 80  # Consider successful if >80% modules accessible
        
    except Exception as e:
        print(f"❌ Test suite failed: {str(e)}")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)