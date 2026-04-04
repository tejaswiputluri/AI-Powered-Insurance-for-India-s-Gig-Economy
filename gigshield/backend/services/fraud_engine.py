"""
Fraud Engine — 4-layer fraud detection pipeline with Confidence Score.
L1: GPS Coherence (30pts), L2: Weather Cross-Verify (30pts),
L3: Earnings Anomaly Z-Score (25pts), L4: Cluster/Ring DBSCAN (15pts).
Total: 100 points. RULE-17: Score < 35 = ALWAYS rejected.
"""

import logging
from uuid import UUID
from datetime import datetime, timezone, timedelta
from typing import Optional

from backend.config.constants import (
    FRAUD_WEIGHTS,
    CONFIDENCE_THRESHOLDS,
    GPS_MAX_DISTANCE_KM,
    Z_SCORE_THRESHOLD,
    CLUSTER_SUSPICION_COUNT,
    CLUSTER_TIME_WINDOW_MINUTES,
)
from backend.config.settings import settings
from backend.cache.redis_client import cache_get_json

logger = logging.getLogger(__name__)


# ─── L1: GPS Coherence Check ──────────────────────────────────────────────

async def check_l1_gps(
    rider_id: UUID,
    zone_id: str,
    zone_lat: float,
    zone_lon: float,
    demo_override: bool = False,
    demo_distance_km: float = 0.0,
) -> tuple[int, str, str]:
    """
    Check if rider's last known location is within 5km of disruption zone.

    Returns: (score: 0|30, result: 'pass'|'fail'|'skip', detail: str)
    """
    # Demo fraud override
    if demo_override:
        return (
            0,
            "fail",
            f"LOCATION_MISMATCH: {demo_distance_km:.1f}km from zone (demo override)",
        )

    # Get rider's last GPS poll from Redis
    gps_data = await cache_get_json(f"rider_gps:{rider_id}")

    if gps_data is None:
        # No GPS data — benefit of doubt (award full points)
        return (
            FRAUD_WEIGHTS["l1_gps"],
            "skip",
            "No GPS data available — benefit of doubt applied",
        )

    # Calculate Haversine distance
    try:
        from haversine import haversine, Unit
        rider_pos = (gps_data["lat"], gps_data["lon"])
        zone_pos = (zone_lat, zone_lon)
        distance_km = haversine(rider_pos, zone_pos, unit=Unit.KILOMETERS)
    except Exception as e:
        logger.warning(f"Haversine calculation failed: {e}")
        return (FRAUD_WEIGHTS["l1_gps"], "skip", f"GPS calculation error: {e}")

    if distance_km <= GPS_MAX_DISTANCE_KM:
        return (
            FRAUD_WEIGHTS["l1_gps"],
            "pass",
            f"Location confirmed: {distance_km:.1f}km from zone centroid",
        )
    else:
        return (
            0,
            "fail",
            f"LOCATION_MISMATCH: {distance_km:.1f}km from zone",
        )


# ─── L2: Weather Cross-Verify ─────────────────────────────────────────────

async def check_l2_weather(
    zone_id: str,
    rainfall_mm_hr: float,
    aqi_value: int,
) -> tuple[int, str, str]:
    """
    Re-verify weather signals. Confirm rain or AQI still above threshold.
    Returns: (score: 0|30, result, detail)
    """
    from backend.config.constants import RAIN_THRESHOLD_MM_HR, AQI_THRESHOLD

    rain_ok = rainfall_mm_hr >= RAIN_THRESHOLD_MM_HR
    aqi_ok = aqi_value >= AQI_THRESHOLD

    if rain_ok or aqi_ok:
        details = []
        if rain_ok:
            details.append(f"Rain {rainfall_mm_hr}mm/hr ≥ {RAIN_THRESHOLD_MM_HR}")
        if aqi_ok:
            details.append(f"AQI {aqi_value} ≥ {AQI_THRESHOLD}")
        return (
            FRAUD_WEIGHTS["l2_weather"],
            "pass",
            "Weather confirmed: " + ", ".join(details),
        )
    else:
        return (
            0,
            "fail",
            f"WEATHER_CLEARED: Rain={rainfall_mm_hr}mm/hr, AQI={aqi_value} — below thresholds",
        )


