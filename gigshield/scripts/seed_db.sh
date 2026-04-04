#!/bin/bash
# seed_db.sh — Initialize database and seed demo data.
# Usage: ./scripts/seed_db.sh

set -e

echo "================================================================"
echo "  GigShield — Database Setup & Seeding"
echo "================================================================"

cd "$(dirname "$0")/.."

# Check .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "Copy .env.example to .env and configure your database URL."
    exit 1
fi

# Load env
export $(grep -v '^#' .env | xargs)

echo ""
echo "📦 [1/3] Creating database tables..."
python -c "
import asyncio
from backend.db.database import init_db
asyncio.run(init_db())
print('✅ Tables created')
"

echo ""
echo "🌱 [2/3] Seeding demo data..."
python -c "
import asyncio
from backend.db.database import async_session_factory
from backend.db.seed import seed_demo_data

async def seed():
    async with async_session_factory() as session:
        await seed_demo_data(session)

asyncio.run(seed())
print('✅ Demo data seeded')
"

echo ""
echo "✅ [3/3] Database ready!"
echo ""
echo "Demo rider: Ravi Kumar (BTM Layout, Swiggy)"
echo "Demo policy: Balanced tier, ₹67/week"
