# GigShield Setup & Deployment Guide

## Prerequisites

### System Requirements
- **OS:** Windows, macOS, or Linux
- **Python:** 3.12 or higher
- **Node.js:** 18 or higher
- **npm:** 9 or higher
- **RAM:** 4GB minimum (8GB recommended)
- **Disk:** 2GB free space

### Verify Installation
```bash
# Check Python version
python --version  # Should be 3.12+

# Check Node.js version
node --version    # Should be 18+

# Check npm version
npm --version     # Should be 9+
```

---

## Installation & Setup

### Step 1: Clone Repository
```bash
git clone https://github.com/tejaswiputluri/AI-Powered-Insurance-for-India-s-Gig-Economy.git
cd GuideWire-main/gigshield
```

### Step 2: Backend Setup

#### 2.1 Create Python Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### 2.2 Install Python Dependencies
```bash
# Navigate to backend
cd backend

# Install requirements (if requirements.txt exists)
pip install fastapi uvicorn sqlalchemy aiosqlite httpx pydantic python-dotenv

# Or use requirements file
pip install -r requirements.txt
```

#### 2.3 Verify Backend Installation
```bash
python -c "import fastapi; print('✅ FastAPI installed')"
python -c "import sqlalchemy; print('✅ SQLAlchemy installed')"
```

### Step 3: Frontend Setup

#### 3.1 Rider PWA Setup
```bash
# Navigate to Rider PWA
cd ../frontend/rider-pwa

# Install dependencies
npm install

# Verify installation
npm list react  # Should show React version
```

#### 3.2 Insurer Dashboard Setup
```bash
# Navigate to Insurer Dashboard
cd ../insurer-dashboard

# Install dependencies
npm install

# Verify installation
npm list react  # Should show React version
```

---

## Running the Application

### Option 1: Run All Services (Recommended for Development)

#### Terminal 1: Start Backend
```bash
cd /path/to/gigshield
python run_backend.py

# Expected output:
# INFO:     Uvicorn running on http://127.0.0.1:8004
# INFO:     Application startup complete
```

#### Terminal 2: Start Rider PWA
```bash
cd /path/to/gigshield/frontend/rider-pwa
npm run dev

# Expected output:
# VITE v4.x.x  ready in XXX ms
# ➜  Local:   http://127.0.0.1:3201/
```

#### Terminal 3: Start Insurer Dashboard
```bash
cd /path/to/gigshield/frontend/insurer-dashboard
npm run dev

# Expected output:
# VITE v4.x.x  ready in XXX ms
# ➜  Local:   http://127.0.0.1:3001/
```

### Option 2: Docker Deployment (Production)

#### Build Docker Image
```bash
# Build backend image
docker build -t gigshield-backend:latest -f backend/Dockerfile .

# Build frontend images
docker build -t gigshield-frontend:latest -f frontend/Dockerfile .
```

#### Run with Docker Compose
```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

### Option 3: Production Deployment (Cloud)

#### Deploy to Heroku
```bash
# Install Heroku CLI
brew install heroku  # macOS
# or download from https://devcenter.heroku.com/articles/heroku-cli

# Login to Heroku
heroku login

# Create Heroku app (backend)
heroku create gigshield-backend
heroku buildpacks:add heroku/python

# Deploy backend
git push heroku main

# Create Heroku app (frontend)
heroku create gigshield-frontend
heroku buildpacks:add heroku/nodejs

# Deploy frontend
git push heroku main
```

#### Deploy to AWS
```bash
# Backend: AWS Elastic Beanstalk
eb init -p python-3.12 gigshield
eb create gigshield-env
eb deploy

