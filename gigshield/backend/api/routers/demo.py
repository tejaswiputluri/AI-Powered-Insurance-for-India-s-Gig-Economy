"""
Demo Router — /api/v1/demo endpoints (DEMO_MODE=true only).
Handles demo reset, event firing, and state inspection.
"""

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, and_, delete
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.database import get_db
from backend.api.middleware import get_demo_rider_id
from backend.config.settings import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/demo", tags=["demo"])


class DemoFireEventRequest(BaseModel):
    scenario: str = "rain_aqi"


class DemoFireEventResponse(BaseModel):
    trigger_event_id: str
    scenario_description: str


@router.post("/reset")
async def demo_reset(db: AsyncSession = Depends(get_db)):
    """Delete all demo rider's claims, reset to clean state."""
    if not settings.DEMO_MODE:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND"})

    if not get_demo_rider_id():
        raise HTTPException(status_code=503, detail={"code": "DEMO_NOT_READY"})

    from backend.models.db.claim import Claim
    from backend.models.db.payout import Payout
    from backend.models.db.fraud_check import FraudCheck
    from backend.models.db.trigger_event import TriggerEvent

    # Delete demo rider's payouts
    await db.execute(
        delete(Payout).where(Payout.rider_id == get_demo_rider_id())
    )

    # Delete fraud checks for demo rider's claims
    claims_result = await db.execute(
        select(Claim.id).where(Claim.rider_id == get_demo_rider_id())
    )
    claim_ids = [row[0] for row in claims_result.all()]

    if claim_ids:
        await db.execute(
            delete(FraudCheck).where(FraudCheck.claim_id.in_(claim_ids))
        )

    # Delete claims
    await db.execute(
        delete(Claim).where(Claim.rider_id == get_demo_rider_id())
    )

    # Delete demo trigger events
    await db.execute(
        delete(TriggerEvent).where(TriggerEvent.is_demo_event.is_(True))
    )

    await db.commit()

    logger.info("Demo state reset complete")
    return {"data": {"reset": True}, "error": None}


@router.post("/fire-event", response_model=DemoFireEventResponse)
async def demo_fire_event(
    request: DemoFireEventRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Fire a demo disruption event.
    Scenarios: rain_aqi | aqi_order | full_3_signal | fraud_attempt
    """
    if not settings.DEMO_MODE:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND"})

    # Map scenario names to event types
    scenario_map = {
        "rain_aqi": "rain_order_drop",
        "rain_order_drop": "rain_order_drop",
        "aqi_order": "aqi_order",
        "full_3_signal": "full_3_signal",
        "fraud_attempt": "fraud_attempt",
    }

    event_type = scenario_map.get(request.scenario)
    if not event_type:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_SCENARIO",
                "message": f"Valid: {list(scenario_map.keys())}",
            },
        )

    descriptions = {
        "rain_order_drop": "Heavy Rain (14.2mm/hr) + Order Drop (41%) in BTM Layout",
        "aqi_order": "High AQI (218) + Order Drop (38%) in BTM Layout",
        "full_3_signal": "Full 3-signal: Rain (18.5mm/hr) + AQI (240) + Order Drop (52%)",
        "fraud_attempt": "Fraud attempt: Rain event but GPS shows rider 8.2km away",
    }

    # Delegate to triggers router logic
    from backend.api.routers.triggers import fire_demo_event, DemoFireRequest
    result = await fire_demo_event(
        DemoFireRequest(zone_id="BTM_LAYOUT", event_type=event_type),
        db=db,
    )

    return DemoFireEventResponse(
        trigger_event_id=result.trigger_event_id,
        scenario_description=descriptions.get(event_type, "Demo event fired"),
    )


@router.get("/state")
async def demo_state(db: AsyncSession = Depends(get_db)):
    """Full current state of demo rider."""
    if not settings.DEMO_MODE:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND"})

    if not get_demo_rider_id():
        return {"data": {"status": "not_seeded"}, "error": None}

    from backend.models.db.rider import Rider
    from backend.models.db.policy import Policy
    from backend.models.db.claim import Claim
    from backend.models.db.trigger_event import TriggerEvent
    from datetime import date, timedelta

    # Get rider
    result = await db.execute(select(Rider).where(Rider.id == get_demo_rider_id()))
    rider = result.scalar_one_or_none()

    # Get current policy
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    policy_result = await db.execute(
        select(Policy).where(
            and_(
                Policy.rider_id == get_demo_rider_id(),
                Policy.week_start_date == monday,
                Policy.status == "active",
            )
        )
    )
    policy = policy_result.scalar_one_or_none()

    # Get claims
    claims_result = await db.execute(
        select(Claim)
        .where(Claim.rider_id == get_demo_rider_id())
        .order_by(Claim.created_at.desc())
        .limit(5)
    )
    claims = claims_result.scalars().all()

    # Get last event
    event_result = await db.execute(
        select(TriggerEvent)
        .where(TriggerEvent.is_demo_event.is_(True))
        .order_by(TriggerEvent.detected_at.desc())
        .limit(1)
    )
    last_event = event_result.scalar_one_or_none()

    return {
        "data": {
            "rider": {
                "id": str(rider.id) if rider else None,
                "name": rider.name if rider else None,
                "zone_id": rider.zone_id if rider else None,
                "premium_paise": rider.computed_weekly_premium_paise if rider else None,
            },
            "policy": {
                "id": str(policy.id) if policy else None,
                "tier": policy.tier if policy else None,
                "status": policy.status if policy else None,
            } if policy else None,
            "claims": [
                {
                    "id": str(c.id),
                    "status": c.status,
                    "payout_paise": c.capped_payout_paise,
                    "confidence_score": c.confidence_score,
                }
                for c in claims
            ],
            "last_event": {
                "id": str(last_event.id),
                "zone_id": last_event.zone_id,
                "msc_status": last_event.msc_status,
                "detected_at": last_event.detected_at.isoformat(),
            } if last_event else None,
        },
        "error": None,
    }
