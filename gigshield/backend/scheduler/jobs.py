"""
APScheduler Job Definitions — background scheduled tasks.
MSC check every 30 min, premium deduction Monday 06:00 IST, forecast weekly.
"""

import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from backend.config.settings import settings

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


def setup_scheduler():
    """Configure and start the APScheduler background jobs."""

    # Job 1: MSC check every 30 minutes
    scheduler.add_job(
        run_msc_job,
        "interval",
        minutes=settings.MSC_POLL_INTERVAL_MINUTES,
        id="msc_check",
        name="MSC Signal Check",
        replace_existing=True,
    )

    # Job 2: Premium deduction — Monday 06:00 IST (00:30 UTC)
    scheduler.add_job(
        run_premium_deduction,
        "cron",
        day_of_week="mon",
        hour=0,
        minute=30,
        id="premium_deduction",
        name="Weekly Premium Deduction",
        replace_existing=True,
    )

    # Job 3: Forecast update — Sunday 20:00 UTC
    scheduler.add_job(
        run_forecast_update,
        "cron",
        day_of_week="sun",
        hour=20,
        minute=0,
        id="forecast_update",
        name="Weekly Forecast Update",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("⏰ APScheduler started with 3 jobs")


async def run_msc_job():
    """Execute MSC check across all zones."""
    from backend.db.database import async_session_factory
    from backend.services.trigger_engine import run_msc_check

    logger.info("🔍 Running scheduled MSC check...")
    async with async_session_factory() as session:
        try:
            await run_msc_check(session)
        except Exception as e:
            logger.error(f"MSC check failed: {e}")


async def run_premium_deduction():
    """Deduct weekly premiums for all active policies."""
    from backend.db.database import async_session_factory
    from backend.models.db.policy import Policy
    from sqlalchemy import select, and_
    from datetime import date, timedelta, datetime, timezone

    logger.info("💰 Running weekly premium deduction...")
    async with async_session_factory() as session:
        today = date.today()
        monday = today - timedelta(days=today.weekday())

        result = await session.execute(
            select(Policy).where(
                and_(
                    Policy.week_start_date == monday,
                    Policy.status == "active",
                    Policy.premium_deduction_status == "pending",
                )
            )
        )
        policies = result.scalars().all()

        for policy in policies:
            # In demo mode / Phase 1: mark as success
            policy.premium_deduction_status = "success"
            policy.premium_deducted_at = datetime.now(timezone.utc)

        await session.commit()
        logger.info(f"✅ Deducted premiums for {len(policies)} policies")


async def run_forecast_update():
    """Update zone forecasts using LSTM service."""
    from backend.db.database import async_session_factory
    from backend.services.forecast_service import get_zone_forecast
    from backend.services.trigger_engine import load_zones
    from backend.models.db.zone_forecast import ZoneForecast
    from datetime import date, timedelta
    from sqlalchemy import select

    logger.info("📊 Running weekly forecast update...")
    async with async_session_factory() as session:
        zones = load_zones()
        today = date.today()
        next_monday = today + timedelta(days=(7 - today.weekday()))

        for zone in zones:
            # Check if forecast already exists
            existing = await session.execute(
                select(ZoneForecast).where(
                    ZoneForecast.zone_id == zone["id"],
                    ZoneForecast.forecast_week_start == next_monday,
                )
            )
            if existing.scalar_one_or_none():
                continue  # Skip — already have forecast for this zone+week

            forecast = await get_zone_forecast(zone["id"])
            forecasts = forecast.get("forecasts", [])

            if forecasts:
                avg_prob = sum(f["disruption_probability"] for f in forecasts) / len(forecasts)
            else:
                avg_prob = 0.4

            zone_forecast = ZoneForecast(
                zone_id=zone["id"],
                forecast_week_start=next_monday,
                disruption_probability=avg_prob,
                expected_claim_count=int(avg_prob * 15),
                reserve_estimate_paise=int(avg_prob * 15 * 35000),
            )
            session.add(zone_forecast)

        await session.commit()
        logger.info(f"✅ Updated forecasts for {len(zones)} zones")
