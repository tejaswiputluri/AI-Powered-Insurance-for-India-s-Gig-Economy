"""
Claims Router — /api/v1/claims endpoints.
Handles claim listing, detail, and timeline views.
"""

import logging
from uuid import UUID
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.database import get_db
from backend.api.middleware import get_current_rider_id
from backend.models.schemas.claim import (
    ClaimResponse,
    ClaimTimelineResponse,
    TimelineEvent,
    ClaimListResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/claims", tags=["claims"])


@router.get("/me")
async def get_rider_claims(
    db: AsyncSession = Depends(get_db),
    rider_id: UUID = Depends(get_current_rider_id),
):
    """Get all claims for the authenticated rider, newest first."""
    from backend.models.db.claim import Claim

    result = await db.execute(
        select(Claim)
        .where(Claim.rider_id == rider_id)
        .order_by(Claim.created_at.desc())
    )
    claims = result.scalars().all()

    return {
        "data": {
            "claims": [ClaimResponse.model_validate(c).model_dump() for c in claims],
            "total": len(claims),
        },
        "error": None,
    }


@router.get("/{claim_id}")
async def get_claim_detail(
    claim_id: UUID,
    db: AsyncSession = Depends(get_db),
    rider_id: UUID = Depends(get_current_rider_id),
):
    """Get full claim detail (rider must own this claim)."""
    from backend.models.db.claim import Claim
    from backend.models.db.fraud_check import FraudCheck
    from backend.models.db.payout import Payout

    result = await db.execute(
        select(Claim).where(
            and_(Claim.id == claim_id, Claim.rider_id == rider_id)
        )
    )
    claim = result.scalar_one_or_none()

    if not claim:
        raise HTTPException(status_code=404, detail={"code": "CLAIM_NOT_FOUND"})

    claim_data = ClaimResponse.model_validate(claim).model_dump()

    # Fetch fraud check via explicit query (avoid lazy loading in async)
    fraud_summary = None
    fc_result = await db.execute(
        select(FraudCheck).where(FraudCheck.claim_id == claim.id)
    )
    fraud_check = fc_result.scalar_one_or_none()
    if fraud_check:
        fraud_summary = {
            "total_score": fraud_check.total_score,
            "decision": fraud_check.decision,
        }

    # Fetch payout via explicit query
    payout_info = None
    po_result = await db.execute(
        select(Payout).where(Payout.claim_id == claim.id)
    )
    payout = po_result.scalar_one_or_none()
    if payout:
        payout_info = {
            "amount_paise": payout.amount_paise,
            "status": payout.status,
            "upi_vpa": payout.upi_vpa,
        }

    return {
        "data": {
            **claim_data,
            "fraud_summary": fraud_summary,
            "payout": payout_info,
        },
        "error": None,
    }


@router.get("/{claim_id}/timeline", response_model=ClaimTimelineResponse)
async def get_claim_timeline(
    claim_id: UUID,
    db: AsyncSession = Depends(get_db),
    rider_id: UUID = Depends(get_current_rider_id),
):
    """
    Full audit trail timeline for a claim.
    Shows: rain_detected → aqi_confirmed → msc_confirmed → fraud_check → payout_sent
    """
    from backend.models.db.claim import Claim
    from backend.models.db.trigger_event import TriggerEvent
    from backend.models.db.audit_log import AuditLog

    result = await db.execute(
        select(Claim).where(
            and_(Claim.id == claim_id, Claim.rider_id == rider_id)
        )
    )
    claim = result.scalar_one_or_none()
    if not claim:
        raise HTTPException(status_code=404, detail={"code": "CLAIM_NOT_FOUND"})

    events = []

    # Get trigger event details
    trigger_result = await db.execute(
        select(TriggerEvent).where(TriggerEvent.id == claim.trigger_event_id)
    )
    trigger = trigger_result.scalar_one_or_none()

    if trigger:
        # Signal detection events
        from backend.config.constants import RAIN_THRESHOLD_MM_HR, AQI_THRESHOLD, ORDER_DROP_THRESHOLD_PCT

        if trigger.rainfall_mm_hr and trigger.rainfall_mm_hr >= RAIN_THRESHOLD_MM_HR:
            events.append(TimelineEvent(
                timestamp=trigger.detected_at.isoformat(),
                event="rain_detected",
                detail=f"{trigger.rainfall_mm_hr}mm/hr",
            ))

        if trigger.aqi_value and trigger.aqi_value >= AQI_THRESHOLD:
            events.append(TimelineEvent(
                timestamp=trigger.detected_at.isoformat(),
                event="aqi_confirmed",
                detail=f"AQI {trigger.aqi_value}",
            ))

        if trigger.order_drop_pct and trigger.order_drop_pct >= ORDER_DROP_THRESHOLD_PCT:
            events.append(TimelineEvent(
                timestamp=trigger.detected_at.isoformat(),
                event="order_drop_confirmed",
                detail=f"{trigger.order_drop_pct:.0%} drop",
            ))

        events.append(TimelineEvent(
            timestamp=trigger.detected_at.isoformat(),
            event="msc_confirmed",
            detail=f"{trigger.signals_confirmed}/3 signals",
        ))

    # Claim creation
    events.append(TimelineEvent(
        timestamp=claim.created_at.isoformat(),
        event="claim_created",
        detail=f"₹{claim.capped_payout_paise / 100:.0f} estimated",
    ))

    # Fraud check
    if claim.fraud_checked_at:
        events.append(TimelineEvent(
            timestamp=claim.fraud_checked_at.isoformat(),
            event="fraud_check_completed",
            detail=f"Score {claim.confidence_score}/100",
        ))

        if claim.fraud_decision:
            events.append(TimelineEvent(
                timestamp=claim.fraud_checked_at.isoformat(),
                event="fraud_decision",
                detail=claim.fraud_decision,
            ))

    # Payout
    if claim.payout_initiated_at:
        events.append(TimelineEvent(
            timestamp=claim.payout_initiated_at.isoformat(),
            event="payout_initiated",
            detail=f"₹{claim.capped_payout_paise / 100:.0f}",
        ))

    if claim.paid_at:
        events.append(TimelineEvent(
            timestamp=claim.paid_at.isoformat(),
            event="payout_sent",
            detail="UPI confirmed",
        ))

    # Rejection reason
    if claim.status == "rejected" and claim.fraud_reason:
        events.append(TimelineEvent(
            timestamp=(claim.fraud_checked_at or claim.created_at).isoformat(),
            event="claim_rejected",
            detail=claim.fraud_reason,
        ))

    # Sort by timestamp
    events.sort(key=lambda e: e.timestamp)

    return ClaimTimelineResponse(events=events)
