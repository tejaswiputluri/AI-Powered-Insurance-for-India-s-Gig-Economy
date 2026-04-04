"""
Trigger Engine — MSC (Multi-Signal Confluence) evaluator.
Called every 30 minutes by APScheduler. Core loop that drives the entire claim pipeline.
RULE-14: MSC requires minimum 2 of 3 core signals: Rain, AQI, Order Volume Drop.
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID
from typing import Optional

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config.constants import (
    RAIN_THRESHOLD_MM_HR,
    AQI_THRESHOLD,
    ORDER_DROP_THRESHOLD_PCT,
    MSC_MINIMUM_SIGNALS,
    MSC_HIGH_SIGNALS,
    COVERAGE_FACTOR_STANDARD,
    COVERAGE_FACTOR_HIGH,
    EVENT_EXPIRY_HOURS,
)
from backend.config.settings import settings
from backend.services import weather_service, order_volume_service
from backend.services.payout_engine import get_zone

logger = logging.getLogger(__name__)

# Load zones data
_zones = None


def load_zones() -> list[dict]:
    """Load all Bengaluru zone definitions."""
    global _zones
    if _zones is None:
        zones_path = Path(__file__).parent.parent.parent / "data" / "zones.json"
        with open(zones_path) as f:
            data = json.load(f)
        _zones = data["zones"]
    return _zones


def count_confirmed_signals(signals: dict) -> int:
    """
    Count how many of the 3 CORE signals are above threshold.
    Note: Road disruption and civic alert are tertiary — they do NOT count
    toward MSC minimum. They are recorded but not required.
    """
    count = 0
    if signals.get("rainfall_mm_hr", 0) >= RAIN_THRESHOLD_MM_HR:
        count += 1
    if signals.get("aqi_value", 0) >= AQI_THRESHOLD:
        count += 1
    if signals.get("order_drop_pct", 0) >= ORDER_DROP_THRESHOLD_PCT:
        count += 1
    return count


async def fetch_all_signals(zone: dict) -> dict:
    """
    Fetch all signals for a zone with Redis cache fallback.
    Each signal has its own TTL: weather = 35min, order_volume = 30min.
    """
    lat, lon, zone_id = zone["lat"], zone["lon"], zone["id"]

    rainfall_result = await weather_service.get_rainfall(lat, lon, zone_id)
    aqi_result = await weather_service.get_aqi(lat, lon, zone_id)

    rainfall = rainfall_result["value"]
    aqi = aqi_result["value"]

    order_drop = await order_volume_service.get_drop_pct(
        zone_id, rainfall_mm_hr=rainfall, aqi=aqi
    )
    road_disruption = await order_volume_service.get_mock_road_disruption(zone_id)
    civic_alert = await order_volume_service.get_civic_alert(zone_id)

    return {
        "rainfall_mm_hr": rainfall,
        "aqi_value": aqi,
        "order_drop_pct": order_drop,
        "road_disruption_pct": road_disruption,
        "civic_alert": civic_alert,
        "rain_source": rainfall_result["source"],
        "aqi_source": aqi_result["source"],
    }


def determine_msc_status(signals_confirmed: int) -> str:
    """Determine MSC status based on confirmed signal count."""
    if signals_confirmed >= MSC_HIGH_SIGNALS:
        return "high"
    elif signals_confirmed >= MSC_MINIMUM_SIGNALS:
        return "standard"
    else:
        return "not_met"


async def run_msc_check(db_session: AsyncSession):
    """
    Called every 30 minutes by APScheduler.
    For each Bengaluru zone:
      1. Fetch weather signals (with cache fallback)
      2. Evaluate MSC
      3. If MSC confirmed and no active event → create trigger_event
      4. Find all riders in zone with active policy this week
      5. For each rider → create claim → run fraud pipeline → initiate payout if approved
    """
    from backend.models.db.trigger_event import TriggerEvent
    from backend.models.db.rider import Rider
    from backend.models.db.policy import Policy
    from backend.models.db.claim import Claim
    from backend.models.db.fraud_check import FraudCheck
    from backend.models.db.payout import Payout
    from backend.models.db.audit_log import AuditLog
    from backend.services.fraud_engine import run_fraud_pipeline
    from backend.services.payout_engine import calculate_payout
    from datetime import date

    zones = load_zones()

    for zone in zones:
        zone_id = zone["id"]

        # 1. Fetch signals
        signals = await fetch_all_signals(zone)
        confirmed = count_confirmed_signals(signals)
        msc_status = determine_msc_status(confirmed)

        logger.info(
            f"MSC Check zone={zone_id}: rain={signals['rainfall_mm_hr']}, "
            f"aqi={signals['aqi_value']}, order_drop={signals['order_drop_pct']:.2%}, "
            f"confirmed={confirmed}/3, status={msc_status}"
        )

        if confirmed >= MSC_MINIMUM_SIGNALS:
            # Check for existing active event
            result = await db_session.execute(
                select(TriggerEvent).where(
                    and_(
                        TriggerEvent.zone_id == zone_id,
                        TriggerEvent.ended_at.is_(None),
                    )
                )
            )
            existing = result.scalar_one_or_none()

            if existing:
                logger.info(f"Active event already exists for zone={zone_id}, skipping")
                continue

            # Create trigger event
            event = TriggerEvent(
                zone_id=zone_id,
                rainfall_mm_hr=signals["rainfall_mm_hr"],
                aqi_value=signals["aqi_value"],
                order_drop_pct=signals["order_drop_pct"],
                road_disruption_pct=signals.get("road_disruption_pct"),
                civic_alert=signals.get("civic_alert", False),
                signals_confirmed=confirmed,
                msc_status=msc_status,
                rain_source=signals.get("rain_source", "open_meteo"),
                aqi_source=signals.get("aqi_source", "open_meteo"),
            )
            db_session.add(event)
            await db_session.flush()

            logger.info(f"Created trigger event {event.id} for zone={zone_id}")

            # Find eligible riders (active policy this week)
            today = date.today()
            riders_result = await db_session.execute(
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

            for rider, policy in riders_with_policies:
                try:
                    await _process_rider_claim(
                        db_session, rider, policy, event, zone, signals
                    )
                except Exception as e:
                    logger.error(f"Error processing claim for rider {rider.id}: {e}")

            await db_session.commit()

        else:
            # Close active events if signals dropped
            result = await db_session.execute(
                select(TriggerEvent).where(
                    and_(
                        TriggerEvent.zone_id == zone_id,
                        TriggerEvent.ended_at.is_(None),
                    )
                )
            )
            active_event = result.scalar_one_or_none()
            if active_event:
                active_event.ended_at = datetime.now(timezone.utc)
                logger.info(f"Closed trigger event {active_event.id} for zone={zone_id}")
                await db_session.commit()


async def _process_rider_claim(
    db_session: AsyncSession,
    rider,
    policy,
    event,
    zone: dict,
    signals: dict,
    demo_override: bool = False,
    demo_distance_km: float = 0.0,
):
    """Process a single rider's claim for a trigger event."""
    from backend.models.db.claim import Claim
    from backend.models.db.fraud_check import FraudCheck
    from backend.models.db.payout import Payout
    from backend.models.db.audit_log import AuditLog
    from backend.services.fraud_engine import run_fraud_pipeline
    from backend.services.payout_engine import calculate_payout
    from backend.services.notification_service import send_notification

    # RULE-19: No payout if event ended more than 4 hours ago
    if event.ended_at:
        hours_since_end = (datetime.now(timezone.utc) - event.ended_at).total_seconds() / 3600
        if hours_since_end > EVENT_EXPIRY_HOURS:
            logger.info(
                f"Skipping claim for rider={rider.id}: event ended "
                f"{hours_since_end:.1f}h ago > {EVENT_EXPIRY_HOURS}h limit (RULE-19)"
            )
            return

    # Calculate payout
    payout_data = await calculate_payout(
        rider_daily_earning_paise=rider.self_reported_daily_earning_paise,
        work_hours_start=rider.work_hours_start,
        work_hours_end=rider.work_hours_end,
        zone_id=event.zone_id,
        signals_confirmed=event.signals_confirmed,
        coverage_cap_paise=policy.coverage_cap_paise,
        disruption_hours=event.duration_hours,
    )

    # Create claim
    claim = Claim(
        rider_id=rider.id,
        policy_id=policy.id,
        trigger_event_id=event.id,
        baseline_hourly_earning_paise=payout_data["baseline_hourly_earning_paise"],
        disruption_hours=payout_data["disruption_hours"],
        zone_impact_factor=payout_data["zone_impact_factor"],
        coverage_factor=payout_data["coverage_factor"],
        calculated_payout_paise=payout_data["calculated_payout_paise"],
        capped_payout_paise=payout_data["capped_payout_paise"],
        status="pending_fraud_check",
    )
    db_session.add(claim)
    await db_session.flush()

    # Update status to fraud_checking
    claim.status = "fraud_checking"

    # Run fraud pipeline (pass demo overrides for fraud_attempt scenario)
    fraud_result = await run_fraud_pipeline(
        rider_id=rider.id,
        zone_id=event.zone_id,
        zone_lat=zone.get("lat", 12.9165),
        zone_lon=zone.get("lon", 77.6101),
        rainfall_mm_hr=signals["rainfall_mm_hr"],
        aqi_value=int(signals["aqi_value"]),
        detected_at=event.detected_at,
        msc_confirmed=True,
        demo_override=demo_override,
        demo_distance_km=demo_distance_km,
        db_session=db_session,
    )

    # Save fraud check
    fraud_check = FraudCheck(
        claim_id=claim.id,
        l1_gps_score=fraud_result["l1_gps_score"],
        l1_gps_result=fraud_result["l1_gps_result"],
        l1_gps_detail=fraud_result["l1_gps_detail"],
        l2_weather_score=fraud_result["l2_weather_score"],
        l2_weather_result=fraud_result["l2_weather_result"],
        l2_weather_detail=fraud_result["l2_weather_detail"],
        l3_earnings_score=fraud_result["l3_earnings_score"],
        l3_earnings_result=fraud_result["l3_earnings_result"],
        l3_earnings_detail=fraud_result["l3_earnings_detail"],
        l4_cluster_score=fraud_result["l4_cluster_score"],
        l4_cluster_result=fraud_result["l4_cluster_result"],
        l4_cluster_detail=fraud_result["l4_cluster_detail"],
        total_score=fraud_result["total_score"],
        decision=fraud_result["decision"],
    )
    db_session.add(fraud_check)

    # Update claim with fraud results
    claim.confidence_score = fraud_result["total_score"]
    claim.fraud_decision = fraud_result["decision"]
    claim.fraud_reason = fraud_result.get("reason")
    claim.fraud_checked_at = datetime.now(timezone.utc)

    # Route based on decision
    if fraud_result["decision"] == "auto_approved":
        claim.status = "approved"
        # Create payout
        payout = Payout(
            claim_id=claim.id,
            rider_id=rider.id,
            amount_paise=claim.capped_payout_paise,
            upi_vpa=getattr(rider, 'upi_vpa', None) or "demo@upi",
            status="processing",
        )
        db_session.add(payout)
        claim.payout_initiated_at = datetime.now(timezone.utc)
        # Send payout notification
        await send_notification(
            rider_id=rider.id,
            notification_type="PAYOUT_SENT",
            template_data={
                "amount": claim.capped_payout_paise // 100,
                "claim_short_id": str(claim.id)[:8],
            },
            db_session=db_session,
        )

    elif fraud_result["decision"] == "flagged":
        claim.status = "flagged"
        # Still create payout (flagged = pay + flag for audit)
        payout = Payout(
            claim_id=claim.id,
            rider_id=rider.id,
            amount_paise=claim.capped_payout_paise,
            upi_vpa=getattr(rider, 'upi_vpa', None) or "demo@upi",
            status="processing",
        )
        db_session.add(payout)
        claim.payout_initiated_at = datetime.now(timezone.utc)
        await send_notification(
            rider_id=rider.id,
            notification_type="PAYOUT_SENT",
            template_data={
                "amount": claim.capped_payout_paise // 100,
                "claim_short_id": str(claim.id)[:8],
            },
            db_session=db_session,
        )

    elif fraud_result["decision"] == "held":
        claim.status = "on_hold"
        await send_notification(
            rider_id=rider.id,
            notification_type="CLAIM_ON_HOLD",
            template_data={"claim_short_id": str(claim.id)[:8]},
            db_session=db_session,
        )

    elif fraud_result["decision"] == "rejected":
        claim.status = "rejected"
        await send_notification(
            rider_id=rider.id,
            notification_type="CLAIM_REJECTED",
            template_data={
                "claim_short_id": str(claim.id)[:8],
                "reason_code": fraud_result.get("reason", "LOW_CONFIDENCE"),
            },
            db_session=db_session,
        )

    # Audit log
    audit = AuditLog(
        entity_type="claim",
        entity_id=claim.id,
        action=f"claim_created_and_fraud_{fraud_result['decision']}",
        detail={
            "confidence_score": fraud_result["total_score"],
            "payout_paise": claim.capped_payout_paise,
            "zone_id": event.zone_id,
        },
    )
    db_session.add(audit)

    logger.info(
        f"Processed claim for rider={rider.id}: score={fraud_result['total_score']}, "
        f"decision={fraud_result['decision']}, payout={claim.capped_payout_paise}"
    )
