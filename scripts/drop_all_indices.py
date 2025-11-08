# scripts/drop_all_indices.py
"""
Drop all indices and constraints in the public schema.
Run: python scripts/drop_all_indices.py
This will list and drop all indices and constraints to clean up for fresh migration.
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

database_url = os.getenv('DATABASE_URL')
if not database_url:
    print("ERROR: DATABASE_URL not found in .env - add it and re-run.")
    exit(1)

# Use sync URL
sync_database_url = database_url.replace('postgresql+asyncpg', 'postgresql+psycopg2') if 'asyncpg' in database_url else database_url

engine = create_engine(sync_database_url)
with engine.connect() as connection:
    # Get all constraint names (pkeys, uniques, fks)
    constraints_query = text("""
        SELECT conname 
        FROM pg_constraint 
        WHERE connamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public');
    """)
    constraints = connection.execute(constraints_query).fetchall()
    constraint_names = [row[0] for row in constraints]
    print(f"Found {len(constraint_names)} constraints: {', '.join(constraint_names)}")
    
    # Drop each constraint
    for constraint_name in constraint_names:
        print(f"Dropping constraint: {constraint_name}")
        drop_query = text(f"ALTER TABLE IF EXISTS alembic_version DROP CONSTRAINT IF EXISTS {constraint_name} CASCADE;")
        connection.execute(drop_query)
    
    # Get all index names (now safe to drop after constraints)
    indices_query = text("""
        SELECT indexname 
        FROM pg_indexes 
        WHERE schemaname = 'public';
    """)
    indices = connection.execute(indices_query).fetchall()
    index_names = [row[0] for row in indices]
    print(f"Found {len(index_names)} indices: {', '.join(index_names)}")
    
    # Drop each index
    for index_name in index_names:
        print(f"Dropping index: {index_name}")
        drop_query = text(f"DROP INDEX IF EXISTS {index_name} CASCADE;")
        connection.execute(drop_query)
    
    connection.commit()
    print("All constraints and indices dropped successfully.")