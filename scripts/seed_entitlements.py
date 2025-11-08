#!/usr/bin/env python3
"""
Seed script for entitlements: modules and submodules taxonomy.
This script is idempotent and can be run multiple times safely.
"""

import sys
import os
import csv
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from app.core.config import settings
from app.models.entitlement_models import Module, Submodule


# Module definitions
MODULES = [
    {"module_key": "sales", "display_name": "Sales & CRM", "description": "Sales pipeline, leads, opportunities, and customer management", "icon": "Business", "sort_order": 1},
    {"module_key": "inventory", "display_name": "Inventory", "description": "Stock management, locations, and movements", "icon": "Inventory", "sort_order": 2},
    {"module_key": "manufacturing", "display_name": "Manufacturing", "description": "Production orders, work orders, jobwork, and quality control", "icon": "Factory", "sort_order": 3},
    {"module_key": "vouchers", "display_name": "Vouchers", "description": "Sales, purchase, and accounting vouchers", "icon": "Receipt", "sort_order": 4},
    {"module_key": "finance", "display_name": "Finance", "description": "Financial management, invoices, bills, and analytics", "icon": "AccountBalance", "sort_order": 5},
    {"module_key": "service", "display_name": "Service CRM", "description": "Service desk, tickets, appointments, and SLA management", "icon": "SupportAgent", "sort_order": 6},
    {"module_key": "projects", "display_name": "Projects", "description": "Project planning, tracking, and resource management", "icon": "Assignment", "sort_order": 7},
    {"module_key": "ai_analytics", "display_name": "AI & Analytics", "description": "Predictive analytics, AutoML, business advisor, and AI tools", "icon": "SmartToy", "sort_order": 8},
    {"module_key": "reports", "display_name": "Reports & Analytics", "description": "Business reports and analytics dashboards", "icon": "BarChart", "sort_order": 9},
    {"module_key": "tasks_calendar", "display_name": "Tasks & Calendar", "description": "Task management, calendar, events, and appointments", "icon": "CalendarToday", "sort_order": 10},
    {"module_key": "email", "display_name": "Email", "description": "Email inbox, compose, templates, and sync", "icon": "Email", "sort_order": 11},
    {"module_key": "settings", "display_name": "Settings", "description": "Organization settings and configuration", "icon": "Settings", "sort_order": 12},
    {"module_key": "master_data", "display_name": "Master Data", "description": "Core data: vendors, customers, products, employees", "icon": "Storage", "sort_order": 13},
    {"module_key": "accounting", "display_name": "Accounting", "description": "Chart of accounts, journal entries, ledgers, and financial statements", "icon": "AccountBalance", "sort_order": 14},
    {"module_key": "hr", "display_name": "Human Resources", "description": "Employee management, payroll, attendance, and recruitment", "icon": "People", "sort_order": 15},
    {"module_key": "marketing", "display_name": "Marketing", "description": "Campaigns, promotions, email marketing, and analytics", "icon": "Campaign", "sort_order": 16},
    {"module_key": "administration", "display_name": "Administration", "description": "Admin tools and demo mode", "icon": "AdminPanelSettings", "sort_order": 17},
]


def load_submodules_from_csv(csv_path: str) -> dict:
    """Load submodules from menu_permission_map.csv grouped by module"""
    submodules_by_module = {}
    
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader):
            module_key = row['module']
            submodule_key = row['submodule']
            menu_path = row['menu_path']
            permission = row['permission']
            
            # Generate display name from submodule_key
            display_name = submodule_key.replace('_', ' ').title()
            
            if module_key not in submodules_by_module:
                submodules_by_module[module_key] = []
            
            submodules_by_module[module_key].append({
                'submodule_key': submodule_key,
                'display_name': display_name,
                'menu_path': menu_path,
                'permission_key': permission,
                'sort_order': idx,
            })
    
    return submodules_by_module


def seed_modules(session: Session):
    """Seed modules using UPSERT (INSERT ... ON CONFLICT)"""
    print("Seeding modules...")
    
    for module_data in MODULES:
        stmt = insert(Module).values(**module_data)
        stmt = stmt.on_conflict_do_update(
            index_elements=['module_key'],
            set_={
                'display_name': stmt.excluded.display_name,
                'description': stmt.excluded.description,
                'icon': stmt.excluded.icon,
                'sort_order': stmt.excluded.sort_order,
            }
        )
        session.execute(stmt)
    
    session.commit()
    print(f"✓ Seeded {len(MODULES)} modules")


def seed_submodules(session: Session, submodules_by_module: dict):
    """Seed submodules using UPSERT with do_nothing on conflict"""
    print("Seeding submodules...")
    
    # Get module IDs
    modules = {m.module_key: m.id for m in session.execute(select(Module)).scalars().all()}
    
    total_count = 0
    for module_key, submodules in submodules_by_module.items():
        if module_key not in modules:
            print(f"⚠ Warning: Module '{module_key}' not found, skipping its submodules")
            continue
        
        module_id = modules[module_key]
        
        for submodule_data in submodules:
            data = {
                'module_id': module_id,
                **submodule_data
            }
            
            stmt = insert(Submodule).values(**data)
            stmt = stmt.on_conflict_do_nothing(
                index_elements=['module_id', 'submodule_key']
            )
            result = session.execute(stmt)
            if result.rowcount > 0:
                total_count += 1
    
    session.commit()
    print(f"✓ Seeded {total_count} new submodules across {len(submodules_by_module)} modules (skipped existing)")


def main():
    """Main seed function"""
    print("=" * 60)
    print("Entitlements Taxonomy Seeder")
    print("=" * 60)
    
    # Load submodules from CSV
    csv_path = Path(__file__).parent.parent / "docs" / "entitlements" / "menu_permission_map.csv"
    if not csv_path.exists():
        print(f"❌ Error: menu_permission_map.csv not found at {csv_path}")
        sys.exit(1)
    
    print(f"Loading submodules from {csv_path}...")
    submodules_by_module = load_submodules_from_csv(str(csv_path))
    print(f"✓ Loaded submodules for {len(submodules_by_module)} modules")
    
    # Create database session
    engine = create_engine(settings.DATABASE_URL)
    session = Session(engine)
    
    try:
        # Seed modules
        seed_modules(session)
        
        # Seed submodules
        seed_submodules(session, submodules_by_module)
        
        print("\n" + "=" * 60)
        print("✓ Seeding completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        session.rollback()
        print(f"\n❌ Error during seeding: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        session.close()


if __name__ == "__main__":
    main()
