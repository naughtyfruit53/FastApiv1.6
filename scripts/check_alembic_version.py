# scripts/check_alembic_version.py
"""
Check if alembic_version table exists and its content.
Run: python scripts/check_alembic_version.py
If exists, drop it with the provided command.
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

database_url = os.getenv('DATABASE_URL')
if not database_url:
    print("ERROR: DATABASE_URL not found in .env - add it and re-run.")
    exit(1)

# Convert to sync URL by replacing asyncpg with psycopg
sync_database_url = database_url.replace('asyncpg', 'psycopg')

engine = create_engine(sync_database_url)
with engine.connect() as connection:
    # Check if table exists
    exists_query = text("""
        SELECT EXISTS (
            SELECT FROM pg_tables 
            WHERE schemaname = 'public' AND tablename = 'alembic_version'
        );
    """)
    exists = connection.execute(exists_query).scalar()
    print(f"alembic_version table exists: {exists}")
    
    if exists:
        # Get current version
        version_query = text("SELECT version_num FROM alembic_version;")
        version = connection.execute(version_query).scalar()
        print(f"Current Alembic version in DB: {version if version else 'None'}")
        
        # Drop the table
        print("\nDropping alembic_version table...")
        drop_query = text("DROP TABLE IF EXISTS alembic_version CASCADE;")
        connection.execute(drop_query)
        connection.commit()
        print("Dropped alembic_version table successfully.")
    else:
        print("No alembic_version table found - DB is fully reset.")