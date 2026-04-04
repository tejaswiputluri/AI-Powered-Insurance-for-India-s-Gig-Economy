"""
Weather Service — Open-Meteo API wrapper + Redis cache + resilience fallback.
RULE-05: Never call external API without try/except and cache fallback.
"""

import json
import logging
from typing import Optional
import httpx
from backend.config.settings import settings
from backend.config.constants import (
    WEATHER_CACHE_TTL,
    DEMO_FALLBACK_WEATHER,
)
from backend.cache.redis_client import (
    cache_get_json, cache_set_json,
    cache_get_stale, cache_set_with_stale,
)

logger = logging.getLogger(__name__)

# Open-Meteo endpoints (free, no API key)
OPEN_METEO_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
OPEN_METEO_AQI_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"

# HTTP client timeout
API_TIMEOUT = 5.0
API_RETRIES = 1


async def _log_resilience_fallback(zone_id: str, signal_type: str, source: str):
    """
    Log all fallbacks to audit_log with actor='resilience_layer'.
    Spec §15: "Log all fallbacks to audit_log with actor='resilience_layer'"
    """
    try:
        import uuid
        from backend.db.database import async_session_factory
        from backend.models.db.audit_log import AuditLog

        async with async_session_factory() as session:
            audit = AuditLog(
                entity_type="resilience",
                entity_id=uuid.uuid5(uuid.NAMESPACE_DNS, f"resilience.{zone_id}"),
                action=f"{signal_type}_fallback_to_{source}",
                actor="resilience_layer",
                detail={
                    "zone_id": zone_id,
                    "signal_type": signal_type,
                    "fallback_source": source,
                },
            )
            session.add(audit)
            await session.commit()
    except Exception as e:
        logger.debug(f"Failed to log resilience fallback: {e}")


async def get_rainfall(lat: float, lon: float, zone_id: str = "") -> dict:
    """
    Get current rainfall for coordinates.
    Returns: {'value': float, 'source': 'live'|'cache'|'stale'|'fallback'}

    Resilience order (RULE-05):
      1. Redis cache (TTL check)
      2. Live API call (5s timeout, 1 retry)
      3. Stale cache (ignore TTL)
      4. Demo fallback values
    """
    cache_key = f"weather:{zone_id}:rain"

    # 1. Try fresh cache
    cached = await cache_get_json(cache_key)
    if cached is not None:
        return {"value": cached["rainfall_mm_hr"], "source": "cache"}

    # 2. Try live API
    if not settings.DEMO_MODE:
        for attempt in range(API_RETRIES + 1):
            try:
                async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
                    resp = await client.get(
                        OPEN_METEO_FORECAST_URL,
                        params={
                            "latitude": lat,
                            "longitude": lon,
                            "current": "precipitation,rain",
                            "timezone": "Asia/Kolkata",
                        },
                    )
                    resp.raise_for_status()
                    data = resp.json()
                    rainfall = data.get("current", {}).get("rain", 0.0)

                    # Cache the result
                    await cache_set_with_stale(
                        cache_key,
                        json.dumps({"rainfall_mm_hr": rainfall}),
                        ttl=WEATHER_CACHE_TTL,
                    )
                    return {"value": rainfall, "source": "live"}

            except Exception as e:
                logger.warning(f"Open-Meteo rainfall API attempt {attempt+1} failed: {e}")
                if attempt < API_RETRIES:
                    import asyncio
                    await asyncio.sleep(1)

    # 3. Try stale cache
    stale = await cache_get_stale(cache_key)
    if stale:
        try:
            stale_data = json.loads(stale)
            logger.info(f"Using stale cache for rainfall zone={zone_id}")
            await _log_resilience_fallback(zone_id, "rainfall", "stale_cache")
            return {"value": stale_data["rainfall_mm_hr"], "source": "stale"}
        except (json.JSONDecodeError, KeyError):
            pass

    # 4. Demo fallback
    fallback = DEMO_FALLBACK_WEATHER.get(zone_id, {"rainfall_mm_hr": 0.0})
    logger.info(f"Using fallback values for rainfall zone={zone_id}")
    await _log_resilience_fallback(zone_id, "rainfall", "demo_fallback")
    return {"value": fallback["rainfall_mm_hr"], "source": "fallback"}


async def get_aqi(lat: float, lon: float, zone_id: str = "") -> dict:
    """
    Get current AQI for coordinates.
    Returns: {'value': int, 'source': 'live'|'cache'|'stale'|'fallback'}
    """
    cache_key = f"weather:{zone_id}:aqi"

    # 1. Try fresh cache
    cached = await cache_get_json(cache_key)
    if cached is not None:
        return {"value": cached["aqi_value"], "source": "cache"}

    # 2. Try live API
    if not settings.DEMO_MODE:
        for attempt in range(API_RETRIES + 1):
            try:
                async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
                    resp = await client.get(
                        OPEN_METEO_AQI_URL,
                        params={
                            "latitude": lat,
                            "longitude": lon,
                            "current": "european_aqi",
                            "timezone": "Asia/Kolkata",
                        },
                    )
                    resp.raise_for_status()
                    data = resp.json()
                    aqi = int(data.get("current", {}).get("european_aqi", 0))

                    await cache_set_with_stale(
                        cache_key,
                        json.dumps({"aqi_value": aqi}),
                        ttl=WEATHER_CACHE_TTL,
                    )
                    return {"value": aqi, "source": "live"}

            except Exception as e:
                logger.warning(f"Open-Meteo AQI API attempt {attempt+1} failed: {e}")
                if attempt < API_RETRIES:
                    import asyncio
                    await asyncio.sleep(1)

    # 3. Stale cache
    stale = await cache_get_stale(cache_key)
    if stale:
        try:
            stale_data = json.loads(stale)
            return {"value": stale_data["aqi_value"], "source": "stale"}
        except (json.JSONDecodeError, KeyError):
            pass

    # 4. Demo fallback
    fallback = DEMO_FALLBACK_WEATHER.get(zone_id, {"aqi_value": 85})
    return {"value": fallback["aqi_value"], "source": "fallback"}
