"""
Synthetic Rider Generator — Creates 200 demo riders across 10 Bengaluru zones.
Used for Phase 2 load testing and multi-rider demo scenarios.

Distribution: ~20 riders per zone
Platforms: swiggy 45%, zomato 35%, dunzo 20%
Earnings: Normally distributed around ₹1100/day (σ = ₹200)
Work hours: Mix of morning (8-18), full day (10-22), evening (14-23)
"""

import json
import random
import uuid
from pathlib import Path

OUTPUT_PATH = Path(__file__).parent / "synthetic_riders.json"

ZONES = [
    "BTM_LAYOUT", "KORAMANGALA", "INDIRANAGAR", "WHITEFIELD", "JAYANAGAR",
    "MARATHAHALLI", "HSR_LAYOUT", "ELECTRONIC_CITY", "HEBBAL", "JP_NAGAR",
]

PLATFORMS = ["swiggy"] * 45 + ["zomato"] * 35 + ["dunzo"] * 20

SHIFT_PATTERNS = [
    (8, 18, 6),   # Morning shift (8am – 6pm, 6 days/week)
    (10, 22, 6),  # Full day (10am – 10pm)
    (14, 23, 5),  # Evening shift (2pm – 11pm, 5 days)
    (9, 21, 7),   # All week
    (11, 20, 6),  # Mid-day
]

FIRST_NAMES = [
    "Ravi", "Suresh", "Prakash", "Venkatesh", "Manoj", "Anil", "Ganesh",
    "Rajesh", "Kumar", "Naveen", "Deepak", "Vijay", "Santosh", "Ramesh",
    "Srinivas", "Harish", "Karthik", "Ashok", "Mohan", "Dinesh",
]

LAST_NAMES = [
    "Kumar", "Reddy", "Gowda", "Naik", "Sharma", "Rao", "Patil",
    "Shetty", "Das", "Babu", "Prasad", "Murthy", "Hegde", "Nair",
]


def generate():
    """Generate 200 synthetic rider profiles."""
    random.seed(42)
    riders = []

    for i in range(200):
        zone = ZONES[i % len(ZONES)]
        platform = random.choice(PLATFORMS)
        shift = random.choice(SHIFT_PATTERNS)
        daily_earning = max(50000, min(200000, int(random.gauss(110000, 20000))))
        name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"

        rider = {
            "id": str(uuid.uuid4()),
            "phone": f"+91{random.randint(6000000000, 9999999999)}",
            "name": name,
            "zone_id": zone,
            "platform": platform,
            "work_hours_start": shift[0],
            "work_hours_end": shift[1],
            "work_days_per_week": shift[2],
            "self_reported_daily_earning_paise": daily_earning,
            "firebase_uid": f"synthetic_uid_{i:04d}",
            "upi_vpa": f"{name.split()[0].lower()}{random.randint(100,999)}@upi",
        }
        riders.append(rider)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump({"riders": riders, "count": len(riders)}, f, indent=2)

    print(f"Generated {len(riders)} synthetic riders → {OUTPUT_PATH}")

    # Distribution summary
    from collections import Counter
    zone_dist = Counter(r["zone_id"] for r in riders)
    platform_dist = Counter(r["platform"] for r in riders)
    print(f"Zone distribution: {dict(zone_dist)}")
    print(f"Platform distribution: {dict(platform_dist)}")


if __name__ == "__main__":
    generate()
