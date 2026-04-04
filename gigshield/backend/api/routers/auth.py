"""
Auth Router — /api/v1/auth endpoints.
Handles Firebase token verification and demo login.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from backend.config.settings import settings
from backend.api.middleware import create_access_token, DEMO_RIDER_UID, get_demo_rider_id
from backend.db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import random
import time

router = APIRouter(prefix="/auth", tags=["auth"])


class VerifyTokenRequest(BaseModel):
    firebase_token: str


class PhoneLoginRequest(BaseModel):
    phone_number: str
    otp: str = None


class AuthResponse(BaseModel):
    rider_id: str
    is_new_rider: bool
    access_token: str


# In-memory OTP storage (in production, use Redis or database)
_otp_store = {}


@router.post("/phone-login", response_model=AuthResponse)
async def phone_login(
    request: PhoneLoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Phone login with OTP verification.
    Step 1: Send OTP to phone
    Step 2: Verify OTP and login
    """
    from backend.models.db.rider import Rider

    phone = request.phone_number
    otp = request.otp

    if not otp:
        # Send OTP
        generated_otp = str(random.randint(1000, 9999))
        _otp_store[phone] = {
            'otp': generated_otp,
            'timestamp': time.time(),
            'attempts': 0
        }

        # In production, send SMS here
        print(f"📱 OTP for {phone}: {generated_otp}")

        raise HTTPException(
            status_code=200,
            detail={"code": "OTP_SENT", "message": "OTP sent to your phone"}
        )

    # Verify OTP
    if phone not in _otp_store:
        raise HTTPException(
            status_code=400,
            detail={"code": "OTP_EXPIRED", "message": "OTP expired or not sent"}
        )

    stored_data = _otp_store[phone]
    if time.time() - stored_data['timestamp'] > 300:  # 5 minutes
        del _otp_store[phone]
        raise HTTPException(
            status_code=400,
            detail={"code": "OTP_EXPIRED", "message": "OTP expired"}
        )

    if stored_data['attempts'] >= 3:
        del _otp_store[phone]
        raise HTTPException(
            status_code=429,
            detail={"code": "TOO_MANY_ATTEMPTS", "message": "Too many failed attempts"}
        )

    if stored_data['otp'] != otp:
        stored_data['attempts'] += 1
        raise HTTPException(
            status_code=400,
            detail={"code": "INVALID_OTP", "message": "Invalid OTP"}
        )

    # OTP verified, clean up
    del _otp_store[phone]

    # Find or create rider
    result = await db.execute(
        select(Rider).where(Rider.phone == phone)
    )
    rider = result.scalar_one_or_none()

    if not rider:
        # Create new rider
        rider = Rider(
            phone=phone,
            firebase_uid=f"phone_{phone}_{int(time.time())}",  # Temporary UID
            name="",
            zone_id="BTM_LAYOUT",  # Default zone
            platform="swiggy",  # Default platform
            work_hours_start=10,  # 10am
            work_hours_end=22,    # 10pm
            self_reported_daily_earning_paise=50000,  # ₹500 default
            upi_vpa="",
            is_active=True
        )
        db.add(rider)
        await db.commit()
        await db.refresh(rider)
        is_new = True
    else:
        is_new = False

    token = create_access_token(rider.id)
    return AuthResponse(
        rider_id=str(rider.id),
        is_new_rider=is_new,
        access_token=token,
    )


@router.post("/facebook-login", response_model=AuthResponse)
async def facebook_login(
    db: AsyncSession = Depends(get_db),
):
    """
    Facebook login using OAuth flow.
    In production, this would handle Facebook OAuth callback.
    For demo, simulate Facebook login.
    """
    from backend.models.db.rider import Rider

    # In production, verify Facebook access token
    # For demo, create/find rider with Facebook UID
    facebook_uid = f"fb_demo_{int(time.time())}"
    facebook_email = "demo@facebook.com"
    facebook_name = "Demo User"

    result = await db.execute(
        select(Rider).where(Rider.firebase_uid == facebook_uid)
    )
    rider = result.scalar_one_or_none()

    if not rider:
    # Create new rider
        rider = Rider(
            firebase_uid=facebook_uid,
            name=facebook_name,
            phone=f"fb_{int(time.time())}",  # Unique phone for Facebook users
            zone_id="BTM_LAYOUT",  # Default zone
            platform="swiggy",  # Default platform
            work_hours_start=10,  # 10am
            work_hours_end=22,    # 10pm
            self_reported_daily_earning_paise=50000,  # ₹500 default
            upi_vpa="",
            is_active=True
        )
        db.add(rider)
        await db.commit()
        await db.refresh(rider)
        is_new = True
    else:
        is_new = False

    token = create_access_token(rider.id)
    return AuthResponse(
        rider_id=str(rider.id),
        is_new_rider=is_new,
        access_token=token,
    )


@router.post("/verify-token", response_model=AuthResponse)
async def verify_token(
    request: VerifyTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Verify Firebase token → lookup rider → return GigShield JWT.
    """
    from backend.models.db.rider import Rider

    if settings.DEMO_MODE:
        # Skip Firebase, use demo rider
        result = await db.execute(
            select(Rider).where(Rider.firebase_uid == DEMO_RIDER_UID)
        )
        rider = result.scalar_one_or_none()

        if rider:
            token = create_access_token(rider.id)
            return AuthResponse(
                rider_id=str(rider.id),
                is_new_rider=False,
                access_token=token,
            )
        else:
            return AuthResponse(
                rider_id="",
                is_new_rider=True,
                access_token="",
            )

    # Production: Verify Firebase token
    try:
        import firebase_admin
        from firebase_admin import auth
        decoded = auth.verify_id_token(request.firebase_token)
        firebase_uid = decoded["uid"]
        phone = decoded.get("phone_number")
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail={"code": "INVALID_FIREBASE_TOKEN", "message": str(e)}
        )

    # Lookup rider
    result = await db.execute(
        select(Rider).where(Rider.firebase_uid == firebase_uid)
    )
    rider = result.scalar_one_or_none()

    if rider:
        token = create_access_token(rider.id)
        return AuthResponse(
            rider_id=str(rider.id),
            is_new_rider=False,
            access_token=token,
        )
    else:
        return AuthResponse(
            rider_id="",
            is_new_rider=True,
            access_token="",
        )


@router.post("/demo-login", response_model=AuthResponse)
async def demo_login():
    """
    Demo login — returns hardcoded demo rider without Firebase verification.
    Only available when DEMO_MODE=true.
    """
    if not settings.DEMO_MODE:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND"})

    demo_rider_id = get_demo_rider_id()
    if not demo_rider_id:
        raise HTTPException(
            status_code=503,
            detail={"code": "DEMO_NOT_READY", "message": "Demo rider not yet seeded"}
        )

    token = create_access_token(demo_rider_id)
    return AuthResponse(
        rider_id=str(demo_rider_id),
        is_new_rider=False,
        access_token=token,
    )
