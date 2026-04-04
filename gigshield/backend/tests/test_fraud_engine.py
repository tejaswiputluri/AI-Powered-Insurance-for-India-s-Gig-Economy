"""
Fraud Engine Tests — verifies 4-layer pipeline and confidence score routing.
"""

import pytest
import uuid
from datetime import datetime, timezone
from backend.services.fraud_engine import (
    check_l1_gps, check_l2_weather, check_l3_earnings,
    check_l4_cluster, route_claim, run_fraud_pipeline,
)


@pytest.mark.asyncio
async def test_l1_gps_pass():
    """Rider GPS within 5km of zone → 30 points"""
    # skip case (no GPS data) → benefit of doubt → 30
    score, result, detail = await check_l1_gps(
        rider_id=uuid.uuid4(),
        zone_id="BTM_LAYOUT",
        zone_lat=12.9165,
        zone_lon=77.6101,
    )
    assert score == 30
    assert result == "skip"


@pytest.mark.asyncio
async def test_l1_gps_fail_demo():
    """Demo override: GPS 8km from zone → 0 points"""
    score, result, detail = await check_l1_gps(
        rider_id=uuid.uuid4(),
        zone_id="BTM_LAYOUT",
        zone_lat=12.9165,
        zone_lon=77.6101,
        demo_override=True,
        demo_distance_km=8.2,
    )
    assert score == 0
    assert result == "fail"
    assert "LOCATION_MISMATCH" in detail


@pytest.mark.asyncio
async def test_l2_weather_pass():
    """Rain above threshold → 30 points"""
    score, result, detail = await check_l2_weather(
        zone_id="BTM_LAYOUT",
        rainfall_mm_hr=14.2,
        aqi_value=85,
    )
    assert score == 30
    assert result == "pass"


@pytest.mark.asyncio
async def test_l2_weather_fail():
    """Both below threshold → 0 points"""
    score, result, detail = await check_l2_weather(
        zone_id="BTM_LAYOUT",
        rainfall_mm_hr=3.0,
        aqi_value=100,
    )
    assert score == 0
    assert result == "fail"


@pytest.mark.asyncio
async def test_l3_earnings_pass():
    """Phase 1: always passes (benefit of doubt)"""
    score, result, detail = await check_l3_earnings(rider_id=uuid.uuid4())
    assert score == 25
    assert result == "pass"


def test_confidence_score_auto_approve():
    """Score ≥ 85 → auto_approved"""
    assert route_claim(100) == "auto_approved"
    assert route_claim(85) == "auto_approved"


def test_confidence_score_flagged():
    """Score 60-84 → flagged"""
    assert route_claim(75) == "flagged"
    assert route_claim(60) == "flagged"


def test_confidence_score_hold():
    """Score 35-59 → held"""
    assert route_claim(50) == "held"
    assert route_claim(35) == "held"


def test_confidence_score_reject():
    """Score < 35 → rejected (RULE-17)"""
    assert route_claim(34) == "rejected"
    assert route_claim(0) == "rejected"


@pytest.mark.asyncio
async def test_full_pipeline_pass():
    """All layers pass → score 100 → auto_approved"""
    result = await run_fraud_pipeline(
        rider_id=uuid.uuid4(),
        zone_id="BTM_LAYOUT",
        zone_lat=12.9165,
        zone_lon=77.6101,
        rainfall_mm_hr=14.2,
        aqi_value=218,
        detected_at=datetime.now(timezone.utc),
        msc_confirmed=True,
    )
    assert result["total_score"] == 100
    assert result["decision"] == "auto_approved"


@pytest.mark.asyncio
async def test_full_pipeline_gps_fail():
    """GPS fail + rest pass → score 70 → flagged"""
    result = await run_fraud_pipeline(
        rider_id=uuid.uuid4(),
        zone_id="BTM_LAYOUT",
        zone_lat=12.9165,
        zone_lon=77.6101,
        rainfall_mm_hr=14.2,
        aqi_value=218,
        detected_at=datetime.now(timezone.utc),
        msc_confirmed=True,
        demo_override=True,
        demo_distance_km=8.0,
    )
    assert result["l1_gps_score"] == 0
    assert result["total_score"] == 70
    assert result["decision"] == "flagged"
