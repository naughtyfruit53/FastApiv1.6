"""Normalize enabled_modules keys to lowercase and ensure organization module

Revision ID: 20251101_01_normalize
Revises: 784448bbeca4_merge_multiple_heads_for_entitlements
Create Date: 2025-11-01

This migration normalizes enabled_modules for all existing organizations:
1. Detects if the column is JSON or JSONB
2. Lowercases all keys in enabled_modules
3. Converts string/numeric values to proper booleans
4. Ensures "organization": true exists for all organizations
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text
import json

# Revision identifiers, used by Alembic.
revision = '20251101_01_normalize'
down_revision = '784448bbeca4'  # Latest merge head for entitlements
branch_labels = None
depends_on = None


def normalize_modules_dict(modules_dict):
    """Normalize a modules dictionary to lowercase keys and boolean values."""
    if not modules_dict:
        return {"organization": True}
    
    normalized = {}
    for key, value in modules_dict.items():
        # Normalize key to lowercase
        normalized_key = key.lower() if isinstance(key, str) else str(key).lower()
        
        # Normalize value to boolean
        if isinstance(value, bool):
            normalized_value = value
        elif isinstance(value, str):
            normalized_value = value.lower() in ('true', '1', 'yes', 'enabled')
        elif isinstance(value, (int, float)):
            normalized_value = bool(value)
        else:
            normalized_value = False
        
        normalized[normalized_key] = normalized_value
    
    # Ensure organization module is always enabled
    normalized['organization'] = True
    
    return normalized


def upgrade():
    """Normalize enabled_modules for all organizations."""
    connection = op.get_bind()
    
    # Check if enabled_modules column exists and get its type
    inspector = sa.inspect(connection)
    columns = {col['name']: col for col in inspector.get_columns('organizations')}
    
    if 'enabled_modules' not in columns:
        print("enabled_modules column not found, skipping normalization")
        return
    
    col_type = str(columns['enabled_modules']['type']).upper()
    is_jsonb = 'JSONB' in col_type
    
    print(f"enabled_modules column type: {col_type}, is_jsonb: {is_jsonb}")
    
    # Fetch all organizations with their current enabled_modules
    result = connection.execute(text(
        "SELECT id, enabled_modules FROM organizations WHERE enabled_modules IS NOT NULL"
    ))
    
    orgs_to_update = []
    for row in result:
        org_id = row[0]
        current_modules = row[1]
        
        # Parse JSON if it's stored as text
        if isinstance(current_modules, str):
            try:
                current_modules = json.loads(current_modules)
            except (json.JSONDecodeError, TypeError):
                print(f"Org {org_id}: Failed to parse enabled_modules, setting to default")
                current_modules = {}
        
        # Normalize the modules
        normalized = normalize_modules_dict(current_modules)
        
        # Only update if changed
        if current_modules != normalized:
            orgs_to_update.append((org_id, normalized))
            print(f"Org {org_id}: Will update enabled_modules from {current_modules} to {normalized}")
    
    # Update organizations with normalized enabled_modules
    if orgs_to_update:
        for org_id, normalized_modules in orgs_to_update:
            if is_jsonb:
                # For JSONB, can use direct JSONB operations
                connection.execute(text(
                    "UPDATE organizations SET enabled_modules = :modules::jsonb WHERE id = :org_id"
                ), {"modules": json.dumps(normalized_modules), "org_id": org_id})
            else:
                # For JSON, use standard JSON operations
                connection.execute(text(
                    "UPDATE organizations SET enabled_modules = :modules::json WHERE id = :org_id"
                ), {"modules": json.dumps(normalized_modules), "org_id": org_id})
        
        print(f"Updated enabled_modules for {len(orgs_to_update)} organizations")
    else:
        print("No organizations needed enabled_modules normalization")
    
    # Set enabled_modules to default for any org with NULL
    default_modules = {"organization": True}
    if is_jsonb:
        connection.execute(text(
            "UPDATE organizations SET enabled_modules = :modules::jsonb WHERE enabled_modules IS NULL"
        ), {"modules": json.dumps(default_modules)})
    else:
        connection.execute(text(
            "UPDATE organizations SET enabled_modules = :modules::json WHERE enabled_modules IS NULL"
        ), {"modules": json.dumps(default_modules)})
    
    updated_null = connection.execute(text(
        "SELECT COUNT(*) FROM organizations WHERE enabled_modules IS NULL"
    )).scalar()
    
    if updated_null == 0:
        print("All organizations now have enabled_modules set")


def downgrade():
    """No downgrade - normalization is idempotent and safe."""
    print("Downgrade not implemented - normalization is safe and idempotent")
    pass
