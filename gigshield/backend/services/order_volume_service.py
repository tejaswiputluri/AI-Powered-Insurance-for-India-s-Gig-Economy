"""
Order Volume Service — Mock engine simulating Zomato/Swiggy order volumes.
Generates realistic order volumes with time-of-day, day-of-week, weather correlation.
"""

import json
import random
import logging
from datetime import datetime, timezone
from backend.config.settings import settings
from backend.config.constants import (
    TIME_OF_DAY_MULTIPLIERS,
    DAY_OF_WEEK_MULTIPLIERS,
    ZONE_ORDER_BASELINES,
    WEATHER_ORDER_MULTIPLIERS,
    ORDER_VOLUME_CACHE_TTL,
)
from backend.cache.redis_client import cache_get_json, cache_set_json

logger = logging.getLogger(__name__)


def _get_time_multiplier(hour: int) -> float:
    """Get order volume multiplier for the current hour."""
    for (start, end), mult in TIME_OF_DAY_MULTIPLIERS.items():
        if start <= hour < end:
            return mult
    return 0.30  # fallback for late night


def _get_day_multiplier(weekday: int) -> float:
    """Get order volume multiplier for the day of week (0=Monday)."""
    return DAY_OF_WEEK_MULTIPLIERS.get(weekday, 0.90)


def _get_weather_multiplier(rainfall_mm_hr: float, aqi: int) -> float:
    """Get order volume multiplier based on weather conditions."""
    if rainfall_mm_hr >= 8.0:
        mult = WEATHER_ORDER_MULTIPLIERS['heavy_rain']
    elif rainfall_mm_hr >= 3.0:
        mult = WEATHER_ORDER_MULTIPLIERS['light_rain']
    else:
        mult = WEATHER_ORDER_MULTIPLIERS['no_rain']

    if aqi > 200:
        mult *= WEATHER_ORDER_MULTIPLIERS['high_aqi_factor']

    return mult


async def get_drop_pct(
    zone_id: str,
    rainfall_mm_hr: float = 0.0,
    aqi: int = 0,
) -> float:
    """
    Return simulated order drop percentage for zone.
    Uses Redis cache (30min TTL).

    Order drop pct = max(0, 1 - (current_volume / baseline_volume))
    """
    cache_key = f"order_volume:{zone_id}"

    # Try cache first
    cached = await cache_get_json(cache_key)
    if cached is not None:
        return cached["drop_pct"]

    # Calculate simulated order drop
    now = datetime.now(timezone.utc)
    # Convert UTC to IST (UTC+5:30) properly
    from datetime import timedelta
    ist_offset = timedelta(hours=5, minutes=30)
    ist_now = now + ist_offset
    hour = ist_now.hour
    weekday = ist_now.weekday()

    zone_baseline = ZONE_ORDER_BASELINES.get(zone_id, 1.0)
    time_mult = _get_time_multiplier(hour)
    day_mult = _get_day_multiplier(weekday)
    weather_mult = _get_weather_multiplier(rainfall_mm_hr, aqi)

    # Current volume as fraction of theoretical baseline
    current_ratio = time_mult * day_mult * weather_mult * zone_baseline

    # Add some noise (±10%)
    noise = random.uniform(-0.10, 0.10)
    current_ratio = max(0.05, current_ratio + noise)

    # Baseline is what the volume "should be" (without weather disruption)
    baseline_ratio = time_mult * day_mult * zone_baseline
    baseline_ratio = max(0.10, baseline_ratio)

    # Order drop percentage
    drop_pct = max(0.0, 1.0 - (current_ratio / baseline_ratio))
    drop_pct = round(min(1.0, drop_pct), 4)

    # Cache result
    await cache_set_json(cache_key, {"drop_pct": drop_pct}, ttl=ORDER_VOLUME_CACHE_TTL)

    logger.debug(
        f"Order volume zone={zone_id}: current_ratio={current_ratio:.2f}, "
        f"baseline={baseline_ratio:.2f}, drop={drop_pct:.2%}"
    )

    return drop_pct


async def get_mock_road_disruption(zone_id: str) -> float:
    """Mock road disruption percentage (tertiary signal)."""
    # Simple deterministic mock based on zone
    base_disruption = {
        'BTM_LAYOUT': 0.15, 'KORAMANGALA': 0.10, 'INDIRANAGAR': 0.08,
        'WHITEFIELD': 0.20, 'JAYANAGAR': 0.12, 'MARATHAHALLI': 0.25,
        'HSR_LAYOUT': 0.10, 'ELECTRONIC_CITY': 0.30, 'HEBBAL': 0.22, 'JP_NAGAR': 0.14,
    }
    base = base_disruption.get(zone_id, 0.15)
    return round(base + random.uniform(-0.05, 0.10), 4)


async def get_civic_alert(zone_id: str) -> bool:
    """Mock civic alert (tertiary signal). Always False in normal operation."""
    return False
