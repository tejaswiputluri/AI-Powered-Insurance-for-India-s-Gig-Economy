# GIGSHIELD — COMPLETE SYSTEM BUILD PROMPT FOR CLAUDE OPUS
## Master Engineering Specification · A to Z · Zero Ambiguity

---

> **YOU ARE THE LEAD ENGINEER FOR GIGSHIELD.**
> This document is your complete specification. Read every section before writing a single line of code. Every decision — file name, variable name, API contract, database column, business rule — is defined here. Your job is to implement exactly what is specified, and flag (do not skip) anything that needs clarification.

---

## TABLE OF CONTENTS

1. [Identity & Mission](#1-identity--mission)
2. [Absolute Rules — Read First](#2-absolute-rules--read-first)
3. [Repository Structure](#3-repository-structure)
4. [Database Schema — Complete](#4-database-schema--complete)
5. [Backend API — All Endpoints](#5-backend-api--all-endpoints)
6. [Trigger Engine](#6-trigger-engine)
7. [Fraud Engine & Confidence Score](#7-fraud-engine--confidence-score)
8. [Payout Engine — Earnings DNA](#8-payout-engine--earnings-dna)
9. [ML Services](#9-ml-services)
10. [Synthetic Data Generator](#10-synthetic-data-generator)
11. [External API Integration](#11-external-api-integration)
12. [Frontend — Rider PWA](#12-frontend--rider-pwa)
13. [Frontend — Insurer Dashboard](#13-frontend--insurer-dashboard)
14. [Notification System](#14-notification-system)
15. [Demo Mode & Resilience Layer](#15-demo-mode--resilience-layer)
16. [Docker & Infrastructure](#16-docker--infrastructure)
17. [Environment Variables](#17-environment-variables)
18. [Build Order — Phase by Phase](#18-build-order--phase-by-phase)
19. [Testing Requirements](#19-testing-requirements)
20. [Business Rules — Non-Negotiable](#20-business-rules--non-negotiable)

---

## 1. IDENTITY & MISSION

**Product Name:** GigShield ⚡
**Tagline:** AI-Powered Parametric Income Insurance for India's Gig Workers
**Hackathon:** Guidewire DEVTrails 2026 — Unicorn Chase
**Persona:** Food Delivery Partners on Swiggy / Zomato in Bengaluru, India
**Demo City:** Bengaluru (all lat/long coordinates, zones, and data are Bengaluru-specific)

### What GigShield Does

GigShield is a **parametric income insurance platform**. It:

1. Onboards a delivery rider in under 2 minutes via phone OTP + 5 questions
2. Calculates their personalised weekly premium using an ML model (FT-Transformer)
3. Monitors live weather (rain + AQI) via Open-Meteo API every 30 minutes
4. Fires payouts **automatically** when Multi-Signal Confluence (MSC) is confirmed — rider does nothing
5. Runs a 4-layer fraud detection pipeline scoring every claim 0–100
6. Delivers payout to UPI within 4 hours of confirmed disruption
7. Forecasts next week's disruption risk per zone using an LSTM model
8. Shows insurers a live analytics dashboard with loss ratios, fraud queue, and risk heatmap

### What GigShield Does NOT Cover (Hard Constraint)
- Vehicle repair
- Health / medical expenses
- Accidents
- Life insurance
- Any event not causing **income loss**

---

## 2. ABSOLUTE RULES — READ FIRST

These rules override any other consideration. If any implementation conflicts with these rules, the rule wins.

### Code Rules

```
RULE-01  Every file must have a module docstring explaining its purpose.
RULE-02  No magic numbers. All thresholds, weights, and limits go in config/constants.py.
RULE-03  All money values (premiums, payouts) stored as INTEGER PAISE (not float rupees).
         Display only converts to rupees. ₹67 stored as 6700. ₹333.50 stored as 33350.
RULE-04  All timestamps stored as UTC in the database. Convert to IST only for display.
RULE-05  Never call an external API without a try/except and Redis cache fallback.
RULE-06  Never store raw GPS coordinates in logs that are user-visible. Hash to zone_id only.
RULE-07  All database writes that touch money must be inside a transaction.
RULE-08  Every API endpoint must validate input with Pydantic. No raw dict access.
RULE-09  The demo override toggle (DEMO_MODE=true) must work without any external API calls.
RULE-10  ML models are never called synchronously from an API endpoint. Always async via queue.
```

### Business Rules

```
RULE-11  Minimum premium: ₹29/week (2900 paise). Maximum premium: ₹99/week (9900 paise).
RULE-12  Maximum payout: ₹2,200/event (220000 paise).
RULE-13  Coverage factor: 0.70 for standard MSC (2 signals). 0.85 for high MSC (3+ signals).
RULE-14  MSC requires minimum 2 of the 3 core signals: Rain, AQI, Order Volume Drop.
RULE-15  A rider can only have ONE active claim per disruption event window.
         Event window = MSC trigger start to MSC trigger end + 2 hours.
RULE-16  No payout if rider has no active policy for current week.
RULE-17  Confidence Score < 35 = auto reject. No exceptions. No manual override for this band.
RULE-18  Premium deduction happens every Monday at 06:00 IST (00:30 UTC).
RULE-19  A rider cannot claim for an event that ended more than 4 hours ago.
RULE-20  Zone Impact Factor (ZIF) minimum value is 0.60. Maximum is 1.00.
```

### Demo Rules

```
RULE-21  The demo must complete the full happy path (signup → disruption → payout) in under 7 minutes real time.
RULE-22  The demo override fires a pre-seeded Heavy Rain + Order Drop event for zone_id='BTM_LAYOUT'.
RULE-23  All Razorpay calls use TEST mode keys only. Never production keys in this build.
RULE-24  Firebase Auth uses phone number +91-9999999999 for demo rider (no real OTP in demo mode).
RULE-25  Demo mode is toggled by environment variable DEMO_MODE=true. Must not require code changes.
```

---

## 3. REPOSITORY STRUCTURE

Create this exact structure. Do not add, rename, or merge directories without noting the deviation.

```
gigshield/
│
├── README.md                          # Already written — do not modify
│
├── backend/
│   ├── main.py                        # FastAPI app entry point
│   ├── config/
│   │   ├── __init__.py
│   │   ├── constants.py               # ALL thresholds, weights, limits (RULE-02)
│   │   └── settings.py                # Pydantic BaseSettings — reads from .env
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routers/
│   │   │   ├── auth.py                # /auth/* endpoints
│   │   │   ├── riders.py              # /riders/* endpoints
│   │   │   ├── policies.py            # /policies/* endpoints
│   │   │   ├── claims.py              # /claims/* endpoints
│   │   │   ├── triggers.py            # /triggers/* endpoints (admin/internal)
│   │   │   ├── insurer.py             # /insurer/* endpoints
│   │   │   └── demo.py                # /demo/* endpoints (demo mode only)
│   │   └── middleware.py              # CORS, auth middleware
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── db/                        # SQLAlchemy ORM models
│   │   │   ├── rider.py
│   │   │   ├── policy.py
│   │   │   ├── claim.py
│   │   │   ├── trigger_event.py
│   │   │   ├── payout.py
│   │   │   ├── fraud_check.py
│   │   │   └── audit_log.py
│   │   └── schemas/                   # Pydantic request/response schemas
│   │       ├── rider.py
│   │       ├── policy.py
│   │       ├── claim.py
│   │       └── insurer.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── trigger_engine.py          # MSC evaluator — core loop
│   │   ├── fraud_engine.py            # L1 + L2 + L3 + Confidence Score
│   │   ├── payout_engine.py           # Earnings DNA formula
│   │   ├── premium_service.py         # Calls ML service for premium
│   │   ├── notification_service.py    # SMS mock + in-app
│   │   ├── weather_service.py         # Open-Meteo wrapper + Redis cache
│   │   ├── order_volume_service.py    # Mock order volume engine
│   │   └── forecast_service.py        # LSTM forecast wrapper
│   │
│   ├── ml/
│   │   ├── __init__.py
│   │   ├── premium/
│   │   │   ├── model.py               # FT-Transformer model definition
│   │   │   ├── train.py               # Training script
│   │   │   ├── serve.py               # FastAPI inference endpoint
│   │   │   └── synthetic_data.py      # 50k rider profile generator
│   │   ├── forecast/
│   │   │   ├── model.py               # LSTM model definition
│   │   │   ├── train.py               # Training script
│   │   │   ├── serve.py               # FastAPI inference endpoint
│   │   │   └── data_prep.py           # Weather history + feature engineering
│   │   └── cnn_verify/
│   │       ├── model.py               # MobileNetV3 definition
│   │       ├── train.py               # Fine-tuning script
│   │       ├── serve.py               # FastAPI inference endpoint
│   │       └── tile_fetcher.py        # NASA POWER tile downloader
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   ├── database.py                # SQLAlchemy engine + session
│   │   ├── migrations/                # Alembic migrations
│   │   └── seed.py                    # Seed demo data
│   │
│   ├── cache/
│   │   ├── __init__.py
│   │   └── redis_client.py            # Redis connection + helpers
│   │
│   ├── scheduler/
│   │   ├── __init__.py
│   │   └── jobs.py                    # APScheduler job definitions
│   │
│   └── tests/
│       ├── test_trigger_engine.py
│       ├── test_fraud_engine.py
│       ├── test_payout_engine.py
│       └── test_api.py
│
├── frontend/
│   ├── rider-pwa/                     # React + Vite + Tailwind (rider app)
│   │   ├── public/
│   │   │   └── manifest.json          # PWA manifest
│   │   ├── src/
│   │   │   ├── main.jsx
│   │   │   ├── App.jsx
│   │   │   ├── pages/
│   │   │   │   ├── Onboarding.jsx     # Step 1: PRF form
│   │   │   │   ├── PremiumPanel.jsx   # Step 2: XAI premium display
│   │   │   │   ├── Simulator.jsx      # Step 3: Coverage simulator
│   │   │   │   ├── PolicySelect.jsx   # Step 4: Choose tier
│   │   │   │   ├── Dashboard.jsx      # Active coverage home
│   │   │   │   ├── ClaimStatus.jsx    # Live claim tracker
│   │   │   │   └── ClaimHistory.jsx   # Past claims + timeline
│   │   │   ├── components/
│   │   │   │   ├── ConfidenceGauge.jsx
│   │   │   │   ├── ClaimTimeline.jsx
│   │   │   │   ├── XAIPanel.jsx
│   │   │   │   ├── CoverageSimulator.jsx
│   │   │   │   ├── PolicyTierCard.jsx
│   │   │   │   ├── MSCStatusCard.jsx
│   │   │   │   └── NotificationBanner.jsx
│   │   │   ├── hooks/
│   │   │   │   ├── useAuth.js
│   │   │   │   ├── usePolicy.js
│   │   │   │   └── useClaims.js
│   │   │   ├── services/
│   │   │   │   └── api.js             # All backend API calls
│   │   │   └── utils/
│   │   │       └── formatters.js      # Paise → rupee, UTC → IST
│   │   ├── sw.js                      # Service worker (Workbox)
│   │   ├── vite.config.js
│   │   └── package.json
│   │
│   └── insurer-dashboard/             # React + Vite + Tailwind (insurer app)
│       ├── src/
│       │   ├── main.jsx
│       │   ├── App.jsx
│       │   ├── pages/
│       │   │   ├── Overview.jsx       # Loss ratio + key metrics
│       │   │   ├── RiskHeatmap.jsx    # Leaflet LSTM heatmap
│       │   │   ├── FraudQueue.jsx     # Pending reviews + scores
│       │   │   ├── ClaimsViewer.jsx   # All claims + timeline
│       │   │   └── Reserves.jsx       # Weekly reserve estimates
│       │   ├── components/
│       │   │   ├── BengaluruMap.jsx   # Leaflet choropleth
│       │   │   ├── LossRatioWidget.jsx
│       │   │   ├── FraudCard.jsx
│       │   │   └── ReserveWidget.jsx
│       │   └── services/
│       │       └── api.js
│       └── package.json
│
├── data/
│   ├── zones.json                     # Bengaluru zone definitions with lat/long
│   ├── synthetic_riders.py            # Run to generate 50k rider CSV
│   ├── synthetic_weather.py           # Run to generate 3yr Bengaluru weather CSV
│   ├── mock_order_volume.py           # Order volume mock engine
│   └── seed_events.json               # Pre-seeded demo disruption events
│
├── infra/
│   ├── docker-compose.yml             # Full stack compose
│   ├── docker-compose.dev.yml         # Dev override
│   └── nginx/
│       └── nginx.conf
│
├── scripts/
│   ├── train_all_models.sh            # Run all 3 ML training scripts
│   ├── seed_db.sh                     # Seed demo data
│   └── run_demo.sh                    # Start full demo environment
│
├── .env.example                       # All required environment variables
├── .gitignore
└── requirements.txt                   # Python dependencies (pinned versions)
```

---

## 4. DATABASE SCHEMA — COMPLETE

**Database:** PostgreSQL 15
**ORM:** SQLAlchemy 2.0 (async)
**Migrations:** Alembic

All tables use UUID primary keys. All timestamps are UTC.

### Table: riders

```sql
CREATE TABLE riders (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    phone           VARCHAR(15) UNIQUE NOT NULL,       -- E.164 format: +919999999999
    name            VARCHAR(100),
    firebase_uid    VARCHAR(128) UNIQUE NOT NULL,
    zone_id         VARCHAR(50) NOT NULL,              -- FK to zones lookup
    platform        VARCHAR(20) NOT NULL,              -- 'swiggy' | 'zomato' | 'dunzo'
    work_hours_start INTEGER NOT NULL,                 -- 24hr: 10 = 10am
    work_hours_end   INTEGER NOT NULL,                 -- 24hr: 22 = 10pm
    work_days_per_week INTEGER NOT NULL DEFAULT 6,
    self_reported_daily_earning_paise BIGINT NOT NULL, -- RULE-03: paise
    -- Computed PRF fields (set by ML service after onboarding)
    prf_zone_risk_score     FLOAT,                    -- 0.0–1.0
    prf_aqi_exposure_score  FLOAT,                    -- 0.0–1.0
    prf_season_multiplier   FLOAT,                    -- 0.85–1.20
    prf_claim_history_score FLOAT DEFAULT 0.0,
    computed_weekly_premium_paise BIGINT,              -- Set by FT-Transformer
    -- XAI attention weights (JSON blob from FT-Transformer)
    xai_factors     JSONB,
    -- Lifecycle
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_active       BOOLEAN NOT NULL DEFAULT TRUE
);
```

### Table: policies

```sql
CREATE TABLE policies (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rider_id        UUID NOT NULL REFERENCES riders(id),
    tier            VARCHAR(20) NOT NULL,              -- 'basic'|'balanced'|'pro'|'aggressive'
    weekly_premium_paise    BIGINT NOT NULL,
    coverage_cap_paise      BIGINT NOT NULL,
    msc_threshold   INTEGER NOT NULL DEFAULT 2,        -- min signals required
    coverage_factor FLOAT NOT NULL DEFAULT 0.70,
    -- Validity
    week_start_date DATE NOT NULL,                     -- Monday of coverage week
    week_end_date   DATE NOT NULL,                     -- Sunday of coverage week
    status          VARCHAR(20) NOT NULL DEFAULT 'active', -- 'active'|'paused'|'expired'
    -- Payment
    premium_deducted_at TIMESTAMPTZ,
    premium_deduction_status VARCHAR(20) DEFAULT 'pending', -- 'pending'|'success'|'failed'
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_policies_rider_week ON policies(rider_id, week_start_date);
CREATE INDEX idx_policies_active ON policies(status) WHERE status = 'active';
```

### Table: trigger_events

```sql
CREATE TABLE trigger_events (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    zone_id         VARCHAR(50) NOT NULL,
    -- Signal values at time of trigger
    rainfall_mm_hr  FLOAT,
    aqi_value       INTEGER,
    order_drop_pct  FLOAT,                             -- e.g. 0.47 = 47% drop
    road_disruption_pct FLOAT,
    civic_alert     BOOLEAN DEFAULT FALSE,
    -- MSC evaluation
    signals_confirmed INTEGER NOT NULL,                -- count of signals above threshold
    msc_status      VARCHAR(20) NOT NULL,              -- 'not_met'|'standard'|'high'
    -- Timing
    detected_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ended_at        TIMESTAMPTZ,                       -- NULL while active
    -- Source flags
    is_demo_event   BOOLEAN NOT NULL DEFAULT FALSE,
    rain_source     VARCHAR(20) DEFAULT 'open_meteo',  -- 'open_meteo'|'cache'|'demo'
    aqi_source      VARCHAR(20) DEFAULT 'open_meteo'
);

CREATE INDEX idx_trigger_events_zone_time ON trigger_events(zone_id, detected_at DESC);
CREATE INDEX idx_trigger_events_active ON trigger_events(zone_id) WHERE ended_at IS NULL;
```

### Table: claims

```sql
CREATE TABLE claims (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rider_id        UUID NOT NULL REFERENCES riders(id),
    policy_id       UUID NOT NULL REFERENCES policies(id),
    trigger_event_id UUID NOT NULL REFERENCES trigger_events(id),
    -- Earnings DNA inputs
    baseline_hourly_earning_paise   BIGINT NOT NULL,
    disruption_hours                FLOAT NOT NULL,
    zone_impact_factor              FLOAT NOT NULL,    -- 0.60–1.00
    coverage_factor                 FLOAT NOT NULL,    -- 0.70 or 0.85
    -- Computed payout
    calculated_payout_paise         BIGINT NOT NULL,
    capped_payout_paise             BIGINT NOT NULL,   -- min(calculated, coverage_cap)
    -- Status machine
    status          VARCHAR(20) NOT NULL DEFAULT 'pending_fraud_check',
    -- Values: pending_fraud_check | fraud_checking | approved | flagged | on_hold | rejected | paid
    -- Fraud pipeline
    confidence_score INTEGER,                          -- 0–100
    fraud_decision  VARCHAR(20),                       -- 'auto_approved'|'flagged'|'held'|'rejected'
    fraud_reason    VARCHAR(100),                      -- rejection reason code
    -- Timing
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    fraud_checked_at TIMESTAMPTZ,
    payout_initiated_at TIMESTAMPTZ,
    paid_at         TIMESTAMPTZ
);

CREATE UNIQUE INDEX idx_claims_rider_event ON claims(rider_id, trigger_event_id);
CREATE INDEX idx_claims_status ON claims(status);
```

### Table: fraud_checks

```sql
CREATE TABLE fraud_checks (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    claim_id        UUID NOT NULL REFERENCES claims(id),
    -- Layer results
    l1_gps_score    INTEGER NOT NULL DEFAULT 0,        -- 0 or 30
    l1_gps_result   VARCHAR(20) NOT NULL,              -- 'pass'|'fail'|'skip'
    l1_gps_detail   TEXT,
    l2_weather_score INTEGER NOT NULL DEFAULT 0,       -- 0 or 30
    l2_weather_result VARCHAR(20) NOT NULL,
    l2_weather_detail TEXT,
    l3_earnings_score INTEGER NOT NULL DEFAULT 0,      -- 0 or 25
    l3_earnings_result VARCHAR(20) NOT NULL,
    l3_earnings_detail TEXT,
    l4_cluster_score INTEGER NOT NULL DEFAULT 0,       -- 0 or 15
    l4_cluster_result VARCHAR(20) NOT NULL,
    l4_cluster_detail TEXT,
    -- Totals
    total_score     INTEGER NOT NULL,                  -- sum of above
    decision        VARCHAR(20) NOT NULL,
    -- CNN verify (optional, Phase 3)
    cnn_classification VARCHAR(20),                    -- 'clear'|'light_rain'|'heavy_rain'|'flood'
    cnn_confidence  FLOAT,
    cnn_agrees_with_api BOOLEAN,
    -- Timing
    checked_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### Table: payouts

```sql
CREATE TABLE payouts (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    claim_id        UUID NOT NULL REFERENCES claims(id),
    rider_id        UUID NOT NULL REFERENCES riders(id),
    amount_paise    BIGINT NOT NULL,
    -- Payment gateway
    gateway         VARCHAR(20) NOT NULL DEFAULT 'razorpay_test',
    gateway_payout_id VARCHAR(100),                    -- Razorpay payout ID
    gateway_status  VARCHAR(20),
    upi_vpa         VARCHAR(100),                      -- UPI VPA of rider
    -- Status
    status          VARCHAR(20) NOT NULL DEFAULT 'initiated',
    -- Values: initiated | processing | success | failed
    initiated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at    TIMESTAMPTZ
);
```

### Table: audit_logs

```sql
CREATE TABLE audit_logs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type     VARCHAR(50) NOT NULL,              -- 'claim'|'policy'|'rider'|'payout'
    entity_id       UUID NOT NULL,
    action          VARCHAR(100) NOT NULL,
    actor           VARCHAR(50) NOT NULL DEFAULT 'system',
    detail          JSONB,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_audit_entity ON audit_logs(entity_type, entity_id, created_at DESC);
```

### Table: zone_forecasts

```sql
CREATE TABLE zone_forecasts (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    zone_id         VARCHAR(50) NOT NULL,
    forecast_week_start DATE NOT NULL,
    disruption_probability FLOAT NOT NULL,             -- 0.0–1.0
    expected_claim_count INTEGER,
    reserve_estimate_paise BIGINT,
    model_version   VARCHAR(20) DEFAULT 'lstm_v1',
    generated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_zone_forecast_week ON zone_forecasts(zone_id, forecast_week_start);
```

### Lookup: zones (Bengaluru)

```json
// data/zones.json
{
  "zones": [
    {"id": "BTM_LAYOUT",    "name": "BTM Layout",     "lat": 12.9165, "lon": 77.6101, "base_zif": 0.87},
    {"id": "KORAMANGALA",   "name": "Koramangala",    "lat": 12.9352, "lon": 77.6245, "base_zif": 0.82},
    {"id": "INDIRANAGAR",   "name": "Indiranagar",    "lat": 12.9784, "lon": 77.6408, "base_zif": 0.91},
    {"id": "WHITEFIELD",    "name": "Whitefield",     "lat": 12.9698, "lon": 77.7499, "base_zif": 0.79},
    {"id": "JAYANAGAR",     "name": "Jayanagar",      "lat": 12.9308, "lon": 77.5839, "base_zif": 0.85},
    {"id": "MARATHAHALLI",  "name": "Marathahalli",   "lat": 12.9591, "lon": 77.6972, "base_zif": 0.76},
    {"id": "HSR_LAYOUT",    "name": "HSR Layout",     "lat": 12.9116, "lon": 77.6389, "base_zif": 0.88},
    {"id": "ELECTRONIC_CITY","name": "Electronic City","lat": 12.8445, "lon": 77.6602, "base_zif": 0.72},
    {"id": "HEBBAL",        "name": "Hebbal",         "lat": 13.0358, "lon": 77.5970, "base_zif": 0.80},
    {"id": "JP_NAGAR",      "name": "JP Nagar",       "lat": 12.9108, "lon": 77.5916, "base_zif": 0.83}
  ]
}
```

---

## 5. BACKEND API — ALL ENDPOINTS

**Base URL:** `/api/v1`
**Auth:** Firebase JWT token in `Authorization: Bearer <token>` header
**Response format:** Always `{"data": ..., "error": null}` or `{"data": null, "error": {"code": "...", "message": "..."}}`

### Auth Router — `/api/v1/auth`

```
POST /auth/verify-token
  Request:  { "firebase_token": "string" }
  Response: { "rider_id": "uuid", "is_new_rider": bool, "access_token": "string" }
  Logic:    Verify Firebase token → lookup rider by firebase_uid → return GigShield JWT

POST /auth/demo-login          (only when DEMO_MODE=true)
  Request:  {}
  Response: { "rider_id": "<demo-rider-uuid>", "access_token": "string" }
  Logic:    Returns hardcoded demo rider without Firebase verification
```

### Riders Router — `/api/v1/riders`

```
POST /riders/onboard
  Auth: required
  Request: {
    "name": "string",
    "zone_id": "string",               -- must exist in zones.json
    "platform": "swiggy|zomato|dunzo",
    "work_hours_start": int,           -- 0–23
    "work_hours_end": int,             -- 0–23
    "work_days_per_week": int,         -- 1–7
    "self_reported_daily_earning": int -- rupees (we convert to paise)
  }
  Response: {
    "rider_id": "uuid",
    "computed_premium_paise": int,
    "xai_factors": [
      {"factor": "aqi_zone_history", "weight": 0.34, "label": "AQI Zone History"},
      {"factor": "monsoon_season",   "weight": 0.27, "label": "Monsoon Season"},
      {"factor": "zone_risk_score",  "weight": 0.21, "label": "Zone Risk Score"},
      {"factor": "claim_history",    "weight": 0.18, "label": "Claim History"}
    ],
    "tier_options": [<PolicyTierObject x4>]
  }
  Logic:
    1. Validate all fields
    2. Create rider record
    3. Call premium_service.calculate_premium(rider_data) → FT-Transformer
    4. Update rider with computed premium + XAI factors
    5. Return result

GET /riders/me
  Auth: required
  Response: Full rider profile including current policy, this week's risk level

GET /riders/me/location
  Auth: required
  Request Query: ?lat=12.9165&lon=77.6101
  Response: { "zone_id": "BTM_LAYOUT", "zone_name": "BTM Layout", "within_active_zone": bool }
  Logic: Find nearest zone centroid within 5km radius. Used by fraud L1 check.

PATCH /riders/me/upi
  Auth: required
  Request: { "upi_vpa": "rider@upi" }
  Response: { "updated": true }
```

### Policies Router — `/api/v1/policies`

```
POST /policies/create
  Auth: required
  Request: { "tier": "basic|balanced|pro|aggressive" }
  Response: { "policy_id": "uuid", "week_start": "date", "week_end": "date",
              "premium_paise": int, "coverage_cap_paise": int }
  Logic:
    1. Check rider has no active policy for current week
    2. Get tier config from POLICY_TIERS constant
    3. Create policy for Monday–Sunday of current week
    4. Schedule Monday premium deduction (APScheduler)
    5. Log to audit_log

GET /policies/me/current
  Auth: required
  Response: Current active policy or null

GET /policies/me/history
  Auth: required
  Response: List of past policies (last 12 weeks)

POST /policies/me/pause
  Auth: required
  Logic: Set policy status = 'paused' if > 48hr before next Monday. Else reject.

GET /policies/simulator
  Auth: required
  Query: ?zone_id=BTM_LAYOUT&disruption_hours=4&signal_count=2
  Response: {
    "estimated_payout_paise": int,
    "breakdown": {
      "baseline_hourly_paise": int,
      "disruption_hours": float,
      "zone_impact_factor": float,
      "coverage_factor": float,
      "formula": "BHE × DW × ZIF × CF"
    }
  }
```

### Claims Router — `/api/v1/claims`

```
GET /claims/me
  Auth: required
  Response: List of all claims for rider, newest first

GET /claims/{claim_id}
  Auth: required (rider must own this claim)
  Response: Full claim detail including fraud_check and payout records

GET /claims/{claim_id}/timeline
  Auth: required
  Response: {
    "events": [
      {"timestamp": "UTC ISO", "event": "rain_detected", "detail": "14.2mm/hr"},
      {"timestamp": "UTC ISO", "event": "aqi_confirmed", "detail": "AQI 218"},
      {"timestamp": "UTC ISO", "event": "msc_confirmed", "detail": "2/3 signals"},
      {"timestamp": "UTC ISO", "event": "fraud_check_passed", "detail": "Score 91/100"},
      {"timestamp": "UTC ISO", "event": "payout_initiated", "detail": "₹333"},
      {"timestamp": "UTC ISO", "event": "payout_sent", "detail": "UPI confirmed"}
    ]
  }
```

### Triggers Router — `/api/v1/triggers` (internal/admin)

```
GET /triggers/current
  Auth: admin token
  Response: All active trigger events with signal values

POST /triggers/demo/fire
  Auth: admin token (or DEMO_MODE=true)
  Request: { "zone_id": "BTM_LAYOUT", "event_type": "rain_order_drop" }
  Response: { "trigger_event_id": "uuid", "claims_created": int }
  Logic: Fire pre-seeded demo event and run full pipeline for all active riders in zone

GET /triggers/history
  Auth: admin
  Query: ?zone_id=BTM_LAYOUT&days=7
  Response: List of past trigger events
```

### Insurer Router — `/api/v1/insurer`

```
GET /insurer/overview
  Auth: insurer token
  Response: {
    "this_week": {
      "active_riders": int,
      "premium_collected_paise": int,
      "claims_paid_paise": int,
      "loss_ratio": float,              -- claims_paid / premium_collected
      "claims_auto_approved": int,
      "claims_flagged": int,
      "claims_rejected": int
    }
  }

GET /insurer/heatmap
  Auth: insurer token
  Response: {
    "zones": [
      {
        "zone_id": "BTM_LAYOUT",
        "zone_name": "BTM Layout",
        "lat": 12.9165, "lon": 77.6101,
        "disruption_probability": 0.73,
        "expected_claims": 12,
        "reserve_estimate_paise": 540000,
        "risk_level": "high"             -- "low"|"medium"|"high"
      },
      ...
    ],
    "forecast_week": "2026-03-23"
  }

GET /insurer/fraud-queue
  Auth: insurer token
  Response: List of claims with status='on_hold', ordered by created_at desc

POST /insurer/fraud-queue/{claim_id}/decision
  Auth: insurer token
  Request: { "decision": "approve|reject", "note": "string" }
  Response: { "updated": true }

GET /insurer/claims
  Auth: insurer token
  Query: ?status=all&zone_id=all&limit=50&offset=0
  Response: Paginated list of all claims

GET /insurer/reserves
  Auth: insurer token
  Response: {
    "current_week_reserve_paise": int,
    "next_week_estimate_paise": int,
    "reserve_ratio": float,
    "breakdown_by_zone": [...]
  }
```

### Demo Router — `/api/v1/demo` (DEMO_MODE=true only)

```
POST /demo/reset
  Logic: Delete all demo rider's claims, reset to clean state

POST /demo/fire-event
  Request: { "scenario": "rain_aqi"|"aqi_order"|"full_3_signal"|"fraud_attempt" }
  Response: { "trigger_event_id": "uuid", "scenario_description": "string" }

GET /demo/state
  Response: Full current state of demo rider (policy, claims, last event)
```

---

## 6. TRIGGER ENGINE

**File:** `backend/services/trigger_engine.py`
**Scheduler:** APScheduler runs `run_msc_check()` every 30 minutes

### Constants (backend/config/constants.py)

```python
# MSC Thresholds
RAIN_THRESHOLD_MM_HR = 8.0          # mm/hr
AQI_THRESHOLD = 200                 # AQI index value
ORDER_DROP_THRESHOLD_PCT = 0.35     # 35% drop from baseline
ROAD_DISRUPTION_THRESHOLD_PCT = 0.60
CIVIC_ALERT_THRESHOLD = True        # boolean

# MSC requirements
MSC_MINIMUM_SIGNALS = 2             # min signals for any payout
MSC_HIGH_SIGNALS = 3                # signals for 85% coverage factor

# Timing
MSC_POLL_INTERVAL_MINUTES = 30
MSC_EVENT_WINDOW_HOURS = 6          # max duration of a single event

# Money
MIN_PREMIUM_PAISE = 2900
MAX_PREMIUM_PAISE = 9900
MAX_PAYOUT_PAISE = 220000
COVERAGE_FACTOR_STANDARD = 0.70
COVERAGE_FACTOR_HIGH = 0.85
ZIF_MINIMUM = 0.60
ZIF_MAXIMUM = 1.00
```

### MSC Algorithm

```python
async def run_msc_check():
    """
    Called every 30 minutes by APScheduler.
    For each Bengaluru zone:
      1. Fetch weather signals (with cache fallback)
      2. Evaluate MSC
      3. If MSC confirmed and no active event for zone → create trigger_event
      4. Find all riders in zone with active policy this week
      5. For each rider → create claim → run fraud pipeline → initiate payout if approved
    """
    zones = load_zones()
    for zone in zones:
        signals = await fetch_all_signals(zone)
        confirmed_signals = count_confirmed_signals(signals)

        if confirmed_signals >= MSC_MINIMUM_SIGNALS:
            # Check if event already active for this zone
            existing = await get_active_trigger_event(zone.id)
            if existing:
                continue  # Don't double-fire

            # Create trigger event
            event = await create_trigger_event(zone, signals, confirmed_signals)

            # Find eligible riders
            riders = await get_riders_with_active_policy(zone.id)

            for rider in riders:
                await process_rider_claim(rider, event)

        else:
            # Close any active events for this zone if signals fell below threshold
            await close_active_trigger_event(zone.id)


async def count_confirmed_signals(signals: dict) -> int:
    """Count how many of the 3 CORE signals are above threshold."""
    count = 0
    if signals.get('rainfall_mm_hr', 0) >= RAIN_THRESHOLD_MM_HR:
        count += 1
    if signals.get('aqi_value', 0) >= AQI_THRESHOLD:
        count += 1
    if signals.get('order_drop_pct', 0) >= ORDER_DROP_THRESHOLD_PCT:
        count += 1
    return count
    # Note: Road disruption and civic alert are tertiary — they do NOT count
    # toward MSC minimum. They are recorded but not required.
```

### Signal Fetching

```python
async def fetch_all_signals(zone) -> dict:
    """
    Fetch all signals with Redis cache fallback.
    Each signal has a TTL: weather = 35min, order_volume = 30min
    """
    return {
        'rainfall_mm_hr':    await weather_service.get_rainfall(zone.lat, zone.lon),
        'aqi_value':         await weather_service.get_aqi(zone.lat, zone.lon),
        'order_drop_pct':    await order_volume_service.get_drop_pct(zone.id),
        'road_disruption_pct': await get_road_disruption(zone.id),  # always mock
        'civic_alert':       await get_civic_alert(zone.id),         # always mock
    }
```

---

## 7. FRAUD ENGINE & CONFIDENCE SCORE

**File:** `backend/services/fraud_engine.py`

### Confidence Score Formula

```python
"""
Total = w1(GPS) + w2(Weather) + w3(Earnings) + w4(Cluster)

L1 GPS Coherence:      0 or 30 points
L2 Weather Cross-Verify: 0 or 30 points
L3 Earnings Anomaly:   0 or 25 points
L4 Cluster Detection:  0 or 15 points
Max total: 100 points
"""

FRAUD_WEIGHTS = {
    'l1_gps': 30,
    'l2_weather': 30,
    'l3_earnings': 25,
    'l4_cluster': 15,
}

CONFIDENCE_THRESHOLDS = {
    'auto_approve': 85,    # ≥ 85: instant payout
    'flag_approve': 60,    # 60–84: pay + flag for audit
    'hold': 35,            # 35–59: human review
    'reject': 0,           # < 35: auto reject (RULE-17)
}
```

### L1 — GPS Coherence Check

```python
async def check_l1_gps(rider_id: UUID, zone_id: str) -> tuple[int, str, str]:
    """
    Check if rider's last known location is within 5km of disruption zone.
    
    Returns: (score: 0|30, result: 'pass'|'fail'|'skip', detail: str)
    
    Logic:
    - Get rider's last GPS poll from Redis (key: f"rider_gps:{rider_id}")
    - If no GPS data → 'skip' → award FULL points (benefit of doubt, RULE not defined otherwise)
    - Calculate Haversine distance between rider GPS and zone centroid
    - If distance <= 5.0 km → pass → 30 points
    - If distance > 5.0 km → fail → 0 points, detail = f"LOCATION_MISMATCH: {distance:.1f}km from zone"
    """
    GPS_MAX_DISTANCE_KM = 5.0
```

### L2 — Weather Cross-Verify

```python
async def check_l2_weather(zone_id: str, trigger_event_id: UUID) -> tuple[int, str, str]:
    """
    Re-query Open-Meteo at the time of claim to confirm weather.
    Also run CNN verify if available (Phase 3).
    
    Returns: (score: 0|30, result, detail)
    
    Logic:
    - Fetch current rain + AQI for zone from cache (use cached value — same as what triggered MSC)
    - If rain >= RAIN_THRESHOLD or AQI >= AQI_THRESHOLD → pass → 30 points
    - If both below threshold → fail → 0 points (weather cleared before claim processed)
    - If CNN available: check cnn_agrees_with_api
      - If CNN says 'clear' but API said 'heavy_rain' → override: fail (CNN wins)
    """
```

### L3 — Earnings Anomaly (Z-Score)

```python
async def check_l3_earnings(rider_id: UUID) -> tuple[int, str, str]:
    """
    Check if rider's recent earnings suggest they were NOT actually disrupted.
    
    Returns: (score: 0|25, result, detail)
    
    Logic:
    - Get rider's last 4 weeks of daily earnings from DB
    - Calculate mean and std of daily earnings
    - Get current week earnings up to today
    - If current week daily average > (mean + 1.5 * std) → suspicious → 0 points
      Detail: f"EARNINGS_SPIKE: week avg ₹{weekly_avg} vs baseline ₹{baseline}"
    - Otherwise → pass → 25 points
    
    Edge case: If rider has < 2 weeks of history → skip → award full 25 points
    """
    Z_SCORE_THRESHOLD = 1.5
```

### L4 — Cluster / Ring Detection

```python
async def check_l4_cluster(rider_id: UUID, zone_id: str, detected_at: datetime) -> tuple[int, str, str]:
    """
    DBSCAN-based ring detection.
    Check if this claim is part of a suspicious cluster of simultaneous claims.
    
    Returns: (score: 0|15, result, detail)
    
    Logic:
    - Get all claims created within 30 minutes of this claim, in same zone
    - If count >= CLUSTER_SUSPICION_COUNT (5):
        - Verify MSC was genuinely active for this zone at that time
        - If MSC was confirmed → pass (legitimate mass event) → 15 points
        - If MSC was NOT confirmed → suspicious ring → 0 points
          Detail: f"RING_DETECTED: {count} claims in {zone_id} within 30min, MSC unconfirmed"
    - If count < 5 → pass → 15 points
    
    Implementation:
    from sklearn.cluster import DBSCAN
    Use lat/lon of claims to cluster. eps=0.01 (approx 1km), min_samples=5
    """
    CLUSTER_SUSPICION_COUNT = 5
    CLUSTER_TIME_WINDOW_MINUTES = 30
```

### Routing Decision

```python
def route_claim(confidence_score: int) -> str:
    if confidence_score >= CONFIDENCE_THRESHOLDS['auto_approve']:
        return 'auto_approved'
    elif confidence_score >= CONFIDENCE_THRESHOLDS['flag_approve']:
        return 'flagged'     # Pay but flag
    elif confidence_score >= CONFIDENCE_THRESHOLDS['hold']:
        return 'held'        # Human review
    else:
        return 'rejected'    # RULE-17: no exceptions below 35
```

---

## 8. PAYOUT ENGINE — EARNINGS DNA

**File:** `backend/services/payout_engine.py`

### Formula

```python
"""
Payout = BHE × DW × ZIF × CF

BHE  = Baseline Hourly Earning (paise)
       = rider.self_reported_daily_earning_paise / rider.work_hours_per_day
       work_hours_per_day = work_hours_end - work_hours_start

DW   = Disruption Window (hours)
       = min(trigger_event.duration_hours, MAX_DISRUPTION_WINDOW_HOURS)
       MAX_DISRUPTION_WINDOW_HOURS = 8 (caps at 8 hours per event)

ZIF  = Zone Impact Factor
       = zone.base_zif (from zones.json), bounded [0.60, 1.00]
       Future: adjusted weekly by LSTM forecast

CF   = Coverage Factor
       = 0.70 if trigger_event.signals_confirmed == 2
       = 0.85 if trigger_event.signals_confirmed >= 3

Final payout = min(BHE × DW × ZIF × CF, policy.coverage_cap_paise)
"""

MAX_DISRUPTION_WINDOW_HOURS = 8

async def calculate_payout(rider: Rider, policy: Policy, trigger_event: TriggerEvent) -> dict:
    bhe = rider.self_reported_daily_earning_paise / (rider.work_hours_end - rider.work_hours_start)
    dw = min(trigger_event.duration_hours or 4.0, MAX_DISRUPTION_WINDOW_HOURS)
    zone = get_zone(trigger_event.zone_id)
    zif = max(ZIF_MINIMUM, min(ZIF_MAXIMUM, zone['base_zif']))
    cf = COVERAGE_FACTOR_HIGH if trigger_event.signals_confirmed >= 3 else COVERAGE_FACTOR_STANDARD

    calculated = int(bhe * dw * zif * cf)
    capped = min(calculated, policy.coverage_cap_paise)

    return {
        'baseline_hourly_earning_paise': int(bhe),
        'disruption_hours': dw,
        'zone_impact_factor': zif,
        'coverage_factor': cf,
        'calculated_payout_paise': calculated,
        'capped_payout_paise': capped,
    }
```

### Razorpay Integration (Test Mode)

```python
"""
Use Razorpay Payouts API in TEST mode.
Docs: https://razorpay.com/docs/api/payouts/

Flow:
1. Create fund account for rider (UPI VPA)
2. Create payout: amount (paise), currency 'INR', mode 'UPI', purpose 'payout'
3. Poll payout status → update payout record
4. On success → update claim status to 'paid' → send notification

In DEMO_MODE: skip actual Razorpay call, simulate 3-second delay, return mock payout_id.
"""

RAZORPAY_PAYOUT_PURPOSE = "payout"
RAZORPAY_CURRENCY = "INR"
RAZORPAY_MODE = "UPI"
```

---

## 9. ML SERVICES

All 3 ML models are served as **separate FastAPI microservices** on different ports.
They are called from the main backend via HTTP (async). Never import ML models directly in main backend.

### ML Service Ports

```
Main Backend:       8000
Premium ML Service: 8001
Forecast ML Service: 8002
CNN Verify Service: 8003
```

### 9.1 FT-Transformer — Premium Pricing

**File:** `backend/ml/premium/model.py`

```python
"""
Model: Feature Tokenizer Transformer (FT-Transformer)
Paper: Revisiting Deep Learning Models for Tabular Data (Gorishniy et al. 2021)
Implementation: Use rtdl library (pip install rtdl) or implement from scratch with PyTorch.

Input features (7 features):
  1. zone_risk_score          float  0.0–1.0  (from zones.json historical disruption rate)
  2. aqi_exposure_score       float  0.0–1.0  (zone AQI > 200 days / 365)
  3. work_hours_per_day       float  4–16
  4. work_days_per_week       int    1–7
  5. season_multiplier        float  0.85–1.20 (monsoon=1.15, summer=0.90, neutral=1.00)
  6. claim_history_count      int    0–20
  7. daily_earning_bucket     int    0–4  (bucket: 0=<500, 1=500-800, 2=800-1200, 3=1200-1600, 4=>1600)

Output:
  weekly_premium_paise: int (clamped to [MIN_PREMIUM_PAISE, MAX_PREMIUM_PAISE])
  attention_weights: list of 7 floats (one per feature) — these ARE the XAI factors

Training:
  Dataset: 50,000 synthetic rider profiles (see synthetic_data.py)
  Labels: premium calculated by formula then perturbed with ±10% noise
  Loss: MSELoss on premium value
  Optimizer: AdamW, lr=1e-4, weight_decay=1e-5
  Epochs: 50, batch_size=256
  GPU: CUDA if available
"""

# Inference endpoint
"""
POST http://localhost:8001/predict
Request: {
  "zone_id": "BTM_LAYOUT",
  "aqi_exposure_score": 0.42,
  "work_hours_per_day": 12,
  "work_days_per_week": 6,
  "season_multiplier": 1.15,
  "claim_history_count": 0,
  "daily_earning_bucket": 2
}
Response: {
  "premium_paise": 6700,
  "attention_weights": {
    "aqi_zone_history": 0.34,
    "monsoon_season": 0.27,
    "zone_risk_score": 0.21,
    "claim_history": 0.18
  }
}
"""
```

**Synthetic Data Generator** — `backend/ml/premium/synthetic_data.py`

```python
"""
Generate 50,000 rider profiles for training.
Save to: data/synthetic_riders.csv

Columns: zone_id, aqi_exposure_score, work_hours_per_day, work_days_per_week,
         season_multiplier, claim_history_count, daily_earning_bucket,
         target_premium_paise

Generation rules:
- zone_id: sample from zones.json with weights proportional to population
- aqi_exposure_score: Beta(2,5) distribution (most riders have low-med exposure)
- work_hours_per_day: Normal(12, 2), clipped [6, 16]
- work_days_per_week: Categorical([5,6,7], probs=[0.2, 0.5, 0.3])
- season_multiplier: 1.15 if month in [6,7,8,9], 0.90 if month in [3,4,5], else 1.00
- claim_history_count: Poisson(0.3) clipped to [0, 10]
- daily_earning_bucket: Categorical([0,1,2,3,4], probs=[0.05,0.25,0.45,0.20,0.05])
- target_premium_paise: rule-based formula then add Normal(0, 300) noise
"""
```

### 9.2 LSTM — Disruption Forecaster

**File:** `backend/ml/forecast/model.py`

```python
"""
Model: 3-layer LSTM
Purpose: Predict next 7 days' disruption probability per Bengaluru zone

Input sequence: 90 days of daily features per zone (sliding window)
  Features per day:
    - max_rainfall_mm
    - mean_aqi
    - order_drop_pct (synthetic)
    - day_of_week (0–6)
    - month (1–12)
    - is_festival (binary — pre-seeded festival calendar)
    - historical_claim_count (synthetic)
  Total input: 90 × 7 = 630 per zone

Architecture:
  LSTM(input_size=7, hidden_size=128, num_layers=3, dropout=0.2, batch_first=True)
  Linear(128, 7)  → outputs disruption probability for next 7 days
  Sigmoid activation on output

Training:
  Dataset: 3 years of synthetic Bengaluru weather data (see synthetic_weather.py)
  Loss: BCELoss (binary cross-entropy — disruption yes/no per day)
  Optimizer: Adam, lr=1e-3
  Epochs: 100, batch_size=32
  GPU: CUDA if available

Inference endpoint:
POST http://localhost:8002/forecast
Request: { "zone_id": "BTM_LAYOUT" }
Response: {
  "zone_id": "BTM_LAYOUT",
  "forecasts": [
    {"date": "2026-03-23", "disruption_probability": 0.73, "risk_level": "high"},
    {"date": "2026-03-24", "disruption_probability": 0.68, "risk_level": "high"},
    ...7 days
  ]
}
"""
```

**Synthetic Weather Generator** — `backend/ml/forecast/data_prep.py`

```python
"""
Generate 3 years (2023-2025) of daily weather data for all 10 Bengaluru zones.
Save to: data/synthetic_weather.csv

Rules:
- Monsoon (Jun–Sep): P(rainfall>8mm) = 0.45, mean_aqi = 85
- Summer (Mar–May): P(rainfall>8mm) = 0.05, mean_aqi = 120
- Winter (Nov–Feb): P(rainfall>8mm) = 0.10, mean_aqi = 95
- Diwali week (Oct/Nov): mean_aqi += 80
- Zones near lakes (Hebbal, HSR): +0.1 rainfall probability
- Festival calendar: Diwali, Kannada Rajyotsava, IPL final weeks
"""
```

### 9.3 MobileNetV3 — CNN Satellite Verification

**File:** `backend/ml/cnn_verify/model.py`

```python
"""
Model: MobileNetV3-Small (pre-trained on ImageNet, fine-tuned)
Purpose: Classify satellite weather tiles into 4 weather categories

Classes:
  0: clear           (no significant cloud cover)
  1: light_rain      (some cloud cover, < 8mm/hr equivalent)
  2: heavy_rain      (dense cloud cover, > 8mm/hr equivalent)
  3: flood_risk      (extreme cloud cover + historical flood zones)

Input: RGB satellite tile image, resized to 224×224
Output: softmax probabilities over 4 classes

Fine-tuning:
  Base: torchvision.models.mobilenet_v3_small(weights='IMAGENET1K_V1')
  Freeze all layers except: classifier[-1] and last 2 conv blocks
  Replace classifier[-1]: Linear(1024, 4) + Softmax
  Loss: CrossEntropyLoss
  Optimizer: AdamW, lr=5e-5 (small — fine-tuning only)
  Epochs: 20, batch_size=32
  Data augmentation: RandomHorizontalFlip, RandomRotation(15), ColorJitter

Training data:
  Source: NASA POWER satellite imagery for Bengaluru region
  Labels: Cross-referenced with ground truth rainfall (IMD data)
  Size: ~8,000 labeled tiles (can augment to ~24,000)
  Split: 70/15/15 train/val/test

Inference endpoint:
POST http://localhost:8003/verify
Content-Type: multipart/form-data
Body: image file (PNG/JPEG satellite tile)
Response: {
  "classification": "heavy_rain",
  "confidence": 0.91,
  "probabilities": {
    "clear": 0.02, "light_rain": 0.05, "heavy_rain": 0.91, "flood_risk": 0.02
  },
  "agrees_with_api": true,       -- true if classification matches MSC signal
  "inference_ms": 145
}
"""
```

---

## 10. SYNTHETIC DATA GENERATOR

### Order Volume Mock Engine

**File:** `backend/services/order_volume_service.py`

```python
"""
This service simulates the Zomato/Swiggy order volume API.
It generates realistic order volumes with:
  - Time-of-day patterns
  - Day-of-week patterns
  - Weather correlation
  - Zone-level baseline differences

Time-of-day multipliers:
  00–06:  0.05  (near zero)
  06–09:  0.40  (breakfast ramp-up)
  09–11:  0.65  (late breakfast)
  11–14:  1.00  (lunch peak)
  14–17:  0.45  (afternoon slump)
  17–19:  0.70  (evening ramp)
  19–22:  0.95  (dinner near-peak)
  22–24:  0.30  (late night)

Day-of-week multipliers:
  Monday:    0.85
  Tuesday:   0.80
  Wednesday: 0.85
  Thursday:  0.90
  Friday:    1.05
  Saturday:  1.15
  Sunday:    1.10

Weather correlation:
  rainfall < 3mm/hr:    order_multiplier = 1.00 (no effect)
  rainfall 3–8mm/hr:    order_multiplier = 0.80 (light reduction)
  rainfall > 8mm/hr:    order_multiplier = 0.58 (significant drop)
  aqi > 200:            order_multiplier *= 0.82

Zone baselines (relative to city average):
  BTM_LAYOUT:    1.10
  KORAMANGALA:   1.25
  INDIRANAGAR:   1.20
  WHITEFIELD:    0.90
  JAYANAGAR:     0.95
  MARATHAHALLI:  0.85
  HSR_LAYOUT:    1.05
  ELECTRONIC_CITY: 0.75
  HEBBAL:        0.88
  JP_NAGAR:      0.92

4-week baseline: average of same day (by day-of-week) across last 4 weeks
Order drop pct = max(0, 1 - (current_volume / baseline_volume))
"""

async def get_drop_pct(zone_id: str) -> float:
    """Return simulated order drop percentage for zone. Uses Redis cache (30min TTL)."""
```

---

## 11. EXTERNAL API INTEGRATION

### Open-Meteo (Weather + AQI)

**File:** `backend/services/weather_service.py`

```python
"""
Open-Meteo Forecast API: https://api.open-meteo.com/v1/forecast
Open-Meteo Air Quality API: https://air-quality-api.open-meteo.com/v1/air-quality

No API key required. Free tier. No credit card.

Rainfall endpoint:
GET https://api.open-meteo.com/v1/forecast
  ?latitude={lat}&longitude={lon}
  &current=precipitation,rain
  &timezone=Asia/Kolkata

AQI endpoint:
GET https://air-quality-api.open-meteo.com/v1/air-quality
  ?latitude={lat}&longitude={lon}
  &current=european_aqi
  &timezone=Asia/Kolkata

Cache strategy:
  Redis key: f"weather:{zone_id}:rain"    TTL: 2100 seconds (35 min)
  Redis key: f"weather:{zone_id}:aqi"     TTL: 2100 seconds (35 min)
  
  On API failure: return cached value with source='cache'
  On cache miss + API failure: return DEMO_FALLBACK_VALUES
  
  DEMO_FALLBACK_VALUES = {
    'BTM_LAYOUT': {'rainfall_mm_hr': 14.2, 'aqi_value': 218}
    -- all other zones: {'rainfall_mm_hr': 0.0, 'aqi_value': 85}
  }

Timeout: 5 seconds. Retry: 1 time with 1 second delay.
"""
```

### Firebase Auth

```python
"""
Use firebase-admin SDK (pip install firebase-admin)
Verify ID token from frontend.

On backend startup:
  firebase_admin.initialize_app(credentials.Certificate(FIREBASE_SERVICE_ACCOUNT_PATH))

Verify token:
  decoded = auth.verify_id_token(firebase_token)
  firebase_uid = decoded['uid']
  phone = decoded.get('phone_number')  -- E.164 format

In DEMO_MODE:
  Skip Firebase entirely. Return hardcoded demo rider.
"""
```

### Razorpay (Test Mode)

```python
"""
pip install razorpay

Client:
  client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
  -- Use TEST mode keys from .env

Payout flow:
  1. Create contact: client.contact.create({...})
  2. Create fund account with UPI VPA: client.fund_account.create({...})
  3. Create payout: client.payout.create({
       "account_number": RAZORPAY_ACCOUNT_NUMBER,
       "fund_account_id": fund_account_id,
       "amount": amount_paise,
       "currency": "INR",
       "mode": "UPI",
       "purpose": "payout",
       "queue_if_low_balance": True,
       "narration": f"GigShield claim payout - {claim_id[:8]}"
     })

In DEMO_MODE: 
  Sleep 2 seconds. Return mock payout_id = f"mock_payout_{uuid4().hex[:8]}"
"""
```

---

## 12. FRONTEND — RIDER PWA

**Stack:** React 18 + Vite + Tailwind CSS + Workbox
**Target:** Mobile-first PWA (375px minimum width)
**Color Scheme:** Dark navy (#002E4E) primary, gold (#E89B0A) accent, white text

### PWA Configuration

```json
// public/manifest.json
{
  "name": "GigShield",
  "short_name": "GigShield",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#002E4E",
  "theme_color": "#002E4E",
  "icons": [
    {"src": "/icon-192.png", "sizes": "192x192", "type": "image/png"},
    {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png"}
  ]
}
```

### Page Specifications

#### Onboarding.jsx

```
Purpose: PRF data collection — 5 questions in step format

Step 1: Phone OTP (Firebase) — show number field + OTP input
Step 2: Name entry
Step 3: Zone selection — dropdown of 10 Bengaluru zones
Step 4: Platform, work hours, days/week — inline form
Step 5: Daily earning estimate — slider with preset buckets

Design:
  - Full screen, one question per screen (swipeable)
  - Progress bar at top (1/5, 2/5, etc.)
  - Navy background, white text, gold CTA button
  - "Skip" not allowed — all 5 must be answered

On submit → POST /riders/onboard → navigate to PremiumPanel
```

#### PremiumPanel.jsx

```
Purpose: Show ML-calculated premium with XAI breakdown

Layout:
  Top: Large number "₹67/week" centered (gold)
  Middle: Horizontal bar chart — 4 factors with % labels
  Bottom: "This looks right" / "Tell me more" buttons

XAI Bar Chart:
  Each bar fills left-to-right proportionally to weight
  Labels: factor name (left) + % (right)
  Colors: gold bars, navy background
  Animation: bars grow from 0 on mount (CSS transition, 600ms)

"Tell me more" → expand modal explaining each factor in plain language:
  "AQI Zone History (34%): Your zone BTM Layout has historically had 
   high air pollution during October–December. This increases your premium slightly."
```

#### Simulator.jsx (Coverage Simulator)

```
Purpose: Let rider preview payouts for different scenarios

Controls:
  - Disruption hours: slider 1–8
  - Signal count: toggle buttons (2 signals / 3 signals)
  - Zone: auto-filled from their zone

Live output (updates as slider moves):
  "If disruption lasts 4 hours..."
  Payout: ₹335
  Breakdown (expandable):
    Baseline hourly: ₹137
    × 4 hours
    × Zone factor: 0.87
    × Coverage: 70%
    = ₹335

CTA: "Get Covered →" → navigate to PolicySelect
```

#### PolicySelect.jsx

```
Purpose: Choose from 4 policy tiers

Layout: Vertical stack of 4 cards (mobile) or 2×2 grid (tablet+)

Each card shows:
  - Tier name (bold)
  - Price (large gold)
  - Coverage cap
  - MSC threshold
  - "RECOMMENDED" badge on Balanced tier

On select → POST /policies/create → navigate to Dashboard
```

#### Dashboard.jsx

```
Purpose: Home screen for active rider

Sections:
  1. Status Banner: "🟢 COVERED THIS WEEK" or "🔴 NOT COVERED"
     Sub-text: "₹49 deducted Monday · ₹900 coverage active"
  
  2. Zone Risk Card: "YOUR ZONE THIS WEEK"
     Zone name + risk level (Low/Medium/High) from LSTM forecast
     Color: green/orange/red based on risk level
  
  3. Active Disruption Banner (only when MSC active):
     "⚡ Disruption detected in BTM Layout"
     "Claim processing... Payout: ₹333"
     Live confidence score meter (animated needle)
  
  4. Recent Claims: Last 3 claims, each showing amount + status

  5. Quick Actions: "Simulate Payout" | "View History"
```

#### ClaimStatus.jsx

```
Purpose: Live view of a claim in progress

Shows:
  1. Status pill: PROCESSING / APPROVED / PAID / REJECTED
  2. Confidence Score Gauge:
     - Semicircle gauge (SVG or recharts RadialBarChart)
     - Needle pointing to score value
     - Green zone (85–100), Yellow (60–84), Orange (35–59), Red (0–34)
     - 4 labeled segments around gauge
  3. Fraud Check Breakdown:
     4 rows — each with check name, score, and PASS/FAIL badge
  4. Payout amount (large, gold)
  5. UPI handle display

Auto-refresh every 10 seconds via polling.
```

#### ClaimHistory.jsx / ClaimTimeline component

```
Purpose: Full audit trail for a claim

Visual: Vertical timeline with dots and lines

Each event:
  - Icon (rain cloud / AQI gauge / checkmark / ₹)
  - Time (IST display — convert from UTC in formatters.js)
  - Bold event name
  - Sub-text detail

Events to show:
  rain_detected | aqi_confirmed | order_drop_confirmed | msc_confirmed |
  claim_created | fraud_check_started | gps_checked | earnings_checked |
  cluster_checked | fraud_decision | payout_initiated | payout_sent

Rejected claims show rejection reason in red at the bottom.
```

### Key Components

#### ConfidenceGauge.jsx

```jsx
/*
SVG-based semicircle gauge.
Props: score (0–100), animating (bool)

Segments:
  0–34:  red    (#C0392B)
  35–59: orange (#E67E22)
  60–84: yellow (#F39C12)
  85–100: green (#1A7A35)

Needle: thin line from center, rotates based on score
  score 0   = -90deg (leftmost)
  score 50  = 0deg (center)
  score 100 = +90deg (rightmost)

Animation: useEffect with requestAnimationFrame, 800ms easing
*/
```

#### MSCStatusCard.jsx

```jsx
/*
Shows 3 signal cards side by side.
Each card: signal name + current value + threshold + status dot

Signal cards:
  🌧 Rain:      "14.2 mm/hr > 8mm/hr ✅"
  😷 AQI:       "218 > 200 ✅"
  📦 Orders:    "41% drop > 35% ✅"

When all 3 active: card glows gold border, text "CONFLUENCE CONFIRMED"
When 0–1 active: "Monitoring... No disruption"
*/
```

---

## 13. FRONTEND — INSURER DASHBOARD

**Stack:** React 18 + Vite + Tailwind + Leaflet.js + Recharts
**Target:** Desktop-first (min 1280px), responsive to tablet

### Overview.jsx

```
Top row — 4 KPI cards:
  Active Riders | Premium Collected | Claims Paid | Loss Ratio
  (animated number counters on load)

Middle row:
  Left:  Recharts LineChart — daily loss ratio trend (last 30 days)
  Right: Recharts PieChart — claim status breakdown (approved/flagged/held/rejected)

Bottom row:
  Left:  Top 3 high-risk zones this week (from LSTM forecast)
  Right: Last 5 fraud queue items (quick preview)
```

### RiskHeatmap.jsx

```
Full-width Leaflet.js map centered on Bengaluru (12.9716, 77.5946), zoom 12

Each zone rendered as:
  - Circle marker at zone centroid
  - Radius proportional to expected_claims
  - Fill color: green (#1A7A35) <40%, orange (#E67E22) 40–70%, red (#C0392B) >70%
  - Opacity 0.6
  - On click: popup showing zone name + probability % + expected claims + reserve estimate

Legend: bottom-right, color gradient from green to red, labeled

Data: GET /insurer/heatmap — refresh every 5 minutes
```

### FraudQueue.jsx

```
Table with columns:
  Rider Name | Zone | Claim Amount | Confidence Score | Score Breakdown | Time Waiting | Actions

Score Breakdown: mini 4-segment bar (GPS|Weather|Earnings|Cluster) each colored by pass/fail

Actions:
  APPROVE button (green) → POST /insurer/fraud-queue/{id}/decision {decision: "approve"}
  REJECT button (red) → same endpoint with reject + required note field

Sorted by: time waiting (oldest first)
Auto-refresh: every 30 seconds
```

### ClaimsViewer.jsx

```
Full claims table with filters:
  Status dropdown | Zone dropdown | Date range picker | Search by rider name

Columns: Rider | Zone | Amount | Confidence | Status | Created | Actions (view timeline)

Row click → expand inline to show ClaimTimeline component

Export button: download CSV of filtered results
```

---

## 14. NOTIFICATION SYSTEM

**File:** `backend/services/notification_service.py`

```python
"""
Phase 1: Mock SMS (print to console + store in DB)
Phase 2+: Integrate real SMS gateway (Twilio or MSG91 free tier)

In DEMO_MODE: show notifications in-app as toast banners instead of SMS

Notification types:

1. PAYOUT_SENT
   Trigger: payout.status = 'success'
   Template: "GigShield: ₹{amount} paid to your UPI. Stay safe! Claim: GS-{claim_short_id}"

2. DISRUPTION_DETECTED
   Trigger: trigger_event created for rider's zone
   Template: "GigShield: ⚡ Disruption in {zone_name}. Auto-processing your payout of ~₹{estimate}."

3. CLAIM_REJECTED
   Trigger: fraud_decision = 'rejected'
   Template: "GigShield: Claim GS-{id} rejected. Reason: {reason_code}. Contact support if incorrect."

4. CLAIM_ON_HOLD
   Trigger: fraud_decision = 'held'
   Template: "GigShield: Claim GS-{id} under review. Decision within 24 hours."

5. WEEKLY_COVERAGE_SUMMARY (every Monday 06:30 IST)
   Template: "GigShield: Week starts! ₹{premium} deducted. Zone risk: {risk_level}. You're covered."

6. PRE_DISRUPTION_WARNING (from LSTM forecast, Sunday 20:00 IST)
   Template: "⚠️ GigShield: High disruption probability in {zone} this week ({pct}%). Coverage active."

All SMS logs stored in audit_logs with entity_type='sms'
"""
```

---

## 15. DEMO MODE & RESILIENCE LAYER

### Demo Mode (DEMO_MODE=true)

**File:** `backend/config/settings.py`

```python
DEMO_MODE: bool = False  # Set via DEMO_MODE=true env var

DEMO_RIDER = {
    "phone": "+919999999999",
    "name": "Ravi Kumar (Demo)",
    "zone_id": "BTM_LAYOUT",
    "platform": "swiggy",
    "work_hours_start": 10,
    "work_hours_end": 22,
    "work_days_per_week": 6,
    "self_reported_daily_earning_paise": 110000,  # ₹1,100
}

DEMO_EVENTS = {
    "rain_order_drop": {
        "zone_id": "BTM_LAYOUT",
        "rainfall_mm_hr": 14.2,
        "aqi_value": 85,
        "order_drop_pct": 0.41,
        "signals_confirmed": 2,
        "msc_status": "standard"
    },
    "aqi_order": {
        "zone_id": "BTM_LAYOUT",
        "rainfall_mm_hr": 2.1,
        "aqi_value": 218,
        "order_drop_pct": 0.38,
        "signals_confirmed": 2,
        "msc_status": "standard"
    },
    "full_3_signal": {
        "zone_id": "BTM_LAYOUT",
        "rainfall_mm_hr": 18.5,
        "aqi_value": 240,
        "order_drop_pct": 0.52,
        "signals_confirmed": 3,
        "msc_status": "high"
    },
    "fraud_attempt": {
        "zone_id": "BTM_LAYOUT",
        "rainfall_mm_hr": 12.0,
        "aqi_value": 95,
        "order_drop_pct": 0.39,
        "fraud_gps_override": True,      # L1 will fail
        "fraud_gps_distance_km": 8.2,
        "signals_confirmed": 2,
        "msc_status": "standard"
    }
}
```

### API Resilience Layer

**File:** `backend/services/weather_service.py`

```python
"""
Resilience order for every external API call:
  1. Try Redis cache (TTL check)
  2. If cache miss or expired → call live API (5s timeout, 1 retry)
  3. If API fails → return stale cache value (ignore TTL)
  4. If no stale cache → return DEMO_FALLBACK_VALUES
  5. Log all fallbacks to audit_log with actor='resilience_layer'

Never raise an exception to the caller. Always return a value.
"""

async def get_rainfall(lat: float, lon: float, zone_id: str) -> dict:
    """Returns: {'value': float, 'source': 'live'|'cache'|'stale'|'fallback'}"""
```

### Frontend Demo Toggle

```jsx
// In all API calls — detect DEMO_MODE from env var
// Vite: VITE_DEMO_MODE=true
// When true:
//   - Skip Firebase OTP — use demo credentials
//   - Show "DEMO MODE" banner at top of every screen
//   - "Fire Disruption" floating action button appears on Dashboard
//   - All notifications are in-app toast (not SMS)
```

---

## 16. DOCKER & INFRASTRUCTURE

**File:** `infra/docker-compose.yml`

```yaml
version: '3.9'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: gigshield
      POSTGRES_USER: gigshield
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U gigshield"]
      interval: 10s

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru

  backend:
    build: ./backend
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    env_file: .env
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_started
    volumes:
      - ./backend:/app

  ml-premium:
    build: ./backend/ml/premium
    command: uvicorn serve:app --host 0.0.0.0 --port 8001
    ports:
      - "8001:8001"
    volumes:
      - ./backend/ml/premium:/app
      - ./data:/data
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

  ml-forecast:
    build: ./backend/ml/forecast
    command: uvicorn serve:app --host 0.0.0.0 --port 8002
    ports:
      - "8002:8002"
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

  ml-cnn:
    build: ./backend/ml/cnn_verify
    command: uvicorn serve:app --host 0.0.0.0 --port 8003
    ports:
      - "8003:8003"
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

  rider-pwa:
    build: ./frontend/rider-pwa
    ports:
      - "3000:80"

  insurer-dashboard:
    build: ./frontend/insurer-dashboard
    ports:
      - "3001:80"

volumes:
  postgres_data:
```

---

## 17. ENVIRONMENT VARIABLES

```bash
# .env.example — copy to .env and fill in values

# App
APP_ENV=development               # development | production
DEMO_MODE=false                   # true to enable demo mode (RULE-09, RULE-25)
SECRET_KEY=changeme               # JWT signing key (32+ chars)
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Database
DATABASE_URL=postgresql+asyncpg://gigshield:password@postgres:5432/gigshield
POSTGRES_PASSWORD=changeme

# Redis
REDIS_URL=redis://redis:6379/0

# Firebase
FIREBASE_SERVICE_ACCOUNT_PATH=./config/firebase-service-account.json
FIREBASE_PROJECT_ID=gigshield-dev

# Razorpay (TEST MODE ONLY — never production)
RAZORPAY_KEY_ID=rzp_test_XXXX
RAZORPAY_KEY_SECRET=XXXX
RAZORPAY_ACCOUNT_NUMBER=XXXXXXXXXXX

# ML Services
ML_PREMIUM_URL=http://ml-premium:8001
ML_FORECAST_URL=http://ml-forecast:8002
ML_CNN_URL=http://ml-cnn:8003
ML_TIMEOUT_SECONDS=10

# Scheduler
MSC_POLL_INTERVAL_MINUTES=30
FORECAST_UPDATE_CRON=0 20 * * 0   # Sunday 20:00 UTC (Sunday 20:00 UTC = 01:30 IST Monday)
PREMIUM_DEDUCTION_CRON=30 0 * * 1  # Monday 00:30 UTC = 06:00 IST

# Logging
LOG_LEVEL=INFO

# Frontend (Vite)
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_FIREBASE_API_KEY=XXXX
VITE_FIREBASE_AUTH_DOMAIN=gigshield-dev.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=gigshield-dev
VITE_DEMO_MODE=false
```

---

## 18. BUILD ORDER — PHASE BY PHASE

Follow this order exactly. Do not skip ahead.

### PHASE 1 — SEED (Build Now)

Build in this sequence:

```
Step 1:  Set up repo structure (all folders + __init__.py files)
Step 2:  Write requirements.txt (see below for pinned versions)
Step 3:  docker-compose.yml + .env.example
Step 4:  backend/config/constants.py (ALL constants in one file)
Step 5:  backend/config/settings.py (Pydantic BaseSettings)
Step 6:  backend/db/database.py (SQLAlchemy async engine)
Step 7:  backend/models/db/*.py (all ORM models)
Step 8:  Alembic init + first migration
Step 9:  backend/cache/redis_client.py
Step 10: backend/db/seed.py (demo rider + zones)
Step 11: backend/api/middleware.py (CORS + auth)
Step 12: backend/api/routers/auth.py
Step 13: backend/api/routers/riders.py (onboard endpoint first)
Step 14: backend/services/weather_service.py (Open-Meteo + cache)
Step 15: backend/services/order_volume_service.py (mock engine)
Step 16: backend/services/trigger_engine.py (static mock version)
Step 17: backend/services/fraud_engine.py (L1 + L2 only first)
Step 18: backend/services/payout_engine.py (Earnings DNA formula)
Step 19: backend/api/routers/policies.py (create + simulator)
Step 20: backend/api/routers/claims.py
Step 21: backend/api/routers/demo.py
Step 22: backend/main.py (wire everything together)
Step 23: ML synthetic data generators (run, save CSVs)
Step 24: ml/premium/train.py (train FT-Transformer, save model)
Step 25: ml/premium/serve.py (inference FastAPI)
Step 26: backend/services/premium_service.py (calls ML service)
Step 27: frontend/rider-pwa scaffold (Vite + React + Tailwind)
Step 28: Onboarding.jsx → PremiumPanel.jsx → Simulator.jsx → PolicySelect.jsx
Step 29: Dashboard.jsx (static data first, then live)
Step 30: Test full flow end-to-end in demo mode
```

### PHASE 2 — SCALE (After Phase 1 complete)

```
Step 31: Wire live Open-Meteo API into weather_service.py
Step 32: fraud_engine.py — add L3 DBSCAN cluster detection
Step 33: Complete Confidence Score routing logic
Step 34: APScheduler jobs (30-min MSC poll + Monday deduction)
Step 35: ml/forecast/train.py (train LSTM)
Step 36: ml/forecast/serve.py
Step 37: backend/services/forecast_service.py
Step 38: Insurer dashboard scaffold
Step 39: Overview.jsx + RiskHeatmap.jsx (Leaflet)
Step 40: FraudQueue.jsx + ClaimsViewer.jsx
Step 41: ClaimStatus.jsx with live confidence gauge
Step 42: Notification system (mock SMS)
Step 43: End-to-end test with live weather data
```

### PHASE 3 — SOAR (After Phase 2 complete)

```
Step 44: ml/cnn_verify/train.py (fine-tune MobileNetV3)
Step 45: ml/cnn_verify/serve.py
Step 46: Integrate CNN into fraud_engine.py L2 check
Step 47: Reserves.jsx for insurer
Step 48: Demo mode polish (all 4 scenarios working)
Step 49: API resilience layer testing (kill Open-Meteo, verify fallback)
Step 50: Performance testing (200 riders, MSC fires, all claims processed < 30s)
Step 51: 5-minute demo video prep — wire all demo scenarios
```

---

## 19. TESTING REQUIREMENTS

Write tests for these exact scenarios:

### trigger_engine tests

```python
# test_trigger_engine.py

def test_msc_standard_2_signals():
    """Rain + AQI both above threshold → MSC standard confirmed"""

def test_msc_high_3_signals():
    """Rain + AQI + Order Drop all above threshold → MSC high confirmed"""

def test_msc_not_met_1_signal():
    """Only rain above threshold → MSC not met → no claim created"""

def test_msc_no_double_fire():
    """MSC fires, active event exists → no second claim created for same event"""

def test_msc_event_closes_when_signals_drop():
    """Signals drop below threshold → active event gets ended_at timestamp"""
```

### fraud_engine tests

```python
# test_fraud_engine.py

def test_l1_gps_pass():
    """Rider GPS within 5km of zone → 30 points"""

def test_l1_gps_fail():
    """Rider GPS 8km from zone → 0 points, reason LOCATION_MISMATCH"""

def test_l1_gps_skip_no_data():
    """No GPS data in Redis → skip → 30 points (benefit of doubt)"""

def test_l3_earnings_fail_spike():
    """Rider earned 180% of baseline this week → 0 points"""

def test_confidence_score_auto_approve():
    """All 4 layers pass → score 100 → auto_approved"""

def test_confidence_score_reject():
    """GPS fail + earnings spike → score 25 → auto rejected"""

def test_confidence_score_hold():
    """GPS fail + rest pass → score 55 → held for review"""
```

### payout_engine tests

```python
# test_payout_engine.py

def test_earnings_dna_standard():
    """₹1100 daily, 4 hrs disruption, BTM ZIF 0.87, 0.70 CF → ₹333"""
    # 137.5 * 4 * 0.87 * 0.70 = 334.65 → 334 (int truncation)

def test_earnings_dna_high():
    """Same but CF=0.85 (3 signals) → ₹406"""

def test_payout_capped_by_coverage():
    """Calculated payout exceeds coverage cap → returns cap value"""

def test_zif_minimum_enforced():
    """ZIF < 0.60 in formula → clamped to 0.60"""
```

### api tests

```python
# test_api.py

def test_onboard_rider_success():
def test_onboard_invalid_zone():
def test_create_policy_success():
def test_create_duplicate_policy_same_week():  # should reject
def test_simulator_returns_breakdown():
def test_demo_fire_event_creates_claims():
def test_claim_timeline_complete():
```

---

## 20. BUSINESS RULES — NON-NEGOTIABLE

Reference these when uncertain about any business logic decision.

```
INSURANCE RULES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Only loss of income is covered. Never: vehicle, health, life, accidents.

A rider must have an ACTIVE policy for the CURRENT WEEK to receive a payout.
  Active = status='active' AND week_start_date <= today <= week_end_date

One claim per rider per trigger event. Enforced by unique constraint:
  UNIQUE(rider_id, trigger_event_id)

Payout is calculated from self-reported earnings (RULE-03 paise).
We do not verify earnings in Phase 1. Verification is a Phase 2+ feature.

FRAUD RULES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Confidence Score < 35 is ALWAYS rejected. No human override for this band.
Scores 35–59 go to human review queue (insurer dashboard).
Scores 60–84 are paid AND flagged. Insurer sees flagged claims in queue.
Scores 85–100 are paid immediately. Insurer can audit later.

MONEY RULES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ALL money is stored as INTEGER PAISE. No floats for money anywhere in DB.
Display: divide by 100, format as ₹{amount:,.0f}
All money DB writes inside SQLAlchemy transactions (RULE-07).

TIMING RULES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
All DB timestamps: UTC.
All display timestamps: IST (UTC+5:30).
Coverage week: Monday 00:00 IST to Sunday 23:59 IST.
Premium deduction: Monday 06:00 IST.
No payout if event ended > 4 hours ago (RULE-19).

API RULES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Never expose internal UUIDs in error messages.
Never expose confidence score breakdown to rider — only final score.
Rider can see: score value + final decision + reason code (if rejected).
Rider cannot see: individual layer scores, earnings z-score, cluster flag.
Insurer CAN see: all layer scores + full fraud check detail.
```

---

## REQUIREMENTS.TXT (Pinned Versions)

```
# Core
fastapi==0.111.0
uvicorn[standard]==0.29.0
pydantic==2.7.1
pydantic-settings==2.2.1

# Database
sqlalchemy==2.0.30
asyncpg==0.29.0
alembic==1.13.1
psycopg2-binary==2.9.9

# Cache
redis==5.0.4

# Scheduler
apscheduler==3.10.4

# HTTP
httpx==0.27.0

# ML
torch==2.3.0
torchvision==0.18.0
scikit-learn==1.4.2
numpy==1.26.4
pandas==2.2.2

# Auth
firebase-admin==6.5.0

# Payment
razorpay==1.4.1

# Utilities
python-dotenv==1.0.1
python-jose[cryptography]==3.3.0
python-multipart==0.0.9
haversine==2.8.1

# Testing
pytest==8.2.0
pytest-asyncio==0.23.7
httpx==0.27.0   # async test client
```

---

## FINAL CHECKLIST BEFORE STARTING

Before writing code, confirm you understand:

- [ ] All money is in paise (integer). ₹67 = 6700 in DB.
- [ ] MSC needs 2 of the 3 CORE signals (Rain, AQI, Order Drop). Road + Civic don't count toward MSC min.
- [ ] Confidence Score < 35 = ALWAYS rejected. No exceptions.
- [ ] Demo mode is controlled by env var only. No code changes needed to switch.
- [ ] ML models are separate microservices on ports 8001/8002/8003. Never imported in main backend.
- [ ] All timestamps stored UTC. Display in IST.
- [ ] One claim per rider per trigger event (DB unique constraint enforces this).
- [ ] API resilience: Redis cache → live API → stale cache → fallback values. Never throw to caller.
- [ ] FT-Transformer produces attention weights = XAI factors (no SHAP needed).
- [ ] DBSCAN ring detection only flags if MSC was NOT confirmed for the zone (legitimate events don't trigger ring flag).

---

> **START WITH: `backend/config/constants.py`**
> Put every number in this file first. If a threshold isn't in constants.py, it doesn't exist.

---

*GigShield Master Build Specification · Guidewire DEVTrails 2026 · v1.0*
