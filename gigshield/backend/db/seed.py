"""
Database Seed — populates demo rider, zones, and initial data.
Run on app startup in DEMO_MODE.
"""

import json
import logging
import uuid
from datetime import date, timedelta, datetime, timezone
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config.settings import settings
from backend.api.middleware import set_demo_rider_id, DEMO_RIDER_UID

logger = logging.getLogger(__name__)

# Fixed demo rider UUID for consistency
DEMO_RIDER_UUID = uuid.UUID("11111111-1111-1111-1111-111111111111")


async def seed_demo_data(db: AsyncSession):
    """Seed demo rider and initial data. Idempotent — safe to run multiple times."""
    from backend.models.db.rider import Rider
    from backend.models.db.policy import Policy
    from backend.models.db.zone_forecast import ZoneForecast

    logger.info("🌱 Seeding demo data...")

    # 1. Create or get demo rider
    result = await db.execute(
        select(Rider).where(Rider.firebase_uid == DEMO_RIDER_UID)
    )
    rider = result.scalar_one_or_none()

    if not rider:
        rider = Rider(
            id=DEMO_RIDER_UUID,
            phone=settings.DEMO_RIDER_PHONE,
            name=settings.DEMO_RIDER_NAME,
            firebase_uid=DEMO_RIDER_UID,
            zone_id=settings.DEMO_RIDER_ZONE,
            platform=settings.DEMO_RIDER_PLATFORM,
            work_hours_start=settings.DEMO_RIDER_WORK_START,
            work_hours_end=settings.DEMO_RIDER_WORK_END,
            work_days_per_week=settings.DEMO_RIDER_WORK_DAYS,
            self_reported_daily_earning_paise=settings.DEMO_RIDER_DAILY_EARNING_PAISE,
            prf_zone_risk_score=0.87,
            prf_aqi_exposure_score=0.42,
            prf_season_multiplier=1.00,
            computed_weekly_premium_paise=6700,  # ₹67
            xai_factors={
                "aqi_zone_history": 0.34,
                "monsoon_season": 0.27,
                "zone_risk_score": 0.21,
                "claim_history": 0.18,
            },
            upi_vpa="ravi@upi",
        )
        db.add(rider)
        await db.flush()
        logger.info(f"✅ Created demo rider: {rider.name} ({rider.id})")
    else:
        logger.info(f"✅ Demo rider already exists: {rider.name}")

    # Set demo rider ID for middleware auth bypass
    set_demo_rider_id(rider.id)

    # 2. Create active policy for current week
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)

    policy_result = await db.execute(
        select(Policy).where(
            Policy.rider_id == rider.id,
            Policy.week_start_date == monday,
        )
    )
    policy = policy_result.scalar_one_or_none()

    if not policy:
        policy = Policy(
            rider_id=rider.id,
            tier="balanced",
            weekly_premium_paise=6700,
            coverage_cap_paise=90000,  # ₹900
            msc_threshold=2,
            coverage_factor=0.70,
            week_start_date=monday,
            week_end_date=sunday,
            status="active",
            premium_deduction_status="success",
            premium_deducted_at=datetime.now(timezone.utc),
        )
        db.add(policy)
        logger.info(f"✅ Created weekly policy: {monday} to {sunday}")

    # 3. Seed zone forecasts
    zones_path = Path(__file__).parent.parent.parent / "data" / "zones.json"
    with open(zones_path) as f:
        zones = json.load(f)["zones"]

    for zone in zones:
        forecast_result = await db.execute(
            select(ZoneForecast).where(
                ZoneForecast.zone_id == zone["id"],
                ZoneForecast.forecast_week_start == monday,
            )
        )
        if not forecast_result.scalar_one_or_none():
            # Seed forecast based on zone risk profile
            risk_map = {
                'BTM_LAYOUT': 0.73, 'KORAMANGALA': 0.55, 'INDIRANAGAR': 0.68,
                'WHITEFIELD': 0.42, 'JAYANAGAR': 0.50, 'MARATHAHALLI': 0.38,
                'HSR_LAYOUT': 0.65, 'ELECTRONIC_CITY': 0.30, 'HEBBAL': 0.48,
                'JP_NAGAR': 0.45,
            }
            prob = risk_map.get(zone["id"], 0.40)

            forecast = ZoneForecast(
                zone_id=zone["id"],
                forecast_week_start=monday,
                disruption_probability=prob,
                expected_claim_count=int(prob * 15),
                reserve_estimate_paise=int(prob * 15 * 35000),
            )
            db.add(forecast)

    await db.commit()
    logger.info("🌱 Demo data seeding complete!")
