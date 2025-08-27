#!/usr/bin/env python3
"""
FastApiV1.5 Comprehensive UI Audit System

This script performs automated UI auditing by:
1. Logging into the system
2. Navigating through all major menus and submenus
3. Testing feature accessibility and functionality
4. Generating comprehensive audit reports in Markdown and JSON formats

Author: Automated UI Audit System
Version: 1.0
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import argparse
import sys
import os

try:
    from playwright.async_api import async_playwright, Browser, Page, BrowserContext, TimeoutError
except ImportError:
    print("❌ Playwright not installed. Run: pip install playwright && playwright install")
    sys.exit(1)


@dataclass
class AuditResult:
    """Data class for individual feature audit results"""
    feature_name: str
    path: str
    status: str  # 'accessible', 'broken', 'not_accessible'
    load_time: float
    error_message: Optional[str] = None
    suggestions: List[str] = None
    screenshot_path: Optional[str] = None
    

@dataclass
class MenuSection:
    """Data class for menu section structure"""
    title: str
    items: List[Dict[str, Any]]


class UIAuditSystem:
    """Main UI Audit System class"""
    
    def __init__(self, base_url: str = "http://localhost:3000", 
                 api_url: str = "http://localhost:8000",
                 headless: bool = True,
                 screenshots: bool = True):
        self.base_url = base_url.rstrip('/')
        self.api_url = api_url.rstrip('/')
        self.headless = headless
        self.screenshots = screenshots
        self.results: List[AuditResult] = []
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        
        # Create audit directories
        self.audit_dir = Path("audit_results")
        self.screenshots_dir = self.audit_dir / "screenshots"
        self.audit_dir.mkdir(exist_ok=True)
        self.screenshots_dir.mkdir(exist_ok=True)
        
        # Define comprehensive menu structure based on FEATURE_AUDIT.md
        self.menu_structure = {
            "dashboard": {
                "title": "Dashboard",
                "path": "/dashboard",
                "items": [
                    {"name": "Main Dashboard", "path": "/dashboard"}
                ]
            },
            "masters": {
                "title": "Master Data",
                "path": "/masters", 
                "items": [
                    {"name": "Vendors", "path": "/masters?tab=vendors"},
                    {"name": "Customers", "path": "/masters?tab=customers"},
                    {"name": "Employees", "path": "/masters?tab=employees"},
                    {"name": "Products", "path": "/masters?tab=products"},
                    {"name": "Categories", "path": "/masters?tab=categories"},
                    {"name": "Units", "path": "/masters?tab=units"},
                    {"name": "Chart of Accounts", "path": "/masters?tab=accounts"},
                    {"name": "Tax Codes", "path": "/masters?tab=tax-codes"},
                    {"name": "Payment Terms", "path": "/masters?tab=payment-terms"},
                    {"name": "Bill of Materials", "path": "/masters?tab=bom"}
                ]
            },
            "inventory": {
                "title": "Inventory Management",
                "path": "/inventory",
                "items": [
                    {"name": "Current Stock", "path": "/inventory/stock"},
                    {"name": "Stock Movements", "path": "/inventory/movements"},
                    {"name": "Low Stock Report", "path": "/inventory/low-stock"},
                    {"name": "Stock Adjustments", "path": "/inventory/adjustments"}
                ]
            },
            "vouchers": {
                "title": "Vouchers",
                "path": "/vouchers",
                "items": [
                    # Purchase Vouchers
                    {"name": "Purchase Order", "path": "/vouchers/Purchase-Vouchers/purchase-order"},
                    {"name": "GRN", "path": "/vouchers/Purchase-Vouchers/grn"},
                    {"name": "Purchase Voucher", "path": "/vouchers/Purchase-Vouchers/purchase-voucher"},
                    {"name": "Purchase Return", "path": "/vouchers/Purchase-Vouchers/purchase-return"},
                    
                    # Pre-Sales Vouchers
                    {"name": "Quotation", "path": "/vouchers/Pre-Sales-Voucher/quotation"},
                    {"name": "Proforma Invoice", "path": "/vouchers/Pre-Sales-Voucher/proforma-invoice"},
                    {"name": "Sales Order", "path": "/vouchers/Pre-Sales-Voucher/sales-order"},
                    
                    # Sales Vouchers
                    {"name": "Sales Voucher", "path": "/vouchers/Sales-Vouchers/sales-voucher"},
                    {"name": "Sales Return", "path": "/vouchers/Sales-Vouchers/sales-return"},
                    
                    # Financial Vouchers
                    {"name": "Payment Voucher", "path": "/vouchers/Financial-Vouchers/payment-voucher"},
                    {"name": "Receipt Voucher", "path": "/vouchers/Financial-Vouchers/receipt-voucher"},
                    {"name": "Journal Voucher", "path": "/vouchers/Financial-Vouchers/journal-voucher"},
                    {"name": "Credit Note", "path": "/vouchers/Financial-Vouchers/credit-note"},
                    {"name": "Debit Note", "path": "/vouchers/Financial-Vouchers/debit-note"},
                    
                    # Manufacturing Vouchers
                    {"name": "Production Order", "path": "/vouchers/Manufacturing-Vouchers/production-order"},
                    {"name": "Material Requisition", "path": "/vouchers/Manufacturing-Vouchers/material-requisition"},
                    {"name": "Work Order", "path": "/vouchers/Manufacturing-Vouchers/work-order"},
                    {"name": "Material Receipt", "path": "/vouchers/Manufacturing-Vouchers/material-receipt"}
                ]
            },
            "reports": {
                "title": "Reports & Analytics",
                "path": "/reports",
                "items": [
                    {"name": "Sales Reports", "path": "/reports/sales-report"},
                    {"name": "Purchase Reports", "path": "/reports/purchase-report"},
                    {"name": "Inventory Reports", "path": "/reports/inventory-report"},
                    {"name": "Financial Reports", "path": "/reports/financial-reports"},
                    {"name": "Complete Ledger", "path": "/reports/complete-ledger"},
                    {"name": "Outstanding Ledger", "path": "/reports/outstanding-ledger"},
                    {"name": "Pending Orders", "path": "/reports/pending-orders"}
                ]
            },
            "service_crm": {
                "title": "Service CRM",
                "path": "/service",
                "items": [
                    {"name": "Service Dashboard", "path": "/service/dashboard"},
                    {"name": "Customer Management", "path": "/service/customers"},
                    {"name": "Ticket Management", "path": "/service/tickets"},
                    {"name": "Installation Tasks", "path": "/service/installation-tasks"},
                    {"name": "Service Analytics", "path": "/service/analytics"},
                    {"name": "Feedback Management", "path": "/service/feedback"}
                ]
            },
            "settings": {
                "title": "Settings",
                "path": "/settings",
                "items": [
                    {"name": "Organization Settings", "path": "/settings/organization"},
                    {"name": "Company Profile", "path": "/settings/company"},
                    {"name": "User Management", "path": "/settings/users"},
                    {"name": "Role Management", "path": "/settings/roles"},
                    {"name": "License Management", "path": "/settings/licenses"}
                ]
            }
        }

    async def start_browser(self):
        """Initialize browser and context"""
        print("🚀 Starting browser...")
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=self.headless,
            args=['--disable-web-security', '--disable-features=VizDisplayCompositor']
        )
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            ignore_https_errors=True
        )
        self.page = await self.context.new_page()
        
        # Set up console logging
        self.page.on("console", lambda msg: print(f"🖥️  Console: {msg.text}"))
        self.page.on("pageerror", lambda error: print(f"❌ Page Error: {error}"))

    async def login(self, username: str = "potymatic@gmail.com", password: str = "Abcd1234@"):
        """Perform login to the system"""
        print(f"🔐 Attempting login with {username}...")
        
        try:
            await self.page.goto(f"{self.base_url}/login", timeout=30000)
            await self.page.wait_for_load_state('networkidle', timeout=10000)
            
            # Fill login form
            await self.page.fill('input[name="email"], input[type="email"]', username)
            await self.page.fill('input[name="password"], input[type="password"]', password)
            
            # Brief pause for any async operations
            await self.page.wait_for_timeout(2000)
            
            # Use locator to click
            login_button = self.page.locator('button[type="submit"], button:text("Login"), button:text("Sign In")')
            await login_button.click(force=True, timeout=60000)
            
            # Wait for navigation or dashboard with longer timeout and retry
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    await self.page.wait_for_url('**/dashboard', timeout=60000)  # Increased to 60s
                    print("✅ Login successful!")
                    return True
                except:
                    # Alternative success check
                    try:
                        await self.page.wait_for_selector('[data-testid="dashboard"], .dashboard, h1:has-text("Dashboard")', timeout=60000)  # Increased to 60s
                        print("✅ Login successful (alternative check)!")
                        return True
                    except Exception as e:
                        print(f"⚠️ Login attempt {attempt + 1}/{max_retries} failed: {str(e)}")
                        if attempt < max_retries - 1:
                            await self.page.wait_for_timeout(5000)  # Wait before retry
                        else:
                            raise
        except Exception as e:
            print(f"❌ Login failed: {str(e)}")
            await self.take_screenshot("login_failure")
            return False

    async def take_screenshot(self, name: str, suffix: str = ""):
        """Take a screenshot for debugging"""
        if not self.screenshots:
            return None
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{suffix}_{timestamp}.png" if suffix else f"{name}_{timestamp}.png"
        screenshot_path = self.screenshots_dir / filename
        
        try:
            await self.page.screenshot(path=str(screenshot_path), full_page=True)
            return str(screenshot_path)
        except Exception as e:
            print(f"⚠️  Failed to take screenshot {filename}: {e}")
            return None

    async def audit_feature(self, feature_name: str, path: str) -> AuditResult:
        """Audit a single feature/page"""
        print(f"🔍 Auditing: {feature_name} ({path})")
        
        start_time = time.time()
        result = AuditResult(
            feature_name=feature_name,
            path=path,
            status="not_accessible",
            load_time=0,
            suggestions=[]
        )
        
        try:
            # Navigate to the feature
            full_url = f"{self.base_url}{path}"
            response = await self.page.goto(full_url, timeout=30000)
            
            # Check for HTTP status (detect 404)
            if response and response.status == 404:
                result.status = "broken"
                result.error_message = "404 Page Not Found"
                result.suggestions.append("Fix invalid path or routing configuration")
                print(f"  ❌ 404 Error: Page not found")
                return result  # Early return for 404
            
            # Wait for page to load
            await self.page.wait_for_load_state('networkidle', timeout=10000)
            
            # Wait for loading spinner to disappear
            await self.page.wait_for_selector('.auth-spinner', state='detached', timeout=60000)  # Wait until spinner is gone
            
            # Calculate load time
            load_time = time.time() - start_time
            result.load_time = round(load_time, 2)
            
            # Check for error indicators
            error_selectors = [
                '[data-testid="error"]',
                '.error',
                '.error-message',
                'h1:has-text("404")',
                'h1:has-text("Error")',
                'h1:has-text("Not Found")',
                '.MuiAlert-standardError',
                '[role="alert"]'
            ]
            
            error_found = False
            for selector in error_selectors:
                try:
                    error_element = await self.page.wait_for_selector(selector, state='visible', timeout=5000)
                    if error_element:
                        error_text = await error_element.text_content()
                        if error_text and "Loading" not in error_text and "Establishing" not in error_text:  # Ignore loading text
                            result.error_message = error_text[:200] if error_text else "Visible error element found"
                            error_found = True
                            break
                except TimeoutError:
                    continue
            
            if error_found:
                result.status = "broken"
                result.suggestions.append("Fix error or exception preventing page load")
                print(f"  ❌ Error found: {result.error_message}")
            else:
                # Check if page has meaningful content
                content_selectors = [
                    'main',
                    '.content',
                    '[data-testid="main-content"]',
                    'form',
                    'table',
                    '.MuiDataGrid-root',
                    '.ant-table',
                    'h1, h2, h3'
                ]
                
                has_content = False
                for selector in content_selectors:
                    try:
                        content = await self.page.wait_for_selector(selector, state='visible', timeout=5000)
                        if content:
                            has_content = True
                            break
                    except TimeoutError:
                        continue
                
                if has_content:
                    result.status = "accessible"
                    print(f"  ✅ Accessible (loaded in {load_time:.2f}s)")
                    
                    # Performance suggestions
                    if load_time > 5:
                        result.suggestions.append("Consider optimizing page load time (>5s)")
                    elif load_time > 3:
                        result.suggestions.append("Page load time could be improved (>3s)")
                else:
                    result.status = "not_accessible"
                    result.suggestions.append("Page loads but appears to lack meaningful content")
                    print(f"  ⚠️  Page loads but lacks content")
            
            # Take screenshot for broken or problematic pages
            if result.status in ["broken", "not_accessible"] or load_time > 5:
                screenshot_path = await self.take_screenshot(
                    f"audit_{feature_name.replace(' ', '_').lower()}",
                    result.status
                )
                result.screenshot_path = screenshot_path
                
        except Exception as e:
            result.status = "broken"
            result.error_message = str(e)[:200]
            result.load_time = time.time() - start_time
            result.suggestions.append("Fix navigation or runtime error")
            print(f"  ❌ Failed to audit: {str(e)}")
            
            # Take screenshot of failure
            screenshot_path = await self.take_screenshot(
                f"audit_{feature_name.replace(' ', '_').lower()}",
                "failed"
            )
            result.screenshot_path = screenshot_path
        
        return result

    async def audit_menu_navigation(self):
        """Test navigation through the mega menu"""
        print("🧭 Testing mega menu navigation...")
        
        try:
            await self.page.goto(f"{self.base_url}/dashboard")
            await self.page.wait_for_load_state('networkidle')
            
            # Check if mega menu is present
            menu_selectors = [
                '[data-testid="mega-menu"]',
                '.mega-menu',
                'nav',
                '.MuiAppBar-root',
                '.ant-menu'
            ]
            
            menu_found = False
            for selector in menu_selectors:
                try:
                    menu = await self.page.query_selector(selector)
                    if menu:
                        menu_found = True
                        break
                except:
                    continue
            
            if not menu_found:
                print("⚠️  Could not locate mega menu component")
                return
            
            print("✅ Mega menu component found")
            
            # Test hover/click interactions for major menu items
            menu_items = ["Masters", "ERP", "Reports", "Service CRM", "Settings"]
            
            for item in menu_items:
                try:
                    # Try to hover over menu item
                    menu_item = await self.page.query_selector(f'text="{item}"')
                    if menu_item:
                        await menu_item.hover()
                        await self.page.wait_for_timeout(500)  # Brief pause for submenu
                        print(f"  ✅ {item} menu item responsive")
                    else:
                        print(f"  ⚠️  {item} menu item not found")
                except Exception as e:
                    print(f"  ❌ Error testing {item} menu: {str(e)}")
                    
        except Exception as e:
            print(f"❌ Menu navigation test failed: {str(e)}")

    async def run_comprehensive_audit(self):
        """Run the complete audit process"""
        print("🎯 Starting Comprehensive UI Audit")
        print("=" * 50)
        
        await self.start_browser()
        
        # Login first
        login_success = await self.login()
        if not login_success:
            print("❌ Cannot proceed without successful login")
            await self.cleanup()
            return
        
        # Test menu navigation
        await self.audit_menu_navigation()
        
        # Audit all features
        print("\n📋 Auditing Individual Features:")
        print("-" * 30)
        
        total_features = sum(len(section["items"]) for section in self.menu_structure.values())
        current = 0
        
        for section_key, section in self.menu_structure.items():
            print(f"\n📂 {section['title']} Section:")
            
            for item in section["items"]:
                current += 1
                print(f"  [{current}/{total_features}]", end=" ")
                
                result = await self.audit_feature(item["name"], item["path"])
                self.results.append(result)
                
                # Brief pause between requests
                await self.page.wait_for_timeout(500)
        
        print(f"\n🏁 Audit Complete! Processed {len(self.results)} features")
        await self.cleanup()

    async def cleanup(self):
        """Clean up browser resources"""
        if self.browser:
            try:
                await self.browser.close()
            except Exception as e:
                print(f"Browser close error: {e}")

    def generate_summary_stats(self) -> Dict[str, Any]:
        """Generate summary statistics"""
        total = len(self.results)
        if total == 0:
            return {
                "audit_date": datetime.now().isoformat(),
                "total_features": 0,
                "accessible": 0,
                "broken": 0,
                "not_accessible": 0,
                "accessibility_rate": 0,
                "average_load_time": 0,
                "slow_pages_count": 0,
                "performance_grade": "N/A"
            }
        accessible = len([r for r in self.results if r.status == "accessible"])
        broken = len([r for r in self.results if r.status == "broken"])
        not_accessible = len([r for r in self.results if r.status == "not_accessible"])
        
        avg_load_time = sum(r.load_time for r in self.results) / total if total > 0 else 0
        slow_pages = len([r for r in self.results if r.load_time > 3])
        
        return {
            "audit_date": datetime.now().isoformat(),
            "total_features": total,
            "accessible": accessible,
            "broken": broken,
            "not_accessible": not_accessible,
            "accessibility_rate": round((accessible / total) * 100, 1) if total > 0 else 0,
            "average_load_time": round(avg_load_time, 2),
            "slow_pages_count": slow_pages,
            "performance_grade": self._calculate_performance_grade(avg_load_time, slow_pages, total)
        }

    def _calculate_performance_grade(self, avg_load_time: float, slow_pages: int, total: int) -> str:
        """Calculate performance grade"""
        if total == 0:
            return "N/A"
        if avg_load_time < 2 and slow_pages == 0:
            return "A+"
        elif avg_load_time < 3 and slow_pages < total * 0.1:
            return "A"
        elif avg_load_time < 4 and slow_pages < total * 0.2:
            return "B"
        elif avg_load_time < 5 and slow_pages < total * 0.3:
            return "C"
        else:
            return "D"

    def generate_improvement_suggestions(self) -> List[str]:
        """Generate overall improvement suggestions"""
        suggestions = []
        stats = self.generate_summary_stats()
        
        # Accessibility suggestions
        if stats["accessibility_rate"] < 90:
            suggestions.append("🎯 Priority: Fix broken or inaccessible features to reach 90%+ accessibility")
        
        if stats["accessibility_rate"] < 95:
            suggestions.append("🔧 Investigate and resolve remaining accessibility issues")
        
        # Performance suggestions
        if stats["average_load_time"] > 3:
            suggestions.append("⚡ Performance: Optimize page load times (target <3s average)")
        
        if stats["slow_pages_count"] > 0:
            suggestions.append(f"📈 Performance: Address {stats['slow_pages_count']} slow-loading pages")
        
        # Feature-specific suggestions
        broken_features = [r for r in self.results if r.status == "broken"]
        if broken_features:
            suggestions.append(f"🚨 Critical: {len(broken_features)} features are completely broken and need immediate attention")
        
        # UX suggestions
        not_accessible_features = [r for r in self.results if r.status == "not_accessible"]
        if not_accessible_features:
            suggestions.append(f"🔍 UX: {len(not_accessible_features)} features may need better content or navigation design")
        
        return suggestions

    def save_json_report(self) -> str:
        """Save detailed JSON report"""
        stats = self.generate_summary_stats()
        suggestions = self.generate_improvement_suggestions()
        
        report_data = {
            "audit_metadata": {
                "system": "FastApiV1.5 TRITIQ ERP",
                "audit_date": stats["audit_date"],
                "base_url": self.base_url,
                "total_features_tested": stats["total_features"]
            },
            "summary_statistics": stats,
            "improvement_suggestions": suggestions,
            "detailed_results": [asdict(result) for result in self.results],
            "workflow_mapping": {
                section_key: {
                    "title": section["title"],
                    "path": section["path"],
                    "feature_count": len(section["items"]),
                    "accessibility_rate": round(
                        (len([r for r in self.results 
                              if r.path in [item["path"] for item in section["items"]] 
                              and r.status == "accessible"]) / len(section["items"])) * 100, 1
                    ) if len(section["items"]) > 0 else 0
                }
                for section_key, section in self.menu_structure.items()
            }
        }
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_path = self.audit_dir / f"audit_report_{timestamp}.json"
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"📄 JSON report saved: {json_path}")
        return str(json_path)

    def save_markdown_report(self) -> str:
        """Save comprehensive Markdown report"""
        stats = self.generate_summary_stats()
        suggestions = self.generate_improvement_suggestions()
        
        # Group results by status
        accessible = [r for r in self.results if r.status == "accessible"]
        broken = [r for r in self.results if r.status == "broken"]
        not_accessible = [r for r in self.results if r.status == "not_accessible"]
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        markdown_content = f"""# FastApiV1.5 UI Audit Report

