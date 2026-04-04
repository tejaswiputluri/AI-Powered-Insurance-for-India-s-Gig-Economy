"""
Insurer Router — /api/v1/insurer endpoints.
Dashboard endpoints for the insurer: overview, heatmap, fraud queue, claims, reserves.
"""

import logging
from uuid import UUID
from datetime import datetime, timezone, timedelta, date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.database import get_db
from backend.api.middleware import get_insurer_auth
from backend.models.schemas.insurer import (
    InsurerOverviewResponse,
    WeekOverview,
    HeatmapResponse,
    HeatmapZone,
    FraudDecisionRequest,
    ReservesResponse,
    ReserveBreakdown,
)
from backend.services.forecast_service import get_zone_forecast
from backend.services.trigger_engine import load_zones

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/insurer", tags=["insurer"])


@router.get("/overview", response_model=InsurerOverviewResponse)
async def get_overview(
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(get_insurer_auth),
):
    """Dashboard overview — this week's KPIs."""
    from backend.models.db.rider import Rider
    from backend.models.db.policy import Policy
    from backend.models.db.claim import Claim
    from backend.models.db.payout import Payout

    today = date.today()
    monday = today - timedelta(days=today.weekday())

    # Active riders
    riders_result = await db.execute(
        select(func.count(Rider.id)).where(Rider.is_active.is_(True))
    )
    active_riders = riders_result.scalar() or 0

    # Premium collected this week
    premium_result = await db.execute(
        select(func.sum(Policy.weekly_premium_paise)).where(
            and_(
                Policy.week_start_date == monday,
                Policy.premium_deduction_status == "success",
            )
        )
    )
    premium_collected = premium_result.scalar() or 0

    # Claims this week
    claims_result = await db.execute(
        select(Claim).where(Claim.created_at >= datetime.combine(monday, datetime.min.time()).replace(tzinfo=timezone.utc))
    )
    claims = claims_result.scalars().all()

    claims_paid = sum(c.capped_payout_paise for c in claims if c.status == "paid")
    claims_auto = sum(1 for c in claims if c.fraud_decision == "auto_approved")
    claims_flagged = sum(1 for c in claims if c.fraud_decision == "flagged")
    claims_rejected = sum(1 for c in claims if c.fraud_decision == "rejected")

    loss_ratio = (claims_paid / premium_collected) if premium_collected > 0 else 0.0

    return InsurerOverviewResponse(
        this_week=WeekOverview(
            active_riders=active_riders,
            premium_collected_paise=premium_collected,
            claims_paid_paise=claims_paid,
            loss_ratio=round(loss_ratio, 4),
            claims_auto_approved=claims_auto,
            claims_flagged=claims_flagged,
            claims_rejected=claims_rejected,
        )
    )


@router.get("/heatmap", response_model=HeatmapResponse)
async def get_heatmap(
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(get_insurer_auth),
):
    """Risk heatmap — LSTM forecast per zone."""
    zones = load_zones()
    today = date.today()
    monday = today - timedelta(days=today.weekday())

    heatmap_zones = []
    for zone in zones:
        forecast = await get_zone_forecast(zone["id"])
        forecasts = forecast.get("forecasts", [])

        # Average probability for the week
        avg_prob = 0.0
        if forecasts:
            avg_prob = sum(f["disruption_probability"] for f in forecasts) / len(forecasts)

        risk_level = "high" if avg_prob >= 0.60 else ("medium" if avg_prob >= 0.35 else "low")
        expected_claims = int(avg_prob * 15)  # Rough estimate
        reserve = expected_claims * 35000     # Avg claim ~₹350

        heatmap_zones.append(HeatmapZone(
            zone_id=zone["id"],
            zone_name=zone["name"],
            lat=zone["lat"],
            lon=zone["lon"],
            disruption_probability=round(avg_prob, 2),
            expected_claims=expected_claims,
            reserve_estimate_paise=reserve,
            risk_level=risk_level,
        ))

    return HeatmapResponse(
        zones=heatmap_zones,
        forecast_week=monday.isoformat(),
    )


