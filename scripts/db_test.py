import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import text

DATABASE_URL = "postgresql+asyncpg://postgres.yxyngwtcegujusekzmqd:Smstus515253@aws-1-ap-south-1.pooler.supabase.com:5432/postgres"  # Copy from .env, e.g., postgresql+asyncpg://postgres:password@db.supabase.co:5432/postgres

async def test_db():
    engine = create_async_engine(DATABASE_URL)
    session = async_sessionmaker(engine)()
    try:
        await session.execute(text("SELECT 1"))
        print("DB connection successful")
    except Exception as e:
        print(f"DB failure: {str(e)}")
    finally:
        await session.close()

asyncio.run(test_db())