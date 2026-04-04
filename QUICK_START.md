# 🚀 QUICK START GUIDE - GigShield Application

## ✅ EVERYTHING IS RUNNING!

### 📱 OPEN THESE URLs IN YOUR BROWSER:

#### Backend API (All endpoints available)
- **API Documentation:** http://127.0.0.1:8002/api/docs
- **Health Check:** http://127.0.0.1:8002/health
- **Base API:** http://127.0.0.1:8002/api/v1

#### Rider PWA (Gig Worker App)
- **URL:** http://127.0.0.1:3201
- **What you'll see:** Rider dashboard, policies, claims, earnings

#### Insurer Dashboard (Admin Panel)
- **URL:** http://localhost:3002
- **What you'll see:** Admin dashboard, rider management, policy analytics, claims review

---

## 🔧 RUNNING SERVICES

| Service | Port | Status | Command to View |
|---------|------|--------|-----------------|
| Backend API | 8002 | ✅ Running | Terminal: python gigshield/run_backend.py |
| Rider PWA | 3201 | ✅ Running | Terminal: cd gigshield/frontend/rider-pwa && npm run dev |
| Insurer Dashboard | 3002 | ✅ Running | Terminal: cd gigshield/frontend/insurer-dashboard && npm run dev |

---

## 🗄️ DATABASE

- **Database:** SQLite (gigshield/gigshield.db)
- **Status:** ✅ Connected and seeded with demo data
- **Tables:** riders, policies, claims, trigger_events, audit_logs

---

## 🔐 TEST CREDENTIALS

Since this is demo mode, use these test rider IDs:
```
11111111-1111-1111-1111-111111111111  (Main test rider)
```

---

## 🎯 WHAT TO TEST

### In Rider PWA (3201):
1. View active policies
2. Check recent claims
3. View earnings dashboard
4. Review trigger events

### In Insurer Dashboard (3002):
1. View all riders
2. Manage policies
3. Review claims submitted
4. Check fraud detection scores
5. View analytics and reports

### In Backend API (8002):
1. Check interactive API documentation
2. Test endpoints directly
3. View request/response examples

---

## 🐛 DEBUGGING TIPS

### If a page shows connection error:
- Make sure all three terminals are still showing "ready" ✅
- Reload the page (Ctrl+R or Cmd+R)
- Check the terminal for error messages

### View Backend Logs:
- All database queries are logged
- Watch terminal for real-time activity
- Check `gigshield.db` if data seems missing

### Clear Cache if needed:
- Backend: Stop and restart with `python gigshield/run_backend.py`
- Frontend: Hard refresh browser (Ctrl+Shift+R)

---

## 📊 API ROUTES AVAILABLE

```
GET  /api/v1/health                    # System health
GET  /api/v1/riders/{rider_id}        # Get rider info
GET  /api/v1/policies/{rider_id}      # Get rider policies
GET  /api/v1/claims/{rider_id}        # Get rider claims
POST /api/v1/policies/activate         # Activate new policy
POST /api/v1/claims/submit             # Submit new claim
GET  /api/v1/demo/riders              # List all demo riders
GET  /api/v1/demo/full-state          # Get full system state
```

All documented at: **http://127.0.0.1:8002/api/docs**

---

## ✨ FEATURES ENABLED

- ✅ Fraud detection on claims
- ✅ Automatic payout calculation
- ✅ Premium deduction from earnings
- ✅ Weather-based trigger events
- ✅ ML-powered forecasting
- ✅ CNN image verification
- ✅ Real-time notifications
- ✅ Comprehensive audit logs

---

## 🎉 YOU'RE ALL SET!

**Your GigShield platform is fully operational.**

Browser tabs should now show:
1. Backend API docs (8002)
2. Rider PWA interface (3201)
3. Insurer Dashboard interface (3002)

Enjoy testing! 🚀

