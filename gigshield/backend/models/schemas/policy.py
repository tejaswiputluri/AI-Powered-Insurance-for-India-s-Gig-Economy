"""
Policy Pydantic Schemas — request/response validation.
"""

from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import date, datetime


class PolicyCreateRequest(BaseModel):
    """Create a new weekly policy."""
    tier: str = Field(..., pattern="^(basic|balanced|pro|aggressive)$")


class PolicyCreateResponse(BaseModel):
    """Response after policy creation."""
    policy_id: UUID
    week_start: date
    week_end: date
    premium_paise: int
    coverage_cap_paise: int
    tier: str
    coverage_factor: float


class PolicyResponse(BaseModel):
    """Full policy detail response."""
    id: UUID
    rider_id: UUID
    tier: str
    weekly_premium_paise: int
    coverage_cap_paise: int
    msc_threshold: int
    coverage_factor: float
    week_start_date: date
    week_end_date: date
    status: str
    premium_deduction_status: str
    created_at: datetime

    class Config:
        from_attributes = True


class SimulatorQuery(BaseModel):
    """Coverage simulator query parameters."""
    zone_id: str = Field(default="BTM_LAYOUT")
    disruption_hours: float = Field(default=4.0, ge=1.0, le=8.0)
    signal_count: int = Field(default=2, ge=2, le=3)


class SimulatorBreakdown(BaseModel):
    """Payout calculation breakdown."""
    baseline_hourly_paise: int
    disruption_hours: float
    zone_impact_factor: float
    coverage_factor: float
    formula: str = "BHE × DW × ZIF × CF"


class SimulatorResponse(BaseModel):
    """Coverage simulator result."""
    estimated_payout_paise: int
    breakdown: SimulatorBreakdown
