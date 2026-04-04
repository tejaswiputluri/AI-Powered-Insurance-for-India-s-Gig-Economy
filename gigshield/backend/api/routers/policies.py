"""
Policies Router — /api/v1/policies endpoints.
Handles policy creation, retrieval, pause, and coverage simulation.
"""

import logging
from uuid import UUID
from datetime import date, timedelta, datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.database import get_db
from backend.api.middleware import get_current_rider_id
from backend.config.constants import POLICY_TIERS, MIN_PREMIUM_PAISE, MAX_PREMIUM_PAISE
from backend.models.schemas.policy import (
    PolicyCreateRequest,
    PolicyCreateResponse,
    PolicyResponse,
    SimulatorQuery,
    SimulatorResponse,
    SimulatorBreakdown,
)
from backend.services.payout_engine import calculate_payout, get_zone

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/policies", tags=["policies"])


def _get_current_week() -> tuple[date, date]:
    """Get Monday and Sunday of the current week."""
    today = date.today()
    monday = today - timedelta(days=today.weekday())  # Monday
    sunday = monday + timedelta(days=6)               # Sunday
    return monday, sunday


@router.post("/create", response_model=PolicyCreateResponse)
async def create_policy(
    request: PolicyCreateRequest,
    db: AsyncSession = Depends(get_db),
    rider_id: UUID = Depends(get_current_rider_id),
):
    """
    Create a new weekly policy for the rider.
    1. Check rider has no active policy for current week
    2. Get tier config
    3. Create policy for Monday–Sunday
    4. Log to audit_log
    """
    from backend.models.db.rider import Rider
    from backend.models.db.policy import Policy
    from backend.models.db.audit_log import AuditLog
    
    try:
        logger.info(f"🏗️  Creating policy - rider_id={rider_id}, tier={request.tier}")

        # Get rider
        logger.info(f"📋 Fetching rider {rider_id}")
        result = await db.execute(select(Rider).where(Rider.id == rider_id))
        rider = result.scalar_one_or_none()
        if not rider:
            logger.error(f"❌ Rider not found: {rider_id}")
            raise HTTPException(status_code=404, detail={"code": "RIDER_NOT_FOUND"})
        logger.info(f"✅ Rider found: {rider.id}, premium={rider.computed_weekly_premium_paise}")

        # Get current week
        week_start, week_end = _get_current_week()
        logger.info(f"📅 Week range: {week_start} - {week_end}")

        # Check for existing active policy this week - allow upgrades/downgrades
        logger.info(f"🔍 Checking for existing active policies")
        existing_result = await db.execute(
            select(Policy).where(
                and_(
                    Policy.rider_id == rider_id,
                    Policy.week_start_date == week_start,
                    Policy.status.in_(["active", "paused"]),
                )
            )
        )
        existing_policy = existing_result.scalar_one_or_none()
        if existing_policy:
            logger.info(f"📝 Existing policy found - allowing upgrade/downgrade to tier {request.tier}")
            # Cancel the existing policy instead of rejecting
            existing_policy.status = "cancelled"
            db.add(existing_policy)
            await db.flush()
            logger.info(f"✅ Existing policy cancelled: {existing_policy.id}")
        else:
            logger.info(f"✅ No existing policy found")

        # Get tier configuration
        logger.info(f"🎯 Looking up tier config for '{request.tier}'")
        tier_config = POLICY_TIERS.get(request.tier)
        if not tier_config:
            logger.error(f"❌ Invalid tier: {request.tier}. Available: {list(POLICY_TIERS.keys())}")
            raise HTTPException(
                status_code=400,
                detail={"code": "INVALID_TIER", "message": f"Unknown tier: {request.tier}"},
            )
        logger.info(f"✅ Tier config found: {tier_config}")

        # Calculate tier-specific premium
        base_premium = rider.computed_weekly_premium_paise or 5000
        tier_premium = max(
            MIN_PREMIUM_PAISE,
            min(MAX_PREMIUM_PAISE, int(base_premium * tier_config["premium_multiplier"]))
        )
        logger.info(f"💰 Calculated premium: base={base_premium}, tier_multiplier={tier_config['premium_multiplier']}, final={tier_premium}")

        # Create policy (RULE-07: money write in transaction)
        logger.info(f"💾 Creating policy object in DB")
        policy = Policy(
            rider_id=rider_id,
            tier=request.tier,
            weekly_premium_paise=tier_premium,
            coverage_cap_paise=tier_config["coverage_cap_paise"],
            msc_threshold=tier_config["msc_threshold"],
            coverage_factor=tier_config["coverage_factor"],
            week_start_date=week_start,
            week_end_date=week_end,
            status="active",
        )
        db.add(policy)
        logger.info(f"✅ Policy object created (flushing to get ID)")
        
        # Flush to get the policy ID before creating audit log
        await db.flush()
        logger.info(f"✅ Policy flushed: {policy.id}")

        # Audit log
        logger.info(f"📝 Creating audit log")
        audit = AuditLog(
            entity_type="policy",
            entity_id=policy.id,
            action="policy_created",
            detail={
                "tier": request.tier,
                "premium_paise": tier_premium,
                "coverage_cap_paise": tier_config["coverage_cap_paise"],
                "week_start": week_start.isoformat(),
            },
        )
        db.add(audit)
        logger.info(f"✅ Audit log created")

        logger.info(f"⏳ Committing transaction")
        await db.commit()
        logger.info(f"✅ Transaction committed")
        
        logger.info(f"🔄 Refreshing policy from DB")
        await db.refresh(policy)
        logger.info(f"✅ Policy refreshed")

        logger.info(f"✨ Policy created successfully: {policy.id}")
        return PolicyCreateResponse(
            policy_id=policy.id,
            week_start=policy.week_start_date,
            week_end=policy.week_end_date,
            premium_paise=policy.weekly_premium_paise,
            coverage_cap_paise=policy.coverage_cap_paise,
            tier=policy.tier,
            coverage_factor=policy.coverage_factor,
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"❌ Unexpected error in create_policy: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "code": "POLICY_CREATION_ERROR",
                "message": f"Failed to create policy: {str(e)}"
            }
        )