# Frontend: AWS S3 + CloudFront
npm run build
aws s3 sync dist/ s3://gigshield-cdn/
```

---

## Accessing the Application

### Development URLs
| Service | URL | Port | Access |
|---------|-----|------|--------|
| Backend API | http://127.0.0.1:8004 | 8004 | Uvicorn server |
| API Docs | http://127.0.0.1:8004/docs | 8004 | Swagger UI |
| Rider PWA | http://127.0.0.1:3201 | 3201 | Vite dev server |
| Insurer Dashboard | http://127.0.0.1:3001 | 3001 | Vite dev server |

### Demo Login Credentials
- **Phone Number:** 9949722949
- **OTP:** Check backend terminal (printed for demo)
- **OTP Duration:** 5 minutes
- **Max Attempts:** 3

### Backend API Documentation
- Swagger UI: http://127.0.0.1:8004/docs
- ReDoc: http://127.0.0.1:8004/redoc

---

## Database Setup

### Initialize Database
```bash
# Automatic initialization on first backend start
# Or manually:

cd backend
python -c "
import asyncio
from db.database import init_db
asyncio.run(init_db())
"
```

### Database File Location
- **File:** `backend/data/gigshield.db`
- **Type:** SQLite
- **Size:** ~500KB (with demo data)

### Database Tables
```sql
-- Core tables
riders          -- Rider profiles
policies        -- Insurance policies
claims          -- Claims data
fraud_checks    -- Fraud detection results
payouts         -- Payout records

-- Reference tables
audit_log       -- Complete audit trail
weather_data    -- Historical weather
zone_data       -- Zone information
```

### Seed Database with Demo Data
```bash
python backend/db/seed.py

# Expected output:
# ✅ Database seeded with:
# - 50 demo riders
# - 75 demo policies
# - 100 demo claims
# - Weather data for 10 zones
```

---

## Configuration

### Environment Variables
Create `.env` file in project root:

```bash
# Backend Configuration
BACKEND_HOST=127.0.0.1
BACKEND_PORT=8004
DATABASE_URL=sqlite:///./data/gigshield.db

# Frontend Configuration
VITE_API_URL=http://127.0.0.1:8004/api/v1
VITE_APP_NAME=GigShield

# ML Services
ML_PREMIUM_URL=http://localhost:8001
ML_FORECAST_URL=http://localhost:8002

# SMS Configuration (Optional - for SMS OTP in production)
SMS_PROVIDER=twilio  # or aws_sns
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_PHONE_NUMBER=+1234567890

# Database
DATABASE_ENV=development  # or production
```

### Backend Configuration File
Location: `backend/config/settings.py`

```python
class Settings(BaseSettings):
    # Server
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "GigShield"
    
    # Database
    DATABASE_URL: str = "sqlite:///./data/gigshield.db"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # ML Services
    ML_PREMIUM_URL: str = "http://localhost:8001"
    PREMIUM_DEDUCTION_CRON: str = "30 0 * * 1"  # Every Monday 00:30
```

---

## Testing

### Run Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run all tests
pytest backend/tests/ -v

# Run specific test file
pytest backend/tests/test_api.py -v

# Run with coverage
pytest backend/tests/ --cov=backend --cov-report=html
```

### Expected Test Output
```
test_api.py::test_onboard_rider_request_validation PASSED
test_api.py::test_onboard_invalid_zone_validation PASSED
test_payout_engine.py::test_payout_calculation PASSED
test_fraud_engine.py::test_four_layer_fraud_detection PASSED
test_trigger_engine.py::test_disruption_event_detection PASSED

====== 5 passed in 2.34s ======
```

---

## Troubleshooting

### Issue: "Port 8004 already in use"
```bash
# Find process using port 8004
# Windows
netstat -ano | findstr :8004

# macOS/Linux
lsof -i :8004

# Kill process
# Windows
taskkill /PID <PID> /F

# macOS/Linux
kill -9 <PID>
```

### Issue: "Module not found" (Python)
```bash
# Ensure virtual environment is activated
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# Reinstall dependencies
pip install –r requirements.txt
```

### Issue: "npm dependencies not installed"
```bash
# Clear npm cache
npm cache clean --force

# Reinstall node modules
rm -rf node_modules package-lock.json
npm install
```

