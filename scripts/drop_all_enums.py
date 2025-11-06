# scripts/drop_all_enums.py
"""
Drop all enum types in the public schema.
Run: python scripts/drop_all_enums.py
This will list and drop all enums to clean up for fresh migration.
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
    # Get all enum names
    enums_query = text("""
        SELECT typname 
        FROM pg_type 
        WHERE typtype = 'e' 
        AND typnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public');
    """)
    enums = connection.execute(enums_query).fetchall()
    enum_names = [row[0] for row in enums]
    print(f"Found {len(enum_names)} enums: {', '.join(enum_names)}")
    
    # Drop each enum
    for enum_name in enum_names:
        print(f"Dropping enum: {enum_name}")
        drop_query = text(f"DROP TYPE IF EXISTS {enum_name} CASCADE;")
        connection.execute(drop_query)
    
    connection.commit()
    print("All enums dropped successfully.")