**Generated:** {timestamp}  
**System:** TRITIQ ERP - FastAPI Backend + Next.js Frontend  
**Base URL:** {self.base_url}  
**Features Tested:** {stats['total_features']}

## 📊 Executive Summary

| Metric | Value | Grade |
|--------|-------|-------|
| **Total Features Tested** | {stats['total_features']} | - |
| **Accessibility Rate** | {stats['accessibility_rate']}% | {'🟢' if stats['accessibility_rate'] >= 95 else '🟡' if stats['accessibility_rate'] >= 85 else '🔴'} |
| **Average Load Time** | {stats['average_load_time']}s | {stats['performance_grade']} |
| **Accessible Features** | {stats['accessible']} | ✅ |
| **Broken Features** | {stats['broken']} | {'❌' if stats['broken'] > 0 else '✅'} |
| **Not Accessible Features** | {stats['not_accessible']} | {'⚠️' if stats['not_accessible'] > 0 else '✅'} |

## 🎯 Key Findings

### Accessibility Status
- **{stats['accessible']} features** are fully accessible and working correctly
- **{stats['broken']} features** are broken or throwing errors  
- **{stats['not_accessible']} features** load but may lack proper content

### Performance Analysis
- **Average load time:** {stats['average_load_time']}s
- **Performance grade:** {stats['performance_grade']}
- **Slow pages (>3s):** {stats['slow_pages_count']}