### Issue: "OTP not appearing in terminal"
```bash
# For demo mode:
# 1. Make sure backend is running: python run_backend.py
# 2. Check terminal output for "OTP GENERATED: XXXX"
# 3. Enable output buffering in Python:
#    - Run backend with: python -u run_backend.py
#    - Or add to backend: sys.stdout.flush()
```

### Issue: "Cannot connect to backend"
```bash
# Check backend is running
curl http://127.0.0.1:8004/docs

# Check firewall/network
# - Verify port 8004 is not blocked
# - Ensure backend URL correct in frontend config

# Check logs
# Look at backend terminal for error messages
```

---

## Performance Optimization

### Development
- Hot reload enabled by default
- Vite provides instant refresh
- Fast API development setup

### Production
```bash
# Build optimized frontend
npm run build

# Run backend with production settings
gunicorn -w 4 -b 0.0.0.0:8004 backend.main:app --workers 4

# Or use Uvicorn with multiple workers
uvicorn backend.main:app --host 0.0.0.0 --port 8004 --workers 4
```

### Database Optimization
```bash
# Create indexes for common queries
sqlite3 data/gigshield.db

CREATE INDEX idx_riders_phone ON riders(phone_number);
CREATE INDEX idx_policies_rider ON policies(rider_id);
CREATE INDEX idx_claims_rider ON claims(rider_id);
CREATE INDEX idx_payouts_claim ON payouts(claim_id);
```

---

## Monitoring & Logging

### Backend Logs
```bash
# Logs written to: backend/logs/gigshield.log
# Monitor logs in real-time:
tail -f backend/logs/gigshield.log

# Or view via FastAPI endpoint:
curl http://127.0.0.1:8004/api/v1/logs/latest
```

### Performance Metrics
```bash
# View via Prometheus endpoint (if configured)
curl http://127.0.0.1:8004/metrics

# Or dashboard: http://127.0.0.1:3000 (Grafana)
```

---

## API Endpoints Reference

### Authentication
- `POST /api/v1/auth/phone-login` - Send OTP
- `POST /api/v1/auth/verify-otp` - Verify OTP

### Riders
- `POST /api/v1/riders/onboard` - Complete onboarding
- `GET /api/v1/riders/me` - Get rider profile

### Policies
- `POST /api/v1/policies` - Create policy
- `GET /api/v1/policies/me` - Get rider policies
- `GET /api/v1/policies/{id}/simulate` - Simulate payout

### Claims
- `GET /api/v1/claims/me` - Get rider claims
- `GET /api/v1/claims/{id}` - Get claim details

### Admin
- `POST /api/v1/triggers/simulate` - Trigger test event
- `GET /api/v1/analytics/dashboard` - Dashboard metrics

Full API documentation: http://127.0.0.1:8004/docs

---

## Clean Up & Reset

### Reset Database
```bash
# Stop backend
# Delete database file
rm backend/data/gigshield.db

# Restart backend (auto-creates new DB)
python run_backend.py
```

### Clear Demo Data
```bash
# Backend
python -c "
import asyncio
from backend.db.database import get_db
# Clear all tables
"
```

### Remove Installation
```bash
# Remove virtual environment
rm -rf venv

# Remove node modules
rm -rf frontend/rider-pwa/node_modules
rm -rf frontend/insurer-dashboard/node_modules

# Remove database
rm -rf backend/data/
```

---

## Next Steps

1. **Test the Application** - Run demo flow as described
2. **Explore API** - Visit http://127.0.0.1:8004/docs
3. **Review Code** - Check implementation in key files
4. **Customize** - Modify for your use case
5. **Deploy** - Follow production deployment steps

---

## Support & Resources

- **GitHub Issues:** Report bugs on GitHub
- **Documentation:** See README.md for overview
- **API Docs:** http://127.0.0.1:8004/docs
- **Video Script:** See VIDEO_SCRIPT.md for walkthrough
- **Features:** See FEATURES.md for detailed feature list

---

**GigShield - Production-Ready Insurance Platform**
Ready to serve India's gig economy!
