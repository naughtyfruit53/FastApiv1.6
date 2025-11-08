# scripts/drop_database.py
"""
Drop and recreate the entire database.
Run: python scripts/drop_database.py
Backup first! This is destructive.
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

load_dotenv()

# Get DB name from URL
database_url = os.getenv('DATABASE_URL')
if not database_url:
    print("ERROR: DATABASE_URL not found in .env - add it and re-run.")
    exit(1)

# Parse DB name (last part of URL)
db_name = database_url.split('/')[-1]
host_user_pass = database_url.rsplit('/', 1)[0]

# Connect to 'template1' system DB to drop/recreate target DB
system_db_url = host_user_pass + '/template1'

sync_system_url = system_db_url.replace('asyncpg', 'psycopg') if 'asyncpg' in system_db_url else system_db_url

engine = create_engine(sync_system_url)
with engine.connect() as connection:
    connection.execution_options(isolation_level="AUTOCOMMIT")
    
    # Drop DB
    print(f"Dropping database: {db_name}")
    try:
        connection.execute(text(f"DROP DATABASE IF EXISTS {db_name};"))
        print("Database dropped.")
    except OperationalError as e:
        print(f"Error dropping DB: {str(e)}")
        print("Suggestions:")
        print("1. Close all connections in Supabase dashboard (Sessions tab).")
        print("2. Kill sessions with: SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '{db_name}';")
        print("3. Re-run script.")
        exit(1)
    
    # Recreate DB
    print(f"Recreating database: {db_name}")
    connection.execute(text(f"CREATE DATABASE {db_name};"))
    print("Database recreated successfully.")