## 🔧 Improvement Recommendations

"""
        
        for i, suggestion in enumerate(suggestions, 1):
            markdown_content += f"{i}. {suggestion}\n"
        
        markdown_content += f"""

## 📈 Workflow Mapping

| Module | Features | Accessibility Rate | Status |
|--------|----------|-------------------|---------|
"""
        
        for section_key, section in self.menu_structure.items():
            section_results = [r for r in self.results if r.path in [item["path"] for item in section["items"]]]
            accessible_count = len([r for r in section_results if r.status == "accessible"])
            total_count = len(section["items"])
            rate = round((accessible_count / total_count) * 100, 1) if total_count > 0 else 0
            status = "🟢 Excellent" if rate >= 95 else "🟡 Good" if rate >= 85 else "🔴 Needs Work"
            
            markdown_content += f"| **{section['title']}** | {total_count} | {rate}% | {status} |\n"
        
        markdown_content += f"""

## ✅ Accessible Features ({len(accessible)})

"""
        
        for result in accessible:
            load_indicator = "⚡" if result.load_time < 2 else "🐌" if result.load_time > 3 else "✅"
            markdown_content += f"- **{result.feature_name}** `{result.path}` {load_indicator} ({result.load_time}s)\n"
        
        if broken:
            markdown_content += f"""

