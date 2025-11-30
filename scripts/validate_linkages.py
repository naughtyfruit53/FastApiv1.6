#!/usr/bin/env python3
"""
Linkage Validation Script
Validates that frontend pages have corresponding backend API routes.
Run as part of CI to ensure frontend-backend consistency.

Enhanced for PR A: Comprehensive router vs client usage mapping.
"""

import os
import sys
import re
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Repository root
REPO_ROOT = Path(__file__).parent.parent

# Paths to scan
FRONTEND_PAGES_DIR = REPO_ROOT / "frontend" / "src" / "pages"
FRONTEND_SERVICES_DIR = REPO_ROOT / "frontend" / "src" / "services"
BACKEND_API_DIR = REPO_ROOT / "app" / "api" / "v1"
BACKEND_MAIN_FILE = REPO_ROOT / "app" / "main.py"

# Expected API routes for each frontend module
EXPECTED_LINKAGES = {
    "auth": ["auth.py", "login.py", "oauth.py"],
    "dashboard": ["entitlements.py", "admin.py"],
    "vouchers": ["vouchers/"],
    "hr": ["hr.py", "payroll.py"],
    "crm": ["crm.py"],
    "inventory": ["inventory.py", "stock.py"],
    "admin": ["admin.py", "rbac.py"],
    "ai": ["ai.py", "chatbot.py"],
    "demo": ["demo.py"],
    "exhibition": ["exhibition.py"],
    "reports": ["reports.py", "management_reports.py"],
    "settings": ["settings.py"],
    "service": ["service_desk.py", "dispatch.py"],
    "marketing": ["marketing.py"],
    "manufacturing": ["manufacturing/"],
    "analytics": ["ai_analytics.py", "customer_analytics.py", "finance_analytics.py"],
    "calendar": ["calendar.py"],
    "tasks": ["tasks.py"],
    "projects": ["project_management.py"],
    "transport": ["transport.py"],
    "assets": ["assets.py"],
    "email": ["email.py", "mail.py"],
    "integrations": ["integration.py", "integration_settings.py"],
    "plugins": ["plugin.py"],
}

# Service file to backend router mapping
SERVICE_ROUTER_MAP = {
    "authService.ts": ["auth.py", "demo.py", "otp.py", "oauth.py", "password.py"],
    "adminService.ts": ["admin.py", "admin_setup.py", "admin_categories.py", "admin_entitlements.py"],
    "organizationService.ts": ["organizations/", "companies.py", "company_branding.py"],
    "userService.ts": ["user.py", "org_user_management.py"],
    "rbacService.ts": ["rbac.py", "role_delegation.py"],
    "vouchersService.ts": ["vouchers/", "dispatch.py"],
    "masterService.ts": ["master_data.py", "products.py", "customers.py", "vendors.py", "items.py", "bom.py"],
    "stockService.ts": ["inventory.py", "stock.py", "warehouse.py"],
    "crmService.ts": ["crm.py", "contacts.py", "ledger.py"],
    "analyticsService.ts": ["customer_analytics.py", "finance_analytics.py", "service_analytics.py"],
    "aiService.ts": ["ai.py", "ai_agents.py", "ai_analytics.py", "chatbot.py"],
    "hrService.ts": ["hr.py", "payroll.py"],
    "reportsService.ts": ["reports.py", "management_reports.py", "reporting_hub.py"],
    "emailService.ts": ["email.py", "mail.py"],
    "serviceDeskService.ts": ["service_desk.py"],
    "exhibitionService.ts": ["exhibition.py"],
    "dispatchService.ts": ["dispatch.py"],
    "feedbackService.ts": ["feedback.py"],
    "slaService.ts": ["sla.py"],
    "transportService.ts": ["transport.py"],
    "assetService.ts": ["assets.py"],
    "marketingService.ts": ["marketing.py"],
    "integrationService.ts": ["integration.py", "integration_settings.py", "external_integrations.py"],
    "notificationService.ts": ["notifications.py"],
    "activityService.ts": ["calendar.py", "tasks.py", "project_management.py"],
    "automlService.ts": ["automl.py", "ml_algorithms.py", "ml_analytics.py"],
    "abTestingService.ts": ["ab_testing.py"],
    "streamingAnalyticsService.ts": ["streaming_analytics.py"],
    "tallyService.ts": ["tally.py"],
    "websiteAgentService.ts": ["website_agent.py"],
    "pdfService.ts": ["pdf_generation.py"],
}


