"""
API Middleware — CORS configuration + Firebase JWT auth dependency.
In DEMO_MODE: auth is bypassed, demo rider credentials used.
"""

import logging
from typing import Optional
from uuid import UUID
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from backend.config.settings import settings

logger = logging.getLogger(__name__)

security = HTTPBearer(auto_error=False)

# Demo rider UUID (consistent across sessions)
DEMO_RIDER_UID = "demo-rider-uid-gigshield-2026"
_DEMO_RIDER_ID: Optional[UUID] = None  # Set after seeding


def set_demo_rider_id(rider_id: UUID):
    """Set the demo rider ID after DB seeding."""
    global _DEMO_RIDER_ID
    _DEMO_RIDER_ID = rider_id


def get_demo_rider_id() -> Optional[UUID]:
    """Get the current demo rider ID. Must be called as function so value is always fresh."""
    return _DEMO_RIDER_ID


# Backward compat: DEMO_RIDER_ID is now a property accessed via function
DEMO_RIDER_ID = property(lambda self: _DEMO_RIDER_ID)


async def get_current_rider_id(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> UUID:
    """
    Auth dependency — extracts rider_id from JWT or demo mode.
    """
    # Demo mode: bypass auth
    if settings.DEMO_MODE:
        demo_id = get_demo_rider_id()
        if demo_id:
            return demo_id
        raise HTTPException(
            status_code=503,
            detail={"code": "DEMO_NOT_SEEDED", "message": "Demo rider not yet seeded"}
        )

    # Production mode: verify JWT
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail={"code": "AUTH_REQUIRED", "message": "Authorization header required"}
        )

    token = credentials.credentials
    try:
        from jose import jwt
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=["HS256"],
        )
        rider_id = UUID(payload.get("rider_id"))
        return rider_id
    except Exception as e:
        logger.warning(f"JWT verification failed: {e}")
        raise HTTPException(
            status_code=401,
            detail={"code": "INVALID_TOKEN", "message": "Invalid or expired token"}
        )


async def get_insurer_auth(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> bool:
    """
    Insurer auth dependency. In demo mode, always grants access.
    """
    if settings.DEMO_MODE:
        return True

    if not credentials:
        raise HTTPException(
            status_code=401,
            detail={"code": "AUTH_REQUIRED", "message": "Insurer authorization required"}
        )

    # In production, verify insurer-specific JWT
    try:
        from jose import jwt
        payload = jwt.decode(
            credentials.credentials,
            settings.SECRET_KEY,
            algorithms=["HS256"],
        )
        if payload.get("role") != "insurer":
            raise HTTPException(status_code=403, detail={"code": "FORBIDDEN"})
        return True
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail={"code": "INVALID_TOKEN"})


def create_access_token(rider_id: UUID) -> str:
    """Create a JWT access token for a rider."""
    from jose import jwt
    from datetime import datetime, timezone, timedelta

    payload = {
        "rider_id": str(rider_id),
        "exp": datetime.now(timezone.utc) + timedelta(days=7),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