## ❌ Broken Features ({len(broken)})

"""
            for result in broken:
                error_msg = result.error_message[:100] + "..." if result.error_message and len(result.error_message) > 100 else result.error_message or "Unknown error"
                markdown_content += f"- **{result.feature_name}** `{result.path}`\n"
                markdown_content += f"  - Error: {error_msg}\n"
                if result.suggestions:
                    markdown_content += f"  - Suggestion: {'; '.join(result.suggestions)}\n"
                markdown_content += "\n"
        
        if not_accessible:
            markdown_content += f"""

## ⚠️ Not Accessible Features ({len(not_accessible)})

"""
            for result in not_accessible:
                markdown_content += f"- **{result.feature_name}** `{result.path}` ({result.load_time}s)\n"
                if result.suggestions:
                    markdown_content += f"  - Suggestions: {'; '.join(result.suggestions)}\n"
        
        markdown_content += f"""

## 🔍 Detailed Analysis

### Performance Distribution
"""
        
        # Performance breakdown
        fast_pages = len([r for r in self.results if r.load_time < 2])
        medium_pages = len([r for r in self.results if 2 <= r.load_time <= 3])
        slow_pages = len([r for r in self.results if r.load_time > 3])
        
        markdown_content += f"""
- **Fast pages (<2s):** {fast_pages} ({round(fast_pages/stats['total_features']*100, 1) if stats['total_features'] > 0 else 0}%)
- **Medium pages (2-3s):** {medium_pages} ({round(medium_pages/stats['total_features']*100, 1) if stats['total_features'] > 0 else 0}%)
- **Slow pages (>3s):** {slow_pages} ({round(slow_pages/stats['total_features']*100, 1) if stats['total_features'] > 0 else 0}%)

