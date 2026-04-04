"""
Mock Order Volume Generator — Generates realistic order volume patterns
for 10 Bengaluru zones. Used by order_volume_service.py as reference data.

Peak hours: 12-14 (lunch), 19-22 (dinner)
Weekend boost: Saturday +20%, Sunday +30%
Weather penalty: Heavy rain -40%, High AQI -25%
"""

import json
import random
from pathlib import Path

OUTPUT_PATH = Path(__file__).parent / "mock_order_volumes.json"

ZONES = [
    "BTM_LAYOUT", "KORAMANGALA", "INDIRANAGAR", "WHITEFIELD", "JAYANAGAR",
    "MARATHAHALLI", "HSR_LAYOUT", "ELECTRONIC_CITY", "HEBBAL", "JP_NAGAR",
]

# Orders per hour baseline by zone (popularity ranking)
ZONE_BASELINES = {
    "KORAMANGALA": 180, "BTM_LAYOUT": 160, "INDIRANAGAR": 170,
    "HSR_LAYOUT": 150, "JAYANAGAR": 140, "MARATHAHALLI": 130,
    "WHITEFIELD": 120, "JP_NAGAR": 110, "HEBBAL": 100,
    "ELECTRONIC_CITY": 90,
}

HOUR_MULTIPLIERS = {
    0: 0.05, 1: 0.02, 2: 0.01, 3: 0.01, 4: 0.02, 5: 0.05,
    6: 0.15, 7: 0.25, 8: 0.40, 9: 0.55, 10: 0.70, 11: 0.85,
    12: 1.00, 13: 0.95, 14: 0.70, 15: 0.50, 16: 0.45, 17: 0.55,
    18: 0.75, 19: 0.95, 20: 1.00, 21: 0.90, 22: 0.60, 23: 0.30,
}


def generate():
    """Generate mock order volume reference data."""
    random.seed(42)
    data = {}

    for zone in ZONES:
        baseline = ZONE_BASELINES[zone]
        hourly_pattern = {}

        for hour, mult in HOUR_MULTIPLIERS.items():
            volume = int(baseline * mult * random.uniform(0.9, 1.1))
            hourly_pattern[str(hour)] = volume

        data[zone] = {
            "baseline_per_hour": baseline,
            "hourly_pattern": hourly_pattern,
            "weekend_boost": {"saturday": 1.20, "sunday": 1.30},
            "weather_penalty": {
                "heavy_rain": 0.60,
                "light_rain": 0.85,
                "high_aqi": 0.75,
            },
        }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Generated order volumes for {len(data)} zones → {OUTPUT_PATH}")


if __name__ == "__main__":
    generate()