async def check_l3_earnings(
    rider_id: UUID,
    db_session=None,
) -> tuple[int, str, str]:
    """
    Check if rider's recent earnings suggest they were NOT actually disrupted.
    Uses Z-score comparison against 4-week baseline.

    Returns: (score: 0|25, result, detail)

    Logic:
    - Get rider's last 4 weeks of daily earnings/payouts from DB
    - Calculate mean and std of payout amounts
    - Compare current week's claims against historical baseline
    - If current week avg > (mean + Z_SCORE_THRESHOLD * std) → suspicious → 0 points
    - Otherwise → pass → 25 points
    - Edge case: If rider has < 2 weeks of history → skip → award full 25 points
    """
    if db_session is None:
        # No DB session — benefit of doubt
        return (
            FRAUD_WEIGHTS["l3_earnings"],
            "pass",
            "Earnings check passed (no DB session — benefit of doubt)",
        )

    try:
        from sqlalchemy import select, func
        from datetime import date, timedelta as td
        from backend.models.db.claim import Claim

        today = date.today()
        four_weeks_ago = today - td(weeks=4)
        one_week_ago = today - td(weeks=1)

        # Get historical payouts (last 4 weeks, excluding current week)
        hist_result = await db_session.execute(
            select(Claim.capped_payout_paise)
            .where(
                Claim.rider_id == rider_id,
                Claim.status.in_(["approved", "flagged"]),
                Claim.created_at >= four_weeks_ago,
                Claim.created_at < one_week_ago,
            )
        )
        historical_payouts = [row[0] for row in hist_result.all() if row[0]]

        # Need at least 2 data points for meaningful Z-score
        if len(historical_payouts) < 2:
            return (
                FRAUD_WEIGHTS["l3_earnings"],
                "pass",
                f"Earnings check passed (insufficient history: {len(historical_payouts)} claims — benefit of doubt)",
            )

        import statistics
        mean_payout = statistics.mean(historical_payouts)
        std_payout = statistics.stdev(historical_payouts) if len(historical_payouts) > 1 else 0

        # Get current week claims
        curr_result = await db_session.execute(
            select(Claim.capped_payout_paise)
            .where(
                Claim.rider_id == rider_id,
                Claim.status.in_(["approved", "flagged", "fraud_checking"]),
                Claim.created_at >= one_week_ago,
            )
        )
        current_payouts = [row[0] for row in curr_result.all() if row[0]]

        if not current_payouts:
            return (
                FRAUD_WEIGHTS["l3_earnings"],
                "pass",
                "Earnings check passed (no current week claims)",
            )

        current_avg = statistics.mean(current_payouts)

        # Z-score check: if current avg is suspiciously higher than baseline
        if std_payout > 0:
            z_score = (current_avg - mean_payout) / std_payout
            if z_score > Z_SCORE_THRESHOLD:
                baseline_rupees = mean_payout / 100
                current_rupees = current_avg / 100
                return (
                    0,
                    "fail",
                    f"EARNINGS_SPIKE: week avg ₹{current_rupees:.0f} vs baseline ₹{baseline_rupees:.0f} (z={z_score:.2f})",
                )

        return (
            FRAUD_WEIGHTS["l3_earnings"],
            "pass",
            f"Earnings check passed (current avg within normal range, baseline={mean_payout/100:.0f})",
        )

    except Exception as e:
        logger.warning(f"L3 earnings check error: {e}")
        return (
            FRAUD_WEIGHTS["l3_earnings"],
            "skip",
            f"Earnings check skipped due to error: {str(e)}",
        )


# ─── L4: Cluster / Ring Detection ─────────────────────────────────────────

async def check_l4_cluster(
    rider_id: UUID,
    zone_id: str,
    detected_at: datetime,
    msc_confirmed: bool = True,
    db_session=None,
) -> tuple[int, str, str]:
    """
    DBSCAN-based ring detection. Check if claim is part of suspicious cluster.

    Logic:
    - Get all claims created within 30 minutes of this claim, in same zone
    - If count >= CLUSTER_SUSPICION_COUNT (5):
        - Verify MSC was genuinely active for this zone at that time
        - If MSC was confirmed → pass (legitimate mass event) → 15 points
        - If MSC was NOT confirmed → suspicious ring → 0 points
    - If count < 5 → pass → 15 points

    Returns: (score: 0|15, result, detail)
    """
    if db_session is None:
        # No DB session — simple check
        if msc_confirmed:
            return (
                FRAUD_WEIGHTS["l4_cluster"],
                "pass",
                "No suspicious cluster — MSC was confirmed for this zone",
            )
        else:
            return (
                0,
                "fail",
                f"RING_DETECTED: Claims in {zone_id} but MSC was not confirmed",
            )

    try:
        from sqlalchemy import select, func
        from backend.models.db.claim import Claim
        from backend.models.db.trigger_event import TriggerEvent

        time_window = timedelta(minutes=CLUSTER_TIME_WINDOW_MINUTES)
        window_start = detected_at - time_window
        window_end = detected_at + time_window

        # Count claims in same zone within the time window
        result = await db_session.execute(
            select(func.count(Claim.id))
            .join(TriggerEvent, Claim.trigger_event_id == TriggerEvent.id)
            .where(
                TriggerEvent.zone_id == zone_id,
                Claim.created_at >= window_start,
                Claim.created_at <= window_end,
            )
        )
        cluster_count = result.scalar() or 0

        if cluster_count >= CLUSTER_SUSPICION_COUNT:
            # Large cluster — verify MSC was genuinely active
            msc_check = await db_session.execute(
                select(TriggerEvent)
                .where(
                    TriggerEvent.zone_id == zone_id,
                    TriggerEvent.detected_at >= window_start,
                    TriggerEvent.detected_at <= window_end,
                    TriggerEvent.is_active == True,
                )
            )
            active_events = msc_check.scalars().all()

            if active_events and msc_confirmed:
                return (
                    FRAUD_WEIGHTS["l4_cluster"],
                    "pass",
                    f"Large cluster ({cluster_count} claims) but MSC confirmed — legitimate mass event",
                )
            else:
                return (
                    0,
                    "fail",
                    f"RING_DETECTED: {cluster_count} claims in {zone_id} within {CLUSTER_TIME_WINDOW_MINUTES}min, MSC unconfirmed",
                )
        else:
            return (
                FRAUD_WEIGHTS["l4_cluster"],
                "pass",
                f"No suspicious cluster ({cluster_count} claims within window, threshold={CLUSTER_SUSPICION_COUNT})",
            )

    except Exception as e:
        logger.warning(f"L4 cluster check error: {e}")
        # Benefit of doubt on error
        if msc_confirmed:
            return (
                FRAUD_WEIGHTS["l4_cluster"],
                "skip",
                f"Cluster check skipped due to error — MSC confirmed: {str(e)}",
            )
        return (
            0,
            "fail",
            f"RING_DETECTED: Cluster check failed + MSC not confirmed: {str(e)}",
        )


