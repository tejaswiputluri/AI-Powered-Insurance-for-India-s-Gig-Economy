"""
Payout Engine — Earnings DNA formula.
Payout = BHE × DW × ZIF × CF, capped at policy coverage cap.
All money in INTEGER PAISE (RULE-03).
"""

import json
import logging
from pathlib import Path
from backend.config.constants import (
    MAX_DISRUPTION_WINDOW_HOURS,
    ZIF_MINIMUM,
    ZIF_MAXIMUM,
    COVERAGE_FACTOR_STANDARD,
    COVERAGE_FACTOR_HIGH,
    MAX_PAYOUT_PAISE,
)

logger = logging.getLogger(__name__)

# Load zones data
_zones_data = None


def _load_zones() -> dict:
    """Load zone definitions from zones.json."""
    global _zones_data
    if _zones_data is None:
        zones_path = Path(__file__).parent.parent.parent / "data" / "zones.json"
        with open(zones_path) as f:
            data = json.load(f)
        _zones_data = {z["id"]: z for z in data["zones"]}
    return _zones_data


def get_zone(zone_id: str) -> dict:
    """Get zone definition by ID."""
    zones = _load_zones()
    return zones.get(zone_id, {"base_zif": 0.80})


async def calculate_payout(
    rider_daily_earning_paise: int,
    work_hours_start: int,
    work_hours_end: int,
    zone_id: str,
    signals_confirmed: int,
    coverage_cap_paise: int,
    disruption_hours: float = 4.0,
) -> dict:
    """
    Calculate payout using Earnings DNA formula.

    Payout = BHE × DW × ZIF × CF

    BHE  = Baseline Hourly Earning (paise) = daily_earning / work_hours_per_day
    DW   = Disruption Window (hours), capped at MAX_DISRUPTION_WINDOW_HOURS
    ZIF  = Zone Impact Factor, bounded [0.60, 1.00]
    CF   = Coverage Factor: 0.70 (2 signals) or 0.85 (3+ signals)

    Returns dict with all intermediate values for transparency.
    """
    # BHE — Baseline Hourly Earning
    work_hours_per_day = work_hours_end - work_hours_start
    if work_hours_per_day <= 0:
        work_hours_per_day = 8  # fallback
    bhe = rider_daily_earning_paise / work_hours_per_day

    # DW — Disruption Window
    dw = min(disruption_hours, MAX_DISRUPTION_WINDOW_HOURS)

    # ZIF — Zone Impact Factor
    zone = get_zone(zone_id)
    raw_zif = zone.get("base_zif", 0.80)
    zif = max(ZIF_MINIMUM, min(ZIF_MAXIMUM, raw_zif))

    # CF — Coverage Factor
    cf = COVERAGE_FACTOR_HIGH if signals_confirmed >= 3 else COVERAGE_FACTOR_STANDARD

    # Calculate
    calculated = int(bhe * dw * zif * cf)
    capped = min(calculated, coverage_cap_paise, MAX_PAYOUT_PAISE)

    result = {
        "baseline_hourly_earning_paise": int(bhe),
        "disruption_hours": dw,
        "zone_impact_factor": zif,
        "coverage_factor": cf,
        "calculated_payout_paise": calculated,
        "capped_payout_paise": capped,
    }

    logger.info(
        f"Payout calculated: BHE={int(bhe)} × DW={dw} × ZIF={zif} × CF={cf} "
        f"= {calculated} paise (capped: {capped})"
    )

    return result
