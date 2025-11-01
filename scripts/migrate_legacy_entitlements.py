#!/usr/bin/env python3
"""
Legacy entitlements migration script.

This script migrates legacy organization module flags to the new entitlements system.
It reads the legacy enabled_modules JSON field and maps it to module/submodule entitlements.

Features:
- Dry-run mode to preview changes
- Idempotent - can be run multiple times safely
- Uses entitlement_mapping_template.csv for mappings
- Creates audit events for all changes
"""

import sys
import os
import csv
import argparse
from pathlib import Path
from typing import Dict, List, Set, Tuple
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert

from app.core.config import settings
from app.models.entitlement_models import Module, Submodule, OrgEntitlement, OrgSubentitlement, EntitlementEvent
from app.models.user_models import Organization


def load_mapping_template(csv_path: str) -> List[Dict]:
    """Load entitlement mappings from CSV"""
    mappings = []
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            mappings.append({
                'legacy_flag': row['legacy_flag'],
                'legacy_route_pattern': row['legacy_route_pattern'],
                'target_module': row['target_module'],
                'target_submodule': row['target_submodule'],
                'default_status': row['default_status'],
                'notes': row.get('notes', '')
            })
    return mappings


def extract_legacy_module_key(legacy_flag: str) -> str:
    """Extract module key from legacy flag (e.g., 'enabled_modules.sales' -> 'sales')"""
    if legacy_flag.startswith('enabled_modules.'):
        return legacy_flag.replace('enabled_modules.', '')
    return legacy_flag


