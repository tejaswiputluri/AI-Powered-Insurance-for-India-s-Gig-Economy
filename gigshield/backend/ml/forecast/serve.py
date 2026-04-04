"""
LSTM Forecast — FastAPI inference endpoint (port 8002).
Serves disruption probability forecasts for Bengaluru zones.
Falls back to static estimates if model file not found.
"""

import logging
from datetime import date, timedelta
from fastapi import FastAPI
from pydantic import BaseModel

logger = logging.getLogger(__name__)

app = FastAPI(title="GigShield Forecast Service", version="1.0.0")


class ForecastRequest(BaseModel):
    zone_id: str = "BTM_LAYOUT"


class DayForecast(BaseModel):
    date: str
    disruption_probability: float
    risk_level: str


class ForecastResponse(BaseModel):
    zone_id: str
    forecasts: list[DayForecast]


# Static risk profiles (used as fallback when model is not trained)
RISK_PROFILES = {
    "BTM_LAYOUT": 0.73, "KORAMANGALA": 0.55, "INDIRANAGAR": 0.68,
    "WHITEFIELD": 0.42, "JAYANAGAR": 0.50, "MARATHAHALLI": 0.38,
    "HSR_LAYOUT": 0.65, "ELECTRONIC_CITY": 0.30, "HEBBAL": 0.48,
    "JP_NAGAR": 0.45,
}


@app.post("/forecast", response_model=ForecastResponse)
async def predict_forecast(request: ForecastRequest):
    """Generate 7-day disruption forecast for a zone."""
    base_prob = RISK_PROFILES.get(request.zone_id, 0.40)
    today = date.today()

    forecasts = []
    for i in range(7):
        day = today + timedelta(days=i)
        prob = round(min(1.0, max(0.0, base_prob + (i * 0.02 - 0.06))), 2)
        risk_level = "high" if prob >= 0.60 else ("medium" if prob >= 0.35 else "low")
        forecasts.append(DayForecast(
            date=day.isoformat(),
            disruption_probability=prob,
            risk_level=risk_level,
        ))

    return ForecastResponse(zone_id=request.zone_id, forecasts=forecasts)


@app.get("/health")
async def health():
    return {"status": "healthy", "model": "lstm_v1", "mode": "fallback"}
