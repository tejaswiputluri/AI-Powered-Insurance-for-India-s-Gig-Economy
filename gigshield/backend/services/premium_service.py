"""
Premium Service — calls ML FT-Transformer microservice for premium pricing.
RULE-10: ML models are never called synchronously. Always async via HTTP.
"""

import logging
from typing import Optional
import httpx
from backend.config.settings import settings
from backend.config.constants import (
    MIN_PREMIUM_PAISE,
    MAX_PREMIUM_PAISE,
    POLICY_TIERS,
    DAILY_EARNING_BUCKETS,
)

logger = logging.getLogger(__name__)


def _get_earning_bucket(daily_earning_rupees: int) -> int:
    """Convert daily earning to bucket index."""
    for bucket, (low, high) in DAILY_EARNING_BUCKETS.items():
        if low <= daily_earning_rupees < high:
            return bucket
    return 4  # > ₹1600


def _get_season_multiplier() -> float:
    """Get current season multiplier for premium calc."""
    from datetime import datetime
    month = datetime.now().month
    if month in [6, 7, 8, 9]:  # Monsoon
        return 1.15
    elif month in [3, 4, 5]:   # Summer
        return 0.90
    else:
        return 1.00


async def calculate_premium(rider_data: dict) -> dict:
    """
    Calculate personalized weekly premium using FT-Transformer ML service.

    Falls back to rule-based calculation if ML service is unavailable.

    Returns: {
        'premium_paise': int,
        'attention_weights': dict (XAI factors)
    }
    """
    zone_data = rider_data.get("zone_data", {})
    daily_earning_rupees = rider_data.get("self_reported_daily_earning_paise", 110000) // 100
    work_hours = rider_data.get("work_hours_end", 22) - rider_data.get("work_hours_start", 10)

    ml_input = {
        "zone_id": rider_data.get("zone_id", "BTM_LAYOUT"),
        "aqi_exposure_score": zone_data.get("aqi_exposure_score", 0.35),
        "work_hours_per_day": work_hours,
        "work_days_per_week": rider_data.get("work_days_per_week", 6),
        "season_multiplier": _get_season_multiplier(),
        "claim_history_count": 0,
        "daily_earning_bucket": _get_earning_bucket(daily_earning_rupees),
    }

    # Try ML service first (RULE-10: async via HTTP)
    if not settings.DEMO_MODE:
        try:
            async with httpx.AsyncClient(timeout=settings.ML_TIMEOUT_SECONDS) as client:
                resp = await client.post(
                    f"{settings.ML_PREMIUM_URL}/predict",
                    json=ml_input,
                )
                resp.raise_for_status()
                result = resp.json()
                return {
                    "premium_paise": max(MIN_PREMIUM_PAISE, min(MAX_PREMIUM_PAISE, result["premium_paise"])),
                    "attention_weights": result.get("attention_weights", {}),
                }
        except Exception as e:
            logger.warning(f"ML premium service unavailable, using fallback: {e}")

    # Fallback: rule-based premium calculation
    return _calculate_premium_fallback(ml_input)


def _calculate_premium_fallback(features: dict) -> dict:
    """
    Rule-based premium calculation — used when ML service is unavailable.
    Approximates the FT-Transformer output.
    """
    base_premium = 5000  # ₹50 base

    # Zone risk adjustment
    zone_risk_scores = {
        'BTM_LAYOUT': 0.87, 'KORAMANGALA': 0.82, 'INDIRANAGAR': 0.91,
        'WHITEFIELD': 0.79, 'JAYANAGAR': 0.85, 'MARATHAHALLI': 0.76,
        'HSR_LAYOUT': 0.88, 'ELECTRONIC_CITY': 0.72, 'HEBBAL': 0.80, 'JP_NAGAR': 0.83,
    }
    zone_risk = zone_risk_scores.get(features.get("zone_id", ""), 0.80)

    # Premium formula
    premium = base_premium * (
        0.3 * zone_risk +                                  # zone risk
        0.2 * features.get("aqi_exposure_score", 0.35) +   # AQI exposure
        0.2 * features.get("season_multiplier", 1.0) +     # season
        0.15 * (features.get("work_hours_per_day", 12) / 16) +  # work hours
        0.15 * (features.get("work_days_per_week", 6) / 7)      # work days
    )

    # Clamp to valid range
    premium_paise = max(MIN_PREMIUM_PAISE, min(MAX_PREMIUM_PAISE, int(premium)))

    # Simulated attention weights (XAI factors)
    attention_weights = {
        "aqi_zone_history": round(0.30 + zone_risk * 0.05, 2),
        "monsoon_season": round(0.20 + (features.get("season_multiplier", 1.0) - 0.85) * 0.5, 2),
        "zone_risk_score": round(0.25 - zone_risk * 0.05, 2),
        "claim_history": round(0.15 + features.get("claim_history_count", 0) * 0.02, 2),
    }

    # Normalize weights to sum to 1.0
    total = sum(attention_weights.values())
    if total > 0:
        attention_weights = {k: round(v / total, 2) for k, v in attention_weights.items()}

    return {
        "premium_paise": premium_paise,
        "attention_weights": attention_weights,
    }


def get_tier_options(base_premium_paise: int) -> list[dict]:
    """Generate policy tier options based on rider's base premium."""
    options = []
    for tier_key, tier in POLICY_TIERS.items():
        tier_premium = max(
            MIN_PREMIUM_PAISE,
            min(MAX_PREMIUM_PAISE, int(base_premium_paise * tier["premium_multiplier"]))
        )
        options.append({
            "tier": tier_key,
            "name": tier["name"],
            "weekly_premium_paise": tier_premium,
            "coverage_cap_paise": tier["coverage_cap_paise"],
            "msc_threshold": tier["msc_threshold"],
            "coverage_factor": tier["coverage_factor"],
            "description": tier["description"],
            "recommended": tier.get("recommended", False),
        })
    return options
