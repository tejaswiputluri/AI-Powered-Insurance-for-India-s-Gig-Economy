"""
Riders Router — /api/v1/riders endpoints.
Handles onboarding, profile, location matching, and UPI updates.
"""

import json
import logging
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.database import get_db
from backend.api.middleware import get_current_rider_id, create_access_token, DEMO_RIDER_UID
from backend.config.settings import settings
from backend.models.schemas.rider import (
    RiderOnboardRequest,
    RiderOnboardResponse,
    RiderProfileResponse,
    RiderUPIUpdate,
    XAIFactor,
    ZoneMatchResponse,
)
from backend.services.premium_service import calculate_premium, get_tier_options
from backend.services.payout_engine import get_zone

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/riders", tags=["riders"])

# Load zones data
_zones_list = None


def _load_zones_list():
    global _zones_list
    if _zones_list is None:
        zones_path = Path(__file__).parent.parent.parent.parent / "data" / "zones.json"
        with open(zones_path) as f:
            data = json.load(f)
        _zones_list = {z["id"]: z for z in data["zones"]}
    return _zones_list


@router.post("/onboard", response_model=RiderOnboardResponse)
async def onboard_rider(
    request: RiderOnboardRequest,
    db: AsyncSession = Depends(get_db),
    rider_id: UUID = Depends(get_current_rider_id),
):
    """
    Onboard a new rider — PRF data collection + ML premium calculation.
    Step 1: Validate all fields
    Step 2: Create rider record
    Step 3: Call premium_service.calculate_premium → FT-Transformer
    Step 4: Update rider with computed premium + XAI factors
    Step 5: Return result with tier options
    """
    from backend.models.db.rider import Rider
    from sqlalchemy import select

    try:
        logger.info(f"🔄 Onboarding rider {rider_id} with data: {request.dict()}")
        
        zones = _load_zones_list()

        # Validate zone
        if request.zone_id not in zones:
            error_msg = f"Zone '{request.zone_id}' not found. Valid zones: {list(zones.keys())}"
            logger.error(f"❌ {error_msg}")
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "INVALID_ZONE",
                    "message": error_msg,
                },
            )

        # Check if rider already exists
        result = await db.execute(select(Rider).where(Rider.id == rider_id))
        existing = result.scalar_one_or_none()

        zone_data = zones[request.zone_id]
        earning_paise = request.self_reported_daily_earning * 100  # RULE-03: convert to paise
        logger.info(f"✅ Zone validated. Earning: ₹{request.self_reported_daily_earning} = {earning_paise} paise")

        if existing:
            # Update existing rider with onboarding data
            logger.info(f"📝 Updating existing rider {rider_id}")
            existing.name = request.name
            existing.zone_id = request.zone_id
            existing.platform = request.platform
            existing.work_hours_start = request.work_hours_start
            existing.work_hours_end = request.work_hours_end
            existing.work_days_per_week = request.work_days_per_week
            existing.self_reported_daily_earning_paise = earning_paise
            rider = existing
        else:
            # Create new rider
            logger.info(f"✨ Creating new rider {rider_id}")
            rider = Rider(
                id=rider_id,
                phone=settings.DEMO_RIDER_PHONE if settings.DEMO_MODE else "+910000000000",
                name=request.name,
                firebase_uid=DEMO_RIDER_UID if settings.DEMO_MODE else f"uid_{rider_id}",
                zone_id=request.zone_id,
                platform=request.platform,
                work_hours_start=request.work_hours_start,
                work_hours_end=request.work_hours_end,
                work_days_per_week=request.work_days_per_week,
                self_reported_daily_earning_paise=earning_paise,
            )
            db.add(rider)

        # Calculate premium via ML service
        logger.info(f"🧠 Calculating premium for {request.zone_id}...")
        premium_result = await calculate_premium({
            "zone_id": request.zone_id,
            "zone_data": {"aqi_exposure_score": zone_data.get("base_zif", 0.80)},
            "work_hours_start": request.work_hours_start,
            "work_hours_end": request.work_hours_end,
            "work_days_per_week": request.work_days_per_week,
            "self_reported_daily_earning_paise": earning_paise,
        })
        logger.info(f"✅ Premium calculated: {premium_result['premium_paise']} paise")

        # Update rider with ML results
        rider.computed_weekly_premium_paise = premium_result["premium_paise"]
        rider.xai_factors = premium_result["attention_weights"]
        rider.prf_zone_risk_score = zone_data.get("base_zif", 0.80)
        rider.prf_aqi_exposure_score = zone_data.get("base_zif", 0.80) * 0.5
        rider.prf_season_multiplier = 1.0

        await db.commit()
        await db.refresh(rider)
        logger.info(f"✅ Rider saved to database")

        # Build XAI factors response
        xai_factors = []
        labels = {
            "aqi_zone_history": "AQI Zone History",
            "monsoon_season": "Monsoon Season",
            "zone_risk_score": "Zone Risk Score",
            "claim_history": "Claim History",
        }
        for factor, weight in premium_result["attention_weights"].items():
            xai_factors.append(XAIFactor(
                factor=factor,
                weight=weight,
                label=labels.get(factor, factor.replace("_", " ").title()),
            ))

        # Build tier options
        tier_options = get_tier_options(premium_result["premium_paise"])
        logger.info(f"✅ Tier options created: {len(tier_options)} tiers")

        response = RiderOnboardResponse(
            rider_id=rider.id,
            computed_premium_paise=premium_result["premium_paise"],
            xai_factors=xai_factors,
            tier_options=tier_options,
        )
        logger.info(f"✅ Onboarding complete for {rider_id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Onboarding failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "code": "ONBOARD_ERROR",
                "message": str(e),
            },
        )


