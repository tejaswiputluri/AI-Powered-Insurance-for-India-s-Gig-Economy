"""
Rider Pydantic Schemas — request/response validation (RULE-08).
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from uuid import UUID
from datetime import datetime


# ─── Request Schemas ─────────────────────────────────────────────────────

class RiderOnboardRequest(BaseModel):
    """Step 2 of onboarding — PRF data collection (5 questions)."""
    name: str = Field(..., min_length=2, max_length=100)
    zone_id: str = Field(..., description="Must exist in zones.json")
    platform: str = Field(..., pattern="^(swiggy|zomato|dunzo)$")
    work_hours_start: int = Field(..., ge=0, le=23)
    work_hours_end: int = Field(..., ge=0, le=23)
    work_days_per_week: int = Field(..., ge=1, le=7)
    self_reported_daily_earning: int = Field(
        ..., ge=100, le=10000,
        description="Daily earning in RUPEES (we convert to paise)"
    )

    @field_validator("work_hours_end")
    @classmethod
    def validate_work_hours(cls, v, info):
        start = info.data.get("work_hours_start")
        if start is not None and v <= start:
            raise ValueError("work_hours_end must be greater than work_hours_start")
        return v


class RiderLocationQuery(BaseModel):
    """GPS location query for zone matching."""
    lat: float = Field(..., ge=10.0, le=20.0, description="Latitude")
    lon: float = Field(..., ge=70.0, le=85.0, description="Longitude")


class RiderUPIUpdate(BaseModel):
    """Update rider's UPI VPA for payouts."""
    upi_vpa: str = Field(..., min_length=5, max_length=100, pattern="^[a-zA-Z0-9._-]+@[a-zA-Z]+$")


# ─── Response Schemas ────────────────────────────────────────────────────

class XAIFactor(BaseModel):
    """Explainable AI factor from FT-Transformer attention weights."""
    factor: str
    weight: float
    label: str


class PolicyTierOption(BaseModel):
    """A policy tier available to the rider."""
    tier: str
    name: str
    weekly_premium_paise: int
    coverage_cap_paise: int
    msc_threshold: int
    coverage_factor: float
    description: str
    recommended: bool = False


class RiderOnboardResponse(BaseModel):
    """Response after successful onboarding with ML premium."""
    rider_id: UUID
    computed_premium_paise: int
    xai_factors: list[XAIFactor]
    tier_options: list[PolicyTierOption]


class RiderProfileResponse(BaseModel):
    """Full rider profile response."""
    id: UUID
    phone: str
    name: Optional[str]
    zone_id: str
    platform: str
    work_hours_start: int
    work_hours_end: int
    work_days_per_week: int
    self_reported_daily_earning_paise: int
    computed_weekly_premium_paise: Optional[int]
    xai_factors: Optional[dict]
    upi_vpa: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ZoneMatchResponse(BaseModel):
    """Zone matching result from GPS coordinates."""
    zone_id: str
    zone_name: str
    within_active_zone: bool
