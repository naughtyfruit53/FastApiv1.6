# scripts/test_db_connection.py
"""
Test database connection independently.
Run: python scripts/test_db_connection.py
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import socket

load_dotenv()

database_url = os.getenv('DATABASE_URL')
if not database_url:
    print("ERROR: DATABASE_URL not found in .env - add it and re-run.")
    exit(1)

# Convert to sync URL
sync_database_url = database_url.replace('asyncpg', 'psycopg') if 'asyncpg' in database_url else database_url

# Ensure sslmode=require is appended for SSL enforcement
if 'sslmode' not in sync_database_url:
    separator = '?' if '?' not in sync_database_url else '&'
    sync_database_url += f"{separator}sslmode=require"

# Mask password for safe printing
def mask_url(url):
    if '@' in url:
        before_at, after_at = url.split('@', 1)
        if ':' in before_at:
            user, pw_host = before_at.split(':', 1)
            masked = f"{user}:[MASKED]@{after_at}"
            return masked
    return url

print(f"Testing connection to: {mask_url(sync_database_url)}")

try:
    # Test DNS resolution
    host = sync_database_url.split('@')[1].split('/')[0].split(':')[0]
    print(f"Resolving host: {host}")
    socket.getaddrinfo(host, None)
    print("DNS resolution successful.")
except socket.gaierror as e:
    print(f"DNS resolution failed: {str(e)}")
    print("Suggestions:")
    print("1. Check internet connection.")
    print("2. Ping the host: ping {host}")
    print("3. Use Google DNS: Set DNS to 8.8.8.8 in network settings.")
    print("4. Verify Supabase host in dashboard - might be incorrect.")
    exit(1)

try:
    engine = create_engine(sync_database_url, connect_args={
        "keepalives": 1,
        "keepalives_idle": 60,
        "keepalives_interval": 10,
        "keepalives_count": 5
    })
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print("Connection successful: ", result.scalar())
except Exception as e:
    print(f"Connection failed: {str(e)}")
    print("Suggestions:")
    print("1. Check .env credentials (user/password/host/port/dbname).")
    print("2. Ensure Supabase allows connections from your IP.")
    print("3. Test with psql: psql '{database_url}'")
    print("4. Disable VPN/firewall temporarily.")
    print("5. Verify SSL (sslmode=require in URL).")
    print("6. Check Supabase dashboard for any restrictions or outages.")