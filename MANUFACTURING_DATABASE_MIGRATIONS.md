# Manufacturing Module - Database Migration Guide

## Overview

This document describes the database schema changes required for the comprehensive manufacturing module implementation.

---

## Required Migrations

### 1. Enhance ManufacturingOrder Table

Add new columns for resource allocation and capacity management:

```sql
-- Add resource allocation fields
ALTER TABLE manufacturing_orders 
ADD COLUMN assigned_operator VARCHAR(255),
ADD COLUMN assigned_supervisor VARCHAR(255),
ADD COLUMN machine_id VARCHAR(100),
ADD COLUMN workstation_id VARCHAR(100),
ADD COLUMN estimated_labor_hours FLOAT DEFAULT 0.0,
ADD COLUMN actual_labor_hours FLOAT DEFAULT 0.0;

-- Add capacity management fields
ALTER TABLE manufacturing_orders
ADD COLUMN estimated_setup_time FLOAT DEFAULT 0.0,
ADD COLUMN estimated_run_time FLOAT DEFAULT 0.0,
ADD COLUMN actual_setup_time FLOAT DEFAULT 0.0,
ADD COLUMN actual_run_time FLOAT DEFAULT 0.0,
ADD COLUMN completion_percentage FLOAT DEFAULT 0.0,
ADD COLUMN last_updated_at TIMESTAMP WITH TIME ZONE;

-- Add indexes for performance
CREATE INDEX idx_mo_operator ON manufacturing_orders(organization_id, assigned_operator);
CREATE INDEX idx_mo_machine ON manufacturing_orders(organization_id, machine_id);
CREATE INDEX idx_mo_workstation ON manufacturing_orders(organization_id, workstation_id);
CREATE INDEX idx_mo_completion ON manufacturing_orders(organization_id, completion_percentage);
```

### 2. Create BOMAlternateComponent Table

New table for managing alternate/substitute components:

```sql
CREATE TABLE bom_alternate_components (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organizations(id),
    primary_component_id INTEGER NOT NULL REFERENCES bom_components(id) ON DELETE CASCADE,
    alternate_item_id INTEGER NOT NULL REFERENCES products(id),
    quantity_required FLOAT NOT NULL,
    unit VARCHAR(50) NOT NULL,
    unit_cost FLOAT DEFAULT 0.0,
    cost_difference FLOAT DEFAULT 0.0,
    preference_rank INTEGER DEFAULT 1,
    is_preferred BOOLEAN DEFAULT FALSE,
    min_order_quantity FLOAT DEFAULT 0.0,
    lead_time_days INTEGER DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Indexes
CREATE INDEX idx_bom_alt_org_primary ON bom_alternate_components(organization_id, primary_component_id);
CREATE INDEX idx_bom_alt_org_item ON bom_alternate_components(organization_id, alternate_item_id);
CREATE INDEX idx_bom_alt_preference ON bom_alternate_components(primary_component_id, preference_rank);
```

### 3. Create BOMRevision Table

New table for tracking BOM changes and engineering revisions:

```sql
CREATE TABLE bom_revisions (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organizations(id),
    bom_id INTEGER NOT NULL REFERENCES bill_of_materials(id) ON DELETE CASCADE,
    revision_number VARCHAR(50) NOT NULL,
    revision_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    previous_version VARCHAR(50),
    new_version VARCHAR(50) NOT NULL,
    change_type VARCHAR(50) NOT NULL,
    change_description TEXT NOT NULL,
    change_reason TEXT,
    change_requested_by INTEGER REFERENCES users(id),
    change_approved_by INTEGER REFERENCES users(id),
    approval_date TIMESTAMP WITH TIME ZONE,
    approval_status VARCHAR(20) DEFAULT 'pending',
    cost_impact FLOAT DEFAULT 0.0,
    affected_orders_count INTEGER DEFAULT 0,
    implementation_date TIMESTAMP WITH TIME ZONE,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_bom_rev_org_bom ON bom_revisions(organization_id, bom_id);
CREATE INDEX idx_bom_rev_org_date ON bom_revisions(organization_id, revision_date);
CREATE INDEX idx_bom_rev_status ON bom_revisions(approval_status);
CREATE INDEX idx_bom_rev_version ON bom_revisions(bom_id, new_version);
```

### 4. Enhance InventoryAlert Table

Add new alert type for MRP shortages:

