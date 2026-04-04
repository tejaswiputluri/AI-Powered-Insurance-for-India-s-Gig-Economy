# ⚡ GigShield

**AI-Powered Parametric Income Insurance for India's Gig Workers**

> Guidewire DEVTrails 2026 · Unicorn Chase  
> 🧠 ML-driven premium pricing · 🌧️ Real-time disruption detection · 🔍 4-layer fraud engine · ⚡ Auto-payouts in minutes

---

## 🎯 What is GigShield?

GigShield is a **full-stack parametric insurance platform** that automatically compensates delivery riders when weather or civic disruptions cause income loss. No paperwork, no claims filing — everything is automated.

### How It Works

```
Rain/AQI event detected → MSC confirms disruption → Claim auto-created →
→ Fraud pipeline scores it → Payout sent to UPI in minutes
```

1. **Signal Detection**: Every 30 minutes, we check rainfall, AQI, and order volume across 10 Bengaluru zones
2. **MSC Confluence**: When 2+ signals cross thresholds, a disruption event is confirmed
3. **Auto-Claims**: Claims are created for all covered riders in the zone — no rider action needed
4. **Fraud Pipeline**: 4-layer confidence scoring (GPS + Weather + Earnings + Cluster)
5. **Instant Payout**: Auto-approved claims get instant UPI payout using Razorpay

---

## 🏗️ Architecture

```
┌─────────────────┐     ┌─────────────────┐
│   Rider PWA     │     │  Insurer Dash   │
│   (React/Vite)  │     │  (React/Vite)   │
│   Port: 3000    │     │   Port: 3001    │
└────────┬────────┘     └───────┬─────────┘
         │                      │
         └──────────┬───────────┘
                    │
         ┌──────────▼──────────┐
         │   FastAPI Backend   │
         │     Port: 8000      │
         │  • API Routers      │
         │  • Trigger Engine   │
         │  • Fraud Engine     │
         │  • Payout Engine    │
         └──────────┬──────────┘
                    │
    ┌───────────────┼───────────────┐
    │               │               │
┌───▼───┐     ┌─────▼─────┐   ┌────▼────┐
│ Redis │     │ Supabase  │   │ ML Svc  │
│ Cache │     │ Postgres  │   │ 8001-03 │
└───────┘     └───────────┘   └─────────┘
```

---

## 🚀 Quick Start (Demo Mode)

### Prerequisites
- Python 3.11+
- Node.js 18+
- Redis (or Docker)
- Supabase project (free tier works)

### 1. Clone & Install Backend

```bash
cd gigshield
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your Supabase credentials
# DEMO_MODE=true is the default — no external APIs needed
```

### 3. Start Backend

```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

### 4. Start Rider PWA

```bash
cd frontend/rider-pwa
npm install
npm run dev
```

### 5. Start Insurer Dashboard

```bash
cd frontend/insurer-dashboard
npm install
npm run dev
```

### 6. Open in Browser

- **Rider PWA**: http://localhost:3000
- **Insurer Dashboard**: http://localhost:3001
- **API Docs**: http://localhost:8001/api/docs

---

## 📐 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI + SQLAlchemy (async) |
| Database | Supabase (PostgreSQL) |
| Cache | Redis (LRU, 256MB) |
| ML Premium | FT-Transformer (PyTorch) |
| ML Forecast | LSTM (PyTorch) |
| Fraud | 4-layer pipeline + DBSCAN |
| Rider Frontend | React 18 + Vite + Tailwind |
| Insurer Frontend | React 18 + Recharts + Leaflet |
| Scheduler | APScheduler (30-min MSC loop) |
| Payments | Razorpay (test mode) |

---

## 🧠 Key Business Rules

| Rule | Description |
|------|------------|
| RULE-03 | All money stored as **INTEGER PAISE** (₹67 = 6700) |
| RULE-04 | All timestamps stored in **UTC** |
| RULE-05 | External APIs use **resilience chain**: Cache → API → Stale → Fallback |
| RULE-14 | MSC requires **minimum 2 of 3** core signals |
| RULE-17 | Confidence Score < 35 = **ALWAYS rejected** (no manual override) |

---

## 📊 Earnings DNA Formula

```
Payout = BHE × DW × ZIF × CF

BHE  = Baseline Hourly Earning (daily ÷ work hours)
DW   = Disruption Window (hours, max 8)
ZIF  = Zone Impact Factor (0.60 – 1.00)
CF   = Coverage Factor (0.70 for 2 signals, 0.85 for 3+)
```

---

## 🔍 Fraud Pipeline (Confidence Score)

| Layer | Points | Check |
|-------|--------|-------|
| L1: GPS Coherence | 30 | Is rider within 5km of disruption zone? |
| L2: Weather Verify | 30 | Are weather signals still active? |
| L3: Earnings Anomaly | 25 | Any earnings spikes suggesting no disruption? |
| L4: Cluster Detection | 15 | Are claims suspiciously clustered? |
| **Total** | **100** | |

| Score Range | Decision |
|------------|----------|
| 85–100 | Auto-approve ✓ |
| 60–84 | Pay + flag for audit ⚠️ |
| 35–59 | Hold for manual review 🔍 |
| 0–34 | Auto-reject ✗ |

---

## 📂 Project Structure

```
gigshield/
├── backend/
│   ├── api/routers/         # FastAPI endpoints
│   ├── config/              # settings.py, constants.py
│   ├── db/                  # SQLAlchemy engine, seed
│   ├── models/db/           # ORM models
│   ├── models/schemas/      # Pydantic schemas
│   ├── services/            # Business logic engines
│   ├── ml/premium/          # FT-Transformer model
│   ├── scheduler/           # APScheduler jobs
│   ├── cache/               # Redis client
│   └── tests/               # pytest tests
├── frontend/
│   ├── rider-pwa/           # React PWA for riders
│   └── insurer-dashboard/   # React dashboard for insurers
├── data/                    # zones.json, seed_events.json
├── infra/                   # docker-compose.yml
└── docs/                    # Architecture docs
```

---

## 🧪 Demo Mode

When `DEMO_MODE=true` (default):

- **Auth is bypassed** — no Firebase needed
- **Demo rider** (Ravi Kumar) is auto-seeded with active policy
- **Fire demo events** from the dashboard to test the full pipeline
- **4 scenarios**: Rain+Orders, AQI+Orders, Full 3-Signal, Fraud Attempt
- **ML falls back** to rule-based pricing (no model training required)
- **Weather uses** fallback values for all zones

---

## 📝 License

Built for Guidewire DEVTrails 2026 · Unicorn Chase
