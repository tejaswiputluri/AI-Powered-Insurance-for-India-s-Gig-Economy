"""
GigShield Constants — ALL thresholds, weights, and limits (RULE-02).
Every number in the system lives here. If a threshold isn't in this file, it doesn't exist.
"""

# =============================================================================
# MSC THRESHOLDS — Multi-Signal Confluence
# =============================================================================

RAIN_THRESHOLD_MM_HR = 8.0          # mm/hr — minimum rainfall to trigger signal
AQI_THRESHOLD = 200                 # AQI index value — minimum for signal
ORDER_DROP_THRESHOLD_PCT = 0.35     # 35% drop from baseline
ROAD_DISRUPTION_THRESHOLD_PCT = 0.60  # tertiary — not counted toward MSC min
CIVIC_ALERT_THRESHOLD = True        # boolean — tertiary signal

# MSC requirements
MSC_MINIMUM_SIGNALS = 2             # min signals for any payout
MSC_HIGH_SIGNALS = 3                # signals for 85% coverage factor

# =============================================================================
# TIMING
# =============================================================================

MSC_POLL_INTERVAL_MINUTES = 30      # APScheduler frequency
MSC_EVENT_WINDOW_HOURS = 6          # max duration of a single event
MAX_DISRUPTION_WINDOW_HOURS = 8     # caps payout calculation at 8 hours
EVENT_EXPIRY_HOURS = 4              # RULE-19: no payout if event ended > 4 hrs ago

# =============================================================================
# MONEY (RULE-03: all values in INTEGER PAISE)
# =============================================================================

MIN_PREMIUM_PAISE = 2900            # ₹29/week minimum (RULE-11)
MAX_PREMIUM_PAISE = 9900            # ₹99/week maximum (RULE-11)
MAX_PAYOUT_PAISE = 220000           # ₹2,200/event maximum (RULE-12)

# Coverage factors (RULE-13)
COVERAGE_FACTOR_STANDARD = 0.70     # 2 signals confirmed
COVERAGE_FACTOR_HIGH = 0.85         # 3+ signals confirmed

# Zone Impact Factor bounds (RULE-20)
ZIF_MINIMUM = 0.60
ZIF_MAXIMUM = 1.00

# =============================================================================
# FRAUD ENGINE — Confidence Score Weights
# =============================================================================

FRAUD_WEIGHTS = {
    'l1_gps': 30,                   # GPS Coherence: 0 or 30 points
    'l2_weather': 30,               # Weather Cross-Verify: 0 or 30 points
    'l3_earnings': 25,              # Earnings Anomaly: 0 or 25 points
    'l4_cluster': 15,               # Cluster/Ring Detection: 0 or 15 points
}

CONFIDENCE_THRESHOLDS = {
    'auto_approve': 85,             # ≥ 85: instant payout
    'flag_approve': 60,             # 60–84: pay + flag for audit
    'hold': 35,                     # 35–59: human review
    'reject': 0,                    # < 35: auto reject (RULE-17)
}

# Fraud detection parameters
GPS_MAX_DISTANCE_KM = 5.0           # L1: max distance from zone centroid
Z_SCORE_THRESHOLD = 1.5             # L3: earnings anomaly z-score
CLUSTER_SUSPICION_COUNT = 5         # L4: min claims for ring detection
CLUSTER_TIME_WINDOW_MINUTES = 30    # L4: time window for clustering
CLUSTER_DBSCAN_EPS = 0.01          # ~1km in lat/lon degrees
CLUSTER_DBSCAN_MIN_SAMPLES = 5

# =============================================================================
# POLICY TIERS
# =============================================================================

POLICY_TIERS = {
    'basic': {
        'name': 'Basic',
        'premium_multiplier': 1.0,          # base premium × 1.0
        'coverage_cap_paise': 50000,        # ₹500 max per event
        'msc_threshold': 2,
        'coverage_factor': COVERAGE_FACTOR_STANDARD,
        'description': 'Essential cover for light disruptions',
    },
    'balanced': {
        'name': 'Balanced',
        'premium_multiplier': 1.3,          # base premium × 1.3
        'coverage_cap_paise': 90000,        # ₹900 max per event
        'msc_threshold': 2,
        'coverage_factor': COVERAGE_FACTOR_STANDARD,
        'description': 'Popular choice — good coverage, fair price',
        'recommended': True,
    },
    'pro': {
        'name': 'Pro',
        'premium_multiplier': 1.7,          # base premium × 1.7
        'coverage_cap_paise': 150000,       # ₹1,500 max per event
        'msc_threshold': 2,
        'coverage_factor': COVERAGE_FACTOR_HIGH,
        'description': 'Higher coverage with 3-signal boost',
    },
    'aggressive': {
        'name': 'Aggressive',
        'premium_multiplier': 2.0,          # base premium × 2.0
        'coverage_cap_paise': 220000,       # ₹2,200 max per event (RULE-12)
        'msc_threshold': 2,
        'coverage_factor': COVERAGE_FACTOR_HIGH,
        'description': 'Maximum protection — full coverage cap',
    },
}