```sql
-- Add new alert type to enum (if using enum)
-- Note: PostgreSQL enum modification requires special handling
ALTER TYPE alert_type ADD VALUE IF NOT EXISTS 'shortage_for_mo';

-- Alternative: If using VARCHAR constraint, update the constraint
-- ALTER TABLE inventory_alerts DROP CONSTRAINT IF EXISTS inventory_alerts_alert_type_check;
-- ALTER TABLE inventory_alerts ADD CONSTRAINT inventory_alerts_alert_type_check 
--   CHECK (alert_type IN ('low_stock', 'out_of_stock', 'reorder', 'shortage_for_mo'));
```

### 5. Add Inventory Transaction Reference Types

Extend transaction types for manufacturing operations:

```sql
-- If using enum for transaction_type
ALTER TYPE transaction_type ADD VALUE IF NOT EXISTS 'manufacturing_order';

-- Alternative: Update constraint if using VARCHAR
-- ALTER TABLE inventory_transactions DROP CONSTRAINT IF EXISTS inventory_transactions_reference_type_check;
-- ALTER TABLE inventory_transactions ADD CONSTRAINT inventory_transactions_reference_type_check 
--   CHECK (reference_type IN ('job', 'purchase', 'manual', 'transfer', 'manufacturing_order'));
```

---

## Alembic Migration Script

For Alembic-based migrations, use this template:

```python
"""Add manufacturing module enhancements

Revision ID: manufacturing_module_v1
Revises: <previous_revision>
Create Date: 2025-10-11 17:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'manufacturing_module_v1'
down_revision = '<previous_revision>'
branch_labels = None
depends_on = None


def upgrade():
    # 1. Enhance manufacturing_orders table
    op.add_column('manufacturing_orders', sa.Column('assigned_operator', sa.String(255), nullable=True))
    op.add_column('manufacturing_orders', sa.Column('assigned_supervisor', sa.String(255), nullable=True))
    op.add_column('manufacturing_orders', sa.Column('machine_id', sa.String(100), nullable=True))
    op.add_column('manufacturing_orders', sa.Column('workstation_id', sa.String(100), nullable=True))
    op.add_column('manufacturing_orders', sa.Column('estimated_labor_hours', sa.Float(), server_default='0.0'))
    op.add_column('manufacturing_orders', sa.Column('actual_labor_hours', sa.Float(), server_default='0.0'))
    op.add_column('manufacturing_orders', sa.Column('estimated_setup_time', sa.Float(), server_default='0.0'))
    op.add_column('manufacturing_orders', sa.Column('estimated_run_time', sa.Float(), server_default='0.0'))
    op.add_column('manufacturing_orders', sa.Column('actual_setup_time', sa.Float(), server_default='0.0'))
    op.add_column('manufacturing_orders', sa.Column('actual_run_time', sa.Float(), server_default='0.0'))
    op.add_column('manufacturing_orders', sa.Column('completion_percentage', sa.Float(), server_default='0.0'))
    op.add_column('manufacturing_orders', sa.Column('last_updated_at', sa.DateTime(timezone=True), nullable=True))
    
    # Indexes for manufacturing_orders
    op.create_index('idx_mo_operator', 'manufacturing_orders', ['organization_id', 'assigned_operator'])
    op.create_index('idx_mo_machine', 'manufacturing_orders', ['organization_id', 'machine_id'])
    op.create_index('idx_mo_workstation', 'manufacturing_orders', ['organization_id', 'workstation_id'])
    op.create_index('idx_mo_completion', 'manufacturing_orders', ['organization_id', 'completion_percentage'])
    
    # 2. Create bom_alternate_components table
    op.create_table(
        'bom_alternate_components',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('primary_component_id', sa.Integer(), nullable=False),
        sa.Column('alternate_item_id', sa.Integer(), nullable=False),
        sa.Column('quantity_required', sa.Float(), nullable=False),
        sa.Column('unit', sa.String(50), nullable=False),
        sa.Column('unit_cost', sa.Float(), server_default='0.0'),
        sa.Column('cost_difference', sa.Float(), server_default='0.0'),
        sa.Column('preference_rank', sa.Integer(), server_default='1'),
        sa.Column('is_preferred', sa.Boolean(), server_default='false'),
        sa.Column('min_order_quantity', sa.Float(), server_default='0.0'),
        sa.Column('lead_time_days', sa.Integer(), server_default='0'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id']),
        sa.ForeignKeyConstraint(['primary_component_id'], ['bom_components.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['alternate_item_id'], ['products.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_bom_alt_org_primary', 'bom_alternate_components', ['organization_id', 'primary_component_id'])
    op.create_index('idx_bom_alt_org_item', 'bom_alternate_components', ['organization_id', 'alternate_item_id'])
    op.create_index('idx_bom_alt_preference', 'bom_alternate_components', ['primary_component_id', 'preference_rank'])
    
    # 3. Create bom_revisions table
    op.create_table(
        'bom_revisions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('bom_id', sa.Integer(), nullable=False),
        sa.Column('revision_number', sa.String(50), nullable=False),
        sa.Column('revision_date', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('previous_version', sa.String(50), nullable=True),
        sa.Column('new_version', sa.String(50), nullable=False),
        sa.Column('change_type', sa.String(50), nullable=False),
        sa.Column('change_description', sa.Text(), nullable=False),
        sa.Column('change_reason', sa.Text(), nullable=True),
        sa.Column('change_requested_by', sa.Integer(), nullable=True),
        sa.Column('change_approved_by', sa.Integer(), nullable=True),
        sa.Column('approval_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('approval_status', sa.String(20), server_default='pending'),
        sa.Column('cost_impact', sa.Float(), server_default='0.0'),
        sa.Column('affected_orders_count', sa.Integer(), server_default='0'),
        sa.Column('implementation_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id']),
        sa.ForeignKeyConstraint(['bom_id'], ['bill_of_materials.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['change_requested_by'], ['users.id']),
        sa.ForeignKeyConstraint(['change_approved_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_bom_rev_org_bom', 'bom_revisions', ['organization_id', 'bom_id'])
    op.create_index('idx_bom_rev_org_date', 'bom_revisions', ['organization_id', 'revision_date'])
    op.create_index('idx_bom_rev_status', 'bom_revisions', ['approval_status'])
    op.create_index('idx_bom_rev_version', 'bom_revisions', ['bom_id', 'new_version'])


def downgrade():
    # Drop bom_revisions table
    op.drop_index('idx_bom_rev_version', table_name='bom_revisions')
    op.drop_index('idx_bom_rev_status', table_name='bom_revisions')
    op.drop_index('idx_bom_rev_org_date', table_name='bom_revisions')
    op.drop_index('idx_bom_rev_org_bom', table_name='bom_revisions')
    op.drop_table('bom_revisions')
    
    # Drop bom_alternate_components table
    op.drop_index('idx_bom_alt_preference', table_name='bom_alternate_components')
    op.drop_index('idx_bom_alt_org_item', table_name='bom_alternate_components')
    op.drop_index('idx_bom_alt_org_primary', table_name='bom_alternate_components')
    op.drop_table('bom_alternate_components')
    
    # Remove manufacturing_orders enhancements
    op.drop_index('idx_mo_completion', table_name='manufacturing_orders')
    op.drop_index('idx_mo_workstation', table_name='manufacturing_orders')
    op.drop_index('idx_mo_machine', table_name='manufacturing_orders')
    op.drop_index('idx_mo_operator', table_name='manufacturing_orders')
    
    op.drop_column('manufacturing_orders', 'last_updated_at')
    op.drop_column('manufacturing_orders', 'completion_percentage')
    op.drop_column('manufacturing_orders', 'actual_run_time')
    op.drop_column('manufacturing_orders', 'actual_setup_time')
    op.drop_column('manufacturing_orders', 'estimated_run_time')
    op.drop_column('manufacturing_orders', 'estimated_setup_time')
    op.drop_column('manufacturing_orders', 'actual_labor_hours')
    op.drop_column('manufacturing_orders', 'estimated_labor_hours')
    op.drop_column('manufacturing_orders', 'workstation_id')
    op.drop_column('manufacturing_orders', 'machine_id')
    op.drop_column('manufacturing_orders', 'assigned_supervisor')
    op.drop_column('manufacturing_orders', 'assigned_operator')
```

---

## Running Migrations

### Using Alembic

1. **Create migration file:**
   ```bash
   cd /path/to/FastApiv1.6
   alembic revision -m "Add manufacturing module enhancements"
   ```

2. **Edit the migration file** with the content above

3. **Run migration:**
   ```bash
   alembic upgrade head
   ```

4. **Verify migration:**
   ```bash
   alembic current
   ```

