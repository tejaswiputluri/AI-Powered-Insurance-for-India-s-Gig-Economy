#!/usr/bin/env python3
import asyncio
import sys
sys.path.insert(0, '.')
from backend.db.database import engine
import sqlalchemy as sa

async def check_db():
    print("\n=== DATABASE CHECK ===")
    try:
        async with engine.begin() as conn:
            tables = ['riders', 'policies', 'claims', 'fraud_checks', 'payouts']
            for table in tables:
                try:
                    result = await conn.execute(sa.text(f'SELECT COUNT(*) FROM {table}'))
                    count = result.scalar()
                    print(f"✅ {table}: {count} records")
                except Exception as e:
                    print(f"❌ {table}: {str(e)[:60]}")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")

async def check_imports():
    print("\n=== IMPORT CHECK ===")
    try:
        from backend.main import app
        print("✅ Backend app imports OK")
    except Exception as e:
        print(f"❌ Backend app import: {e}")
    
    try:
        from backend.db.database import init_db, close_db
        print("✅ Database utils import OK")
    except Exception as e:
        print(f"❌ Database utils import: {e}")
    
    try:
        from backend.services.premium_service import calculate_premium
        print("✅ Premium service import OK")
    except Exception as e:
        print(f"❌ Premium service import: {e}")

async def main():
    print("🔍 GIGSHIELD SYSTEM CHECK")
    await check_imports()
    await check_db()
    print("\n✅ Check complete!\n")

if __name__ == "__main__":
    asyncio.run(main())