### Next Steps

1. **Immediate Actions:** Fix broken features to restore functionality
2. **Short-term Goals:** Improve accessibility of non-accessible features  
3. **Long-term Optimization:** Enhance performance for slow-loading pages
4. **Monitoring:** Set up automated alerts for new accessibility issues

---

**Audit System:** FastApiV1.5 Automated UI Audit  
**Report Format:** Comprehensive Markdown + JSON  
**Next Audit:** Recommended within 7 days for broken features, 30 days for accessible features
"""
        
        timestamp_file = datetime.now().strftime("%Y%m%d_%H%M%S")
        markdown_path = self.audit_dir / f"audit_report_{timestamp_file}.md"
        
        with open(markdown_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"📝 Markdown report saved: {markdown_path}")
        return str(markdown_path)


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="FastApiV1.5 UI Audit System")
    parser.add_argument("--url", default="http://localhost:3000", help="Frontend URL")
    parser.add_argument("--api", default="http://localhost:8000", help="API URL") 
    parser.add_argument("--username", default="potymatic@gmail.com", help="Login username")
    parser.add_argument("--password", default="Abcd1234@", help="Login password")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode")
    parser.add_argument("--no-screenshots", action="store_true", help="Disable screenshots")
    
    args = parser.parse_args()
    
    print("🎯 FastApiV1.5 Comprehensive UI Audit System")
    print("=" * 50)
    print(f"Frontend URL: {args.url}")
    print(f"API URL: {args.api}")
    print(f"Headless mode: {args.headless}")
    print(f"Screenshots: {not args.no_screenshots}")
    print("")
    
    # Initialize audit system
    audit_system = UIAuditSystem(
        base_url=args.url,
        api_url=args.api, 
        headless=args.headless,
        screenshots=not args.no_screenshots
    )
    
    try:
        # Run comprehensive audit
        await audit_system.run_comprehensive_audit()
        
        # Generate reports
        print("\n📊 Generating Reports...")
        json_path = audit_system.save_json_report()
        markdown_path = audit_system.save_markdown_report()
        
        # Print summary
        stats = audit_system.generate_summary_stats()
        print(f"\n\n🎊 Audit Complete!")
        print(f"📈 Accessibility Rate: {stats['accessibility_rate']}%")
        print(f"⚡ Average Load Time: {stats['average_load_time']}s")
        print(f"📄 Reports saved to: {audit_system.audit_dir}")
        
        # Exit code based on results
        if stats['broken'] > 0:
            print("⚠️  Warning: Broken features detected")
            sys.exit(1)
        elif stats['accessibility_rate'] < 85:
            print("⚠️  Warning: Low accessibility rate")
            sys.exit(1)
        else:
            print("✅ All systems operational!")
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n🛑 Audit interrupted by user")
        await audit_system.cleanup()
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Audit failed: {str(e)}")
        await audit_system.cleanup()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())