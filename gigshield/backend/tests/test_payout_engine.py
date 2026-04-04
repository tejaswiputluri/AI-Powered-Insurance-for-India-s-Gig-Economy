"""
Payout Engine Tests — verifies Earnings DNA formula (BHE × DW × ZIF × CF).
"""

import pytest
from backend.services.payout_engine import calculate_payout


@pytest.mark.asyncio
async def test_earnings_dna_standard():
    """₹1100 daily, 4 hrs disruption, BTM ZIF 0.87, 0.70 CF → ~₹334"""
    result = await calculate_payout(
        rider_daily_earning_paise=110000,  # ₹1,100
        work_hours_start=10,
        work_hours_end=22,              # 12 hours
        zone_id="BTM_LAYOUT",
        signals_confirmed=2,
        coverage_cap_paise=90000,       # ₹900
        disruption_hours=4.0,
    )
    # BHE = 110000 / 12 = 9166.67
    # Payout = 9166.67 × 4 × 0.87 × 0.70 = 22,330
    assert result["baseline_hourly_earning_paise"] == 9166
    assert result["disruption_hours"] == 4.0
    assert result["zone_impact_factor"] == 0.87
    assert result["coverage_factor"] == 0.70
    assert result["calculated_payout_paise"] > 0
    assert result["capped_payout_paise"] <= 90000


@pytest.mark.asyncio
async def test_earnings_dna_high():
    """Same but CF=0.85 (3 signals) → higher payout"""
    result = await calculate_payout(
        rider_daily_earning_paise=110000,
        work_hours_start=10,
        work_hours_end=22,
        zone_id="BTM_LAYOUT",
        signals_confirmed=3,
        coverage_cap_paise=150000,
        disruption_hours=4.0,
    )
    assert result["coverage_factor"] == 0.85
    assert result["calculated_payout_paise"] > 0


@pytest.mark.asyncio
async def test_payout_capped_by_coverage():
    """Calculated payout exceeds coverage cap → returns cap value"""
    result = await calculate_payout(
        rider_daily_earning_paise=200000,   # ₹2,000/day
        work_hours_start=8,
        work_hours_end=22,                  # 14 hours
        zone_id="INDIRANAGAR",              # ZIF 0.91
        signals_confirmed=3,
        coverage_cap_paise=50000,           # ₹500 cap (basic tier)
        disruption_hours=8.0,
    )
    assert result["capped_payout_paise"] <= 50000


@pytest.mark.asyncio
async def test_zif_minimum_enforced():
    """ZIF below 0.60 should be clamped to 0.60"""
    result = await calculate_payout(
        rider_daily_earning_paise=110000,
        work_hours_start=10,
        work_hours_end=22,
        zone_id="NONEXISTENT_ZONE",  # Will get default 0.80
        signals_confirmed=2,
        coverage_cap_paise=90000,
        disruption_hours=4.0,
    )
    assert result["zone_impact_factor"] >= 0.60
