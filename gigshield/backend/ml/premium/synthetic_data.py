"""
Synthetic Data Generator — generates 50,000 rider profiles for FT-Transformer training.
Output: data/synthetic_riders.csv
"""

import numpy as np
import pandas as pd
from pathlib import Path


# Zone risk profiles
ZONES = {
    'BTM_LAYOUT': {'risk': 0.87, 'aqi_exp': 0.42, 'weight': 0.15},
    'KORAMANGALA': {'risk': 0.82, 'aqi_exp': 0.35, 'weight': 0.18},
    'INDIRANAGAR': {'risk': 0.91, 'aqi_exp': 0.48, 'weight': 0.15},
    'WHITEFIELD': {'risk': 0.79, 'aqi_exp': 0.30, 'weight': 0.10},
    'JAYANAGAR': {'risk': 0.85, 'aqi_exp': 0.38, 'weight': 0.08},
    'MARATHAHALLI': {'risk': 0.76, 'aqi_exp': 0.25, 'weight': 0.08},
    'HSR_LAYOUT': {'risk': 0.88, 'aqi_exp': 0.45, 'weight': 0.10},
    'ELECTRONIC_CITY': {'risk': 0.72, 'aqi_exp': 0.20, 'weight': 0.05},
    'HEBBAL': {'risk': 0.80, 'aqi_exp': 0.32, 'weight': 0.06},
    'JP_NAGAR': {'risk': 0.83, 'aqi_exp': 0.36, 'weight': 0.05},
}


def generate_synthetic_riders(n_samples: int = 50000, seed: int = 42) -> pd.DataFrame:
    """
    Generate synthetic rider profiles for training.

    Features:
    - zone_id: sampled with population-proportional weights
    - aqi_exposure_score: Beta(2,5) distribution
    - work_hours_per_day: Normal(12, 2) clipped [6, 16]
    - work_days_per_week: Categorical([5,6,7], probs=[0.2, 0.5, 0.3])
    - season_multiplier: based on synthetic month
    - claim_history_count: Poisson(0.3) clipped [0, 10]
    - daily_earning_bucket: Categorical([0-4])
    - target_premium_paise: formula + noise
    """
    np.random.seed(seed)

    zone_ids = list(ZONES.keys())
    zone_weights = [ZONES[z]['weight'] for z in zone_ids]

    # Sample zones
    zones_sampled = np.random.choice(zone_ids, size=n_samples, p=zone_weights)

    # Feature generation
    data = {
        'zone_id': zones_sampled,
        'zone_risk_score': [ZONES[z]['risk'] for z in zones_sampled],
        'aqi_exposure_score': np.clip(np.random.beta(2, 5, n_samples), 0, 1),
        'work_hours_per_day': np.clip(np.random.normal(12, 2, n_samples), 6, 16).astype(int),
        'work_days_per_week': np.random.choice([5, 6, 7], n_samples, p=[0.2, 0.5, 0.3]),
        'season_multiplier': np.random.choice(
            [0.90, 1.00, 1.15],
            n_samples,
            p=[0.25, 0.35, 0.40]  # monsoon-heavy for training
        ),
        'claim_history_count': np.clip(np.random.poisson(0.3, n_samples), 0, 10),
        'daily_earning_bucket': np.random.choice(
            [0, 1, 2, 3, 4],
            n_samples,
            p=[0.05, 0.25, 0.45, 0.20, 0.05]
        ),
    }

    df = pd.DataFrame(data)

    # Target premium formula
    base = 5000  # ₹50 base in paise
    df['target_premium_paise'] = (
        base * (
            0.30 * df['zone_risk_score'] +
            0.25 * df['aqi_exposure_score'] +
            0.20 * df['season_multiplier'] +
            0.15 * (df['work_hours_per_day'] / 16) +
            0.10 * (df['work_days_per_week'] / 7)
        )
    ).astype(int)

    # Add noise (±10%)
    noise = np.random.normal(0, 300, n_samples).astype(int)
    df['target_premium_paise'] = np.clip(
        df['target_premium_paise'] + noise,
        2900,  # MIN_PREMIUM_PAISE
        9900,  # MAX_PREMIUM_PAISE
    )

    return df


def main():
    """Generate and save synthetic rider data."""
    output_path = Path(__file__).parent.parent.parent.parent / "data" / "synthetic_riders.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print("Generating 50,000 synthetic rider profiles...")
    df = generate_synthetic_riders()
    df.to_csv(output_path, index=False)
    print(f"✅ Saved to {output_path}")
    print(f"   Shape: {df.shape}")
    print(f"   Premium stats: mean={df['target_premium_paise'].mean():.0f}, "
          f"min={df['target_premium_paise'].min()}, max={df['target_premium_paise'].max()}")
    print(df.head())


if __name__ == "__main__":
    main()