5. **Rollback if needed:**
   ```bash
   alembic downgrade -1
   ```

### Manual SQL Execution

If not using Alembic:

1. Connect to your database
2. Execute the SQL statements in order
3. Verify tables and columns were created successfully

```bash
psql -U your_user -d your_database -f manufacturing_migrations.sql
```

---

## Verification Queries

After running migrations, verify the changes:

```sql
-- Check manufacturing_orders new columns
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'manufacturing_orders'
AND column_name IN (
    'assigned_operator', 'assigned_supervisor', 'machine_id', 
    'workstation_id', 'completion_percentage'
);

-- Check bom_alternate_components table exists
SELECT table_name FROM information_schema.tables
WHERE table_name = 'bom_alternate_components';

-- Check bom_revisions table exists
SELECT table_name FROM information_schema.tables
WHERE table_name = 'bom_revisions';

-- Check indexes
SELECT indexname, tablename
FROM pg_indexes
WHERE tablename IN ('manufacturing_orders', 'bom_alternate_components', 'bom_revisions')
ORDER BY tablename, indexname;
```

---

## Data Integrity

### Default Values

The migration sets appropriate default values for new columns:
- Numeric fields: `0.0`
- Percentage fields: `0.0`
- Boolean fields: `false`
- Status fields: `'pending'`

### Foreign Key Constraints

All foreign keys are properly constrained with:
- CASCADE DELETE for dependent records
- RESTRICT for referenced records
- Proper indexing for performance

### Indexes

All indexes are created for optimal query performance:
- Organization-scoped queries
- Resource-based lookups
- Status-based filtering
- Date-range queries

---

## Backward Compatibility

The migration is designed to be backward compatible:
- All new columns are nullable or have defaults
- Existing functionality is not affected
- New features are opt-in
- Rollback is supported

---

## Post-Migration Steps

After running the migration:

1. **Verify data integrity:**
   ```sql
   SELECT COUNT(*) FROM manufacturing_orders;
   SELECT COUNT(*) FROM bom_alternate_components;
   SELECT COUNT(*) FROM bom_revisions;
   ```

2. **Update application code** to use new models

3. **Test new endpoints:**
   - MRP analysis
   - Resource allocation
   - BOM cloning
   - Progress tracking

4. **Monitor performance** of new indexes

5. **Update documentation** for users

---

## Troubleshooting

### Common Issues

1. **Enum type conflicts:**
   - If using PostgreSQL enums, may need to handle type modifications carefully
   - Consider using VARCHAR with CHECK constraints instead

2. **Foreign key violations:**
   - Ensure referenced tables exist before creating foreign keys
   - Check for orphaned records

3. **Index creation timeouts:**
   - For large tables, consider creating indexes concurrently:
     ```sql
     CREATE INDEX CONCURRENTLY idx_name ON table_name(column);
     ```

4. **Permission issues:**
   - Ensure database user has CREATE TABLE and ALTER TABLE permissions

---

## Performance Considerations

### Index Strategy

The migration creates indexes for:
- Frequently filtered columns (organization_id, status)
- Join columns (foreign keys)
- Sorting columns (dates, priority)
- Resource lookups (operator, machine, workstation)

### Table Size Estimates

Expected growth rates:
- `manufacturing_orders`: ~1000 rows/month
- `bom_alternate_components`: ~100 rows/month
- `bom_revisions`: ~50 rows/month

### Monitoring

Monitor these metrics post-migration:
- Query execution times for MRP analysis
- Index usage statistics
- Table sizes and growth rates
- Lock contention during high-load periods

---

## Backup Recommendations

Before running migration:

1. **Full database backup:**
   ```bash
   pg_dump -U your_user your_database > backup_$(date +%Y%m%d_%H%M%S).sql
   ```

2. **Verify backup:**
   ```bash
   # Test restore to a temp database
   createdb temp_restore_test
   psql -U your_user temp_restore_test < backup_*.sql
   ```

3. **Document rollback plan**

---

## Support

For migration issues:
1. Check Alembic logs: `alembic.log`
2. Verify database permissions
3. Review error messages carefully
4. Test on development environment first
5. Consult database administrator if needed

---

## Conclusion

This migration adds essential tables and columns for the comprehensive manufacturing module while maintaining backward compatibility and data integrity. Follow the steps carefully and test thoroughly in a non-production environment before applying to production.
