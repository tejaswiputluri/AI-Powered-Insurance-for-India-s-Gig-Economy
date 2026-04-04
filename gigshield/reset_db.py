import asyncio
from backend.db.database import engine, Base
from backend.db.seed import seed_demo_data
from sqlalchemy.ext.asyncio import AsyncSession

async def reset_database():
    """Drop all tables and reseed with demo data"""
    
    # Drop all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        print("✅ Dropped all tables")
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("✅ Created all tables")
    
    # Seed demo data
    async with AsyncSession(engine) as db:
        await seed_demo_data(db)
        print("✅ Seeded fresh demo data")
    
    print("\n🎉 Database reset complete!")

if __name__ == "__main__":
    asyncio.run(reset_database())