@router.get("/me/current")
async def get_current_policy(
    db: AsyncSession = Depends(get_db),
    rider_id: UUID = Depends(get_current_rider_id),
):
    """Get current active policy or null."""
    from backend.models.db.policy import Policy

    week_start, week_end = _get_current_week()

    result = await db.execute(
        select(Policy).where(
            and_(
                Policy.rider_id == rider_id,
                Policy.week_start_date == week_start,
                Policy.status == "active",
            )
        )
    )
    policy = result.scalar_one_or_none()

    if policy:
        return {
            "data": PolicyResponse.model_validate(policy).model_dump(),
            "error": None,
        }
    return {"data": None, "error": None}


@router.get("/me/history")
async def get_policy_history(
    db: AsyncSession = Depends(get_db),
    rider_id: UUID = Depends(get_current_rider_id),
):
    """Get past policies (last 12 weeks)."""
    from backend.models.db.policy import Policy

    cutoff = date.today() - timedelta(weeks=12)

    result = await db.execute(
        select(Policy).where(
            and_(
                Policy.rider_id == rider_id,
                Policy.week_start_date >= cutoff,
            )
        ).order_by(Policy.week_start_date.desc())
    )
    policies = result.scalars().all()

    return {
        "data": [PolicyResponse.model_validate(p).model_dump() for p in policies],
        "error": None,
    }


@router.post("/me/pause")
async def pause_policy(
    db: AsyncSession = Depends(get_db),
    rider_id: UUID = Depends(get_current_rider_id),
):
    """Pause active policy. Must be > 48hr before next Monday."""
    from backend.models.db.policy import Policy

    week_start, _ = _get_current_week()
    next_monday = week_start + timedelta(weeks=1)
    hours_to_monday = (
        datetime.combine(next_monday, datetime.min.time()).replace(tzinfo=timezone.utc)
        - datetime.now(timezone.utc)
    ).total_seconds() / 3600

    if hours_to_monday < 48:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "TOO_LATE_TO_PAUSE",
                "message": "Must pause at least 48 hours before next Monday",
            },
        )

    result = await db.execute(
        select(Policy).where(
            and_(
                Policy.rider_id == rider_id,
                Policy.week_start_date == week_start,
                Policy.status == "active",
            )
        )
    )
    policy = result.scalar_one_or_none()

    if not policy:
        raise HTTPException(status_code=404, detail={"code": "NO_ACTIVE_POLICY"})

    policy.status = "paused"
    await db.commit()

    return {"data": {"paused": True}, "error": None}


@router.get("/simulator", response_model=SimulatorResponse)
async def simulate_coverage(
    zone_id: str = Query(default="BTM_LAYOUT"),
    disruption_hours: float = Query(default=4.0, ge=1.0, le=8.0),
    signal_count: int = Query(default=2, ge=2, le=3),
    rider_id: UUID = Depends(get_current_rider_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Coverage simulator — preview payout for different scenarios.
    """
    from backend.models.db.rider import Rider

    result = await db.execute(select(Rider).where(Rider.id == rider_id))
    rider = result.scalar_one_or_none()

    if not rider:
        raise HTTPException(status_code=404, detail={"code": "RIDER_NOT_FOUND"})

    # Use Balanced tier as reference for simulation
    coverage_cap = POLICY_TIERS["balanced"]["coverage_cap_paise"]

    payout_data = await calculate_payout(
        rider_daily_earning_paise=rider.self_reported_daily_earning_paise,
        work_hours_start=rider.work_hours_start,
        work_hours_end=rider.work_hours_end,
        zone_id=zone_id,
        signals_confirmed=signal_count,
        coverage_cap_paise=coverage_cap,
        disruption_hours=disruption_hours,
    )

    return SimulatorResponse(
        estimated_payout_paise=payout_data["capped_payout_paise"],
        breakdown=SimulatorBreakdown(
            baseline_hourly_paise=payout_data["baseline_hourly_earning_paise"],
            disruption_hours=payout_data["disruption_hours"],
            zone_impact_factor=payout_data["zone_impact_factor"],
            coverage_factor=payout_data["coverage_factor"],
        ),
    )
