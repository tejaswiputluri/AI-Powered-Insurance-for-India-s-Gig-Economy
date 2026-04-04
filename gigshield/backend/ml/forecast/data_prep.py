"""
Synthetic Weather Generator — 3 years (2023-2025) of daily weather data
for all 10 Bengaluru zones. Saves to data/synthetic_weather.csv.

Season rules:
  - Monsoon (Jun-Sep): P(rainfall>8mm) = 0.45, mean_aqi = 85
  - Summer (Mar-May): P(rainfall>8mm) = 0.05, mean_aqi = 120
  - Winter (Nov-Feb): P(rainfall>8mm) = 0.10, mean_aqi = 95
  - Diwali week (Oct/Nov): mean_aqi += 80
  - Zones near lakes (Hebbal, HSR): +0.1 rainfall probability
  - Festival calendar: Diwali, Kannada Rajyotsava, IPL final weeks
"""

import numpy as np
import pandas as pd
from datetime import date, timedelta
from pathlib import Path

OUTPUT_PATH = Path(__file__).parent.parent.parent.parent / "data" / "synthetic_weather.csv"

ZONES = [
    "BTM_LAYOUT", "KORAMANGALA", "INDIRANAGAR", "WHITEFIELD", "JAYANAGAR",
    "MARATHAHALLI", "HSR_LAYOUT", "ELECTRONIC_CITY", "HEBBAL", "JP_NAGAR",
]

LAKE_ZONES = {"HEBBAL", "HSR_LAYOUT"}

FESTIVAL_DATES = {
    # Approximate Diwali weeks
    (2023, 11, 12): "diwali", (2024, 11, 1): "diwali", (2025, 10, 20): "diwali",
    # Kannada Rajyotsava
    (2023, 11, 1): "kannada_rajyotsava",
    (2024, 11, 1): "kannada_rajyotsava",
    (2025, 11, 1): "kannada_rajyotsava",
}


def get_season(month: int) -> str:
    if month in [6, 7, 8, 9]:
        return "monsoon"
    elif month in [3, 4, 5]:
        return "summer"
    else:
        return "winter"


def is_diwali_week(d: date) -> bool:
    for (y, m, day), fest in FESTIVAL_DATES.items():
        if fest == "diwali":
            diwali_date = date(y, m, day)
            if abs((d - diwali_date).days) <= 3:
                return True
    return False


def is_festival(d: date) -> bool:
    for (y, m, day) in FESTIVAL_DATES:
        fest_date = date(y, m, day)
        if abs((d - fest_date).days) <= 1:
            return True
    return False


def generate():
    """Generate 3 years of synthetic weather data for all zones."""
    np.random.seed(42)

    start = date(2023, 1, 1)
    end = date(2025, 12, 31)
    days = (end - start).days + 1

    records = []

    for zone in ZONES:
        lake_bonus = 0.10 if zone in LAKE_ZONES else 0.0

        for i in range(days):
            d = start + timedelta(days=i)
            season = get_season(d.month)

            # Rainfall
            if season == "monsoon":
                rain_prob = 0.45 + lake_bonus
                base_aqi = 85
            elif season == "summer":
                rain_prob = 0.05 + lake_bonus
                base_aqi = 120
            else:
                rain_prob = 0.10 + lake_bonus
                base_aqi = 95

            # Generate rainfall
            has_heavy_rain = np.random.random() < rain_prob
            if has_heavy_rain:
                max_rainfall = np.random.uniform(8.0, 35.0)
            else:
                max_rainfall = np.random.uniform(0.0, 7.5)

            # AQI
            mean_aqi = base_aqi + np.random.normal(0, 15)
            if is_diwali_week(d):
                mean_aqi += 80
            mean_aqi = max(20, min(400, mean_aqi))

            # Order drop
            order_drop = 0.0
            if max_rainfall >= 8.0:
                order_drop = np.random.uniform(0.25, 0.60)
            elif mean_aqi >= 200:
                order_drop = np.random.uniform(0.15, 0.40)
            else:
                order_drop = np.random.uniform(0.0, 0.15)

            # Disruption label (for training)
            disrupted = 1 if (max_rainfall >= 8.0 and order_drop >= 0.35) or \
                             (mean_aqi >= 200 and order_drop >= 0.35) else 0

            # Claims (synthetic)
            claim_count = np.random.poisson(disrupted * 3 + 0.5)

            records.append({
                "zone_id": zone,
                "date": d.isoformat(),
                "max_rainfall_mm": round(max_rainfall, 1),
                "mean_aqi": round(mean_aqi),
                "order_drop_pct": round(order_drop, 4),
                "day_of_week": d.weekday(),
                "month": d.month,
                "is_festival": int(is_festival(d)),
                "historical_claim_count": claim_count,
                "disrupted": disrupted,
            })

    df = pd.DataFrame(records)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Generated {len(df)} records → {OUTPUT_PATH}")
    print(f"Zones: {len(ZONES)}, Days: {days}, Records per zone: {days}")


if __name__ == "__main__":
    generate()
