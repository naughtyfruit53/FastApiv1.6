"""add_rls_policies_and_enable

Revision ID: fcf7c7a70f0a
Revises: a475535ea199
Create Date: 2025-12-03 08:04:34.137594

"""
from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = 'fcf7c7a70f0a'
down_revision = 'a475535ea199'
branch_labels = None
depends_on = None

# Set to True to enable RLS on ALL public tables (fixes all lints)
enable_on_all_tables = True

def upgrade():
    connection = op.get_bind()
    
    if enable_on_all_tables:
        # Get ALL public base tables
        result = connection.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE' 
            AND table_name NOT LIKE 'pg_%'
            AND table_name NOT IN ('spatial_ref_sys', 'geography_columns', 'geometry_columns')
        """))
    else:
        # Get only tables with organization_id
        result = connection.execute(text("""
            SELECT table_name 
            FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND column_name = 'organization_id'
            AND table_name NOT LIKE 'pg_%'
            AND table_name NOT IN ('spatial_ref_sys', 'geography_columns', 'geometry_columns')
        """))
    
    tables = [row[0] for row in result]
    
    for table_name in tables:
        # Check if organization_id exists for this table
        has_org_id = connection.execute(text(f"""
            SELECT EXISTS (
                SELECT 1 
                FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = '{table_name}' 
                AND column_name = 'organization_id'
            )
        """)).scalar()
        
        if has_org_id:
            # Add tenant-specific policy
            op.execute(f"""
                CREATE POLICY tenant_isolation ON {table_name} 
                USING (organization_id = current_setting('app.current_organization_id')::integer);
            """)
        else:
            # Add permissive policy for non-tenant tables (allows all access; review for security)
            op.execute(f"""
                CREATE POLICY permissive_access ON {table_name} 
                USING (true);
            """)
        
        # Enable RLS
        op.execute(f"ALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY;")

def downgrade():
    connection = op.get_bind()
    
    if enable_on_all_tables:
        result = connection.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE' 
            AND table_name NOT LIKE 'pg_%'
            AND table_name NOT IN ('spatial_ref_sys', 'geography_columns', 'geometry_columns')
        """))
    else:
        result = connection.execute(text("""
            SELECT table_name 
            FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND column_name = 'organization_id'
            AND table_name NOT LIKE 'pg_%'
            AND table_name NOT IN ('spatial_ref_sys', 'geography_columns', 'geometry_columns')
        """))
    
    tables = [row[0] for row in result]
    
    for table_name in tables:
        # Drop policies
        op.execute(f"DROP POLICY IF EXISTS tenant_isolation ON {table_name};")
        op.execute(f"DROP POLICY IF EXISTS permissive_access ON {table_name};")
        # Disable RLS
        op.execute(f"ALTER TABLE {table_name} DISABLE ROW LEVEL SECURITY;")
        