"""
Forecast Service — wraps the LSTM forecast ML microservice.
RULE-10: ML models called async via HTTP, never imported directly.
"""

import logging
from typing import Optional
import httpx
from backend.config.settings import settings

logger = logging.getLogger(__name__)


async def get_zone_forecast(zone_id: str) -> dict:
    """
    Get 7-day disruption forecast for a zone from LSTM service.
    Falls back to static estimates if ML service unavailable.
    """
    # Try ML service
    if not settings.DEMO_MODE:
        try:
            async with httpx.AsyncClient(timeout=settings.ML_TIMEOUT_SECONDS) as client:
                resp = await client.post(
                    f"{settings.ML_FORECAST_URL}/forecast",
                    json={"zone_id": zone_id},
                )
                resp.raise_for_status()
                return resp.json()
        except Exception as e:
            logger.warning(f"LSTM forecast service unavailable: {e}")

    # Fallback: static risk estimates
    return _static_forecast(zone_id)


def _static_forecast(zone_id: str) -> dict:
    """Static forecast fallback based on zone risk profiles."""
    from datetime import date, timedelta

    risk_profiles = {
        'BTM_LAYOUT': 0.73, 'KORAMANGALA': 0.55, 'INDIRANAGAR': 0.68,
        'WHITEFIELD': 0.42, 'JAYANAGAR': 0.50, 'MARATHAHALLI': 0.38,
        'HSR_LAYOUT': 0.65, 'ELECTRONIC_CITY': 0.30, 'HEBBAL': 0.48, 'JP_NAGAR': 0.45,
    }

    base_prob = risk_profiles.get(zone_id, 0.40)
    today = date.today()

    forecasts = []
    for i in range(7):
        day = today + timedelta(days=i)
        # Slightly vary probability
        prob = round(min(1.0, max(0.0, base_prob + (i * 0.02 - 0.06))), 2)
        risk_level = "high" if prob >= 0.60 else ("medium" if prob >= 0.35 else "low")
        forecasts.append({
            "date": day.isoformat(),
            "disruption_probability": prob,
            "risk_level": risk_level,
        })

    return {
        "zone_id": zone_id,
        "forecasts": forecasts,
    }