def find_frontend_pages() -> Set[str]:
    """Find all frontend pages."""
    pages = set()
    if not FRONTEND_PAGES_DIR.exists():
        return pages
    
    for tsx_file in FRONTEND_PAGES_DIR.rglob("*.tsx"):
        # Skip internal Next.js files
        if tsx_file.name.startswith("_"):
            continue
        
        # Get relative path from pages directory
        rel_path = tsx_file.relative_to(FRONTEND_PAGES_DIR)
        module = str(rel_path.parts[0]) if len(rel_path.parts) > 0 else "root"
        pages.add(module)
    
    return pages


def find_backend_routes() -> Set[str]:
    """Find all backend API routes."""
    routes = set()
    if not BACKEND_API_DIR.exists():
        return routes
    
    for py_file in BACKEND_API_DIR.rglob("*.py"):
        if py_file.name == "__init__.py":
            continue
        routes.add(py_file.name)
    
    # Also check for subdirectories (like vouchers/, manufacturing/)
    for subdir in BACKEND_API_DIR.iterdir():
        if subdir.is_dir() and not subdir.name.startswith("_"):
            routes.add(f"{subdir.name}/")
    
    return routes


def find_frontend_services() -> Set[str]:
    """Find all frontend service files."""
    services = set()
    if not FRONTEND_SERVICES_DIR.exists():
        return services
    
    for ts_file in FRONTEND_SERVICES_DIR.glob("*.ts"):
        if ts_file.name.endswith("Service.ts") or ts_file.name == "index.ts":
            services.add(ts_file.name)
    
    return services


def find_service_api_calls(service_file: Path) -> Set[str]:
    """Extract API endpoint paths from a service file."""
    endpoints = set()
    if not service_file.exists():
        return endpoints
    
    content = service_file.read_text()
    
    # Match API path patterns
    patterns = [
        r'api/v1/([a-zA-Z0-9_/-]+)',
        r'/api/v1/([a-zA-Z0-9_/-]+)',
        r'this\.endpoint\s*=\s*["\']/?([a-zA-Z0-9_/-]+)["\']',
        r'`\${this\.endpoint}/([a-zA-Z0-9_/-]+)`',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, content)
        for match in matches:
            # Clean up the endpoint
            endpoint = match.strip("/").split("/")[0]
            endpoints.add(endpoint)
    
    return endpoints


def check_registered_routers() -> List[str]:
    """Check which routers are registered in main.py."""
    registered = []
    if not BACKEND_MAIN_FILE.exists():
        return registered
    
    content = BACKEND_MAIN_FILE.read_text()
    
    # Pattern to match router imports and registrations
    import_pattern = r'from\s+app\.api\.v1(?:\.(\w+))?\s+import\s+(?:router\s+as\s+(\w+)|(\w+))'
    registration_pattern = r'routers\.append\s*\(\s*\([^,]+,\s*["\']([^"\']+)["\']'
    
    for match in re.finditer(registration_pattern, content):
        prefix = match.group(1)
        registered.append(prefix)
    
    return registered


