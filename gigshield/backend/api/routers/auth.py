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

router = APIRouter(prefix="/auth", tags=["auth"])


class VerifyTokenRequest(BaseModel):
    firebase_token: str


class AuthResponse(BaseModel):
    rider_id: str
    is_new_rider: bool
    access_token: str


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
