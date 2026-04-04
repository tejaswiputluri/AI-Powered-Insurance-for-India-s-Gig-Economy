"""
Triggers Router — /api/v1/triggers endpoints (admin/internal).
Handles trigger event viewing and demo event firing.
"""

import logging
from uuid import UUID
from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.database import get_db
from backend.api.middleware import get_insurer_auth
from backend.config.settings import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/triggers", tags=["triggers"])


class DemoFireRequest(BaseModel):
    zone_id: str = "BTM_LAYOUT"
    event_type: str = "rain_order_drop"


class DemoFireResponse(BaseModel):
    trigger_event_id: str
    claims_created: int


@router.get("/current")
async def get_current_triggers(
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(get_insurer_auth),
):
    """Get all active (non-ended) trigger events."""
    from backend.models.db.trigger_event import TriggerEvent

    result = await db.execute(
        select(TriggerEvent).where(TriggerEvent.ended_at.is_(None))
    )
    events = result.scalars().all()

    return {
        "data": [
            {
                "id": str(e.id),
                "zone_id": e.zone_id,
                "rainfall_mm_hr": e.rainfall_mm_hr,
                "aqi_value": e.aqi_value,
                "order_drop_pct": e.order_drop_pct,
                "signals_confirmed": e.signals_confirmed,
                "msc_status": e.msc_status,
                "detected_at": e.detected_at.isoformat(),
                "is_demo_event": e.is_demo_event,
            }
            for e in events
        ],
        "error": None,
    }


@router.post("/demo/fire", response_model=DemoFireResponse)
async def fire_demo_event(
    request: DemoFireRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Fire a pre-seeded demo event and run full pipeline.
    Only available when DEMO_MODE=true or with admin token.
    """
    if not settings.DEMO_MODE:
        raise HTTPException(status_code=403, detail={"code": "DEMO_MODE_REQUIRED"})

    from backend.models.db.trigger_event import TriggerEvent
    from backend.models.db.rider import Rider
    from backend.models.db.policy import Policy
    from backend.models.db.claim import Claim
    from backend.services.trigger_engine import _process_rider_claim, load_zones
    from backend.services.payout_engine import get_zone
    from datetime import date

    # Get demo event config
    demo_event = settings.DEMO_EVENTS.get(request.event_type)
    if not demo_event:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_EVENT_TYPE",
                "message": f"Valid types: {list(settings.DEMO_EVENTS.keys())}",
            },
        )

    zone_id = demo_event["zone_id"]

    # Create trigger event
    event = TriggerEvent(
        zone_id=zone_id,
        rainfall_mm_hr=demo_event["rainfall_mm_hr"],
        aqi_value=demo_event["aqi_value"],
        order_drop_pct=demo_event["order_drop_pct"],
        signals_confirmed=demo_event["signals_confirmed"],
        msc_status=demo_event["msc_status"],
        is_demo_event=True,
        rain_source="demo",
        aqi_source="demo",
    )
    db.add(event)
    await db.flush()

    # Find eligible riders
    today = date.today()
    riders_result = await db.execute(
        select(Rider, Policy).join(
            Policy, Rider.id == Policy.rider_id
        ).where(
            and_(
                Rider.zone_id == zone_id,
                Rider.is_active.is_(True),
                Policy.status == "active",
                Policy.week_start_date <= today,
                Policy.week_end_date >= today,
            )
        )
    )
    riders_with_policies = riders_result.all()

    # Load zone data
    zones = {z["id"]: z for z in load_zones()}
    zone_data = zones.get(zone_id, {"lat": 12.9165, "lon": 77.6101})

    claims_created = 0
    for rider, policy in riders_with_policies:
        try:
            # Check for fraud override
            demo_override = demo_event.get("fraud_gps_override", False)
            demo_distance = demo_event.get("fraud_gps_distance_km", 0.0)

            signals = {
                "rainfall_mm_hr": demo_event["rainfall_mm_hr"],
                "aqi_value": demo_event["aqi_value"],
                "order_drop_pct": demo_event["order_drop_pct"],
            }

            await _process_rider_claim(
                db, rider, policy, event, zone_data, signals,
                demo_override=demo_override,
                demo_distance_km=demo_distance,
            )
            claims_created += 1
        except Exception as e:
            if "idx_claims_rider_event" in str(e) or "UniqueViolation" in str(e.__class__.__name__):
                logger.warning(f"Duplicate claim for rider {rider.id} on event {event.id}, skipping")
                await db.rollback()
            else:
                logger.error(f"Error processing demo claim for rider {rider.id}: {e}")

    await db.commit()

    return DemoFireResponse(
        trigger_event_id=str(event.id),
        claims_created=claims_created,
    )


@router.get("/history")
async def get_trigger_history(
    zone_id: str = Query(default="BTM_LAYOUT"),
    days: int = Query(default=7, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(get_insurer_auth),
):
    """Get past trigger events for a zone."""
    from backend.models.db.trigger_event import TriggerEvent

    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    result = await db.execute(
        select(TriggerEvent).where(
            and_(
                TriggerEvent.zone_id == zone_id,
                TriggerEvent.detected_at >= cutoff,
            )
        ).order_by(TriggerEvent.detected_at.desc())
    )
    events = result.scalars().all()

    return {
        "data": [
            {
                "id": str(e.id),
                "zone_id": e.zone_id,
                "signals_confirmed": e.signals_confirmed,
                "msc_status": e.msc_status,
                "detected_at": e.detected_at.isoformat(),
                "ended_at": e.ended_at.isoformat() if e.ended_at else None,
                "is_demo_event": e.is_demo_event,
            }
            for e in events
        ],
        "error": None,
    }