@router.get("/fraud-queue")
async def get_fraud_queue(
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(get_insurer_auth),
):
    """Pending fraud reviews — claims with status='on_hold' or 'flagged'."""
    from backend.models.db.claim import Claim
    from backend.models.db.rider import Rider
    from backend.models.db.fraud_check import FraudCheck
    from backend.models.db.trigger_event import TriggerEvent

    result = await db.execute(
        select(Claim, Rider, FraudCheck, TriggerEvent)
        .join(Rider, Claim.rider_id == Rider.id)
        .join(TriggerEvent, Claim.trigger_event_id == TriggerEvent.id)
        .outerjoin(FraudCheck, Claim.id == FraudCheck.claim_id)
        .where(Claim.status.in_(["on_hold", "flagged"]))
        .order_by(Claim.created_at.asc())
    )
    rows = result.all()

    queue_items = []
    for claim, rider, fraud_check, trigger_event in rows:
        minutes_waiting = int(
            (datetime.now(timezone.utc) - claim.created_at).total_seconds() / 60
        )
        item = {
            "claim_id": str(claim.id),
            "rider_name": rider.name or "Unknown",
            "zone_id": trigger_event.zone_id if trigger_event else "Unknown",
            "claim_amount_paise": claim.capped_payout_paise,
            "confidence_score": claim.confidence_score or 0,
            "l1_gps_score": fraud_check.l1_gps_score if fraud_check else 0,
            "l1_gps_result": fraud_check.l1_gps_result if fraud_check else "skip",
            "l2_weather_score": fraud_check.l2_weather_score if fraud_check else 0,
            "l2_weather_result": fraud_check.l2_weather_result if fraud_check else "skip",
            "l3_earnings_score": fraud_check.l3_earnings_score if fraud_check else 0,
            "l3_earnings_result": fraud_check.l3_earnings_result if fraud_check else "skip",
            "l4_cluster_score": fraud_check.l4_cluster_score if fraud_check else 0,
            "l4_cluster_result": fraud_check.l4_cluster_result if fraud_check else "skip",
            "created_at": claim.created_at.isoformat(),
            "time_waiting_minutes": minutes_waiting,
        }
        queue_items.append(item)

    return {"data": queue_items, "error": None}


@router.post("/fraud-queue/{claim_id}/decision")
async def fraud_decision(
    claim_id: UUID,
    request: FraudDecisionRequest,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(get_insurer_auth),
):
    """Insurer approves or rejects a held claim."""
    from backend.models.db.claim import Claim
    from backend.models.db.payout import Payout
    from backend.models.db.audit_log import AuditLog

    result = await db.execute(
        select(Claim).where(Claim.id == claim_id)
    )
    claim = result.scalar_one_or_none()

    if not claim:
        raise HTTPException(status_code=404, detail={"code": "CLAIM_NOT_FOUND"})

    if claim.status not in ("on_hold", "flagged"):
        raise HTTPException(
            status_code=400,
            detail={"code": "INVALID_STATUS", "message": f"Claim is {claim.status}, not reviewable"},
        )

    if request.decision == "approve":
        claim.status = "approved"
        # Create payout
        payout = Payout(
            claim_id=claim.id,
            rider_id=claim.rider_id,
            amount_paise=claim.capped_payout_paise,
            status="processing",
        )
        db.add(payout)
        claim.payout_initiated_at = datetime.now(timezone.utc)
    else:
        claim.status = "rejected"
        claim.fraud_reason = request.note or "Manual rejection by insurer"

    # Audit
    audit = AuditLog(
        entity_type="claim",
        entity_id=claim.id,
        action=f"insurer_{request.decision}",
        actor="insurer",
        detail={"note": request.note},
    )
    db.add(audit)

    await db.commit()

    return {"data": {"updated": True}, "error": None}


@router.get("/claims")
async def get_all_claims(
    status: str = Query(default="all"),
    zone_id: str = Query(default="all"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(get_insurer_auth),
):
    """Paginated list of all claims with optional filters."""
    from backend.models.db.claim import Claim
    from backend.models.db.rider import Rider
    from backend.models.db.trigger_event import TriggerEvent

    query = (
        select(Claim, Rider, TriggerEvent)
        .join(Rider, Claim.rider_id == Rider.id)
        .join(TriggerEvent, Claim.trigger_event_id == TriggerEvent.id)
    )

    if status != "all":
        query = query.where(Claim.status == status)

    if zone_id != "all":
        query = query.where(TriggerEvent.zone_id == zone_id)

    query = query.order_by(Claim.created_at.desc()).limit(limit).offset(offset)

    result = await db.execute(query)
    rows = result.all()

    claims_data = []
    for claim, rider, trigger_event in rows:
        claims_data.append({
            "id": str(claim.id),
            "rider_name": rider.name,
            "zone_id": trigger_event.zone_id if trigger_event else rider.zone_id,
            "capped_payout_paise": claim.capped_payout_paise,
            "confidence_score": claim.confidence_score,
            "fraud_decision": claim.fraud_decision,
            "status": claim.status,
            "created_at": claim.created_at.isoformat(),
        })

    return {"data": claims_data, "error": None}


@router.get("/reserves", response_model=ReservesResponse)
async def get_reserves(
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(get_insurer_auth),
):
    """Weekly reserve estimates."""
    zones = load_zones()

    breakdown = []
    total_current = 0
    total_next = 0

    for zone in zones:
        forecast = await get_zone_forecast(zone["id"])
        forecasts = forecast.get("forecasts", [])

        if forecasts:
            prob = forecasts[0]["disruption_probability"]
        else:
            prob = 0.3

        expected = int(prob * 10)
        reserve = expected * 35000
        total_current += reserve
        total_next += int(reserve * 1.1)

        breakdown.append(ReserveBreakdown(
            zone_id=zone["id"],
            zone_name=zone["name"],
            reserve_paise=reserve,
            expected_claims=expected,
        ))

    return ReservesResponse(
        current_week_reserve_paise=total_current,
        next_week_estimate_paise=total_next,
        reserve_ratio=round(total_next / max(total_current, 1), 2),
        breakdown_by_zone=breakdown,
    )
