# GigShield API Documentation

Complete API reference for GigShield backend services.

**Base URL:** `http://127.0.0.1:8004/api/v1`  
**API Version:** 1.0  
**Authentication:** JWT Bearer Token (from /auth/verify-otp)

---

## Table of Contents

1. [Authentication](#authentication-endpoints)
2. [Riders](#riders-endpoints)
3. [Policies](#policies-endpoints)
4. [Claims](#claims-endpoints)
5. [Triggers](#triggers-endpoints)
6. [Admin](#admin-endpoints)
7. [Error Handling](#error-handling)

---

## Authentication Endpoints

### Phone Login
Send OTP to phone number

**Endpoint:** `POST /auth/phone-login`

**Request Body:**
```json
{
  "phone_number": "9949722949"
}
```

**Query Parameters:**
- `phone_number` (string, required) - 10-digit phone number

**Response (200 OK):**
```json
{
  "message": "OTP sent successfully",
  "expires_in": 300,
  "note": "In demo mode, OTP is printed to backend console"
}
```

**Response (400 Bad Request):**
```json
{
  "detail": "Invalid phone number format"
}
```

**Demo Note:** 
In demo mode, the OTP is printed to the backend terminal console. This is intentional to avoid requiring SMS infrastructure setup. In production, SMS is sent via Twilio/AWS SNS.

**Example Terminal Output:**
```
INFO: OTP GENERATED for 9949722949: 7382 (expires in 5 minutes)
```

---

### Verify OTP
Verify OTP and get JWT token

**Endpoint:** `POST /auth/verify-otp`

**Request Body:**
```json
{
  "phone_number": "9949722949",
  "otp": "7382"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "rider_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response (400 Bad Request):**
```json
{
  "detail": "Invalid OTP"
}
```

**Response (401 Unauthorized):**
```json
{
  "detail": "OTP expired. Please request a new one."
}
```

**Usage:**
Include token in Authorization header:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## Riders Endpoints

### Complete Rider Onboarding
Register a new rider with complete profile

**Endpoint:** `POST /riders/onboard`

**Headers:**
```
Authorization: Bearer {token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "age": 28,
  "daily_earning_bracket": 2,
  "zone_id": "whitefield",
  "vehicle_type": "two_wheeler",
  "prf_questions": [
    {"question": "experience", "answer": 3},
    {"question": "accident_history", "answer": 0},
    {"question": "traffic_awareness", "answer": 4},
    {"question": "ride_frequency", "answer": 5},
    {"question": "area_familiarity", "answer": 4}
  ]
}
```

**Parameters:**
- `age` (integer, 18-65) - Rider's age
- `daily_earning_bracket` (integer, 0-3) - Income bracket:
  - 0: ₹0-₹500/day
  - 1: ₹500-₹1000/day
  - 2: ₹1000-₹1600/day
  - 3: >₹1600/day
- `zone_id` (string) - Bengaluru zone (see zones list below)
- `vehicle_type` (string) - "two_wheeler" or "three_wheeler"
- `prf_questions` (array) - Personal Risk Factor Q&A

**Response (201 Created):**
```json
{
  "rider_id": "550e8400-e29b-41d4-a716-446655440000",
  "phone_number": "9949722949",
  "profile": {
    "age": 28,
    "zone": "whitefield",
    "vehicle": "two_wheeler",
    "prf_score": 16
  },
  "message": "Rider onboarded successfully",
  "auto_policy_created": {
    "policy_id": "660e8400-e29b-41d4-a716-446655440001",
    "tier": "standard",
    "weekly_premium": 79,
    "coverage": 90000
  }
}
```

**Validation Rules:**
- Age: 18-65 years
- Zone: Must be valid Bengaluru zone
- Vehicle: "two_wheeler" or "three_wheeler"
- PRF answers: 0-5 scale

---

### Get Rider Profile
Get current rider's profile

**Endpoint:** `GET /riders/me`

**Headers:**
```
Authorization: Bearer {token}
```

**Response (200 OK):**
```json
{
  "rider_id": "550e8400-e29b-41d4-a716-446655440000",
  "phone_number": "9949722949",
  "age": 28,
  "zone": "whitefield",
  "daily_earning_bracket": 2,
  "vehicle_type": "two_wheeler",
  "prf_score": 16,
  "status": "verified",
  "created_at": "2026-04-04T09:30:45Z",
  "updated_at": "2026-04-04T09:35:22Z"
}
```

---

### Supported Zones
List of all 10 Bengaluru zones supported:

```
1. whitefield       - Tech hub, high order volume
2. koramangala      - Urban center, high traffic
3. indiranagar      - Residential, moderate volume
4. frazer-town      - Urban, high weather exposure
5. marathahalli     - Tech zone, moderate volume
6. electronic-city  - Industrial, high volume
7. jp-nagar         - Residential, low volume
8. vijayanagar      - Industrial, moderate volume
9. jayanagar        - Residential, moderate volume
10. bellandur       - Tech zone, high weather exposure
```

**Zone Multipliers:**
```
whitefield:    0.95 (low risk)
koramangala:   1.05 (moderate risk)
electronic-city: 0.90 (low risk)
bellandur:     1.20 (high weather risk)
marathahalli:  1.00 (baseline)
```

---

## Policies Endpoints

### Create Policy
Create a new insurance policy for rider

**Endpoint:** `POST /policies`

**Headers:**
```
Authorization: Bearer {token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "tier": "standard",
  "start_date": "2026-04-07",
  "end_date": "2026-04-14"
}
```

**Parameters:**
- `tier` (string) - Policy tier:
  - "basic" (₹29/week, ₹50K coverage)
  - "standard" (₹79/week, ₹90K coverage)
  - "premium" (₹99/week, ₹150K coverage)
  - "elite" (₹120/week, ₹200K coverage)
- `start_date` (string, ISO format) - Week start
- `end_date` (string, ISO format) - Week end

**Response (201 Created):**
```json
{
  "policy_id": "660e8400-e29b-41d4-a716-446655440001",
  "rider_id": "550e8400-e29b-41d4-a716-446655440000",
  "tier": "standard",
  "weekly_premium": 79,
  "coverage": 90000,
  "status": "active",
  "activated_at": "2026-04-04T10:00:00Z",
  "week_starts": "2026-04-07",
  "week_ends": "2026-04-14",
  "url": "/policies/660e8400-e29b-41d4-a716-446655440001"
}
```

---

### Get Rider Policies
Get all active policies for current rider

**Endpoint:** `GET /policies/me`

**Headers:**
```
Authorization: Bearer {token}
```

**Query Parameters:**
- `status` (string, optional) - Filter by status: "active", "paused", "expired"

**Response (200 OK):**
```json
{
  "policies": [
    {
      "policy_id": "660e8400-e29b-41d4-a716-446655440001",
      "tier": "standard",
      "weekly_premium": 79,
      "coverage": 90000,
      "status": "active",
      "week_starts": "2026-04-07",
      "week_ends": "2026-04-14",
      "claims_count": 2,
      "total_claimed": 1050
    }
  ],
  "total_active": 1,
  "total_coverage": 90000,
  "total_weekly_cost": 79
}
```

---

### Get Policy Details
Get detailed policy information

**Endpoint:** `GET /policies/{policy_id}`

**Headers:**
```
Authorization: Bearer {token}
```

**Path Parameters:**
- `policy_id` (string, UUID) - Policy ID

**Response (200 OK):**
```json
{
  "policy_id": "660e8400-e29b-41d4-a716-446655440001",
  "rider_id": "550e8400-e29b-41d4-a716-446655440000",
  "tier": "standard",
  "weekly_premium": 79,
  "coverage": 90000,
  "status": "active",
  "activated_at": "2026-04-04T10:00:00Z",
  "week_starts": "2026-04-07",
  "week_ends": "2026-04-14",
  "rider_profile": {
    "zone": "whitefield",
    "vehicle": "two_wheeler",
    "age": 28
  },
  "claims": [
    {
      "claim_id": "770e8400-e29b-41d4-a716-446655440002",
      "event": "heavy_rainfall",
      "amount": 525,
      "status": "settled"
    }
  ]
}
```

---

### Simulate Policy Payout
Calculate payout for a hypothetical disruption scenario

**Endpoint:** `GET /policies/{policy_id}/simulate`

**Headers:**
```
Authorization: Bearer {token}
```

**Query Parameters:**
- `event_type` (string) - Event type: "rain", "aqi", "volume_drop"
- `severity` (number) - Severity level 1-10
- `duration_hours` (number) - Duration in hours

**Example:**
```
GET /policies/660e8400-e29b-41d4-a716-446655440001/simulate?event_type=rain&severity=8&duration_hours=4
```

**Response (200 OK):**
```json
{
  "scenario": "Heavy rainfall (45mm) for 4 hours in Whitefield",
  "policy_tier": "standard",
  "coverage_limit": 90000,
  "calculation": {
    "base_hourly_earnings": 410,
    "disruption_hours": 4,
    "disruption_weight": 2.0,
    "zone_impact_factor": 0.87,
    "coverage_factor": 0.70,
    "formula": "410 × 2.0 × 0.87 × 0.70",
    "calculated_payout": 500.58,
    "within_limit": true,
    "final_payout": 500.58
  },
  "note": "This is a simulation. Actual payout depends on fraud verification."
}
```

---

### Pause Policy
Temporarily pause a policy

**Endpoint:** `PUT /policies/{policy_id}/pause`

**Headers:**
```
Authorization: Bearer {token}
```

**Response (200 OK):**
```json
{
  "policy_id": "660e8400-e29b-41d4-a716-446655440001",
  "status": "paused",
  "paused_at": "2026-04-04T12:00:00Z",
  "message": "Policy paused. You will not receive claims for this period."
}
```

---

### Resume Policy
Resume a paused policy

**Endpoint:** `PUT /policies/{policy_id}/resume`

**Headers:**
```
Authorization: Bearer {token}
```

**Response (200 OK):**
```json
{
  "policy_id": "660e8400-e29b-41d4-a716-446655440001",
  "status": "active",
  "resumed_at": "2026-04-04T14:00:00Z",
  "message": "Policy resumed. Coverage is active."
}
```

---

## Claims Endpoints

### Get Rider Claims
Get all claims for current rider

**Endpoint:** `GET /claims/me`

**Headers:**
```
Authorization: Bearer {token}
```

**Query Parameters:**
- `status` (string, optional) - Filter: "detected", "approved", "paid", "rejected"
- `limit` (integer, default: 20) - Number of results
- `offset` (integer, default: 0) - Pagination offset

**Response (200 OK):**
```json
{
  "claims": [
    {
      "claim_id": "770e8400-e29b-41d4-a716-446655440002",
      "policy_id": "660e8400-e29b-41d4-a716-446655440001",
      "event_type": "heavy_rainfall",
      "zone": "whitefield",
      "status": "settled",
      "amount": 525,
      "coverage_limit": 90000,
      "created_at": "2026-04-04T08:00:00Z",
      "approved_at": "2026-04-04T08:00:45Z",
      "paid_at": "2026-04-04T08:01:15Z"
    }
  ],
  "total": 5,
  "total_claimed": 2750
}
```

---

### Get Claim Details
Get detailed information about a specific claim

**Endpoint:** `GET /claims/{claim_id}`

**Headers:**
```
Authorization: Bearer {token}
```

**Path Parameters:**
- `claim_id` (string, UUID) - Claim ID

**Response (200 OK):**
```json
{
  "claim_id": "770e8400-e29b-41d4-a716-446655440002",
  "policy_id": "660e8400-e29b-41d4-a716-446655440001",
  "rider_id": "550e8400-e29b-41d4-a716-446655440000",
  "event": {
    "type": "heavy_rainfall",
    "zone": "whitefield",
    "detected_at": "2026-04-04T08:00:00Z",
    "description": "45mm rainfall detected in Whitefield zone"
  },
  "fraud_check": {
    "status": "passed",
    "layers": {
      "gps_verification": {
        "status": "passed",
        "score": 15,
        "details": "Rider location history confirms presence in Whitefield"
      },
      "weather_correlation": {
        "status": "passed",
        "score": 12,
        "details": "Weather API confirms 45mm rainfall at coordinates"
      },
      "earnings_validation": {
        "status": "passed",
        "score": 8,
        "details": "Earnings disruption matches weather severity"
      },
      "cluster_analysis": {
        "status": "passed",
        "score": 5,
        "details": "Claim pattern consistent with peer group"
      }
    },
    "total_score": 40,
    "confidence": "100%"
  },
  "payout": {
    "calculation": "410 × 2.0 × 0.87 × 0.70",
    "base_earnings": 410,
    "disruption_weight": 2.0,
    "zone_factor": 0.87,
    "coverage_factor": 0.70,
    "gross_payout": 500.58,
    "coverage_limit": 90000,
    "final_payout": 500.58,
    "currency": "INR"
  },
  "settlement": {
    "status": "settled",
    "upi_account": "rider****@okhdfcbank",
    "sent_at": "2026-04-04T08:01:15Z",
    "confirmed_at": "2026-04-04T08:02:33Z",
    "transaction_id": "upi123456789"
  },
  "timeline": [
    {"event": "disruption_detected", "time": "2026-04-04T08:00:00Z"},
    {"event": "claim_created", "time": "2026-04-04T08:00:15Z"},
    {"event": "fraud_check_passed", "time": "2026-04-04T08:00:45Z"},
    {"event": "payout_initiated", "time": "2026-04-04T08:01:00Z"},
    {"event": "funds_sent", "time": "2026-04-04T08:01:15Z"},
    {"event": "confirmed", "time": "2026-04-04T08:02:33Z"}
  ]
}
```

---

## Triggers Endpoints

### Simulate Event Trigger
Trigger a test disruption event (admin/demo only)

**Endpoint:** `POST /triggers/simulate`

**Headers:**
```
Authorization: Bearer {token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "event_type": "heavy_rainfall",
  "zone_id": "whitefield",
  "severity": 8,
  "duration_hours": 4
}
```

**Parameters:**
- `event_type` (string) - "heavy_rainfall", "high_aqi", "order_volume_drop"
- `zone_id` (string) - Bengaluru zone
- `severity` (number) - 1-10 scale
- `duration_hours` (number) - Event duration

**Response (200 OK):**
```json
{
  "event_id": "880e8400-e29b-41d4-a716-446655440003",
  "type": "heavy_rainfall",
  "zone": "whitefield",
  "severity": 8,
  "duration_hours": 4,
  "claims_created": 12,
  "claims_details": [
    {
      "claim_id": "770e8400-e29b-41d4-a716-446655440002",
      "rider_id": "550e8400-e29b-41d4-a716-446655440000",
      "payout": 525,
      "status": "settled"
    }
  ],
  "message": "Event simulation completed. Claims processed automatically."
}
```

---

## Admin Endpoints

### Get Analytics Dashboard
Get platform analytics for insurer

**Endpoint:** `GET /admin/analytics/dashboard`

**Headers:**
```
Authorization: Bearer {admin_token}
```

**Response (200 OK):**
```json
{
  "dashboard": {
    "overview": {
      "total_riders": 127,
      "active_policies": 89,
      "active_coverage": 7250000,
      "total_claims_this_month": 45
    },
    "financial": {
      "total_premiums_collected": 35460,
      "claims_paid": 22340,
      "claims_ratio": 0.63,
      "gross_revenue": 13120
    },
    "by_zone": {
      "whitefield": {
        "riders": 34,
        "policies": 28,
        "claims": 12,
        "avg_payout": 485
      }
    },
    "fraud_metrics": {
      "total_checked": 45,
      "passed": 43,
      "rejected": 2,
      "detection_rate": 0.98
    },
    "payout_speed": {
      "avg_time_to_payout": 52,
      "fastest": 28,
      "slowest": 89,
      "unit": "seconds"
    }
  }
}
```

---

## Error Handling

### Error Response Format
```json
{
  "detail": "Error message describing what went wrong",
  "status": 400,
  "type": "validation_error"
}
```

### Common Error Codes

| Code | Message | Cause |
|------|---------|-------|
| 400 | Invalid phone number format | Phone not 10 digits |
| 400 | Invalid OTP | OTP wrong or expired |
| 401 | Invalid token | Missing or expired JWT |
| 403 | Insufficient permissions | Admin endpoint as user |
| 404 | Resource not found | Policy/claim doesn't exist |
| 422 | Validation error | Invalid request body |
| 429 | Rate limit exceeded | Too many requests |
| 500 | Internal server error | Backend error |

### Example Error Responses

#### Invalid Phone Format
```json
{
  "detail": "Phone number must be 10 digits",
  "status": 400,
  "type": "validation_error"
}
```

#### Expired Token
```json
{
  "detail": "Token has expired. Please login again.",
  "status": 401,
  "type": "authentication_error"
}
```

#### Policy Not Found
```json
{
  "detail": "Policy not found",
  "status": 404,
  "type": "not_found"
}
```

---

## Rate Limiting

API requests are rate limited to:
- **Authentication endpoints:** 5 requests per minute
- **Regular endpoints:** 100 requests per minute
- **Admin endpoints:** 50 requests per minute

**Rate Limit Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1712228400
```

---

## Testing the API

### Using cURL

**Login:**
```bash
curl -X POST "http://127.0.0.1:8004/api/v1/auth/phone-login" \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "9949722949"}'
```

**Verify OTP (check terminal for OTP):**
```bash
curl -X POST "http://127.0.0.1:8004/api/v1/auth/verify-otp" \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "9949722949", "otp": "7382"}'
```

**Get Policies (with token):**
```bash
curl -X GET "http://127.0.0.1:8004/api/v1/policies/me" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Using Postman
1. Import collection from `postman/GigShield.postman_collection.json`
2. Create environment with `base_url` and `access_token` variables
3. Run through demo scenarios

---

## API Documentation Tool

Interactive API documentation available at:
- **Swagger UI:** http://127.0.0.1:8004/docs
- **ReDoc:** http://127.0.0.1:8004/redoc

---

**GigShield API - Production Ready**  
For questions or issues, check the [SETUP_GUIDE.md](./SETUP_GUIDE.md) troubleshooting section.