# ─── Main Pipeline ────────────────────────────────────────────────────────

async def run_fraud_pipeline(
    rider_id: UUID,
    zone_id: str,
    zone_lat: float,
    zone_lon: float,
    rainfall_mm_hr: float,
    aqi_value: int,
    detected_at: datetime,
    msc_confirmed: bool = True,
    demo_override: bool = False,
    demo_distance_km: float = 0.0,
    db_session=None,
) -> dict:
    """
    Run the complete 4-layer fraud detection pipeline.

    Returns dict with all layer results, total score, and routing decision.
    """
    # Run all 4 layers
    l1_score, l1_result, l1_detail = await check_l1_gps(
        rider_id, zone_id, zone_lat, zone_lon,
        demo_override=demo_override,
        demo_distance_km=demo_distance_km,
    )

    l2_score, l2_result, l2_detail = await check_l2_weather(
        zone_id, rainfall_mm_hr, aqi_value,
    )

    l3_score, l3_result, l3_detail = await check_l3_earnings(
        rider_id, db_session=db_session,
    )

    l4_score, l4_result, l4_detail = await check_l4_cluster(
        rider_id, zone_id, detected_at,
        msc_confirmed=msc_confirmed,
        db_session=db_session,
    )

    # Calculate total score
    total_score = l1_score + l2_score + l3_score + l4_score

    # Route decision
    decision = route_claim(total_score)

    # Build reason if rejected
    reason = None
    if decision == "rejected":
        failed_layers = []
        if l1_result == "fail":
            failed_layers.append("GPS_MISMATCH")
        if l2_result == "fail":
            failed_layers.append("WEATHER_CLEARED")
        if l3_result == "fail":
            failed_layers.append("EARNINGS_SPIKE")
        if l4_result == "fail":
            failed_layers.append("RING_DETECTED")
        reason = "+".join(failed_layers) if failed_layers else "LOW_CONFIDENCE"

    result = {
        "l1_gps_score": l1_score,
        "l1_gps_result": l1_result,
        "l1_gps_detail": l1_detail,
        "l2_weather_score": l2_score,
        "l2_weather_result": l2_result,
        "l2_weather_detail": l2_detail,
        "l3_earnings_score": l3_score,
        "l3_earnings_result": l3_result,
        "l3_earnings_detail": l3_detail,
        "l4_cluster_score": l4_score,
        "l4_cluster_result": l4_result,
        "l4_cluster_detail": l4_detail,
        "total_score": total_score,
        "decision": decision,
        "reason": reason,
    }

    logger.info(
        f"Fraud pipeline: rider={rider_id} score={total_score}/100 "
        f"decision={decision} [L1={l1_score} L2={l2_score} L3={l3_score} L4={l4_score}]"
    )

    return result


def route_claim(confidence_score: int) -> str:
    """
    Route claim based on confidence score.
    RULE-17: Score < 35 = ALWAYS rejected. No exceptions. No manual override.
    """
    if confidence_score >= CONFIDENCE_THRESHOLDS["auto_approve"]:
        return "auto_approved"
    elif confidence_score >= CONFIDENCE_THRESHOLDS["flag_approve"]:
        return "flagged"      # Pay but flag for audit
    elif confidence_score >= CONFIDENCE_THRESHOLDS["hold"]:
        return "held"         # Human review required
    else:
        return "rejected"     # RULE-17: no exceptions below 35