# =============================================================================
# CACHE TTLs (seconds)
# =============================================================================

WEATHER_CACHE_TTL = 2100             # 35 minutes
ORDER_VOLUME_CACHE_TTL = 1800        # 30 minutes
GPS_CACHE_TTL = 300                  # 5 minutes

# =============================================================================
# ORDER VOLUME MOCK ENGINE — Time-of-day multipliers
# =============================================================================

TIME_OF_DAY_MULTIPLIERS = {
    (0, 6): 0.05,     # near zero (midnight to 6am)
    (6, 9): 0.40,     # breakfast ramp-up
    (9, 11): 0.65,    # late breakfast
    (11, 14): 1.00,   # lunch peak
    (14, 17): 0.45,   # afternoon slump
    (17, 19): 0.70,   # evening ramp
    (19, 22): 0.95,   # dinner near-peak
    (22, 24): 0.30,   # late night
}

DAY_OF_WEEK_MULTIPLIERS = {
    0: 0.85,   # Monday
    1: 0.80,   # Tuesday
    2: 0.85,   # Wednesday
    3: 0.90,   # Thursday
    4: 1.05,   # Friday
    5: 1.15,   # Saturday
    6: 1.10,   # Sunday
}

ZONE_ORDER_BASELINES = {
    'BTM_LAYOUT': 1.10,
    'KORAMANGALA': 1.25,
    'INDIRANAGAR': 1.20,
    'WHITEFIELD': 0.90,
    'JAYANAGAR': 0.95,
    'MARATHAHALLI': 0.85,
    'HSR_LAYOUT': 1.05,
    'ELECTRONIC_CITY': 0.75,
    'HEBBAL': 0.88,
    'JP_NAGAR': 0.92,
}

# =============================================================================
# WEATHER ORDER CORRELATION
# =============================================================================

WEATHER_ORDER_MULTIPLIERS = {
    'no_rain': 1.00,          # rainfall < 3mm/hr
    'light_rain': 0.80,      # rainfall 3–8mm/hr
    'heavy_rain': 0.58,      # rainfall > 8mm/hr
    'high_aqi_factor': 0.82, # applied when AQI > 200
}

# =============================================================================
# ML MODEL CONFIG
# =============================================================================

FT_TRANSFORMER_FEATURES = [
    'zone_risk_score',
    'aqi_exposure_score',
    'work_hours_per_day',
    'work_days_per_week',
    'season_multiplier',
    'claim_history_count',
    'daily_earning_bucket',
]

DAILY_EARNING_BUCKETS = {
    0: (0, 500),       # < ₹500
    1: (500, 800),     # ₹500–800
    2: (800, 1200),    # ₹800–1200
    3: (1200, 1600),   # ₹1200–1600
    4: (1600, float('inf')),  # > ₹1600
}

# =============================================================================
# DEMO MODE FALLBACK VALUES
# =============================================================================

DEMO_FALLBACK_WEATHER = {
    'BTM_LAYOUT': {'rainfall_mm_hr': 14.2, 'aqi_value': 218},
    'KORAMANGALA': {'rainfall_mm_hr': 0.0, 'aqi_value': 85},
    'INDIRANAGAR': {'rainfall_mm_hr': 0.0, 'aqi_value': 85},
    'WHITEFIELD': {'rainfall_mm_hr': 0.0, 'aqi_value': 85},
    'JAYANAGAR': {'rainfall_mm_hr': 0.0, 'aqi_value': 85},
    'MARATHAHALLI': {'rainfall_mm_hr': 0.0, 'aqi_value': 85},
    'HSR_LAYOUT': {'rainfall_mm_hr': 0.0, 'aqi_value': 85},
    'ELECTRONIC_CITY': {'rainfall_mm_hr': 0.0, 'aqi_value': 85},
    'HEBBAL': {'rainfall_mm_hr': 0.0, 'aqi_value': 85},
    'JP_NAGAR': {'rainfall_mm_hr': 0.0, 'aqi_value': 85},
}

# =============================================================================
# API PAGINATION
# =============================================================================

DEFAULT_PAGE_LIMIT = 50
MAX_PAGE_LIMIT = 100

# =============================================================================
# RAZORPAY
# =============================================================================

RAZORPAY_PAYOUT_PURPOSE = "payout"
RAZORPAY_CURRENCY = "INR"
RAZORPAY_MODE = "UPI"