def validate_linkages() -> Tuple[List[str], List[str], int]:
    """Validate frontend-backend linkages."""
    errors = []
    warnings = []
    score = 100
    
    frontend_pages = find_frontend_pages()
    backend_routes = find_backend_routes()
    frontend_services = find_frontend_services()
    registered_routers = check_registered_routers()
    
    print(f"Found {len(frontend_pages)} frontend modules")
    print(f"Found {len(backend_routes)} backend route files")
    print(f"Found {len(frontend_services)} frontend services")
    print(f"Found {len(registered_routers)} registered routers")
    
    # Check that expected linkages exist
    for module, expected_backends in EXPECTED_LINKAGES.items():
        if module in frontend_pages:
            for backend in expected_backends:
                if backend.endswith("/"):
                    # Check for directory
                    if backend[:-1] not in [r.replace("/", "") for r in backend_routes if "/" in r]:
                        errors.append(f"Frontend module '{module}' expects backend '{backend}' but not found")
                        score -= 5
                else:
                    if backend not in backend_routes:
                        errors.append(f"Frontend module '{module}' expects backend '{backend}' but not found")
                        score -= 5
    
    # Check service file to router mapping
    for service, expected_routers in SERVICE_ROUTER_MAP.items():
        service_path = FRONTEND_SERVICES_DIR / service
        if service_path.exists():
            for router in expected_routers:
                if router.endswith("/"):
                    if router not in backend_routes and f"{router[:-1]}/" not in backend_routes:
                        warnings.append(f"Service '{service}' expects router '{router}' but not found in backend")
                elif router not in backend_routes:
                    warnings.append(f"Service '{service}' expects router '{router}' but not found in backend")
    
    # Check for orphan backend routes (routes without frontend usage)
    core_routes = {"health.py", "debug.py", "__init__.py", "reset.py", "pdf_extraction.py", 
                   "gst_search.py", "pincode.py", "master_auth.py"}
    for route in backend_routes:
        if route in core_routes or route.endswith("/"):
            continue
        
        route_base = route.replace(".py", "").replace("_", "-")
        found_usage = False
        
        for module in frontend_pages:
            if route_base in module or module in route_base:
                found_usage = True
                break
        
        # Check in service map
        for service, routers in SERVICE_ROUTER_MAP.items():
            if route in routers:
                found_usage = True
                break
        
        if not found_usage:
            warnings.append(f"Backend route '{route}' may not have frontend coverage")
    
    return errors, warnings, max(0, score)


def generate_linkage_report() -> Dict:
    """Generate a comprehensive linkage report."""
    frontend_pages = find_frontend_pages()
    backend_routes = find_backend_routes()
    frontend_services = find_frontend_services()
    registered_routers = check_registered_routers()
    
    # Build detailed mapping
    page_to_service = {}
    for page in frontend_pages:
        possible_services = []
        for service, routers in SERVICE_ROUTER_MAP.items():
            # Check if any router name relates to the page
            for router in routers:
                router_base = router.replace(".py", "").replace("/", "").replace("_", "")
                if router_base in page.lower() or page.lower() in router_base:
                    possible_services.append(service)
                    break
        page_to_service[page] = list(set(possible_services))
    
    return {
        "frontend_pages": sorted(frontend_pages),
        "backend_routes": sorted(backend_routes),
        "frontend_services": sorted(frontend_services),
        "registered_routers": registered_routers,
        "page_to_service_mapping": page_to_service,
        "service_to_router_mapping": SERVICE_ROUTER_MAP,
    }


def main():
    """Main entry point."""
    print("=" * 60)
    print("Frontend-Backend Linkage Validation")
    print("=" * 60)
    print()
    
    errors, warnings, score = validate_linkages()
    
    print()
    print("-" * 60)
    print(f"Validation Score: {score}/100")
    print("-" * 60)
    
    if errors:
        print()
        print("ERRORS:")
        for error in errors:
            print(f"  ❌ {error}")
    
    if warnings:
        print()
        print("WARNINGS:")
        for warning in warnings[:10]:  # Limit warnings output
            print(f"  ⚠️ {warning}")
        if len(warnings) > 10:
            print(f"  ... and {len(warnings) - 10} more warnings")
    
    print()
    print("=" * 60)
    
    # Generate comprehensive report
    linkage_report = generate_linkage_report()
    
    # Generate validation report
    report = {
        "score": score,
        "errors_count": len(errors),
        "warnings_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "linkage_details": linkage_report,
    }
    
    report_path = REPO_ROOT / "docs" / "linkage_validation_report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"Report saved to: {report_path}")
    
    # Exit with error if validation failed
    if errors:
        print()
        print("❌ Validation FAILED")
        sys.exit(1)
    else:
        print()
        print("✅ Validation PASSED")
        sys.exit(0)


if __name__ == "__main__":
    main()
