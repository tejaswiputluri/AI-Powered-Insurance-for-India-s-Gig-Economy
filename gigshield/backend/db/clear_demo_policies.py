"""
Clear existing demo rider policies to allow creating fresh ones.
Run this to reset the demo environment for testing policy creation.
"""

import asyncio
import sys
from pathlib import Path

# Add gigshield directory to path
sys.path.insert(0, str(Path(__file__).parent))

async def clear_demo_policies():
    """Delete all policies for the demo rider."""
    from backend.db.database import async_session_factory
    from backend.models.db.policy import Policy
    from sqlalchemy import delete
    from uuid import UUID
    
    async with async_session_factory() as db:
        try:
            # Demo rider UUID
            DEMO_RIDER_UUID = UUID("11111111-1111-1111-1111-111111111111")
            
            print(f"🗑️  Clearing policies for demo rider {DEMO_RIDER_UUID}...")
            
            # Delete all policies for demo rider
            result = await db.execute(
                delete(Policy).where(Policy.rider_id == DEMO_RIDER_UUID)
            )
            
            await db.commit()
            
            print(f"✅ Deleted {result.rowcount} policies!")
            print("✨ You can now create a new policy from the frontend")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            await db.rollback()

if __name__ == "__main__":
    asyncio.run(clear_demo_policies())