class LegacyMigrator:
    """Migrator for legacy entitlements"""
    
    def __init__(self, session: Session, dry_run: bool = True):
        self.session = session
        self.dry_run = dry_run
        self.stats = {
            'orgs_processed': 0,
            'modules_created': 0,
            'modules_updated': 0,
            'submodules_created': 0,
            'submodules_updated': 0,
            'events_created': 0,
            'errors': 0
        }
    
    def get_modules_map(self) -> Dict[str, int]:
        """Get module_key -> id mapping"""
        result = self.session.execute(select(Module))
        return {m.module_key: m.id for m in result.scalars().all()}
    
    def get_submodules_map(self) -> Dict[Tuple[int, str], int]:
        """Get (module_id, submodule_key) -> id mapping"""
        result = self.session.execute(select(Submodule))
        submodules_map = {}
        for sub in result.scalars().all():
            submodules_map[(sub.module_id, sub.submodule_key)] = sub.id
        return submodules_map
    
    def map_legacy_to_modules(
        self,
        enabled_modules: Dict,
        mappings: List[Dict],
        modules_map: Dict[str, int]
    ) -> Dict[str, str]:
        """
        Map legacy enabled_modules to module entitlements.
        Returns dict of module_key -> status
        """
        module_entitlements = {}
        
        # Process module-level flags
        for mapping in mappings:
            if not mapping['target_submodule']:  # Module-level mapping
                legacy_key = extract_legacy_module_key(mapping['legacy_flag'])
                target_module = mapping['target_module']
                default_status = mapping['default_status']
                
                # Check if module is enabled in legacy system
                is_enabled = enabled_modules.get(legacy_key, False) if enabled_modules else False
                
                if is_enabled and target_module in modules_map:
                    module_entitlements[target_module] = default_status
        
        return module_entitlements
    
    def map_legacy_to_submodules(
        self,
        enabled_modules: Dict,
        mappings: List[Dict],
        modules_map: Dict[str, int],
        submodules_map: Dict[Tuple[int, str], int]
    ) -> List[Tuple[int, int, bool]]:
        """
        Map legacy route access to submodule entitlements.
        Returns list of (module_id, submodule_id, enabled)
        """
        submodule_entitlements = []
        
        # Process submodule-level mappings
        for mapping in mappings:
            if mapping['target_submodule']:  # Submodule-level mapping
                target_module = mapping['target_module']
                target_submodule = mapping['target_submodule']
                
                if target_module in modules_map:
                    module_id = modules_map[target_module]
                    key = (module_id, target_submodule)
                    
                    if key in submodules_map:
                        submodule_id = submodules_map[key]
                        # For now, default all to enabled if module is enabled
                        # In a real scenario, you'd check route-level flags
                        legacy_key = extract_legacy_module_key(mapping['legacy_flag'])
                        is_enabled = enabled_modules.get(legacy_key, False) if enabled_modules else False
                        
                        if is_enabled:
                            submodule_entitlements.append((module_id, submodule_id, True))
        
        return submodule_entitlements
    
    def migrate_organization(
        self,
        org: Organization,
        mappings: List[Dict],
        modules_map: Dict[str, int],
        submodules_map: Dict[Tuple[int, str], int]
    ):
        """Migrate entitlements for a single organization"""
        print(f"\n📋 Processing organization: {org.name} (ID: {org.id})")
        
        # Get legacy enabled_modules
        enabled_modules = org.enabled_modules or {}
        print(f"   Legacy enabled_modules: {list(enabled_modules.keys())}")
        
        # Map to new entitlements
        module_entitlements = self.map_legacy_to_modules(enabled_modules, mappings, modules_map)
        print(f"   Mapped modules: {list(module_entitlements.keys())}")
        
        changes = []
        
        # Apply module entitlements
        for module_key, status in module_entitlements.items():
            module_id = modules_map[module_key]
            
            # Check if already exists
            result = self.session.execute(
                select(OrgEntitlement).where(
                    OrgEntitlement.org_id == org.id,
                    OrgEntitlement.module_id == module_id
                )
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                if existing.source == 'legacy_migration':
                    print(f"   ℹ Module '{module_key}' already migrated, skipping")
                    continue
                else:
                    print(f"   ⚠ Module '{module_key}' has manual entitlement, skipping")
                    continue
            
            if not self.dry_run:
                org_ent = OrgEntitlement(
                    org_id=org.id,
                    module_id=module_id,
                    status=status,
                    source='legacy_migration'
                )
                self.session.add(org_ent)
                self.stats['modules_created'] += 1
            
            changes.append({
                'type': 'module',
                'module_key': module_key,
                'status': status
            })
            print(f"   ✓ {'[DRY-RUN] Would create' if self.dry_run else 'Created'} module entitlement: {module_key} -> {status}")
        
        # Create entitlement event
        if changes and not self.dry_run:
            event = EntitlementEvent(
                org_id=org.id,
                event_type='legacy_migration',
                actor_user_id=None,
                reason='Automated migration from legacy enabled_modules',
                payload={'changes': changes, 'migration_date': datetime.utcnow().isoformat()}
            )
            self.session.add(event)
            self.stats['events_created'] += 1
        
        self.stats['orgs_processed'] += 1
    
    def migrate_all(self, mappings: List[Dict]):
        """Migrate all organizations"""
        print("\n" + "=" * 70)
        print("LEGACY ENTITLEMENTS MIGRATION")
        print("=" * 70)
        print(f"Mode: {'DRY-RUN (no changes will be made)' if self.dry_run else 'EXECUTE'}")
        print("=" * 70)
        
        # Get mappings
        modules_map = self.get_modules_map()
        submodules_map = self.get_submodules_map()
        
        print(f"\n📊 Loaded {len(modules_map)} modules and {len(submodules_map)} submodules")
        print(f"📊 Loaded {len(mappings)} mapping rules")
        
        # Get all organizations
        result = self.session.execute(select(Organization))
        orgs = result.scalars().all()
        
        print(f"📊 Found {len(orgs)} organizations to process\n")
        
        # Process each organization
        for org in orgs:
            try:
                self.migrate_organization(org, mappings, modules_map, submodules_map)
            except Exception as e:
                print(f"❌ Error processing org {org.id}: {e}")
                self.stats['errors'] += 1
                import traceback
                traceback.print_exc()
        
        # Commit if not dry-run
        if not self.dry_run:
            self.session.commit()
            print("\n✓ Changes committed to database")
        else:
            self.session.rollback()
            print("\n[DRY-RUN] No changes were made to the database")
        
        # Print summary
        print("\n" + "=" * 70)
        print("MIGRATION SUMMARY")
        print("=" * 70)
        print(f"Organizations processed: {self.stats['orgs_processed']}")
        print(f"Module entitlements created: {self.stats['modules_created']}")
        print(f"Module entitlements updated: {self.stats['modules_updated']}")
        print(f"Submodule entitlements created: {self.stats['submodules_created']}")
        print(f"Submodule entitlements updated: {self.stats['submodules_updated']}")
        print(f"Events created: {self.stats['events_created']}")
        print(f"Errors: {self.stats['errors']}")
        print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description='Migrate legacy entitlements to new system')
    parser.add_argument(
        '--execute',
        action='store_true',
        help='Execute migration (default is dry-run)'
    )
    parser.add_argument(
        '--mapping-csv',
        type=str,
        default=None,
        help='Path to entitlement_mapping_template.csv'
    )
    
    args = parser.parse_args()
    
    # Load mapping template
    if args.mapping_csv:
        csv_path = args.mapping_csv
    else:
        csv_path = Path(__file__).parent.parent / "docs" / "entitlements" / "entitlement_mapping_template.csv"
    
    if not Path(csv_path).exists():
        print(f"❌ Error: Mapping CSV not found at {csv_path}")
        sys.exit(1)
    
    print(f"📄 Loading mappings from: {csv_path}")
    mappings = load_mapping_template(str(csv_path))
    
    # Create database session
    engine = create_engine(settings.DATABASE_URL)
    session = Session(engine)
    
    try:
        migrator = LegacyMigrator(session, dry_run=not args.execute)
        migrator.migrate_all(mappings)
    except KeyboardInterrupt:
        print("\n\n⚠ Migration interrupted by user")
        session.rollback()
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        session.rollback()
        sys.exit(1)
    finally:
        session.close()


if __name__ == "__main__":
    main()
