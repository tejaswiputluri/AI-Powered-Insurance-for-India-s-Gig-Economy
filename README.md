# AI-Powered-Insurance-for-India-s-Gig-Economy
# 🛡️ GigShield — AI-Powered Parametric Income Insurance for India's Gig Workers

> **Guidewire DEVTrails 2026 — University Hackathon**  
> Persona: Food · E-Commerce · Grocery Delivery Partners · Bengaluru, India  
> Platform: Web PWA + Mobile | Stack: React · FastAPI · PostgreSQL · PyTorch

---

## 📋 Table of Contents

1. [The Problem](#1-the-problem)
2. [Our Solution — GigShield](#2-our-solution--gigshield)
3. [Persona & Scenarios](#3-persona--scenarios)
4. [Application Workflow](#4-application-workflow)
5. [Weekly Premium Model](#5-weekly-premium-model)
6. [Parametric Triggers](#6-parametric-triggers)
7. [Platform Choice — Web PWA](#7-platform-choice--web-pwa)
8. [AI/ML Integration Plan](#8-aiml-integration-plan)
9. [Tech Stack](#9-tech-stack)
10. [6-Week Development Plan](#10-6-week-development-plan)
11. [What Makes GigShield Different](#11-what-makes-gigshield-different)
12. [Repository Structure](#12-repository-structure)
13. [Adversarial Defense & Anti-Spoofing Strategy](#13-adversarial-defense--anti-spoofing-strategy)
14. [Demo Video](#14-demo-video)

---

## 1. The Problem

India's 15+ million platform-based delivery partners (Zomato, Swiggy, Blinkit, Amazon Flex, Zepto, Flipkart) are the backbone of our digital economy. Yet they are completely exposed to income loss caused by events entirely outside their control:

| Disruption | Impact |
|-----------|--------|
| Heavy rain / floods | Cannot ride safely — deliveries halted |
| Toxic AQI spike (> 200) | Unsafe outdoor conditions — platform order volume drops |
| Sudden curfew / local strike | Pickup zones become inaccessible |
| Hyper-local road blockage | Routes to restaurants / warehouses / dark stores blocked |

These workers lose **20–30% of monthly income** during such events. They have no safety net.

Current insurance products don't help:
- Health and vehicle insurance exists but covers the wrong things
- No product covers lost income from external disruptions
- Platform companies offer no compensation for weather/civic events
- Traditional claim processes are too slow and complex for daily-wage workers

**GigShield insures the one thing that matters: the income they couldn't earn.**

---

## 2. Our Solution — GigShield

GigShield is an AI-enabled parametric income insurance platform built for all three major delivery sub-categories — **Food (Zomato/Swiggy), E-Commerce (Amazon/Flipkart), and Grocery/Q-Commerce (Zepto/Blinkit)**. It:

- Calculates a **personalised weekly premium** based on each rider's risk profile using an ML model (FT-Transformer)
- Monitors **multiple real-time signals simultaneously** (weather, AQI, order volume, civic disruptions)
- **Automatically detects disruptions** and initiates payouts — no claim filing needed by the worker
- Runs a **4-layer progressive fraud detection pipeline** with a Confidence Score system (0–100)
- Provides **proactive LSTM forecasting** so riders know their risk level before the week starts
- Delivers **payouts to UPI within 4 hours** of a confirmed disruption

>  **Coverage Scope:** GigShield strictly covers **loss of income only**. Health, life, accident, and vehicle repair claims are explicitly excluded by design.

---

## 3. Persona & Scenarios

GigShield covers all three delivery segments. Each has distinct risk profiles, earning patterns, and disruption sensitivities.

---

###  Food Delivery — Primary Persona: Ravi (Swiggy, Bengaluru)

```
Name:         Ravi Kumar
City:         Bengaluru — BTM Layout zone
Platform:     Swiggy (food delivery)
Experience:   2 years active
Work hours:   10am – 10pm, 6 days/week
Avg earning:  ₹1,100/day (~₹137/hr)
Phone:        Android, budget model
Concern:      "When it rains heavily, I lose the whole day. No orders, no income."
```

**Scenario 1 — Heavy Monsoon Rain + Order Drop**

> Southwest monsoon brings 18mm/hr rainfall to BTM Layout. Swiggy order volume drops 47%. AQI normal.

GigShield Response:
- Rain signal fires  (> 8mm/hr threshold)
- Order volume drop signal fires  (> 35% below 4-week baseline)
- MSC (Multi-Signal Confluence) confirmed — 2/3 core signals active
- Earnings DNA calculates: ₹137 × 4 hrs × 0.87 ZIF × 0.70 = **₹333 payout**
- Fraud pipeline scores claim: **91/100 Confidence — Auto Approved**
- Razorpay UPI payout initiated — Ravi receives ₹333 within 4 hours
- SMS: *"GigShield paid ₹333 to your UPI. Stay safe, Ravi."*

Ravi did nothing. No form. No call. No waiting.

**Scenario 2 — AQI Spike (Diwali Season)**

> Post-Diwali AQI reaches 287 (Very Poor) across South Bengaluru. Order volume drops 38%.

- AQI signal fires  (> 200 threshold)
- Order volume drop fires 
- MSC confirmed → Payout: **₹291** — Auto-approved and sent to UPI

**Scenario 3 — Light Drizzle (NO Payout — Correct Behaviour)**

> Light intermittent rain, 3mm/hr. Orders continue normally.

- Rain signal does NOT meet threshold (< 8mm/hr) 
- Order volume normal — no drop signal 
- MSC NOT confirmed → **No payout triggered**

This scenario is as important as the payout scenarios. GigShield does not pay on every weather event — only on genuine income-disrupting confluences.

**Scenario 4 — Fraudulent Claim Attempt**

> A bad actor claims during a rain event, but GPS shows their location is 8.2km from their registered zone.

- L1 GPS Coherence check fires 
- Confidence Score: **12/100 — Auto Rejected**
- Rider notified with reason code: `LOCATION_MISMATCH`
- Claim logged in fraud audit trail

---

###  E-Commerce — Persona: Suresh (Amazon Flex, Bengaluru)

```
Name:         Suresh Nair
City:         Bengaluru — Whitefield zone
Platform:     Amazon Flex
Experience:   1.5 years
Work hours:   8am – 8pm, 5 days/week
Avg earning:  ₹900/day
Concern:      "When there's a strike, I can't even reach the pickup hub."
```

**Scenario — Local Transport Strike / Bandh**

> A transport union strike blocks all major arterial roads in Whitefield. Suresh cannot reach the Amazon pickup hub.

- Civic Disruption signal fires ✅ (verified bandh in rider's PIN cluster)
- GPS confirms Suresh attempted to reach hub and was blocked ✅
- MSC confirmed → Payout: **₹630 (70% of daily rate)**

**Scenario — Zone Flooding**

> Flooding in Electronic City causes Amazon to suspend deliveries in 3 zones.

- Flood alert fires ✅ (Red Alert issued for district)
- Platform suspension signal fires ✅ (zero order assignments for > 2 hours)
- MSC at HIGH confidence → Payout: **₹765 (85% — 3-signal event)**

---

### 🛒 Grocery / Q-Commerce — Persona: Priya (Blinkit, Bengaluru)

```
Name:         Priya Sharma
City:         Bengaluru — Koramangala zone
Platform:     Blinkit (Zepto backup)
Experience:   8 months
Work hours:   9am – 9pm, 7 days/week
Avg earning:  ₹700/day
Concern:      "AQI goes crazy in winter. I can't breathe and Blinkit orders drop to zero."
```

**Scenario — Severe AQI + Dark Store Closure**

> AQI reaches 340 in Koramangala during crop stubble burning season. Blinkit dark store suspends operations.

- AQI signal fires ✅ (> 200 threshold)
- Platform zero-order signal fires ✅
- Civic closure signal fires ✅
- 3-signal MSC → HIGH confidence → Payout: **₹595 (85% of daily rate)**

---

## 4. Application Workflow

```
┌─────────────────────────────────────────────────────────────────────┐
│                          RIDER JOURNEY                              │
└─────────────────────────────────────────────────────────────────────┘

  [1] ONBOARDING
      Rider scans QR code (shared by zone captain / platform)
      → Firebase OTP phone login (no password required)
      → 5-question PRF form (zone, platform, work hours, daily earnings, sub-category)
      → FT-Transformer calculates personalised weekly premium
      → XAI panel shows:
            "Your premium is ₹67/week because:
             AQI zone history (34%) · Monsoon season (27%) · Zone risk score (21%)"
      → Coverage Simulator: "If 4hr rain in BTM Layout → estimated payout: ₹335"
      → Rider selects policy tier (Basic / Balanced / Pro / Aggressive)
      → Policy created — premium scheduled for Monday auto-deduction

         ↓

  [2] ACTIVE COVERAGE (Every Week — Mon to Sun)
      Monday: ₹29–₹99 auto-deducted from platform payout (zero friction)
      App shows: active coverage status, this week's risk forecast, claim history

         ↓

  [3] DISRUPTION DETECTION (Automated — Every 30 Minutes)
      Trigger Engine polls simultaneously:
        → Open-Meteo API:         rainfall mm/hr at rider GPS zone
        → Open-Meteo AQI API:     air quality index at rider zone
        → Order Volume Engine:    platform order drop vs. 4-week baseline (mock)
        → Road Disruption Feed:   route blockage simulation (mock, real Bengaluru routes)
        → Civic Alert Feed:       bandh/curfew for rider PIN cluster (simulated)

      MSC Evaluator: are 2+ signals above threshold simultaneously?
      If YES → claim auto-filed on rider's behalf

         ↓

  [4] FRAUD PIPELINE (< 1 second)
      L1: GPS Coherence        — rider within 5km of active disruption zone?
      L2: Behavioural Anomaly  — z-score on earnings baseline (normal week so far?)
      L3: Spatial Ring Detect  — DBSCAN clusters of simultaneous nearby claims
      L4: CNN Satellite Verify — MobileNetV3 confirms weather API via satellite tile

      Confidence Score calculated (0–100):
        ≥ 85   → Auto-Approve
        60–84  → Auto-Approve + flag for audit
        35–59  → Hold — human review queue (24 hrs)
        < 35   → Auto-Reject — reason code sent to rider

         ↓

  [5] PAYOUT
      Earnings DNA formula → exact rupee amount calculated
      Razorpay Test Mode → UPI payout initiated
      SMS notification sent to rider
      Claim Timeline logged (full audit trail in DB)

┌─────────────────────────────────────────────────────────────────────┐
│                        INSURER JOURNEY                              │
└─────────────────────────────────────────────────────────────────────┘

  Insurer Dashboard shows:
  → Live loss ratio tracker
  → LSTM 7-day forecast heatmap (Bengaluru zones coloured by risk level)
  → Fraud queue with Confidence Scores and reason codes
  → Claim timeline viewer with full audit trail
  → Weekly reserve estimate
  → Predictive analytics: "Expected 73 claims next week — BTM Layout HIGH RISK"
  → Sub-category breakdown: Food vs E-Com vs Grocery claim distribution
```

---

## 5. Weekly Premium Model

> The problem statement mandates weekly pricing. Every aspect of GigShield's financial model is structured on a 7-day cycle — matching how gig workers actually think about money and how platforms actually pay them.

### Premium Tiers

| Tier | Weekly Premium | Coverage Cap | MSC Threshold | Best For |
|------|---------------|--------------|---------------|----------|
| Basic | ₹29/week | Up to ₹500/event | 2+ signals | New workers, low-risk zones |
| Balanced | ₹49/week | Up to ₹900/event | 2+ signals | Most workers — recommended |
| Pro | ₹79/week | Up to ₹1,500/event | 1+ signal | High-exposure zones, monsoon season |
| Aggressive | ₹99/week | Up to ₹2,200/event | Any trigger | Top earners, festival periods |

### How Premium is Calculated — Personal Risk Fingerprint (PRF)

Each rider's premium is calculated individually by our **FT-Transformer** model, trained on 50,000 synthetic rider profiles.

**Input Features:**
- Operational zone (historical disruption frequency per pin code)
- Delivery sub-category (food / e-commerce / grocery — risk exposure differs)
- Average daily working hours and platform acceptance rate
- 4-week rolling AQI exposure in their zone
- Season multiplier (monsoon: +15%, winter smog: +10%, summer: -5%)
- Claim history (if returning rider)

**Output:** Weekly premium ₹29–₹99 + attention weight breakdown (XAI panel)

**Example XAI Output for Ravi:**
```
  Premium: ₹67/week
  ─────────────────────────────────────
  Top factors driving your premium:
  ████████░░░░  AQI Zone History         34%
  ██████░░░░░░  Monsoon Season Mult.     27%
  ████░░░░░░░░  Zone Risk Score          21%
  ██░░░░░░░░░░  Claim History            18%
```

### Payout Calculation — Earnings DNA

```
Payout = BHE × DW × ZIF × Coverage_Factor

  BHE  = Baseline Hourly Earning  (rider's 4-week median hourly income)
  DW   = Disruption Window        (hours MSC trigger was active in rider's zone)
  ZIF  = Zone Impact Factor       (0.60–1.00, derived from historical order drop in cluster)
  CF   = 0.70 for standard event  | 0.85 for 3-signal high-confidence event
```

> **Why 70%/85% and not 100%?** Covering partial income (not full replacement) prevents moral hazard — riders still have mild incentive to work during marginal disruptions. This is standard parametric insurance actuarial design.

### Premium Collection

- Auto-deducted from platform payout every Monday 12:00 AM — riders never manually transfer money
- Can pause with 48-hour notice — no penalty
- A rider working both Swiggy and Zepto can hold two separate sub-category policies

### Unit Economics (per 1,000 Riders)

| Metric | Value |
|--------|-------|
| Avg weekly premium collected | ₹49,000 |
| Expected weekly claims (5% disruption rate) | ~50 claims |
| Avg payout per claim | ~₹450 |
| Total weekly claim payout | ~₹22,500 |
| Weekly gross margin | ₹26,500 **(54% loss ratio — sustainable)** |

---

## 6. Parametric Triggers

GigShield uses **Multi-Signal Confluence (MSC)** — payouts only fire when **2 or more independent signals** confirm disruption simultaneously. This eliminates false claims by design, without requiring manual review.

### The 5 Signals

| # | Signal | Type | Source | Threshold |
|---|--------|------|--------|-----------|
| 1 | Heavy Rain | LIVE | Open-Meteo API (free, no key) | Rainfall > 8mm/hr at rider GPS zone |
| 2 | AQI Spike | LIVE | Open-Meteo Air Quality API (free) | AQI > 200 (Poor) in rider zone |
| 3 | Order Volume Drop | MOCK ENGINE | Synthetic generator (realistic Bengaluru patterns) | > 35% drop vs. 4-week same-day average |
| 4 | Road Disruption | SIMULATED | Pre-seeded mock with real Bengaluru routes | > 60% of rider's top-3 routes blocked |
| 5 | Civic Alert | SIMULATED | Mock government SMS feed | Active curfew/strike in rider PIN cluster |

> Signals 1 & 2 are live APIs. Signals 3, 4, 5 use realistic mock data engines built from published gig economy research (Fairwork India, BCG). In production, these connect to platform partner APIs and government alert systems.

### MSC Decision Table

| Signals Confirmed | MSC Status | System Action |
|-------------------|-----------|---------------|
| 0 or 1 only | NOT MET | No claim — rider sees live status in app |
| 2 signals (any combo) | MET — STANDARD | Payout at 70% Earnings DNA |
| 3+ signals | MET — HIGH | Payout at 85% Earnings DNA + priority processing |
| API data failed / stale | HELD | Redis cached fallback used, 2-hr review window |

### Satellite Visual Verification (CNN Layer)

To prevent API spoofing, every weather claim is cross-verified by our **MobileNetV3 CNN** trained on NASA satellite weather tiles:

- Fetches latest cloud-cover tile for rider's zone from NASA POWER / Copernicus (free, open access)
- Classifies in < 200ms: `Clear` / `Light Rain` / `Heavy Rain` / `Flood Risk`
- If CNN contradicts API → Confidence Score w₂ set to 0 → claim routed to review

> A fraudster can fake an API response. They cannot fake a satellite image.

---

## 7. Platform Choice — Web PWA

We chose a **Progressive Web App (PWA)** over a native mobile app.

| Factor | Native App | PWA (Our Choice) |
|--------|-----------|-----------------|
| Installation | Requires Play Store, 50–100MB | Zero — accessible via QR link |
| Device support | Needs Android 8+, enough storage | Works on any Android with a browser |
| Offline capability | Yes | Yes — Workbox service workers |
| Update delivery | Play Store review cycle | Instant — deploy and all users get it |
| Onboarding friction | High | Minimal — scan QR, open browser, done |
| Development speed | Separate iOS/Android builds | Single codebase |

> **Key insight:** Budget Android phones used by delivery workers often have < 4GB free storage and slow Play Store connections. A PWA removes every friction point from onboarding.

**Distribution:** QR code shared by zone captains at morning fleet briefings — no marketing spend needed for initial adoption.

---

## 8. AI/ML Integration Plan

### Model 1 — FT-Transformer (Premium Pricing + XAI)

| Attribute | Detail |
|-----------|--------|
| Purpose | Personalised weekly premium calculation + factor attribution |
| Model | Feature Tokenizer Transformer (FT-Transformer, Gorishniy et al. 2021) |
| Why not XGBoost | FT-Transformer produces per-prediction attention weights → native XAI panel |
| Training data | 50,000 synthetic rider profiles |
| Training time | ~12 min on GPU |
| Output | Premium ₹29–₹99 + top-3 attention factors |
| Retraining | Every Sunday — incremental update |

### Model 2 — LSTM Disruption Forecaster

| Attribute | Detail |
|-----------|--------|
| Purpose | Predict next 7 days' disruption probability per zone |
| Model | 3-layer LSTM, 128 hidden units, PyTorch |
| Input | 7-day weather forecast + 3-year Bengaluru synthetic history + seasonal calendar |
| Training time | ~4 min on GPU |
| Output | Zone risk scores → Leaflet.js choropleth heatmap |
| Fallback | Holt-Winters exponential smoothing if LSTM doesn't converge |

### Model 3 — MobileNetV3 CNN (Satellite Verification)

| Attribute | Detail |
|-----------|--------|
| Purpose | Visual cross-validation of weather API claims via satellite imagery |
| Model | MobileNetV3-Small, fine-tuned — 4-class classification |
| Classes | `Clear` · `Light Rain` · `Heavy Rain` · `Flood Risk` |
| Training data | ~8,000 labeled Bengaluru satellite tiles (NASA POWER / Copernicus) |
| Inference latency | < 200ms per tile — runs at claim initiation |

### Fraud Detection — Confidence Score System

```
Confidence Score = w₁·GPS + w₂·Weather + w₃·Earnings + w₄·Cluster

  w₁  GPS Coherence Check         30 pts    Rider within 5km of disruption zone?
  w₂  Weather CNN Cross-Verify    30 pts    CNN satellite confirms API weather reading?
  w₃  Earnings Anomaly (Z-score)  25 pts    Earnings normal this week (not already high)?
  w₄  Cluster Ring Detection      15 pts    Not part of suspicious simultaneous-claim cluster?
```

| Score | Decision | Time to Payout |
|-------|---------|----------------|
| 85–100 | Auto Approve | < 4 hours |
| 60–84 | Auto Approve + flag for audit | < 4 hours |
| 35–59 | Hold — human review queue | 24 hours |
| 0–34 | Auto Reject — reason code sent to rider | Immediate |

**Progressive build order:**
- Phase 1 (Seed): L1 GPS + L2 Z-score rules — live and demoable
- Phase 2 (Scale): L3 DBSCAN ring detection + full Confidence Score system
- Phase 3 (Soar): CNN satellite integration + full pipeline end-to-end

---

## 9. Tech Stack

```
┌──────────────────────────────────────────────────────────┐
│  FRONTEND                                                │
│  React + Tailwind CSS + Workbox (PWA)                    │
│  Rider app:    Onboarding, XAI panel, Claim status,      │
│                Coverage Simulator, Push Notifications    │
│  Insurer app:  LSTM heatmap, Fraud queue, Loss ratio,    │
│                Claim timeline, Reserve widget            │
│  Maps:         Leaflet.js + OpenStreetMap (free)         │
├──────────────────────────────────────────────────────────┤
│  BACKEND                                                 │
│  FastAPI (Python 3.11) + Uvicorn                         │
│  APScheduler — 30-min MSC polling loop                   │
│  Redis — API response cache + trigger state              │
│  PostgreSQL — Policies, riders, claims, audit trail      │
├──────────────────────────────────────────────────────────┤
│  ML SERVICES  (GPU-accelerated)                          │
│  FT-Transformer  → PyTorch (premium pricing + XAI)       │
│  LSTM            → PyTorch (disruption forecasting)      │
│  MobileNetV3     → PyTorch (satellite tile CNN)          │
│  Fraud L1/L2/L3  → scikit-learn (rules + DBSCAN)         │
├──────────────────────────────────────────────────────────┤
│  EXTERNAL SERVICES                                       │
│  Open-Meteo          → Rain + AQI (free, no API key)     │
│  NASA POWER          → Satellite tiles (open access)     │
│  Firebase Auth       → Phone OTP login (free tier)       │
│  Razorpay Test Mode  → UPI payout simulation             │
│  Railway.app/Render  → Hosting (free tier)               │
└──────────────────────────────────────────────────────────┘
```

| Decision | Rationale |
|----------|-----------|
| FastAPI over Django/Flask | Async-native, ideal for ML model serving, auto-generates OpenAPI docs |
| PostgreSQL over MongoDB | Insurance data is inherently relational (policies, riders, claims, events) |
| Redis | Sub-millisecond cache for API responses — critical for demo reliability |
| Open-Meteo over OpenWeatherMap | Fully free, no credit card, global coverage, AQI included |
| Firebase Auth | Phone OTP works without passwords — perfect for budget Android users |
| Razorpay Test Mode | UPI simulation that looks and feels real for judges |
| PWA + Workbox | Offline-first — riders in poor-connectivity zones still get the experience |

---

## 10. 6-Week Development Plan

### Phase 1 — Seed (March 4–20) · Ideate & Know Your Delivery Worker

| Week | Build Targets |
|------|--------------|
| Week 1 | PWA shell, Firebase Auth (OTP), PRF form, Policy DB schema, Basic MSC evaluator (mock data), Razorpay sandbox integration |
| Week 2 | FT-Transformer training (50k synthetic riders), XAI panel UI, Coverage Simulator, L1 GPS fraud check, Claim Timeline DB logging, README + video |

**Deliverables:** README.md · GitHub repo · 2-minute video

### Phase 2 — Scale (March 21 – April 4) · Automation & Protection

| Week | Build Targets |
|------|--------------|
| Week 3 | Live Open-Meteo integration (Rain + AQI), Mock Order Volume engine, L2 Z-score anomaly detection, L3 DBSCAN ring detector, Confidence Score system end-to-end |
| Week 4 | LSTM training on GPU, LSTM API endpoint, Rider dashboard, SMS notification mock, Insurer dashboard v1 |

**Deliverables:** Demo video · Executable source code

### Phase 3 — Soar (April 5–17) · Scale & Optimise

| Week | Build Targets |
|------|--------------|
| Week 5 | MobileNetV3 fine-tuning (8k satellite tiles), CNN inference endpoint, CNN into fraud pipeline, Insurer dashboard v2 |
| Week 6 | Demo mode fallback toggle, Redis resilience layer, XAI panel polish, 5-min demo video, Final pitch deck |

**Deliverables:** 5-minute demo video · Final pitch deck PDF · Complete platform

### Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| CNN training data insufficient | Transfer learning from ImageNet — only fine-tune final 2 layers |
| LSTM doesn't converge | Holt-Winters exponential smoothing fallback |
| Open-Meteo down during demo | Redis cache returns last known good value. Demo override toggle available. |
| Judge asks about real platform API | "Signals 3–5 use mock engines from published research. Here is what the production API integration looks like." |

---

## 11. What Makes GigShield Different

| Feature | Generic Team | GigShield |
|---------|-------------|-----------|
| Trigger model | Single API | Multi-Signal Confluence (3 live + 2 simulated) |
| Payout calculation | Flat ₹200 | Earnings DNA — personalised per rider |
| Fraud detection | None | 4-layer progressive stack + Confidence Score |
| Premium AI | Flat rate | FT-Transformer + attention-based XAI panel |
| Forecasting | None | LSTM 7-day zone risk → heatmap + notifications |
| Rider engagement | Passive | Pre-disruption notifications from LSTM forecast |
| Demo reliability | May break | Redis cache + fallback demo override |
| Transparency | Black box | Claim Timeline + Confidence Score meter |
| GPU models | None | FT-Transformer + LSTM + MobileNetV3 CNN |
| Persona coverage | Single segment | Food · E-Commerce · Grocery all covered |

---

## 12. Repository Structure

```
gigshield/
├── frontend/
│   ├── rider-pwa/            # React PWA — rider-facing app
│   └── insurer-dashboard/    # React — insurer analytics dashboard
├── backend/
│   ├── api/                  # FastAPI main application
│   ├── trigger_engine/       # MSC evaluator + APScheduler (30-min loop)
│   ├── fraud_engine/         # L1/L2/L3/L4 + Confidence Score pipeline
│   └── payout_engine/        # Earnings DNA + Razorpay mock integration
├── ml/
│   ├── premium/              # FT-Transformer training + serving
│   ├── forecast/             # LSTM training + serving
│   └── cnn_verify/           # MobileNetV3 training + serving
├── data/
│   ├── synthetic/            # Rider profile + order volume generators
│   └── mock_feeds/           # Simulated civic + road disruption data
├── infra/
│   └── docker-compose.yml
├── docs/
│   └── architecture.md
└── README.md
```

---

## 13. Adversarial Defense & Anti-Spoofing Strategy

> **🚨 Market Crash Scenario:** A coordinated fraud ring of 500 delivery partner accounts is using fake GPS signals to falsely claim they are in disruption-affected zones, triggering automated income-loss payouts and draining the platform's liquidity pool. Simple GPS coordinate verification is dead. This section describes GigShield's multi-layered defense architecture against such attacks.

---

### Layer 1 — Device-Level GPS Spoofing Detection

The first line of defense detects that GPS data itself is being fabricated at the device level.

**Signals monitored:**

- **Mock Location Flag:** Android's `Location.isFromMockProvider()` API and iOS equivalent are checked on every location ping. Any claim where location data originated from a mock provider is automatically held for review — no exceptions.
- **Sensor Fusion Cross-Check:** Real physical movement produces correlated signals across GPS, accelerometer, and gyroscope. A stationary device faking GPS movement will show GPS coordinates changing while accelerometer data remains flat. We compare these sensor streams — inconsistency raises the fraud score significantly.
- **Cell Tower / Wi-Fi Triangulation vs GPS:** We cross-check GPS coordinates against cell tower and Wi-Fi network triangulation. A mismatch > 500 metres between GPS-reported location and network-triangulated location is a strong spoofing indicator.
- **Altitude & Speed Plausibility:** GPS spoofers often forget to simulate realistic altitude and travel speeds. A delivery partner "moving" at 180 km/h through congested Bengaluru traffic, or altitude readings physically impossible for their location, triggers an immediate anomaly flag.

---

### Layer 2 — Behavioural & Delivery Activity Validation

Even if a device successfully spoofs GPS, its actual delivery behaviour contradicts the fraud claim.

**Key checks:**

- **Platform Activity Cross-Reference (Simulated):** During a claimed disruption window, we check whether the worker's linked platform account shows completed deliveries, accepted orders, or online active status. A worker claiming income loss due to heavy rain while completing 8 deliveries is an automatic fraud flag.
- **Order Acceptance Pattern:** Genuine workers in a disruption zone show a sharp drop in acceptance and completion rates. Fraudulent accounts physically elsewhere show normal or elevated activity.
- **Historical Work Zone Consistency:** Each worker builds a GPS heatmap of their operating zone over weeks. A worker whose heatmap shows 95% activity in Koramangala suddenly claiming from a flood zone in Chennai is flagged for immediate review — this pattern does not occur organically.

---

### Layer 3 — Coordinated Ring Detection (Network Analysis)

500 accounts acting simultaneously is not individual fraud — it is an organised ring. Individual-account checks alone will miss this. We apply **network-level graph analysis**.

**Detection methods:**

- **Geospatial Clustering (DBSCAN):** If 50+ accounts submit claims from the same 500-metre radius simultaneously, our DBSCAN clustering algorithm flags the entire group. Genuine disruptions cause dispersed claims across a wide zone; coordinated fraud produces unnatural spatial density.
- **Device Fingerprint Graph:** We maintain a graph of device identifiers (device ID, screen resolution, browser fingerprint, hardware signature). If one physical device is linked to multiple worker accounts, all accounts in that cluster are flagged. A single device operating 10 "different" delivery partners is an unmistakable ring indicator.
- **Account Age vs Claim Velocity:** Newly created accounts (< 30 days old) with no delivery history that immediately file disruption claims are assigned a high prior fraud probability. Legitimate workers build history before encountering disruptions.
- **Temporal Correlation Spike:** A natural disruption produces a gradual rise in claims over 20–40 minutes. A fraud ring produces a near-simultaneous spike — all 500 claims within a 2-minute window. This is statistically anomalous and auto-triggers a ring investigation and payout freeze.
- **IP Address / Network Clustering:** Multiple accounts submitting claims from the same IP address or mobile hotspot strongly indicates coordinated fraud from a single physical location.

---

### Layer 4 — Environmental Ground Truth Verification (CNN)

The disruption must actually exist in the claimed zone. We verify this independently of any API.

**Process:**

- **Multi-Source Weather Corroboration:** A valid weather trigger must be confirmed by at least 2 independent data sources (e.g., Open-Meteo + IMD alert). A claim zone where only one source reports disruption enters a verification hold.
- **Hyper-Local Satellite Validation:** Weather events are validated at pin-code level, not city level. Our MobileNetV3 CNN classifies the satellite tile independently of the API feed. A fraudster who spoofs the API cannot spoof the satellite image.
- **Historical Baseline Comparison:** We compare reported disruption intensity against historical weather patterns. A "record-breaking heatwave" with no satellite confirmation and no news corroboration is held pending investigation.

---

### Layer 5 — Graduated Response (Protecting Honest Workers)

A binary block/approve system wrongly penalises genuine workers caught in edge cases. GigShield uses a **Trust Score System** to ensure fraud defence never punishes honest workers.

**Trust Score (0–100) per worker, updated weekly:**

| Score Range | Action |
|-------------|--------|
| 80–100 | Auto-approve, instant payout (< 4 hours) |
| 50–79 | 50% instant payout, 50% after 24-hr verification |
| 25–49 | Full payout held, manual review within 4 hours |
| 0–24 | Claim flagged, account temporarily suspended, worker notified with reason code + appeal option |

**Trust Score inputs:**
- Delivery tenure and platform history length
- Sensor data consistency score (GPS vs accelerometer)
- Historical claim legitimacy rate
- Account and device uniqueness score
- Zone-disruption corroboration score (CNN + API agreement)

**Appeals Process:** Any worker whose payout is held can submit an appeal via the app — photo of flooded road, platform screenshot showing cancelled orders, or local news link. Appeals reviewed within 24 hours. False positives are paid immediately plus a **₹25 goodwill credit** and a Trust Score correction.

> **Why this matters:** The fraud ring of 500 accounts will trigger geospatial clustering and device fingerprint graph detection long before individual trust scores are evaluated — the ring is caught at a structural level, not an individual one. A genuine Swiggy partner stranded during a real Bengaluru flood will never be caught in the net.

---

### Summary: What Catches the Fraud Ring

| Attack Vector | GigShield Defence |
|---------------|------------------|
| Fake GPS coordinates | Mock provider flag + sensor fusion mismatch (accelerometer vs GPS) |
| Coordinated simultaneous claims | Temporal spike detection + DBSCAN geospatial clustering |
| Same device, multiple accounts | Device fingerprint graph analysis |
| Claiming from wrong zone | Hyper-local satellite CNN + cell tower triangulation |
| New fake accounts | Account age + delivery history prior score |
| Fake platform inactivity | Platform activity cross-reference (simulated) |
| Spoofed weather API | MobileNetV3 CNN satellite visual verification |
| Punishing honest workers | Trust Score system + graduated payout + 24-hr appeals |

---

## 14. Demo Video

> 📹 **[2-Minute Phase 1 Demo Video]** — Link to be added before March 20 submission deadline

The video covers:
- Problem statement and persona introduction
- Onboarding flow — OTP login → PRF form → XAI premium panel
- Coverage Simulator walkthrough
- Static MSC disruption trigger demo (mock data)
- Adversarial defense architecture overview
- Prototype scope for Phase 1 + roadmap for Phases 2 & 3

---

## 👥 Team

> Team details to be added before submission.

---

## 📄 License

This project is submitted as part of **Guidewire DEVTrails 2026 University Hackathon**.

---

<div align="center">

⚡ **GigShield — Protecting the people who deliver India's future.**

*Build fast. Ship the CNN. Don't go broke.*

</div>

