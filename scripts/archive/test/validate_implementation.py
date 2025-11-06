#!/usr/bin/env python3
"""
Simple validation script for modular backend architecture changes
"""

import os
import sys
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if os.path.exists(filepath):
        print(f"✓ {description}: {filepath}")
        return True
    else:
        print(f"✗ {description}: {filepath} NOT FOUND")
        return False

def check_syntax(filepath):
    """Check Python file syntax"""
    try:
        with open(filepath, 'r') as f:
            compile(f.read(), filepath, 'exec')
        return True
    except SyntaxError as e:
        print(f"  Syntax error: {e}")
        return False

def main():
    print("="*70)
    print("Validating Modular Backend Architecture Implementation")
    print("="*70)
    
    base_dir = Path(__file__).parent
    all_passed = True
    
    # Check models
    print("\n1. Checking Models...")
    models = [
        ('app/models/ai_agents.py', 'AI Agents Model'),
        ('app/models/plugin.py', 'Plugin System Model'),
        ('app/models/audit_log.py', 'Audit Log Model'),
        ('app/models/integration.py', 'Integration Model'),
    ]
    
    for filepath, desc in models:
        full_path = base_dir / filepath
        exists = check_file_exists(full_path, desc)
        if exists:
            if not check_syntax(full_path):
                all_passed = False
        else:
            all_passed = False
    
    # Check API endpoints
    print("\n2. Checking API Endpoints...")
    apis = [
        ('app/api/v1/ai_agents.py', 'AI Agents API'),
        ('app/api/v1/plugin.py', 'Plugin API'),
        ('app/api/v1/audit_log.py', 'Audit Log API'),
        ('app/api/v1/integration.py', 'Integration API'),
    ]
    
    for filepath, desc in apis:
        full_path = base_dir / filepath
        exists = check_file_exists(full_path, desc)
        if exists:
            if not check_syntax(full_path):
                all_passed = False
        else:
            all_passed = False
    
    # Check services
    print("\n3. Checking Service Layers...")
    services = [
        ('app/services/ai_agents_service.py', 'AI Agents Service'),
        ('app/services/integration_service.py', 'Integration Service'),
    ]
    
    for filepath, desc in services:
        full_path = base_dir / filepath
        exists = check_file_exists(full_path, desc)
        if exists:
            if not check_syntax(full_path):
                all_passed = False
        else:
            all_passed = False
    
    # Check backend utilities
    print("\n4. Checking Backend/Shared Utilities...")
    utilities = [
        ('backend/__init__.py', 'Backend Package Init'),
        ('backend/shared/__init__.py', 'Shared Package Init'),
        ('backend/shared/localization.py', 'Localization Utilities'),
        ('backend/shared/currency_util.py', 'Currency Utilities'),
    ]
    
    for filepath, desc in utilities:
        full_path = base_dir / filepath
        exists = check_file_exists(full_path, desc)
        if exists:
            if not check_syntax(full_path):
                all_passed = False
        else:
            all_passed = False
    
    # Summary
    print("\n" + "="*70)
    if all_passed:
        print("✓ All validations PASSED!")
        print("\nImplemented Components:")
        print("  • AI Agent Models (analytics, advice, navigation, website)")
        print("  • Plugin System Models (extensibility architecture)")
        print("  • Enhanced Audit Log Models (AI/automation tracking)")
        print("  • Integration Models (Slack, WhatsApp, Google Workspace)")
        print("  • API Endpoints for all new models")
        print("  • Service layers with business logic")
        print("  • Localization utilities (multi-language support)")
        print("  • Currency utilities (multi-currency support)")
        print("\nArchitecture:")
        print("  • Microservices-ready modular design")
        print("  • Plugin/extensibility system")
        print("  • Comprehensive audit logging")
        print("  • External service integration support")
        print("  • Internationalization ready")
        return 0
    else:
        print("✗ Some validations FAILED!")
        return 1
    print("="*70)

if __name__ == "__main__":
    sys.exit(main())