@router.get("/me", response_model=RiderProfileResponse)
async def get_rider_profile(
    db: AsyncSession = Depends(get_db),
    rider_id: UUID = Depends(get_current_rider_id),
):
    """Get full rider profile including computed premium."""
    from backend.models.db.rider import Rider
    from sqlalchemy import select

    result = await db.execute(select(Rider).where(Rider.id == rider_id))
    rider = result.scalar_one_or_none()

    if not rider:
        raise HTTPException(status_code=404, detail={"code": "RIDER_NOT_FOUND"})

    return RiderProfileResponse.model_validate(rider)


@router.get("/me/location", response_model=ZoneMatchResponse)
async def match_zone(
    lat: float = Query(..., ge=10.0, le=20.0),
    lon: float = Query(..., ge=70.0, le=85.0),
    rider_id: UUID = Depends(get_current_rider_id),
):
    """
    Find nearest zone centroid within 5km radius.
    Used by fraud L1 GPS check.
    """
    from haversine import haversine, Unit

    zones = _load_zones_list()
    nearest_zone = None
    min_distance = float("inf")

    for zone_id, zone in zones.items():
        dist = haversine(
            (lat, lon), (zone["lat"], zone["lon"]),
            unit=Unit.KILOMETERS,
        )
        if dist < min_distance:
            min_distance = dist
            nearest_zone = zone

    if nearest_zone and min_distance <= 5.0:
        return ZoneMatchResponse(
            zone_id=nearest_zone["id"],
            zone_name=nearest_zone["name"],
            within_active_zone=True,
        )
    elif nearest_zone:
        return ZoneMatchResponse(
            zone_id=nearest_zone["id"],
            zone_name=nearest_zone["name"],
            within_active_zone=False,
        )
    else:
        raise HTTPException(
            status_code=404,
            detail={"code": "NO_ZONE_FOUND", "message": "No zone within range"},
        )


@router.patch("/me/upi")
async def update_upi(
    request: RiderUPIUpdate,
    db: AsyncSession = Depends(get_db),
    rider_id: UUID = Depends(get_current_rider_id),
):
    """Update rider's UPI VPA for payouts."""
    from backend.models.db.rider import Rider
    from sqlalchemy import select

    result = await db.execute(select(Rider).where(Rider.id == rider_id))
    rider = result.scalar_one_or_none()

    if not rider:
        raise HTTPException(status_code=404, detail={"code": "RIDER_NOT_FOUND"})

    rider.upi_vpa = request.upi_vpa
    await db.commit()

    return {"data": {"updated": True}, "error": None}
