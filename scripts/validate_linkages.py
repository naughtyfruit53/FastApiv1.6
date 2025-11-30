#!/usr/bin/env python3
"""
Linkage Validation Script
Validates that frontend pages have corresponding backend API routes.
Run as part of CI to ensure frontend-backend consistency.
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

# Expected API routes for each frontend module
EXPECTED_LINKAGES = {
    "auth": ["auth.py", "login.py", "oauth.py"],
    "dashboard": ["entitlements.py", "admin.py"],
    "vouchers": ["vouchers/"],
    "hr": ["hr.py"],
    "crm": ["crm.py"],
    "inventory": ["inventory.py", "stock.py"],
    "admin": ["admin.py", "rbac.py"],
    "ai": ["ai.py"],
    "demo": ["demo.py"],
    "exhibition": ["exhibition.py"],
    "reports": ["reports.py"],
    "settings": ["settings.py"],
    "service": ["service_desk.py", "dispatch.py"],
    "marketing": ["marketing.py"],
    "manufacturing": ["manufacturing/"],
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


def find_service_api_calls(service_file: Path) -> Set[str]:
    """Extract API endpoint paths from a service file."""
    endpoints = set()
    if not service_file.exists():
        return endpoints
    
    content = service_file.read_text()
    
    # Match API path patterns
    patterns = [
        r'api/v1/([a-zA-Z0-9_-]+)',
        r'/api/v1/([a-zA-Z0-9_-]+)',
        r'"([a-zA-Z0-9_-]+)".*fetch',
        r"'([a-zA-Z0-9_-]+)'.*fetch",
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, content)
        endpoints.update(matches)
    
    return endpoints


def validate_linkages() -> Tuple[List[str], List[str], int]:
    """Validate frontend-backend linkages."""
    errors = []
    warnings = []
    score = 100
    
    frontend_pages = find_frontend_pages()
    backend_routes = find_backend_routes()
    
    print(f"Found {len(frontend_pages)} frontend modules")
    print(f"Found {len(backend_routes)} backend route files")
    
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
    
    # Check for orphan backend routes (routes without frontend usage)
    # This is informational, not an error
    core_routes = {"health.py", "debug.py", "__init__.py", "reset.py"}
    for route in backend_routes:
        if route in core_routes or route.endswith("/"):
            continue
        
        route_base = route.replace(".py", "").replace("_", "-")
        found_usage = False
        
        for module in frontend_pages:
            if route_base in module or module in route_base:
                found_usage = True
                break
        
        if not found_usage:
            warnings.append(f"Backend route '{route}' may not have frontend coverage")
    
    return errors, warnings, max(0, score)


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
    
    # Generate report
    report = {
        "score": score,
        "errors_count": len(errors),
        "warnings_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
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
